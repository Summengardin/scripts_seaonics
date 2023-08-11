import sys
import gi
from rtspStreamFactory import create_stream
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
    
    def create_stream(self, input: str):
        id = uuid()
        stream = create_stream()
        self.server.get_mount_points().add_factory(f"/{id}", stream)
        self.streams[id] = input
        self.server.attach()
        return id
    
    def list_devices(self):
        return []