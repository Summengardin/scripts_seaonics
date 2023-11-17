#!./venv/bin/python3

# TO DISPLAY: gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test ! rtph264depay  ! autovideosink

#gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test ! rtph264depay ! h264parse ! nvv4l2decoder enable-max-performance=1 ! fakevideosink sync=0

# gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test ! fakesink dump=1

# DISPLAY THAT WORKS:
# launch_str_4
# gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test latency=0 ! rtph264depay ! h264parse ! nvv4l2decoder enable-max-performance=1 ! nvvidconv ! autovideosink sync=0

import time
import gi
import numpy as np
import gentl_cam_grab as camgrab
import cv2

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer

Gst.debug_set_active(False)
Gst.debug_set_default_threshold(0)

Gst.init(None)

W = 640
H = 480
FPS_PRINT_INTERVAL = 1

class RTSPServer:
    def __init__(self, port="8554", mount_point="/test", no_cam = False, test_src = False, W=W, H=H):
        self.server = GstRtspServer.RTSPServer.new()
        self.server.set_service(port)
        self.mounts = self.server.get_mount_points()
        self.factory = GstRtspServer.RTSPMediaFactory.new()
        self.no_cam = no_cam
        
        self.pts = 0
        
        self.time_per_frame = Gst.SECOND / 30  # Assuming 30 fps
        self.current_pts = 0
        
        self.H = H
        self.W = W
        
        if not no_cam:
            self.cam_grabber = camgrab.CamGrabber(W=self.W, H=self.H)

        # Set up the pipeline
        
        test_str = ("videotestsrc is-live=true ! nvvidconv ! nvv4l2h264enc ! rtph264pay config-interval=1 pt=96 name=pay0")
        
        launch_str = (
            "appsrc name=source emit-signals=True is-live=True block=True format=GST_FORMAT_TIME "
            "caps=video/x-raw,format=BayerBG8,width=640,height=480,framerate=30/1 ! "
            "queue leaky=upstream max-size-buffers=6 max-size-time=0 max-size-bytes=0 ! "
            "videoconvert ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0"

            )
        
        launch_str_1 = ("appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ! video/x-raw, width=1280 , height=720, format=RGB framerate=60/1 ! nvvidconv ! nvv4l2h264enc enable-full-frame=true ! rtph264pay pt=96 name=pay0")
        
        launch_str_2_WORKING = (
            "appsrc name=source is-live=true block=true format=GST_FORMAT_TIME " 
            "caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 "
            "! videoconvert "
            "! video/x-raw,format=I420 " 
            "! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay config-interval=1 name=pay0 pt=96"
        )
        
        launch_str_3 = ( "appsrc name=source is-live=true block=true format=GST_FORMAT_TIME " 
            "caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 "
            "! nvvidconv "
            "! nvh264enc " 
            "! rtph264pay pt=96 name=pay0"
        )
                
        
        launch_str_4_WORKING = (f"appsrc name=source is-live=true block=true format=GST_FORMAT_TIME "
    f"caps=video/x-raw,width={W},height={H},framerate=30/1,format=RGB "
    "! videoconvert "
    "! nvvidconv "
    "! nvv4l2h264enc "
    "! rtph264pay config-interval=1 pt=96 name=pay0")

        
        launch_str_5 = (" appsrc name=source is-live=true format=GST_FORMAT_TIME "
                        "caps=video/x-raw, width=(int)1280 , height=(int)720, format=(string)BGR, framerate=(fraction)30/1 "
                        
                        
                        "! nvvidconv "
                        "! nvv4l2h264enc"
                        "! rtph264pay config-interval=1 pt=96 name=pay0")
        
        
        
        if test_src:
            self.factory.set_launch(test_str)
        else:
            self.factory.set_launch(launch_str_4_WORKING)
        
    

        self.mounts.add_factory(mount_point, self.factory)
        self.server.attach()

        # Set up the main loop
        self.loop = GLib.MainLoop()
        self.context = self.loop.get_context()

        # Set up the appsrc
        self.source = None
        self.factory.connect('media-configure', self.on_media_configure)
        
        self.last_fps_print_time = time.time()
        self.fps_counter = 0    

    def on_media_configure(self, factory, media):
        self.source = media.get_element().get_child_by_name('source')
        if self.source:
            self.source.connect('need-data', self.on_need_data)
            
        print("Media configured")
        #GLib.timeout_add(33, self.feed_frame)

    def on_need_data(self, src, length):
        self.feed_frame(src)
        return True
    
    def dummy_frame(self): 
        # Generate a dummy frame

        # Background
        frame = np.full((self.H, self.W, 3), (25, 83, 95), dtype=np.uint8)
        
        # setup text
        font = cv2.FONT_HERSHEY_DUPLEX
        text = "No frame available"
        font_scale = 1.5
        font_thickness = 2

        # get boundary of this text
        textsize = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

        # get coords based on boundary
        textX = (frame.shape[1] - textsize[0]) / 2
        textY = (frame.shape[0] + textsize[1]) / 2
        
        # add text centered on image
        cv2.putText(frame, text, (int(textX), int(textY) ), font, font_scale, (240, 243, 245), font_thickness)
        return frame
    
    def feed_frame(self, src):
        # Retrieve and push frames here
        # As an example, generate a dummy numpy array
        if not self.no_cam:
            frame = self.cam_grabber.get_newest_frame()
            self.fps_counter += 1
        else:
            frame = None
        
        
        if frame is None:
            frame = self.dummy_frame()
        else:
            self.fps_counter, self.last_fps_print_time = self.__print_fps(self.fps_counter, self.last_fps_print_time)
        
        data = frame.tobytes()
        
        if data is None:
            src.emit('end-of-stream')
            return False

        #buf = Gst.Buffer.new_allocate(None, len(data), None)
        #buf.fill(0, data)      
        
        # convert np.ndarray to Gst.Buffer
        gst_buffer = Gst.Buffer.new_wrapped(data)
        
         # Set buffer PTS and duration
        gst_buffer.pts = self.current_pts
        gst_buffer.duration = self.time_per_frame
        self.current_pts += self.time_per_frame  
        
        retval = src.emit('push-buffer', gst_buffer)
        if retval != Gst.FlowReturn.OK:
            print("Error pushing buffer")
        return True  # Return True to keep the timeout active

    def start(self):
        print(f"Starting RTSP server on port {self.server.get_service()}")
        try:
            self.loop.run()
        except KeyboardInterrupt:
            pass  # Allow clean exit on Ctrl+C

    def stop(self):
        if not self.no_cam:
            self.cam_grabber.stop()
        self.loop.quit()
        print("RTSP server stopped")
        
        
    def __print_fps(self, fps_counter: int ,last_print_time: float):
        if (time.time() - last_print_time) > FPS_PRINT_INTERVAL:
            last_print_time = time.time()
            print(f"Streamer FPS: {fps_counter/FPS_PRINT_INTERVAL}")
            fps_counter = 0
            
        return fps_counter, last_print_time

        
        
if __name__ == "__main__":
    # Usage:
    server = RTSPServer(no_cam=False, test_src=False)
    try:
        server.start()
    except Exception as e:
        print(f"An error occurred: {e}")

    server.stop()