#!/bin/usr/python3

import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer

try:
    source = sys.argv[1]
except:
    source = "test"

print(source)

class VideoServerRTSP:

    def __init__(self):

        self.loop = self._generate_gst_rtsp_server()
        self.loop.run()

    def _generate_gst_rtsp_server(self):

        Gst.init(None)

        if source == "usb_cam":
            pipeline = "v4l2src device=/dev/video0 ! mjpeg=1 enable-max-performance=true disable-dpb=true ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0"
        elif source == "basler":
            #pipeline = "pylonsrc ! video/x-raw(memory:NVMM), width=1280 , height=720 ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0"
            pipeline = "pylonsrc ! video/x-raw, width=1280 , height=720, format=(string)YUY2, framerate=60/1 ! nvvidconv ! nvv4l2h264enc enable-full-frame=true ! rtph264pay pt=96 name=pay0"
        elif source == "test":
            pipeline = "videotestsrc ! x264enc ! rtph264pay pt=96 name=pay0"
        else:
            raise Exception(f"Invalid video source : {source}")

        #pipeline = "v4l2src device=/dev/video0 ! videoconvert ! videoscale ! video/x-raw,width=[1,640],height=[1,480] ! x264enc tune=zerolatency bitrate=250 ! rtph264pay pt=96 name=pay0"
        

        server = GstRtspServer.RTSPServer.new()
        server.set_service(str('5050'))
        mounts = server.get_mount_points()

        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(pipeline)
        factory.set_shared(True)
        mounts.add_factory('/test', factory)

        server.attach()
        loop = GLib.MainLoop()

        print("Ret loop")
        return loop


if __name__ == '__main__':
    print("Runnin")
    server = VideoServerRTSP()