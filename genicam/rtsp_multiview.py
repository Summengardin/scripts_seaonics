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


def write_to_csv(filename = './log/events_receiver.csv', frame_id=0, event='unknown', timestamp=0):
    #print(f"Writing to csv: {filename} \t {frame_id}, {event}, {timestamp}")
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([frame_id, event, timestamp])
frame_counter = 0

class StreamViewer:
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
            write_to_csv('/home/seaonics/Desktop/scripts_seaonics/genicam/log/events.csv', frame_counter, 'frame_recieved', time.time())
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


def display_frames(frame_queues):
    while True:
        for q in frame_queues:
            if not q.empty():
                rtsp_url, frame, frame_count = q.get()
                write_to_csv('/home/seaonics/Desktop/scripts_seaonics/genicam/log/events.csv', frame_count, 'frame_displayed', time.time())
                cv2.imshow(rtsp_url, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    return


def main(rtsp_urls):
    frame_queues = [queue.Queue() for _ in rtsp_urls]
    viewers = [StreamViewer(url, frame_queue) for url, frame_queue in zip(rtsp_urls, frame_queues)]

    # Start each stream in its own thread
    for viewer in viewers:
        threading.Thread(target=viewer.start).start()

    # Display frames in the main thread
    try:
        display_frames(frame_queues)
    finally:
        for viewer in viewers:
            viewer.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stream_viewer.py <RTSP URL 1> <RTSP URL 2> ...")
        sys.exit(1)

    rtsp_urls = sys.argv[1:]
    main(rtsp_urls)
