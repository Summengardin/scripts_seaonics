import subprocess
import time

PYTHON_SCRIPT_PATH = "./rtsp_multiview.py"

while True:
    print("Starting Python script...")
    process = subprocess.Popen(["python3", PYTHON_SCRIPT_PATH])
    process.wait()
    print(f"Python script exited with status {process.returncode}. Respawning...")
    time.sleep(1)
