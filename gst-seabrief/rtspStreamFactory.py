import gi
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GstRtspServer
from pypylon import pylon
from os import listdir
from os.path import isdir
from re import findall
import cv2 

class RTSPStreamFactory:
    def __init__(self):
        self.__v4_devices = self.__list_v4l_devices()
        self.__basler_devices = self.__list_basler_devices()

    def list_v4l_devices(self):
        return self.__v4_devices
    
    def list_basler_devices(self):
        return self.__basler_devices

    def __list_v4l_devices(self):
        devices = []
        if isdir('/sys/class/video4linux/'):
            for device in listdir('/sys/class/video4linux/'):
                device_name = open(f"/sys/class/video4linux/{device}/name").read()
                with open(f"/sys/class/video4linux/{device}/uevent") as file:
                    paths = findall("video\d", file.read())
                    for path in paths:
                        # TODO find out how to validate that a path/camera works
                        path = f"/dev/{path}"
                        cam = cv2.VideoCapture(path)
                        if cam.isOpened():
                            devices.append({'model': device_name, 'path': path})
        return devices
    
    def __list_basler_devices(self):        
        tlFactory = pylon.TlFactory.GetInstance()
        devices = tlFactory.EnumerateDevices()
        devices = [{'serial_number': x.GetSerialNumber(), 'model': x.GetModelName()} for x in devices]
        return devices


    def create_test_stream(self):
        pipeline = "videotestsrc ! x264enc ! rtph264pay pt=96 name=pay0"
        return self.__make_factory(pipeline)
    

    def create_v4l2_stream(self, device: str):
        if not any([x['path'] == device for x in self.__v4_devices]):
            raise Exception(f'Cannot start stream for device "{device}" as it is not found')
        pipeline = f"v4l2src device={device} ! nvv4l2decoder mjpeg=1 enable-max-performance=true disable-dpb=true ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0"
        return self.__make_factory(pipeline)


    def __format_basler_device_string(self, device: str):
        if device is None:
            return ''
        return f"device-serial-number={device}"


    def create_basler_stream(self, device: str or None):
        if device is not None and not any([x['serial_number'] == device for x in self.__basler_devices]):
            raise Exception(f'Cannot start stream for device "{device}" as it is not found')
        pipeline = f"pylonsrc {self.__format_basler_device_string(device)} ! video/x-raw, width=1280 , height=720, format=(string)YUY2, framerate=60/1 ! nvvidconv ! nvv4l2h264enc enable-full-frame=true ! rtph264pay pt=96 name=pay0"
        return self.__make_factory(pipeline)


    def __make_factory(self, pipeline: str):
        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(pipeline)
        factory.set_shared(True)

        return factory