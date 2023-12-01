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


from rtsp_cam_grab import RTSPCamGrabber


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

class FrameGrabber:
    def __init__(self, rtsp_url, frame_queue, enable_logging=False):
        self.enable_logging = enable_logging
        self.rtsp_url = rtsp_url
        self.frame_queue = frame_queue
        self.new_frame_received = False
        self.is_running = False
        self.pipeline = None
        self.create_pipeline()
        self.restart_counter = 0
        
        
        
    
    def __del__(self):
        if self.check_and_restart_thread:
            self.check_and_restart_thread.join()
        
        
    def check_and_restart_pipeline(self):
        # Check if the pipeline is in the expected state, restart if not
        state = self.pipeline.get_state(Gst.CLOCK_TIME_NONE).state
        if state != Gst.State.PLAYING and self.is_running:
            self.restart_counter += 1
            print(f"Pipeline is not playing. Attempt to restart #{self.restart_counter}...")
            self.restart_pipeline()
            
    def restart_pipeline(self):
        self.stop()
        self.create_pipeline()
        self.start()

    def create_pipeline(self):
        # Create a GStreamer pipeline with 'appsink' as the sink
        self.pipeline = Gst.parse_launch(
            "rtspsrc location={} latency=0 ! rtph264depay ! h264parse ! decodebin ! videoconvert " 
            "! appsink emit-signals=True name=sink".format(self.rtsp_url)
        )
        appsink = self.pipeline.get_by_name("sink")
        appsink.set_property("max-buffers", 1)
        appsink.set_property("drop", True)
        appsink.set_property("sync", False)
        appsink.connect("new-sample", self.new_sample, appsink)

    def new_sample(self, sink, data):
        try:
            sample = sink.emit("pull-sample")
            
            
            if sample:
                global frame_counter
                frame_counter += 1
                if self.enable_logging: write_to_csv(frame_id=frame_counter, event='frame_recieved', timestamp=time.time())
                
                
                buffer = sample.get_buffer()
                caps = sample.get_caps()
                width = caps.get_structure(0).get_value("width")
                height = caps.get_structure(0).get_value("height")

                # Calculate the expected size of an I420 frame
                expected_size = width * height * 3 // 2  # I420 has 1.5 bytes per pixel
                if buffer.get_size() != expected_size:
                    print("Buffer size does not match expected size.")
                    return Gst.FlowReturn.ERROR

                #start_time = time.perf_counter()
                buffer = buffer.extract_dup(0, buffer.get_size())
                frame = np.ndarray((height + height // 2, width), buffer=buffer, dtype=np.uint8)

                # Convert I420 (YUV) to BGR for display with OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)

                #print(f"Frame converted in {(time.perf_counter() - start_time)*1000}ms")
                
                
                # Put the frame in the queue for the main thread to display
                self.frame_queue.put((self.rtsp_url, frame, frame_counter))
                self.new_frame_received = True
                
                return Gst.FlowReturn.OK
            return Gst.FlowReturn.ERROR
        except Exception as e:
            print(f"Error in pipeline: {e}")
            self.check_and_restart_pipeline()
            return Gst.FlowReturn.ERROR

    def start(self):
        self.is_running = True
        self.pipeline.set_state(Gst.State.PLAYING)
        self.check_and_restart_thread = threading.Thread(target=self.monitor_pipeline)
        self.check_and_restart_thread.start()

    def stop(self):
        self.is_running = False
        self.pipeline.set_state(Gst.State.NULL)
        
            
    def monitor_pipeline(self):
        last_frame_time = None
        while self.is_running:
            current_time = time.time()

            # Check if the pipeline is in the expected state
            state = self.pipeline.get_state(Gst.CLOCK_TIME_NONE).state
            if state != Gst.State.PLAYING:
                self.restart_pipeline()

            # Check if frames are being received
            if last_frame_time is not None and (current_time - last_frame_time) > FRAME_RECEIVE_TIMEOUT:
                print("No frames received for a while. Attempting to restart...")
                self.restart_pipeline()

            # Update last_frame_time if a new frame has been received
            if self.new_frame_received:
                last_frame_time = current_time
                self.new_frame_received = False

            time.sleep(CHECK_INTERVAL)  # Check every few seconds


def dummy_frame(): 
        # Generate a dummy frame

        # Background
        frame = np.full((720, 1280, 3), (95, 83, 25), dtype=np.uint8)
        
        # setup text
        font = cv2.FONT_HERSHEY_DUPLEX
        text = "No framesesdfg available"
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
    

def display_frames(frame_queues, enable_logging=False):
    global last_frame_time
    last_frames = {q: None for q in frame_queues}  # Store the last frame of each queue

    while True:
        for q in frame_queues:
            frame = None
            now = time.time()
            if not q.empty():
                rtsp_url, frame, frame_count = q.get()
                last_frames[q] = (rtsp_url, frame, frame_count)  # Update last frame for this queue
                last_frame_time = now
            elif now - last_frame_time <= 2 and last_frames[q] is not None:
                rtsp_url, frame, frame_count = last_frames[q]  # Use the last frame if queue is empty
            
            if frame is not None:
                if enable_logging: write_to_csv(frame_id=frame_count, event='frame_displayed', timestamp=time.time())
            else:
                frame = dummy_frame()
            
            cv2.imshow(rtsp_url, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return


def display_frames_same_window(frame_queues, enable_logging=False):
    global last_frame_time
    last_frames = {q: None for q in frame_queues}  # Store the last frame of each queue 
    
    cv2.namedWindow("Combined Frames", cv2.WINDOW_NORMAL)
    primary_index = 0  # Index to determine which frame is primary


    while True:
        frames_to_display = []

        for i, q in enumerate(frame_queues):
            frame = None
            now = time.time()
            if not q.empty():
                rtsp_url, frame, frame_count = q.get()
                last_frames[q] = (rtsp_url, frame, frame_count)  # Update last frame for this queue
                last_frame_time = now
            elif now - last_frame_time <= 2 and last_frames[q] is not None:
                rtsp_url, frame, frame_count = last_frames[q]  # Use the last frame if queue is empty

            if frame is not None:
                if enable_logging: write_to_csv(frame_id=frame_count, event='frame_displayed', timestamp=time.time())
                frames_to_display.append(frame)
            else:
                frame = dummy_frame()
                cv2.putText(frame, str(i), (50, 200), cv2.FONT_HERSHEY_DUPLEX, 5, (240, 243, 245), 2)
                frames_to_display.append(frame)

        # Merge the frames horizontally or vertically
        if frames_to_display:
            # Decide which frame is primary and which is secondary
            primary_frame = frames_to_display[primary_index]
            secondary_frame = frames_to_display[1 - primary_index]

            # Resize secondary frame to be smaller, e.g., 1/4th of the primary frame
            small_frame = cv2.resize(secondary_frame, (primary_frame.shape[1] // 4, primary_frame.shape[0] // 4))

            # Place the small frame on the top-right corner of the primary frame
            primary_frame[-small_frame.shape[0]:, -small_frame.shape[1]:] = small_frame

            # Show the combined frame
            cv2.imshow("Combined Frames", primary_frame)

        # Check for spacebar press or window close
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Spacebar pressed
            primary_index = 1 - primary_index  # Swap the primary frame
        elif key == ord('q') or cv2.getWindowProperty('Combined Frames', cv2.WND_PROP_VISIBLE) < 1:
            break
    
def display_rtsp_frames_same_window(cam_grabbers, enable_logging=False):
    #global last_frame_time
    
    cv2.namedWindow("Combined Frames", cv2.WINDOW_NORMAL)
    primary_index = 0  # Index to determine which frame is primary


    while True:
        frames_to_display = []

        for i, grabber in enumerate(cam_grabbers):
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

        # Merge the frames horizontally or vertically
        if frames_to_display:
            # Decide which frame is primary and which is secondary
            primary_frame = frames_to_display[primary_index]
            secondary_frame = frames_to_display[1 - primary_index]

            # Resize secondary frame to be smaller, e.g., 1/4th of the primary frame
            small_frame = cv2.resize(secondary_frame, (primary_frame.shape[1] // 4, primary_frame.shape[0] // 4))

            # Place the small frame on the top-right corner of the primary frame
            primary_frame[-small_frame.shape[0]:, -small_frame.shape[1]:] = small_frame

            # Show the combined frame
            cv2.imshow("Combined Frames", primary_frame)

        # Check for spacebar press or window close
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Spacebar pressed
            primary_index = 1 - primary_index  # Swap the primary frame
        elif key == ord('q') or cv2.getWindowProperty('Combined Frames', cv2.WND_PROP_VISIBLE) < 1:
            break


def main(rtsp_urls, enable_logging=False):
    rtsp_grabbers = [RTSPCamGrabber(rtsp_url=url) for url in rtsp_urls]
    
    # Display frames in the main thread
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
