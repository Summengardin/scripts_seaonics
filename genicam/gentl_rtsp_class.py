import time
import gi
import numpy as np
import gentl_cam_grab as camgrab

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer

Gst.debug_set_active(False)
Gst.debug_set_default_threshold(3)

Gst.init(None)

class RTSPServer:
    def __init__(self, port="8554", mount_point="/test"):
        self.server = GstRtspServer.RTSPServer.new()
        self.server.set_service(port)
        self.mounts = self.server.get_mount_points()
        self.factory = GstRtspServer.RTSPMediaFactory.new()
        
        self.cam_grabber = camgrab.CamGrabber()

        # Set up the pipeline
        
        test_str = ("videotestsrc ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0")
        
        launch_str = (
            "appsrc name=source emit-signals=True is-live=True block=True format=GST_FORMAT_TIME "
            "caps=video/x-raw,format=BayerBG8,width=640,height=480,framerate=30/1 ! "
            "queue leaky=upstream max-size-buffers=6 max-size-time=0 max-size-bytes=0 ! "
            "videoconvert ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0"

            )
        
        launch_str_1 = ("appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ! video/x-raw, width=1280 , height=720, format=RGB framerate=60/1 ! nvvidconv ! nvv4l2h264enc enable-full-frame=true ! rtph264pay pt=96 name=pay0")
        
        launch_str_2 = (
            "appsrc name=source is-live=true block=true format=GST_FORMAT_TIME " 
            "caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! videoconvert ! video/x-raw,format=I420 " 
            "! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay config-interval=1 name=pay0 pt=96"
        )
        
        self.factory.set_launch(launch_str)
        
    

        self.mounts.add_factory(mount_point, self.factory)
        self.server.attach()

        # Set up the main loop
        self.loop = GLib.MainLoop()
        self.context = self.loop.get_context()

        # Set up the appsrc
        self.source = None
        self.factory.connect('media-configure', self.on_media_configure)

    def on_media_configure(self, factory, media):
        self.source = media.get_element().get_child_by_name('source')
        if self.source:
            self.source.connect('need-data', self.on_need_data)
        #GLib.timeout_add(33, self.feed_frame)

    def on_need_data(self, src, length):
        self.feed_frame(src)
        return True
    
    def feed_frame(self, src):
        # Retrieve and push frames here
        # As an example, generate a dummy numpy array
        frame = self.cam_grabber.get_newest_frame()
        
        if frame is None:
            return True
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        print(frame.shape)
        data = frame.tobytes()

        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        
        
        retval = src.emit('push-buffer', buf)
        if retval != Gst.FlowReturn.OK:
            print("Error pushing buffer")
        return True  # Return True to keep the timeout active

    def start(self):
        print("Starting RTSP server")
        try:
            self.loop.run()
        except KeyboardInterrupt:
            pass  # Allow clean exit on Ctrl+C

    def stop(self):
        self.cam_grabber.stop()
        self.loop.quit()
        print("RTSP server stopped")

        
        
if __name__ == "__main__":
    # Usage:
    server = RTSPServer()
    try:
        server.start()
    except Exception as e:
        print(f"An error occurred: {e}")
        
    server.stop()