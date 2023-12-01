import os
import time
import threading
import multiprocessing
import multiprocessing.sharedctypes
import numpy as np
import typing
import ctypes
import cv2
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)


CAM_GRABBER_PROCESS_SILENT = False
DEFAULT_RTSP_LOCATION = "rtsp://169.254.54.69:8554/test"
FRAME_RECEIVE_TIMEOUT = 1 # seconds


class RTSPCamGrabber():
    def __init__(self, rtsp_url, W=1280, H=720, FPS=100, cam_id=0) -> None:
        self.cam_grabber_process = RTSPCamGrabberProcess(rtsp_url, W, H, FPS, cam_id)   
        
        self.last_frame = None
        self.last_new_frame_time = time.time()
        self.max_frame_age = 1 # seconds
        self.dummy_frame = self.create_dummy_frame()
        
        
        self.p = multiprocessing.Process(target=self.cam_grabber_process.run, args=())
        self.p.daemon = CAM_GRABBER_PROCESS_SILENT
        self.p.start()
        
    def get_frame(self):
        with self.cam_grabber_process.lock:
            now = time.time()
            if self.cam_grabber_process.new_frame_available.value:
                self.cam_grabber_process.new_frame_available.value = False
                self.last_new_frame_time = now
                frame = np.ndarray((self.cam_grabber_process.H, self.cam_grabber_process.W, 3), buffer=self.cam_grabber_process.frame_arr, dtype=np.uint8)
                
                self.last_frame = frame
                return frame
            
            else:
                # Frames are only valid for a certain amount of time
                if now - self.last_new_frame_time > self.max_frame_age:
                    return self.dummy_frame
                return self.last_frame
        
    def stop(self):
        try:
            
            self.cam_grabber_process.stop()
            if self.p.is_alive():
                self.p.terminate()
                print('Terminated RTSP grabber process')
        except:
            pass
        try:
            self.p.join()
            print('Joined RTSP grabber process')
        except:
            pass
        
        print('Stopped RTSP grabber')
        
    def create_dummy_frame(self):
        frame = np.full((self.cam_grabber_process.H, self.cam_grabber_process.W, 3), (95, 83, 25), dtype=np.uint8)
    

        font = cv2.FONT_HERSHEY_DUPLEX
        text = "No frame available"
        font_scale = 1.5
        font_thickness = 2
        textsize = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        
        textX = (frame.shape[1] - textsize[0]) / 2
        textY = (frame.shape[0] + textsize[1]) / 2
        
        cv2.putText(frame, text, (int(textX), int(textY) ), font, font_scale, (240, 243, 245), font_thickness)
        cv2.putText(frame, f"From {self.cam_grabber_process.rtsp_url}", (int(textX), int(textY+50) ), font, font_scale*0.5, (240, 243, 245), font_thickness//2)
        
        return frame
    
    
    def __del__(self):
        self.stop()
    
    
    def __enter__(self):
        return self   
        
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
         
        
class RTSPCamGrabberProcess():
    def __init__(self, rtsp_url, W=1280, H=720, FPS=100, cam_id=0) -> None:
        self.W = W
        self.H = H
        self.FPS = FPS
        self.cam_id = cam_id
        self.rtsp_url = rtsp_url
        
        self.frame_arr = multiprocessing.sharedctypes.RawArray(ctypes.c_uint8, self.W * self.H * 3)
        self.lock = multiprocessing.Lock()
        self.new_frame_available = multiprocessing.Value('b', False)
        self.is_running = multiprocessing.Value('b', False)
        
        self.pipeline = None
        self.pipeline = self.create_pipeline()
        print('Created pipeline')
        
    
    def create_pipeline(self):
        pipeline_str = (
            f"rtspsrc location={self.rtsp_url} latency=0 "
            "! rtph264depay "
            "! h264parse "
            "! decodebin "
            "! videoconvert " 
            "! appsink emit-signals=True name=sink"
        )

        pipeline = Gst.parse_launch(pipeline_str)
        printable_pipeline_str = pipeline_str.replace('! ', '! \n')
        print(f"Created pipeline: {printable_pipeline_str}")   
        sink = pipeline.get_by_name('sink')
        sink.set_property('emit-signals', True)
        sink.set_property('max-buffers', 1)
        sink.set_property('drop', True)
        sink.set_property('sync', False)
        sink.connect('new-sample', self.on_new_sample, sink)
        return pipeline
    
    def run(self):
        print('Starting RTSP grabber process')
        with self.lock:
            self.is_running.value = True
        self.pipeline.set_state(Gst.State.PLAYING)
        self.check_and_restart_thread = threading.Thread(target=self.monitor_pipeline)
        self.check_and_restart_thread.start()
        
    def stop(self):
        
        with self.lock:
            self.is_running.value = False
        print('RTSP grabber process is stopping')
        self.check_and_restart_thread.join()
        self.pipeline.set_state(Gst.State.NULL)
        print('Stopped RTSP grabber process')
     
    def restart_pipeline(self):
        print('Restarting pipeline')
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline = self.create_pipeline()
        self.pipeline.set_state(Gst.State.PLAYING)
 
        
    def monitor_pipeline(self):
        last_frame_time = time.time()
        while self.is_running.value:
            time.sleep(3)
            if not self.is_running.value:
                break
            now = time.time()
            
            # Check if pipeline is still running
            if self.pipeline.get_state(0)[1] != Gst.State.PLAYING:
                self.restart_pipeline()
                continue
                
            # Check if frames are still being received
            restart = False
            with self.lock:
                if self.new_frame_available.value:
                    last_frame_time = now
                elif now - last_frame_time > FRAME_RECEIVE_TIMEOUT:
                    restart = True
                      
            if restart:
                self.restart_pipeline()
                
        print('Exiting monitor thread')
    
    
    def on_new_sample(self, sink, data):
        sample = sink.emit('pull-sample')
        if sample:
            buffer = sample.get_buffer()
            caps = sample.get_caps()
            width = caps.get_structure(0).get_value('width')
            height = caps.get_structure(0).get_value('height')
            
            expected_size = width * height * 3 // 2 # I420 has 1.5 bytes per pixel
            if buffer.get_size() != expected_size:
                print('Buffer size does not match expected size.')
                return Gst.FlowReturn.ERROR
            
            buffer = buffer.extract_dup(0, buffer.get_size())
            frame = np.ndarray((height + height // 2, width), buffer=buffer, dtype=np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)
            
            with self.lock:
                ctypes.memmove(self.frame_arr, frame.ctypes.data, self.frame_arr._length_)
                self.new_frame_available.value = True
                
                
            return Gst.FlowReturn.OK
        return Gst.FlowReturn.ERROR
    
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rtsp_url', type=str, default=DEFAULT_RTSP_LOCATION, help='RTSP URL to connect to. Default: {}'.format(DEFAULT_RTSP_LOCATION))
    
    args = parser.parse_args()
    
    with RTSPCamGrabber(rtsp_url=args.rtsp_url) as cam_grabber:
        cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
        while True:
            frame = cam_grabber.get_frame()
            
            if frame is not None:
                #cv2.cvtColor(frame, cv2.COLOR_RGB2BGR, frame)
                cv2.imshow("Window", frame)
                    
            if cv2.waitKey(1) == "q" or cv2.getWindowProperty("Window", cv2.WND_PROP_VISIBLE) < 1:
                break
            
        cv2.destroyAllWindows()
        
    
    print('Exiting main')
            
            
            