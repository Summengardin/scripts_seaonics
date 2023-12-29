#!./venv/bin/python3

import signal

import time
import gi
import numpy as np
import lib.gentl_cam_grab as camgrab
import cv2
import argparse


gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer, GstRtsp


Gst.debug_set_active(False)
Gst.debug_set_default_threshold(0)

Gst.init(None)

W = 1280
H = 1024
FPS = 200
FPS_PRINT_INTERVAL = 10


argparser = argparse.ArgumentParser(description='RTSP server')
argparser.add_argument('--port', type=str, default="8554", help='Port to run RTSP server on')
argparser.add_argument('-c', '--cti', type=str, default="", help='Relative path to .cti file')

class RTSPServer:
    def __init__(self, ip=None, port="8554", mount_point="/cam", no_cam = False, test_src = False, W=W, H=H, FPS=FPS, enable_logging=False, cti_file=""):
        self.ip = ip
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
        self.is_running = False

        if not no_cam:
            self.setup_cam_grabber(self.cti_file)
                 
        self.launch_str = (f"appsrc name=source is-live=true block=true format=GST_FORMAT_TIME "
                            f"caps=video/x-raw,width={W},height={H},framerate={FPS}/1,format=RGB "
                            "! videoconvert "
                            "! nvvidconv "
                            "! video/x-raw(memory:NVMM), format=(string)I420"
                            "! nvv4l2h264enc" #profile=0-Baseline preset-level=4-Ultrafast
                            "! rtph264pay config-interval=0 pt=96 name=pay0"
                            )

        self.setup_factory()

        self.loop = GLib.MainLoop()
        self.context = self.loop.get_context()

        self.source = None
        
        self.last_fps_print_time = time.time()
        self.fps_counter = 0    
        self.frame_counter = 0
        
        self.client = None
        
    
    def setup_factory(self):
        print(f"Setting up factory")
        self.server = GstRtspServer.RTSPServer.new()
        if self.ip is not None:
            self.server.set_address(self.ip)
        self.server.set_service(self.port)
        
        
        self.mounts = self.server.get_mount_points()
        
        self.factory = GstRtspServer.RTSPMediaFactory.new()
        self.factory.set_launch(self.launch_str)
        self.factory.set_latency(0)
        self.factory.set_shared(False)
        self.factory.set_stop_on_disconnect(True) 
        self.factory.set_protocols(GstRtsp.RTSPLowerTrans.UDP)
        
        self.mounts.add_factory(self.mount_point, self.factory)
        #self.server.attach(None)
        
        self.factory.connect('media-configure', self.on_media_configure)
        self.server.connect('client-connected', self.on_client_connected)
        print("Factory setup complete")

        
        
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
                frame = self.cam_grabber.get_frame()
            except Exception as e:
                print(f"Error getting frame: {e}")
                frame, timestamp = None, 0       
            
            self.fps_counter += 1
        else:
            frame = None
        
        if frame is None:
            msg = "Dummy-frame" if self.no_cam else "No camera connected"
            frame = self.create_dummy_frame(msg)
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
              
        return True  # Return True to keep the timeout active
    
    def create_dummy_frame(self, message="Camera not connected"):
        frame = np.full((self.H, self.W, 3), (25, 83, 95), dtype=np.uint8)

        font = cv2.FONT_HERSHEY_SIMPLEX
        text = message
        font_scale = 1.5
        font_thickness = 2
        textsize = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        
        textX = (frame.shape[1] - textsize[0]) / 2
        textY = (frame.shape[0] + textsize[1]) / 2
        
        cv2.putText(frame, f"RTSP Server says:", (int(textX), int(textY-50) ), font, font_scale*0.5, (240, 243, 245), font_thickness//2)
        cv2.putText(frame, text, (int(textX), int(textY) ), font, font_scale, (240, 243, 245), font_thickness)
        
        return frame


    def start(self):
        print(f"Starting RTSP server on port {self.server.get_service()}")
        self.is_running = True
        try:
            self.server.attach(None)
            self.loop.run()
        except KeyboardInterrupt:
            pass
    
    def stop(self):
        self.is_running = False
        
        try:          
            if not self.no_cam:
                self.cam_grabber.stop()
                print("RTSP stopped grabbing frames")
        except:
            print("Could not stop RTSP grabbing frames")
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
    
    
    ip = None #'10.1.5.66'
      
    # while True:
    print(f"Starting new RTSP server on port {port}")
    server = RTSPServer(W=W, H=H, ip=ip, no_cam=False, test_src=False, enable_logging=False, port=port, cti_file=cti_file)
    
    
    def sig_handler(signum, frame):
        print(f"Caught signal {signum}")
        try:
            server.stop()
        except: 
            pass
        exit(0)
    signal.signal(signal.SIGINT | signal.SIGTERM, sig_handler)
    try:
        server.start()
    except Exception as e:
        print(f"[Error in server main]: {e}")
    finally:
        server.stop()
        server = None
        #time.sleep(10)

        #print("\n\n\n")

    #server.stop()
    
