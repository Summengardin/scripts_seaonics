import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer
from uuid import uuid4 as uuid
from rtspStreamFactory import RTSPStreamFactory
import os
from time import time
from threading import Timer
from typing import Dict, Callable


class Stream:
    t: Timer = None

    def __init__(self, terminate_func: Callable[[], None], source: str, device: str):
        self.__terminate_func = terminate_func
        self.source = source
        self.device = device
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



class StreamManager(RTSPStreamFactory):

    def __init__(self):
        super().__init__()
        self.__streams: Dict[str, Stream] = dict()
        self.server = self.__create_server()
        
    def __create_server(self):
        server = GstRtspServer.RTSPServer.new()
        server.set_service(str(os.environ.port))
        server.attach()
        return server
    
    def create_stream(self, source: str, device: str) -> str:
        # Default to /dev/video0 for v4l2
        if source == 'v4l2' and device is None:
            device = '/dev/video0'

        # Check if device is already streaming
        id = self.__check_device_active(source, device)
        if id is not None:
            return id
        id = str(uuid())

        if source == 'test':
            stream = self.create_test_stream()

        elif source == 'v4l2':
            stream = self.create_v4l2_stream(device)
        
        elif source == 'basler':
            stream = self.create_basler_stream(device)
        
        else:
            raise Exception(f"No source type \"{source}\" supported")
        
        self.server.get_mount_points().add_factory(f"/{id}", stream)

        def terminate():
            self.server.get_mount_points().remove_factory(f"/{id}")
            del self.__streams[id]
        
        self.__streams[id] = Stream(terminate, source, device)
        self.server.attach()
        return id

    def __check_device_active(self, source: str, device: str) -> str or None:
        for k, v in self.__streams.items():
            if v.source == source and v.device == device:
                return k
        return None
    
    def ping_stream(self, stream: str) -> bool:
        if self.__streams.get(stream) is None:
            return False
        self.__streams[stream].ping()
        return True
