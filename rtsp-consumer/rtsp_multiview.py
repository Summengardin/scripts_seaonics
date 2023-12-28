import cv2
import sys
import numpy as np
import time

from lib.rtsp_cam_grab import RTSPCamGrabber


W = 640
H = 512


def dummy_frame(tag = "", W=1280, H=1024): 
        # Generate a dummy frame

        # Background
        frame = np.full((H, W, 3), (95, 83, 25), dtype=np.uint8)
        
        # setup text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "Server is not connected"
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
    


def create_small_frame(frame1, frame2, rgb_color, outline_color=(0, 255, 0), outline_thickness=2):
    # Resize frame2 if it's larger than frame1
    if frame2.shape[0] > frame1.shape[0] or frame2.shape[1] > frame1.shape[1]:
        scale_ratio = min(frame1.shape[0] / frame2.shape[0], frame1.shape[1] / frame2.shape[1])
        frame2 = cv2.resize(frame2, None, fx=scale_ratio, fy=scale_ratio, interpolation=cv2.INTER_AREA)

    # Create a new temporary frame with the height of frame1 and the width of frame2
    temp_frame = np.zeros((frame1.shape[0], frame2.shape[1], 3), dtype=np.uint8)

    # Fill the temporary frame with the specified RGB color
    temp_frame[:] = rgb_color

    # Overlay frame2 onto the bottom part of the temporary frame
    y_offset = frame1.shape[0] - frame2.shape[0]
    temp_frame[y_offset:y_offset+frame2.shape[0], :frame2.shape[1]] = frame2

    # Draw an outline around frame2
    cv2.rectangle(temp_frame, (0, y_offset), (frame2.shape[1], y_offset + frame2.shape[0]), outline_color, outline_thickness)

    return temp_frame
    
def display_rtsp_frames_same_window(cam_grabbers, enable_logging=False):
    cv2.namedWindow("Camera view", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Camera view", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    primary_index = 0  # Index to determine which frame is primary

    while True:
        frames_to_display = []

        for i, grabber in enumerate(cam_grabbers):
            frame = grabber.get_frame()
            if frame is not None:
                frames_to_display.append(frame)
            else:
                frame = dummy_frame(grabber.rtsp_url, W=grabber.W, H=grabber.H)
                cv2.putText(frame, str(i), (50, 200), cv2.FONT_HERSHEY_DUPLEX, 5, (240, 243, 245), 2)
                frames_to_display.append(frame)

        if frames_to_display:
            primary_frame = frames_to_display[primary_index]
            secondary_frame = frames_to_display[1 - primary_index]

            # Resize the secondary frame to be smaller
            small_frame = cv2.resize(secondary_frame, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)

            small_frame = create_small_frame(primary_frame, small_frame, (0,0,0))

            output_frame = np.hstack([primary_frame, small_frame])


            cv2.putText(output_frame, "Press 'ESC' to exit        Press 'SPACE' to change camera", (20, primary_frame.shape[0] - 20), cv2.FONT_HERSHEY_DUPLEX, 0.4, (240, 243, 245), 1)
           
            cv2.imshow("Camera view", output_frame)


        # Check for spacebar press or window close
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Spacebar pressed
            primary_index = 1 - primary_index  # Swap the primary frame
        elif key == ord('q') or key == 27 or cv2.getWindowProperty('Camera view', cv2.WND_PROP_VISIBLE) < 1:
            # 'q', ESC or window closed
            break
        continue
        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        #print("Usage: python3 stream_viewer.py <RTSP URL 1> <RTSP URL 2> ...")
        print("Using 'rtsp://10.1.2.81:8554/cam' and 'rtsp://10.1.2.82:8554/cam'")
        
        rtsp_urls = ["rtsp://10.1.2.81:8554/cam", "rtsp://10.1.2.82:8554/cam"]
        rtsp_urls = ["rtsp://10.0.0.34:8554/cam", "rtsp://10.0.0.39:8554/cam"]
    else:
        rtsp_urls = sys.argv[1:]
        
        
    enable_logging = False   
    rtsp_grabbers = [RTSPCamGrabber(rtsp_url=url, W=W, H=H) for url in rtsp_urls]
    
    try:
        display_rtsp_frames_same_window(rtsp_grabbers, enable_logging=enable_logging)
    except Exception as e:
        print(f"Error displaying frames: {e}")
        
    for grabber in rtsp_grabbers:
        grabber.stop()
    
    
    cv2.destroyAllWindows()
