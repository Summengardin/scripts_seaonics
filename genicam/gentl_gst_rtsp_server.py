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
        "fakesink dump=1 "
    )
    '''
        "x264enc speed-preset=ultrafast tune=zerolatency ! "
        "rtph264pay config-interval=1 name=pay0 pt=96 "
        decodebin ! x264enc ! rtph264pay ! udpsink host=192.168.52.129 port=9001
    )'''
    
    pipeline_str_2 = ("appsrc name=src is-live=true format=GST_FORMAT_TIME " 
        "caps=video/x-raw(memory:NVMM),format=BGR,width=640,height=480,framerate=30/1 !" 
        "nvvidconv !" 
        "nvh264enc enable-full-frame=true !" 
        "rtph264pay pt=96 name=pay0")
    
    pipeline_str_3 = ("appsrc name=src is-live=true format=GST_FORMAT_TIME "
        "caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! "
        "decodebin !"
        "x264enc ! "
        "rtph264pay !"
        "udpsink port=9001"
        )
        
    pipeline = Gst.parse_launch(pipeline_str_3)
    
    appsrc = pipeline.get_by_name("src")
    

    # Set to playing state
    pipeline.set_state(Gst.State.PLAYING)

    # Properly timing your frames
    pts = 0
    duration = Gst.SECOND / 30  # Assuming 30 fps

    with camgrab.CamGrabber() as cam_grabber:
        cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
        while cam_grabber.is_active():
            if cam_grabber.is_connected():
                frame = cam_grabber.get_newest_frame()
                
                if frame is not None:
                    # Push frame to GStreamer pipeline
                    data = frame.tobytes()
                    # Create the GstBuffer and set its duration and pts
                    buffer = Gst.Buffer.new_allocate(None, len(data), None)
                    buffer.fill(0, data)
                    buffer.duration = duration
                    buffer.pts = pts
                    pts += duration  # Increment pts for the next frame

                    time.sleep(0.05)
                    #cv2.imshow("Window", frame)
                    
                    # Emit the buffer
                    result = appsrc.emit('push-buffer', buffer)
                    if result != Gst.FlowReturn.OK:
                        print("Error pushing buffer")
                        break

                    # Sleep if you're pushing frames faster than real-time
                    time.sleep(duration)
                    
            if cv2.waitKey(1) == "q" or cv2.getWindowProperty("Window", cv2.WND_PROP_VISIBLE) < 1:
                break

        
        cv2.destroyAllWindows()
        
    pipeline.set_state(Gst.State.NULL)     
    


if __name__ == "__main__":
    main()

