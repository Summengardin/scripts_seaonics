import gi
import sys
import threading

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

class StreamViewer:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.pipeline = None
        self.create_pipeline()

    def create_pipeline(self):
        # Create a GStreamer pipeline for the RTSP stream
        self.pipeline = Gst.parse_launch(
            f"rtspsrc location={self.rtsp_url} latency=0 ! rtph264depay ! h264parse ! decodebin ! videoconvert ! autovideosink sync=0"
        )

        # Set up a bus to listen to messages on the pipeline
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self.on_eos)
        bus.connect("message::error", self.on_error)

    def on_eos(self, bus, msg):
        print("End-Of-Stream reached.")
        self.pipeline.set_state(Gst.State.NULL)

    def on_error(self, bus, msg):
        error = msg.parse_error()
        print("Error occurred:", error)
        self.pipeline.set_state(Gst.State.NULL)

    def start(self):
        print(f"Started stream from {self.rtsp_url}")
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)


def main(rtsp_urls):
    viewers = [StreamViewer(url) for url in rtsp_urls]

    # Start each stream in its own thread
    threads = []
    for viewer in viewers:
        thread = threading.Thread(target=viewer.start)
        threads.append(thread)
        thread.start()

    # Keep the program running
    try:
        loop = GLib.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        pass

    # Stop all streams
    for viewer in viewers:
        viewer.stop()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stream_viewer.py <RTSP URL 1> <RTSP URL 2> ...")
        sys.exit(1)

    rtsp_urls = sys.argv[1:]
    main(rtsp_urls)
