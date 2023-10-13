"""
Et forsøk på å la GenTL håndtere pylon-kameraer.
G-streamer får bare ansvar for å enkode å sende over rtsp

"""

import platform
import os
import multiprocessing
import numpy as np
import typing


PRODUCER = "mvGenTLProducer.cti"
SERIAL_NUMBER_ACE2 = "24595666"
H, W, D = 1024, 1280, 3


def find_producer(name: str):
    """ Helper for the GenTL producers from the environment path.
    """
    try:
        paths = os.environ['GENICAM_GENTL64_PATH3000'].split(os.pathsep)
    except:
        paths = []

    if platform.system() == "Linux":
        paths.append('/opt/mvIMPACT_Acquire/lib/x86_64/')
        paths.append('/opt/mvIMPACT_Acquire/lib/arm64/')
    elif platform.system() == "Windows":
        paths.append('C:/Program Files/MATRIX VISION/mvIMPACT Acquire/bin/x64/')


    for path in paths:
        path += name
        if os.path.exists(path):
            return path
    return ""


class CamGrabber():
    def __init__(self) -> None:
        self.cam_grabber_process = CamGrabberProcess(SERIAL_NUMBER_ACE2, H: int = 1024, W: int = 1280, D: int = 3)
        self.H, self.W, self.D = H, W, D
    
    def get_newest_frame(self) -> np.ndarray[typing.Any, np.dtype[typing.Any]] or None:
        with self.cam_grabber_process.lock:
            if self.cam_grabber_process.newest_frame.value:
                self.cam_grabber_process.newest_frame.value = 0
                frame = np.asarray(self.camGrabberProcess.frame_arr_lower_right).reshape(H,W,D)
                return frame

        
class CamGrabberProcess():
    def __init__(self, serial_number: str) -> None:
        self.first_run = True
        self.running = True
        
        self.serial_number = serial_number
        self.lock_right = multiprocessing.Lock()

        self.newest_frame = multiprocessing.Value('i', 0)
    
        



if __name__== "__main__":
    # Location of the Basler blaze GenTL producer.
    if platform.system() == "Windows" or platform.system() == "Linux":
        gentl_file = find_producer(PRODUCER)  
    else:
        print(f"{platform.system()} is not supported.")
        assert False
        