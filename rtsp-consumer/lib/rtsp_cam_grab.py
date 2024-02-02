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
import logging


gi.require_version('Gst', '1.0')
from gi.repository import Gst

log = logging.getLogger(__name__)

Gst.debug_set_active(False)
Gst.debug_set_default_threshold(0)
Gst.init(None)


CAM_GRABBER_PROCESS_SILENT = False
DEFAULT_RTSP_LOCATION = "rtsp://localhost:8554/cam"
FRAME_RECEIVE_TIMEOUT = 1 # seconds


class RTSPCamGrabber():
    def __init__(self, rtsp_url, W=1280, H=720, FPS=100, cam_id=0) -> None: 
        self.rtsp_url = rtsp_url
        self.W = W
        self.H = H
        self.FPS = FPS
        self.cam_id = cam_id
        
        self.last_frame = None
        self.last_new_frame_time = time.time()
        self.max_frame_age = 1 # seconds
        self.dummy_frame = self.create_dummy_frame()
        
        self.cam_grabber_process = RTSPCamGrabberProcess(rtsp_url, W, H, FPS, cam_id)  
        self.p = multiprocessing.Process(target=self.cam_grabber_process.run, args=())
        self.p.daemon = CAM_GRABBER_PROCESS_SILENT
        
        log.info(f'{self.rtsp_url}: Starting RTSP grabber')
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
        
      
    def get_fps(self):
        with self.cam_grabber_process.lock:
            return self.cam_grabber_process.fps_value.value
        
          
    def stop(self):
        try:
            
            self.cam_grabber_process.stop()
            if True:
            #if self.p.is_alive():
                self.p.terminate()
                log.debug(f'{self.rtsp_url}: Terminated RTSP grabber process')
        except:
            log.debug(f'{self.rtsp_url}: Could not terminate RTSP grabber process')
        try:
            self.p.join()
            log.debug(f'{self.rtsp_url}: Joined RTSP grabber process')
        except:
            log.debug(f'{self.rtsp_url}: Could not join RTSP grabber process')
        
        log.info(f'{self.rtsp_url}: Stopped RTSP grabber')
        
        
    def create_dummy_frame(self, message=None):
        if message is None:
            message = f"No connection with: {self.rtsp_url}"
        frame = np.full((self.H, self.W, 3), (95, 83, 25), dtype=np.uint8)

        font = cv2.FONT_HERSHEY_SIMPLEX
        text = message
        font_scale = 1.5
        font_thickness = 2
        textsize = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        
        textX = (frame.shape[1] - textsize[0]) / 2
        textY = (frame.shape[0] + textsize[1]) / 2
        
        cv2.putText(frame, f"RTSP Client says:", (int(textX), int(textY-50) ), font, font_scale*0.5, (240, 243, 245), font_thickness//2)
        cv2.putText(frame, text, (int(textX), int(textY) ), font, font_scale, (240, 243, 245), font_thickness)
        
        return frame
    
    
    def __del__(self):
        pass
        
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
        self.last_frame_time = multiprocessing.Value('d', 0)
        self.is_running = multiprocessing.Value('b', False)
        self.exit_event = multiprocessing.Event()
        self.fps_value = multiprocessing.Value('d', 0.0)
        
        self.pipeline = None
        self.pipeline = self.create_pipeline()
        
        
    
    def create_pipeline(self):
        pipeline_str = (
            f"rtspsrc location={self.rtsp_url} latency=0 "
            "! rtph264depay "
            #"! h264parse " # H264 parsing is done on server-side
            #"! decodebin "
            
            "! avdec_h264 "
            "! queue max-size-buffers=1 leaky=downstream "
            "! videoconvert " 
            "! video/x-raw, format=BGR "
            "! appsink emit-signals=True name=sink sync=False max-buffers=1 drop=True"
        )
        pipeline = Gst.parse_launch(pipeline_str)
        
        sink = pipeline.get_by_name('sink')
        sink.set_property('emit-signals', True)
        sink.set_property('max-buffers', 1)
        sink.set_property('drop', True)
        sink.set_property('sync', False)
        sink.connect('new-sample', self.on_new_sample, sink)
        
        log.debug(f'{self.rtsp_url}: Created pipeline')
        
        return pipeline
    
    def run(self):
        log.debug(f'{self.rtsp_url}: Starting RTSP grabber process')
        with self.lock:
            self.is_running.value = True
        self.pipeline.set_state(Gst.State.PLAYING)
        self.check_and_restart_thread = threading.Thread(target=self.monitor_pipeline)
        self.check_and_restart_thread.start()
        
    def stop(self):
        with self.lock:
            self.is_running.value = False
            self.exit_event.set()
        log.debug(f'{self.rtsp_url}: RTSP grabber process is stopping')
        self.check_and_restart_thread.join()
        self.pipeline.set_state(Gst.State.NULL)
        log.debug(f'{self.rtsp_url}: Stopped RTSP grabber process')
     
    def restart_pipeline(self):
        log.debug(f'{self.rtsp_url}: Restarting pipeline\n')
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline = self.create_pipeline()
        self.pipeline.set_state(Gst.State.PLAYING)
 
        
    def monitor_pipeline(self):
        restart = False
        while self.is_running.value:
            if restart:
                self.restart_pipeline()
                self.exit_event.wait(10)
            restart = False


            if not self.is_running.value:
                break
            now = time.time()

            # Check if pipeline is still running
            if self.pipeline.get_state(0)[1] != Gst.State.PLAYING:
                log.info(f'{self.rtsp_url}: Pipeline is not running. Will try to restart.')
                restart = True
                continue
            
            # Check if frames are still being received
            with self.lock:
                last_frame_age = now - self.last_frame_time.value
                if last_frame_age > FRAME_RECEIVE_TIMEOUT:
                    log.info(f'No frames received for {last_frame_age * 1000:.3f} milliseconds. Will try to restart.')
                    restart = True
             
                
        log.debug(f'{self.rtsp_url}: Exiting monitor thread')
    
    
    def on_new_sample(self, sink, data):
        sample = sink.emit('pull-sample')
        if sample:
            buffer = sample.get_buffer()
            caps = sample.get_caps()
            width = caps.get_structure(0).get_value('width')
            height = caps.get_structure(0).get_value('height')
            
            #expected_size = width * height * 3 // 2 # I420 has 1.5 bytes per pixel
            expected_size = width * height * 3 # BGR has 3 bytes per pixel
            if buffer.get_size() != expected_size:
                log.error(f'{self.rtsp_url}: Buffer size does not match expected size.')
                return Gst.FlowReturn.ERROR
            
            buffer = buffer.extract_dup(0, buffer.get_size())
            frame = np.ndarray((height, width, 3), buffer=buffer, dtype=np.uint8)
        
            
            #buffer = buffer.extract_dup(0, buffer.get_size())
            #frame = np.ndarray((height + height // 2, width), buffer=buffer, dtype=np.uint8)
            #frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)
            
            with self.lock:
                self.last_frame_time.value = time.time()
                
                ctypes.memmove(self.frame_arr, frame.ctypes.data, self.frame_arr._length_)
                self.new_frame_available.value = True
                
                
            return Gst.FlowReturn.OK
        return Gst.FlowReturn.ERROR
    
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rtsp_url', type=str, default=DEFAULT_RTSP_LOCATION, help='RTSP URL to connect to. Default: {}'.format(DEFAULT_RTSP_LOCATION))
    
    args = parser.parse_args()
    
    with RTSPCamGrabber(rtsp_url=args.rtsp_url, H=1024, W=1280) as cam_grabber:
        cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
        while True:
            frame = cam_grabber.get_frame()
            
            if frame is not None:
                #cv2.cvtColor(frame, cv2.COLOR_RGB2BGR, frame)
                cv2.imshow("Window", frame)
                    
            if cv2.waitKey(1) == "q" or cv2.getWindowProperty("Window", cv2.WND_PROP_VISIBLE) < 1:
                break
            
        cv2.destroyAllWindows()
        
    
    log.debug('Exiting main')
            
            
            