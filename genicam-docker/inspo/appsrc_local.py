import gi
import numpy as np
import cv2
import time

import gentl_cam_grab as CG

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

Gst.init(None)

# Create a GStreamer pipeline string
pipeline_str = (
    "appsrc name=source is-live=true block=true format=GST_FORMAT_TIME "
    "caps=video/x-raw,width=1280,height=720,framerate=30/1,format=RGB "
    "! videoconvert "
    "! nvvidconv "
    "! autovideosink sync=false"
)

# Create a GStreamer pipeline
pipeline = Gst.parse_launch(pipeline_str)

# Get the appsrc element from the pipeline
appsrc = pipeline.get_by_name("source")
appsrc.set_property("format", Gst.Format.TIME)

# Start the GStreamer pipeline
pipeline.set_state(Gst.State.PLAYING)


pts = 0
def push_frame_to_pipeline(frame):
    global pts
    try:
        print(frame)
        # Create a GStreamer buffer from the frame
        buffer = Gst.Buffer.new_wrapped(frame.tobytes())
        

        # Set buffer PTS and duration
        duration = Gst.SECOND / 30
        buffer.pts = pts
        buffer.duration = duration
        pts += duration

        # Push the buffer into the appsrc
        appsrc.emit("push-buffer", buffer)
    except Exception as e:
        print(f"Error pushing frame to pipeline: {e}")

# Your cam_grabber logic to get frames here
# For this example, we'll generate a synthetic frame
try:
    with CG.CamGrabber() as cam_grabber:
        cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
        time.sleep(3)
        while cam_grabber.is_active():
            if cam_grabber.is_connected():
                frame = cam_grabber.get_newest_frame()
                
                if frame is not None:
                    push_frame_to_pipeline(frame)
                    
            if cv2.waitKey(1) == "q" or cv2.getWindowProperty("Window", cv2.WND_PROP_VISIBLE) < 1:
                break

        
        cv2.destroyAllWindows()
        print("Exiting main")
except KeyboardInterrupt:
    pass
# Stop and cleanup the GStreamer pipeline
pipeline.set_state(Gst.State.NULL)
