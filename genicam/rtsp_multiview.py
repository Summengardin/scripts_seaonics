import gi
import cv2
import sys
import threading
import queue
import numpy as np
import csv
import time


'''

class FrameGrabber:
    # ... [rest of your existing code] ...

    def __init__(self, rtsp_url, frame_queue):
        # ... [rest of your existing __init__ code] ...
        self.monitoring_thread_active = False

    def start(self):
        # ... [your existing start method code] ...
        self.monitoring_thread_active = True
        self.check_and_restart_thread = threading.Thread(target=self.monitor_pipeline)
        self.check_and_restart_thread.start()

    def stop(self):
        # ... [your existing stop method code, minus the join call] ...
        self.monitoring_thread_active = False
        # Note: Do not join the thread here if this method can be called from the monitoring thread

    def monitor_pipeline(self):
        while self.monitoring_thread_active:
            # ... [rest of your monitor_pipeline code] ...
            time.sleep(1)  # Check every 1 second

# In your main function or where you stop the FrameGrabber instances:
for viewer in frame_grabbers:
    viewer.stop()

# After stopping all viewers, join their threads:
for viewer in frame_grabbers:
    if viewer.check_and_restart_thread:
        viewer.check_and_restart_thread.join()

# ... [rest of your code] ...


'''


from lib.rtsp_cam_grab import RTSPCamGrabber


gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

last_frame_time = 0
CHECK_INTERVAL = 2  # Check every few seconds
FRAME_RECEIVE_TIMEOUT = 5  # Restart pipeline if no frames received for 5 seconds


def write_to_csv(filename = './log/events_receiver.csv', frame_id=0, event='unknown', timestamp=0):
    #print(f"Writing to csv: {filename} \t {frame_id}, {event}, {timestamp}")
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([frame_id, event, timestamp])
frame_counter = 0

def dummy_frame(tag = ""): 
        # Generate a dummy frame

        # Background
        frame = np.full((720, 1280, 3), (95, 83, 25), dtype=np.uint8)
        
        # setup text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "No frames available"
        font_scale = 1.5
        font_thickness = 2

        # get boundary of this text
        textsize = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

        # get coords based on boundary
        textX = (frame.shape[1] - textsize[0]) / 2
        textY = (frame.shape[0] + textsize[1]) / 2
        
        # add text centered on image
        cv2.putText(frame, text, (int(textX), int(textY) ), font, font_scale, (240, 243, 245), font_thickness)
        cv2.putText(frame, f"From {tag}", (int(textX), int(textY+50) ), font, font_scale*0.5, (240, 243, 245), font_thickness//2)
        return frame
    

    
def display_rtsp_frames_same_window(cam_grabbers, enable_logging=False):
    cv2.namedWindow("Combined Frames", cv2.WINDOW_NORMAL)
    primary_index = 0  # Index to determine which frame is primary


    while True:
        frames_to_display = []

        for i, grabber in enumerate(cam_grabbers):
            tag = grabber.rtsp_url
            frame = None
            now = time.time()
            frame = grabber.get_frame()
            if frame is not None:
                if enable_logging: write_to_csv(frame_id=frame_count, event='frame_displayed', timestamp=time.time())
                frames_to_display.append(frame)
            else:
                frame = dummy_frame()
                cv2.putText(frame, str(i), (50, 200), cv2.FONT_HERSHEY_DUPLEX, 5, (240, 243, 245), 2)
                frames_to_display.append(frame)

        if frames_to_display:
            primary_frame = frames_to_display[primary_index]
            secondary_frame = frames_to_display[1 - primary_index]

            
            small_frame = cv2.resize(secondary_frame, (primary_frame.shape[1] // 4, primary_frame.shape[0] // 4))

            x_offset = primary_frame.shape[1] - small_frame.shape[1]
            y_offset = primary_frame.shape[0] - small_frame.shape[0]

            combined_frame = primary_frame.copy()
            frame_thickness = 10
            border_color = (0, 255, 0) 
            cv2.rectangle(combined_frame, (x_offset, y_offset), (x_offset + small_frame.shape[1], y_offset + small_frame.shape[0]), border_color, frame_thickness)
            #combined_frame[y_offset:y_offset+small_frame.shape[0], x_offset:x_offset+small_frame.shape[1]] = small_frame
            combined_frame[-small_frame.shape[0]:, -small_frame.shape[1]:] = small_frame 

           
            cv2.imshow("Combined Frames", combined_frame)
            

        # Check for spacebar press or window close
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Spacebar pressed
            primary_index = 1 - primary_index  # Swap the primary frame
        elif key == ord('q') or cv2.getWindowProperty('Combined Frames', cv2.WND_PROP_VISIBLE) < 1:
            break


def main(rtsp_urls, enable_logging=False):
    rtsp_grabbers = [RTSPCamGrabber(rtsp_url=url, W=1280, H=1024) for url in rtsp_urls]
    
    try:
        display_rtsp_frames_same_window(rtsp_grabbers, enable_logging=enable_logging)
    except Exception as e:
        print(f"Error displaying frames: {e}")
        
    for grabber in rtsp_grabbers:
        grabber.stop()
    

    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stream_viewer.py <RTSP URL 1> <RTSP URL 2> ...")
        rtsp_urls = ["rtsp://127.0.0.1:8554/test", "rtsp://169.254.54.69:8554/test"]
    else:
        rtsp_urls = sys.argv[1:]
        
        
    enable_logging = False    
    main(rtsp_urls)
