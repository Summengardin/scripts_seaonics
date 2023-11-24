import gi
import cv2
import sys
import threading
import queue
import numpy as np
import csv
import time


gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

last_frame_repeat_time = 0


def write_to_csv(filename = './log/events_receiver.csv', frame_id=0, event='unknown', timestamp=0):
    #print(f"Writing to csv: {filename} \t {frame_id}, {event}, {timestamp}")
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([frame_id, event, timestamp])
frame_counter = 0

class FrameGrabber:
    def __init__(self, rtsp_url, frame_queue):
        self.rtsp_url = rtsp_url
        self.frame_queue = frame_queue
        self.pipeline = None
        self.create_pipeline()
        self.is_running = False

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
        sample = sink.emit("pull-sample")
        
        
        if sample:
            global frame_counter
            frame_counter += 1
            write_to_csv(frame_id=frame_counter, event='frame_recieved', timestamp=time.time())
            buffer = sample.get_buffer()
            caps = sample.get_caps()
            width = caps.get_structure(0).get_value("width")
            height = caps.get_structure(0).get_value("height")

            # Calculate the expected size of an I420 frame
            expected_size = width * height * 3 // 2  # I420 has 1.5 bytes per pixel
            if buffer.get_size() != expected_size:
                print("Buffer size does not match expected size.")
                return Gst.FlowReturn.ERROR

            buffer = buffer.extract_dup(0, buffer.get_size())
            frame = np.ndarray((height + height // 2, width), buffer=buffer, dtype=np.uint8)

            # Convert I420 (YUV) to BGR for display with OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)

            # Put the frame in the queue for the main thread to display
            self.frame_queue.put((self.rtsp_url, frame, frame_counter))
            return Gst.FlowReturn.OK
        return Gst.FlowReturn.ERROR

    def start(self):
        self.is_running = True
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.is_running = False
        self.pipeline.set_state(Gst.State.NULL)

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
    

def display_frames(frame_queues):
    last_frames = {q: None for q in frame_queues}  # Store the last frame of each queue

    while True:
        for q in frame_queues:
            frame = None
            now = time.time()
            if not q.empty():
                rtsp_url, frame, frame_count = q.get()
                last_frames[q] = (rtsp_url, frame, frame_count)  # Update last frame for this queue
            else:
                
                if now - last_frame_repeat_time > 2:
                    frame = dummy_frame()
                    
                elif last_frames[q] is not None:
                    last_frame_repeat_time = now
                    rtsp_url, frame = last_frames[q]  # Use the last frame if queue is empty
            
            if frame is not None:
                write_to_csv(frame_id=frame_count, event='frame_displayed', timestamp=time.time())
                cv2.imshow(rtsp_url, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                return


def main(rtsp_urls):
    frame_queues = [queue.Queue() for _ in rtsp_urls]
    frame_grabbers = [FrameGrabber(url, frame_queue) for url, frame_queue in zip(rtsp_urls, frame_queues)]

    # Start each stream in its own thread
    for viewer in frame_grabbers:
        threading.Thread(target=viewer.start).start()

    # Display frames in the main thread
    try:
        display_frames(frame_queues)
    finally:
        for viewer in frame_grabbers:
            viewer.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stream_viewer.py <RTSP URL 1> <RTSP URL 2> ...")
        sys.exit(1)

    rtsp_urls = sys.argv[1:]
    main(rtsp_urls)
