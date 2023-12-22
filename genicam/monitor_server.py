import subprocess
import time
import argparse

PYTHON_SCRIPT_PATH = "./gentl_rtsp_server.py"

argparser = argparse.ArgumentParser(description='RTSP server')
argparser.add_argument('--port', type=str, default="8554", help='Port to run RTSP server on')
argparser.add_argument('-c', '--cti', type=str, default="", help='Relative path to .cti file')
args = argparser.parse_args()
port = args.port
cti_file = args.cti

while True:
    print("Starting Python script...")
    process = subprocess.Popen(["python3", PYTHON_SCRIPT_PATH, "-c", cti_file])
    process.wait()
    print(f"Python script exited with status {process.returncode}. Respawning...")
    time.sleep(1)
