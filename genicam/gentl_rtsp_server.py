#!./venv/bin/python3

# TO DISPLAY: gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test ! rtph264depay  ! autovideosink

#gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test ! rtph264depay ! h264parse ! nvv4l2decoder enable-max-performance=1 ! fakevideosink sync=0

# gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test ! fakesink dump=1

# DISPLAY THAT WORKS:
# launch_str_4
# gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test latency=0 ! rtph264depay ! h264parse ! nvv4l2decoder enable-max-performance=1 ! nvvidconv ! autovideosink sync=0


'''
NOTE-TO-SELF:

1.des.23
(Nesten) alt funker
    - Stream
    - Display (kan skifte mellom kameraer)
    - Kamera kan plugges ut
    - Server kan stoppes og startes igjen, clinten reconnecter
Utenom det
    - Om klienten kobler fra, så må serveren restartes for at klienten skal kunne koble til igjen


'''




import time
import gi
import numpy as np
import lib.gentl_cam_grab as camgrab
import cv2
import csv
import argparse

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer, GstRtsp


Gst.debug_set_active(False)
Gst.debug_set_default_threshold(0)

Gst.init(None)

W = 1280
H = 1024
FPS = 100
FPS_PRINT_INTERVAL = 1
GUID_FRAME_ID = 0


argparser = argparse.ArgumentParser(description='RTSP server')
argparser.add_argument('--port', type=str, default="8554", help='Port to run RTSP server on')
argparser.add_argument('-c', '--cti', type=str, default="", help='Relative path to .cti file')


def write_to_csv(filename = '/home/seaonics/Desktop/scripts_seaonics/genicam/log/events_sender.csv', frame_id=0, event='unknown', timestamp=0):
    #print(f"Writing to csv: {filename} \t {frame_id}, {event}, {timestamp}")
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([frame_id, event, timestamp])



class RTSPServer:
    def __init__(self, port="8554", mount_point="/test", no_cam = False, test_src = False, W=W, H=H, FPS=FPS, enable_logging=False, cti_file=""):
        self.port = port
        self.mount_point = mount_point
        self.no_cam = no_cam
        self.test_src = test_src
        self.H = H
        self.W = W
        self.FPS = FPS
        self.enable_logging = enable_logging
        self.cti_file = cti_file
        
        self.pts = 0
        self.time_per_frame = Gst.SECOND / FPS

        if not no_cam:
            self.setup_cam_grabber(self.cti_file)
            
            
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
    f"caps=video/x-raw,width={W},height={H},framerate={FPS}/1,format=RGB "
    "! videoconvert "
    "! nvvidconv "
    "! video/x-raw(memory:NVMM), format=(string)I420"
    "! nvv4l2h264enc" #profile=0-Baseline preset-level=4-Ultrafast
    "! rtph264pay config-interval=0 pt=96 name=pay0")

        
        launch_str_5_NO_NVIDIA = (f"appsrc name=source is-live=true block=true format=GST_FORMAT_TIME "
    f"caps=video/x-raw,width={W},height={H},framerate=100/1,format=RGB "
    "! videoconvert "
    "! x265enc "
    "! rtph265pay config-interval=0 pt=96 name=pay0")
        
        
        
        launch_str_5 = (f"appsrc name=source is-live=true block=true format=GST_FORMAT_TIME "
    f"caps=video/x-raw,width={W},height={H},framerate={FPS}/1,format=RGB "
    "! videoconvert "
    "! nvvidconv "
    "! video/x-raw(memory:NVMM), format=(string)I420"
    "! nvv4l2h265enc" #profile=0-Baseline preset-level=4-Ultrafast
    "! rtph265pay config-interval=0 pt=96 name=pay0")
        
        
        
        if test_src:
            self.launch_str = test_str
        else:
            self.launch_str = launch_str_4_WORKING
        self.setup_factory()

        self.loop = GLib.MainLoop()
        self.context = self.loop.get_context()

        self.source = None
        
        self.last_fps_print_time = time.time()
        self.fps_counter = 0    
        self.frame_counter = 0
        
        self.client = None
        
    
    def setup_factory(self):
        print("Setting up factory")
        self.server = GstRtspServer.RTSPServer.new()
        self.server.set_service(self.port)
        
        
        self.mounts = self.server.get_mount_points()
        
        self.factory = GstRtspServer.RTSPMediaFactory.new()
        self.factory.set_launch(self.launch_str)
        self.factory.set_latency(0)
        self.factory.set_shared(True)
        self.factory.set_stop_on_disconnect(True) 
        
        self.mounts.add_factory(self.mount_point, self.factory)
        self.server.attach(None)
        
        print(f"is_shared: {self.factory.is_shared()}")
        
        self.factory.connect('media-configure', self.on_media_configure)
        self.server.connect('client-connected', self.on_client_connected)

        
        
    def setup_cam_grabber(self, cti_file):
        self.cam_grabber = camgrab.CamGrabber(W=self.W, H=self.H, cti_file=cti_file)

    
    def on_client_connected(self, server, client):
        print("Client connected: ", client.get_connection().get_ip())
        self.client = client
        self.client.connect('closed', self.on_client_disconnected)
        
        
    def on_client_disconnected(self, user_data):
        print("Client disconnected: ", self.client.get_connection().get_ip())
        self.stop()
        raise Exception("Client disconnected")
        
        print(f"Session pool size before cleanup: {self.server.get_session_pool().get_n_sessions()}")
        def filter_func(pool, session):
            return GstRtspServer.RTSPFilterResult.REMOVE
        self.server.get_session_pool().filter(filter_func)
        self.server.get_session_pool().cleanup()
        print(f"Session pool size after cleanup: {self.server.get_session_pool().get_n_sessions()}")


    def on_media_configure(self, factory, media):
        self.source = media.get_element().get_child_by_name('source')
        if self.source:
            self.source.connect('need-data', self.on_need_data)
        
        self.frame_counter = 0
        print("Media configured")
       

    def on_need_data(self, src, length):
        self.feed_frame(src)
        return True
    
    
    def feed_frame(self, src):

        if not self.no_cam:
            try:
                if self.enable_logging: 
                    frame, timestamp = self.cam_grabber.get_frame_with_timestamp()   
                    self.frame_counter += 1
                    write_to_csv(frame_id=self.frame_counter, event="frame_grabbed", timestamp=timestamp)   
                else: 
                    frame = self.cam_grabber.get_frame()
            except Exception as e:
                print(f"Error getting frame: {e}")
                frame, timestamp = None, 0       
            
            self.fps_counter += 1
        else:
            frame = None
        
        if frame is None:
            frame = self.create_dummy_frame()
        else:
            self.fps_counter, self.last_fps_print_time = self.__print_fps(self.fps_counter, self.last_fps_print_time)
        
        data = frame.tobytes()
        
        if data is None:
            src.emit('end-of-stream')
            return False

        gst_buffer = Gst.Buffer.new_wrapped(data)
        gst_buffer.pts = self.pts
        gst_buffer.duration = self.time_per_frame
        self.pts += self.time_per_frame  
        
        ret = src.emit('push-buffer', gst_buffer)
        if ret != Gst.FlowReturn.OK:
            print("Error pushing buffer")
            
        if self.enable_logging:    
            write_to_csv(frame_id=self.frame_counter, event="frame_pushed", timestamp=time.time())
            
        return True  # Return True to keep the timeout active
    
    def create_dummy_frame(self):
        frame = np.full((self.H, self.W, 3), (25, 83, 95), dtype=np.uint8)

        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "No frame available"
        font_scale = 1.5
        font_thickness = 2
        textsize = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        
        textX = (frame.shape[1] - textsize[0]) / 2
        textY = (frame.shape[0] + textsize[1]) / 2
        
        cv2.putText(frame, f"GENTLCamGrabber says:", (int(textX), int(textY-50) ), font, font_scale*0.5, (240, 243, 245), font_thickness//2)
        cv2.putText(frame, text, (int(textX), int(textY) ), font, font_scale, (240, 243, 245), font_thickness)
        
        return frame


    def start(self):
        print(f"Starting RTSP server on port {self.server.get_service()}")
        
        try:
            self.server.attach(None)
            self.loop.run()
        except KeyboardInterrupt:
            pass
            
    
    
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
    args = argparser.parse_args()
    port = args.port
    cti_file = args.cti
    
    while True:
        print(f"Starting new RTSP server on port {port}")
        server = RTSPServer(no_cam=False, test_src=False, enable_logging=False, port=port, cti_file=cti_file)
        try:
            server.start()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            server.stop()
            server = None
            time.sleep(10)
            print("\n\n\n")

    server.stop()