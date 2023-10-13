"""
Et forsøk på å la GenTL håndtere pylon-kameraer.
G-streamer får bare ansvar for å enkode å sende over rtsp


Multiprocessing kukker med alt

"""


import os
import time
import multiprocessing
import multiprocessing.sharedctypes
import numpy as np
import typing

import cv2

from harvesters.core import Harvester, ImageAcquirer, Component
from genicam.gentl import TimeoutException

PRODUCER_PATH = "/opt/pylon/lib/gentlproducer/gtl/ProducerGEV.cti"
SERIAL_NUMBER_ACE2 = "24595666"
H, W, D = 1024, 1280, 3

CAM_GRABBER_PROCESS_SILENT = False
NO_CAM_COUNTER_MAX = 20


class CamGrabber():
    def __init__(self) -> None:
        self.cam_grabber_process = CamGrabberProcess(SERIAL_NUMBER_ACE2)
        global H, W, D
        self.H, self.W, self.D = H, W, D
        
        self.p = multiprocessing.Process(target=self.cam_grabber_process.run, args=())
        self.p.daemon = CAM_GRABBER_PROCESS_SILENT
        self.p.start()
    
    
    def get_newest_frame(self) -> np.ndarray[typing.Any, np.dtype[typing.Any]] or None:
        with self.cam_grabber_process.lock:
            if self.cam_grabber_process.new_frame_available.value:
                self.cam_grabber_process.new_frame_available.value = 0
                frame = np.asarray(self.cam_grabber_process.frame_arr).reshape(H,W,D)
                return frame
            
    def is_connected(self) -> bool:
        return self.cam_grabber_process.has_cam
    
    def __del__(self):
        self.p.join()

        
class CamGrabberProcess():
    def __init__(self, serial_number: str) -> None:
        self.serial_number = serial_number
        
        global H, W, D
        self.frame_arr = multiprocessing.sharedctypes.RawArray('i', H*W*D)
        self.lock = multiprocessing.Lock()
        self.new_frame_available = multiprocessing.Value('i', 1)
    
        self.camera = None
        self.has_cam = False
        
        self.running = True
        self.connected = False


    def run(self):
        print("Starting CamGrabberProcess")
        self.h = Harvester()
        
        try:
            gentl_file = self.__check_gentl_file()
        except AssertionError as e:
            print(f"[ERROR] Could not GenTL file (.cti). Expected to find: {PRODUCER_PATH}")
            return
        
        self.h.add_file(gentl_file)
        print("CLI-file added")
        
        self.has_cam = False
        
        self.h.update()
        print("Device list updated. Found following devices:")
        for device in self.h.device_info_list:
            properties = device.property_dict
            print(f"S/N: {properties['serial_number']} | Model: {properties['model']}")
        
        if not self.h.device_info_list:
            print(f"[ERROR] Could not find any devices")
            return
        
        no_cam_counter = 0
        while self.running:
            time.sleep(0.001) 
            if no_cam_counter > NO_CAM_COUNTER_MAX:
                print(f"NO_CAM_COUNTER exceeded {NO_CAM_COUNTER_MAX}")
                self.running = False
                continue
                
            if not self.has_cam:
                self.camera, self.has_cam, no_cam_counter = self.__find_cam(self.serial_number, no_cam_counter)

            if self.has_cam and self.camera is not None:
                self.has_cam = self.__try_fetch_frame(self.camera, self.lock, self.frame_arr)
            
            
        if self.camera:
            self.camera.stop()             

            
        
    def __find_cam(self, serial_number: str, error_counter: int):
        print("[->]Find Cam")
        camera = None
        has_cam = False
        print(f"Searching for camera: {serial_number}")

        device_info = next((d for d in self.h.device_info_list if str(d.serial_number).startswith(serial_number)), None)
        if device_info is not None:
            camera = self.h.create({"serial_number":device_info.serial_number}) # type:ignore
            try:
                camera.start()
            except Exception as e:
                print("Exception when starting camera: ",e)
                
            has_cam = True
        else:
            print("Could not find camera")
            error_counter += 1
        
        return camera, has_cam, error_counter
  
        
    def __check_gentl_file(self):
        print("[->] Check gentl")
        if os.path.exists(PRODUCER_PATH):
            return PRODUCER_PATH
        else:
            assert False
    
    
    def __try_fetch_frame(self, camera: ImageAcquirer, lock: multiprocessing.Lock, frame_array):
        print("[->]Fetch frame")
        has_cam = True
        frame = None
        
        try:
            with camera.fetch(timeout=1) as buffer:
                component = buffer.payload.components[0]
                frame = self.__retrieve_img_from_component(component)
            
                with lock:
                    self.new_frame_available.value = 1
                    frame_array[:] = frame.flatten()[:]
                    
                 
        except IndexError as e:
            print(f"Exception when reading from stream. Trying to restart. {e}")
            has_cam = False

        except TimeoutException as e:
            print(f"Fetching from camera timed out. {e}")
            has_cam = False

        except Exception as e:
            print(f"Something went wrong during fetch, {e}")
            has_cam = False
            
        return has_cam
    
    
    def __retrieve_img_from_component(self, component: Component):
        
        img = None
        data_format = component.data_format
        frame = component.data.reshape(component.height, component.width, int(component.num_components_per_pixel))

        if data_format == "Mono8":
            img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif data_format == "BayerBG8" or data_format == "BayerBG10p" or data_format == "BayerBG10":
            img = cv2.cvtColor(frame, cv2.COLOR_BayerBG2RGB)
        elif data_format == "YUV422_8":
            img = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUYV)    

        return img
    
    def __del__(self):
        print("CamGrabberProcess has been deleted")
        

if __name__== "__main__":

    cam_grabber = CamGrabber()
    
    while True:
        print("Main loop")
        if cam_grabber.is_connected():
            frame = cam_grabber.get_newest_frame()
            print(frame.shape)
            cv2.imshow("Window", frame.astype(np.uint8))
        
        if cv2.waitKey(1) == "q":
            break
    del cam_grabber
    
    cv2.destroyAllWindows()
    
    
       