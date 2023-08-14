import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer
from uuid import uuid4 as uuid
import os
from time import time
from threading import Timer
from typing import Dict, Callable
from pypylon import pylon
from os import listdir
from os.path import isdir
from re import findall
import cv2 
from pipelineBuilder import PipelineConfig, PipelineBuilder

class Stream:
    t: Timer = None

    def __init__(self, terminate_func: Callable[[], None], config: PipelineConfig):
        self.__terminate_func = terminate_func
        self.config = config
        self.__reset_timer()
        
    def __reset_timer(self):
        self.last_healthcheck = time()
        if self.t is not None:
            self.t.cancel()
        t = Timer(60, self.__terminate_func)
        t.start()
        self.t = t
        
    def ping(self):
        self.__reset_timer()



class StreamManager:
    def __init__(self):
        self.__streams: Dict[str, Stream] = dict()
        self.server = self.__create_server()
        self.timer = self.__refresh_devices()

    def __create_timer(self):
        t = Timer(30, self.__refresh_devices)
        t.start()

    def __refresh_devices(self):
        self.__v4l_devices = self.__list_v4l_devices()
        self.__basler_devices = self.__list_basler_devices()
        self.timer = self.__create_timer()


    def __create_server(self):
        server = GstRtspServer.RTSPServer.new()
        server.set_service(str(os.environ.port))
        server.attach()
        return server
    
    def create_stream(self, config: PipelineConfig) -> str:
        # Check if device is already streaming
        id = self.__check_device_active(config)
        if id is not None:
            return id
        id = str(uuid())

        if config.source == 'basler' and not any([x['serial_number'] == config.device for x in self.__basler_devices]):
            raise Exception(f'Cannot create stream with device {config.device} as it is not found')
        if config.source == 'v4l2' and not any([x['path'] == config.device for x in self.__v4l_devices]):
            raise Exception(f'Cannot create stream with device {config.device} as it is not found')

        stream = self.__make_factory(PipelineBuilder.build(config))
        self.server.get_mount_points().add_factory(f"/{id}", stream)

        def terminate():
            self.server.get_mount_points().remove_factory(f"/{id}")
            del self.__streams[id]
        
        self.__streams[id] = Stream(terminate, config)
        self.server.attach()
        return id

    def __check_device_active(self, config: PipelineConfig) -> str or None:
        for k, v in self.__streams.items():
            if v.config.source == config.source and v.config.device == config.device:
                return k
        return None
    
    def ping_stream(self, stream: str) -> bool:
        if self.__streams.get(stream) is None:
            return False
        self.__streams[stream].ping()
        return True

    def __list_v4l_devices(self):
        devices = []
        if isdir('/sys/class/video4linux/'):
            for device in listdir('/sys/class/video4linux/'):
                device_name = open(f"/sys/class/video4linux/{device}/name").read()
                with open(f"/sys/class/video4linux/{device}/uevent") as file:
                    paths = findall("video\d", file.read())
                    for path in paths:
                        # TODO find out how to validate that a path/camera works that works better than this
                        path = f"/dev/{path}"
                        cam = cv2.VideoCapture(path)
                        if cam.isOpened() or any([x.config.device == path for x in self.__streams.values()]):
                            devices.append({'model': device_name, 'path': path})
        return devices
    
    def __list_basler_devices(self):        
        tlFactory = pylon.TlFactory.GetInstance()
        devices = tlFactory.EnumerateDevices()
        devices = [{'serial_number': x.GetSerialNumber(), 'model': x.GetModelName()} for x in devices]
        return devices
    
    def __make_factory(self, pipeline: str):
        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(pipeline)
        factory.set_shared(True)

        return factory
    
    def list_basler_devices(self):
        return self.__basler_devices
    
    def list_v4l_devices(self):
        return self.__v4l_devices