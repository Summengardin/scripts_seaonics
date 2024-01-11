import cv2
import sys

def main(rtsp_url):
    # Define the GStreamer pipeline
    gst_pipeline = (
        f"rtspsrc location={rtsp_url} latency=0 "
        "! rtph264depay "
        "! h264parse "
        "! avdec_h264 "
        "! videoconvert " 
        "! video/x-raw,format=BGR "
        "! appsink emit-signals=True sync=False"
    )

    # Create an OpenCV VideoCapture object
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("Error: Unable to open video source")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to fetch frame")
                break

            cv2.imshow('RTSP Stream', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <RTSP_URL>")
        sys.exit(1)

    rtsp_url = sys.argv[1]
    main(rtsp_url)
