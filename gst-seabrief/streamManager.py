import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer
from pypylon import pylon
from uuid import uuid4 as uuid

class StreamManager:

    def __init__(self):
        self.streams = dict()
        self.server = self.__create_server()

    def __create_server(self):
        server = GstRtspServer.RTSPServer.new()
        server.set_service(str('5050'))
        server.attach()
        return server
    
    def create_stream(self, source: str, device: str) -> str:
        id = uuid()
        
        if source == 'test':
            stream = self.__create_test_stream()

        elif source == 'v4l2':
            # Default to /dev/video0
            if device is None:
                device = '/dev/video0'
            stream = self.__create_v4l2_stream(device)
        
        elif source == 'basler':
            stream = self.__create_basler_stream(device)
        
        else:
            raise Exception(f"No source type \"{source}\" supported")
        
        self.server.get_mount_points().add_factory(f"/{id}", stream)
        self.streams[id] = input
        self.server.attach()
        return id

    
    def list_devices(self):
        return []
    
    def __create_test_stream(self):
        pipeline = "videotestsrc ! x264enc ! rtph264pay pt=96 name=pay0"
        return self.__make_factory(pipeline)
    

    def __create_v4l2_stream(self, device: str):
        pipeline = f"v4l2src device={device} ! nvv4l2decoder mjpeg=1 enable-max-performance=true disable-dpb=true ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0"
        return self.__make_factory(pipeline)


    def __format_basler_device_string(self, device: str):
        if device is None:
            return ''
        return f"device-serial-number={device}"


    def __create_basler_stream(self, device: str):
        pipeline = f"pylonsrc {self.__format_basler_device_string(device)} ! video/x-raw, width=1280 , height=720, format=(string)YUY2, framerate=60/1 ! nvvidconv ! nvv4l2h264enc enable-full-frame=true ! rtph264pay pt=96 name=pay0"
        return self.__make_factory(pipeline)


    def __make_factory(self, pipeline: str):
        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(pipeline)
        factory.set_shared(True)

        return factory