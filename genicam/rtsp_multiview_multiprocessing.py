import gi
import cv2
import sys
import multiprocessing
import numpy as np
import csv
import time

gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

def write_to_csv(filename='./log/events_receiver.csv', frame_id=0, event='unknown', timestamp=0):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([frame_id, event, timestamp])

def frame_grabber_process(rtsp_url, frame_queue):
    pipeline = Gst.parse_launch(
        "rtspsrc location={} latency=0 ! rtph264depay ! h264parse ! decodebin ! videoconvert " 
        "! appsink emit-signals=True name=sink".format(rtsp_url)
    )
    appsink = pipeline.get_by_name("sink")
    appsink.set_property("max-buffers", 1)
    appsink.set_property("drop", True)
    appsink.set_property("sync", False)
    
    frame_counter = 0
    is_running = True
    pipeline.set_state(Gst.State.PLAYING)

    def new_sample(sink, data):
        nonlocal frame_counter
        sample = sink.emit("pull-sample")
        if sample:
            frame_counter += 1
            write_to_csv(frame_id=frame_counter, event='frame_received', timestamp=time.time())

            buffer = sample.get_buffer()
            caps = sample.get_caps()
            width = caps.get_structure(0).get_value("width")
            height = caps.get_structure(0).get_value("height")

            expected_size = width * height * 3 // 2  # I420 has 1.5 bytes per pixel
            if buffer.get_size() != expected_size:
                print("Buffer size does not match expected size.")
                return Gst.FlowReturn.ERROR

            buffer = buffer.extract_dup(0, buffer.get_size())
            frame = np.ndarray((height + height // 2, width), buffer=buffer, dtype=np.uint8)

            frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)
            frame_queue.put((rtsp_url, frame, frame_counter))
            return Gst.FlowReturn.OK
        return Gst.FlowReturn.ERROR

    appsink.connect("new-sample", new_sample, appsink)

    while is_running:
        time.sleep(0.1)  # Replace with a more appropriate wait method if needed

    pipeline.set_state(Gst.State.NULL)

# Rest of your functions (dummy_frame, display_frames) remain the same
def dummy_frame(): 
        # Generate a dummy frame

        # Background
        frame = np.full((720, 1280, 3), (95, 83, 25), dtype=np.uint8)
        
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
                write_to_csv(frame_id=frame_count, event='frame_displayed', timestamp=time.time())
            else:
                frame = dummy_frame()
            
            cv2.imshow(rtsp_url, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return


def main(rtsp_urls):
    frame_queues = [multiprocessing.Queue() for _ in rtsp_urls]
    for q in frame_queues:
        q.put(('Placeholder', dummy_frame(), 0))

    processes = []
    for url, q in zip(rtsp_urls, frame_queues):
        p = multiprocessing.Process(target=frame_grabber_process, args=(url, q))
        p.start()
        processes.append(p)

    try:
        display_frames(frame_queues)
    finally:
        for p in processes:
            p.terminate()
            p.join()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stream_viewer.py <RTSP URL 1> <RTSP URL 2> ...")
        sys.exit(1)

    rtsp_urls = sys.argv[1:]
    main(rtsp_urls)
