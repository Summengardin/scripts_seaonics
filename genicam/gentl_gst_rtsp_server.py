import cv2
import numpy as np
import gentl_cam_grab as camgrab
import time

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

def main():
    # Initialize GStreamer
    Gst.init(None)

    # Create the GStreamer pipeline with appsrc element and output to RTSP
    
    pipeline_str_1 = (
        "appsrc name=src is-live=true format=GST_FORMAT_TIME "
        "caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! "
        "videoconvert ! "
        "x264enc speed-preset=ultrafast tune=zerolatency ! "
        "rtph264pay config-interval=1 name=pay0 pt=96 "

    )
    
    pipeline_str_2 = ("appsrc name=src is-live=true format=GST_FORMAT_TIME " 
        "caps=video/x-raw(memory:NVMM),format=BGR,width=640,height=480,framerate=30/1 !" 
        "nvvidconv !" 
        "nvh264enc enable-full-frame=true !" 
        "rtph264pay pt=96 name=pay0")
        
    pipeline = Gst.parse_launch(pipeline_str_1)
    appsrc = pipeline.get_by_name("src")

    # Set to playing state
    pipeline.set_state(Gst.State.PLAYING)


    with camgrab.CamGrabber() as cam_grabber:
        cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
        while cam_grabber.is_active():
            if cam_grabber.is_connected():
                frame = cam_grabber.get_newest_frame()
                
                if frame is not None:
                    # Push frame to GStreamer pipeline
                    data = frame.tostring()
                    buffer = Gst.Buffer.new_allocate(None, len(data), None)
                    buffer.fill(0, data)
                    appsrc.emit('push-buffer', buffer)
                    cv2.imshow("Window", frame)
                    
            if cv2.waitKey(1) == "q" or cv2.getWindowProperty("Window", cv2.WND_PROP_VISIBLE) < 1:
                break

        
        cv2.destroyAllWindows()
        
    pipeline.set_state(Gst.State.NULL)     
    


if __name__ == "__main__":
    main()

