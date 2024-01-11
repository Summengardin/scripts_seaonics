import cv2
import numpy as np
import yaml

from lib.rtsp_cam_grab import RTSPCamGrabber

import logging
logging.basicConfig(
    filename='consumer.log', encoding='utf-8',
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%d-%m-%Y %H:%M:%S')
log = logging.getLogger(__name__)


def parse_config():
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
        
        width = cfg.get("width")
        height = cfg.get("height")
        ip_windmill = cfg.get("ip").get("windmill")
        ip_ship = cfg.get("ip").get("ship")
        port_windmill = cfg.get("port").get("windmill")
        port_ship = cfg.get("port").get("ship")
        mount = cfg.get("mount")
    
    log.info("Config parsed")
    log.debug(f"Config: {cfg}")
    
    return width, height, ip_windmill, ip_ship, port_windmill, port_ship, mount


def dummy_frame(tag = "", W=1280, H=1024):        
    frame = np.full((H, W, 3), (95, 83, 25), dtype=np.uint8)

    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "Server is not connected"
    font_scale = 1.5
    font_thickness = 2

    # get boundary of this text
    textsize = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    textX = (frame.shape[1] - textsize[0]) / 2
    textY = (frame.shape[0] + textsize[1]) / 2
    
    cv2.putText(frame, text, (int(textX), int(textY) ), font, font_scale, (240, 243, 245), font_thickness)
    cv2.putText(frame, f"From {tag}", (int(textX), int(textY+50) ), font, font_scale*0.5, (240, 243, 245), font_thickness//2)
    return frame
    

def create_preview_frame(big_frame, small_frame, fill_rgb=(0,0,0), outline_rgb=(200,200,200), outline_thickness=2):
    # Resize the small frame if needed
    if small_frame.shape[0] > big_frame.shape[0] or small_frame.shape[1] > big_frame.shape[1]:
        scale_ratio = min(big_frame.shape[0] / small_frame.shape[0], big_frame.shape[1] / small_frame.shape[1])
        small_frame = cv2.resize(small_frame, None, fx=scale_ratio, fy=scale_ratio, interpolation=cv2.INTER_AREA)

    # Create frame with the width of the small frame and the height of the big frame
    temp_frame = np.zeros((big_frame.shape[0], small_frame.shape[1], 3), dtype=np.uint8)
    temp_frame[:] = fill_rgb

    # Add the small frame to temp
    y_offset = big_frame.shape[0] - small_frame.shape[0]
    temp_frame[y_offset:y_offset+small_frame.shape[0], :small_frame.shape[1]] = small_frame

    # Draw an outline
    cv2.line(temp_frame, (0, y_offset), (small_frame.shape[1], y_offset), outline_rgb, outline_thickness)
    cv2.line(temp_frame, (0+outline_thickness//2, y_offset), (0+outline_thickness//2, big_frame.shape[0]), outline_rgb, outline_thickness)

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
            small_frame = create_preview_frame(primary_frame, small_frame, (0,0,0))
            output_frame = np.hstack([primary_frame, small_frame])

            cv2.putText(output_frame, "Press 'ESC' to exit        Press 'SPACE' to change camera", (20, primary_frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (240, 243, 245), 1)
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
    W, H, IP_WINDMILL, IP_SHIP, PORT_WINDMILL, PORT_SHIP, MOUNT = parse_config()
    log.debug(f"Image resolution: {W} x {H}")

    log.info(f"Using 'rtsp://{IP_WINDMILL}:{PORT_WINDMILL}/{MOUNT}' and 'rtsp://{IP_SHIP}:{PORT_SHIP}]/{MOUNT}'\n")
    rtsp_urls = [f"rtsp://{IP_WINDMILL}:{PORT_WINDMILL}/{MOUNT}", f"rtsp://{IP_SHIP}:{PORT_SHIP}/{MOUNT}"]

    rtsp_grabbers = [RTSPCamGrabber(rtsp_url=url, W=W, H=H) for url in rtsp_urls]
    
    try:
        display_rtsp_frames_same_window(rtsp_grabbers)
    except Exception as e:
        log.error(f"Error displaying frames: {e}")
        
    for grabber in rtsp_grabbers:
        grabber.stop()
    
    
    cv2.destroyAllWindows()
