"""
Et forsøk på å la GenTL håndtere pylon-kameraer.
G-streamer får bare ansvar for å enkode å sende over rtsp

13.10.23
Multiprocessing kukker til alt.

20.10.23
Ting virker. Latency ned mot 60ms på lokal kjøring
Neste nå: Restart ved disconnect
            Stream over rtsp/mjpeg med gstreamer

27.10.23
Fikset restart ved disconnect
    Kom en exception fra harvesters.update()

"""


import os
import time
import multiprocessing
import multiprocessing.sharedctypes
import numpy as np
import typing
import ctypes

import cv2

from harvesters.core import Harvester, ImageAcquirer, Component
from genicam.gentl import TimeoutException, IoException

PRODUCER_PATH = "/opt/pylon/lib/gentlproducer/gtl/ProducerGEV.cti"
SERIAL_NUMBER_ACE2 = "24595666"
H, W, D = 720, 1280, 3
IMAGE_FORMAT = "BayerBG8"
#IMAGE_FORMAT = "YUV422_YUYV_Packed"

CAM_GRABBER_PROCESS_SILENT = False
NO_CAM_COUNTER_MAX = 20
FPS_PRINT_INTERVAL = 1 # [s]


class CamGrabber():
    def __init__(self, H = H, W = W, D = D) -> None:
        self.cam_grabber_process = CamGrabberProcess(SERIAL_NUMBER_ACE2, H, W, D)
        self.last_frame = np.zeros((H, W, D))
        
        
        self.last_new_frame_time = time.time()
        self.max_frame_time = 2 #s
        
        self.p = multiprocessing.Process(target=self.cam_grabber_process.run, args=())
        self.p.daemon = CAM_GRABBER_PROCESS_SILENT
        self.p.start()
        
        self.H = H
        self.W = W
        self.D = D
        
    def __enter__(self):
        return self
    
    def get_newest_frame(self) -> np.ndarray[typing.Any, np.dtype[np.uint8]] or None:      
        with self.cam_grabber_process.lock:
            now = time.time()
            if self.cam_grabber_process.new_frame_available.value:
                self.last_new_frame_time = now
                self.cam_grabber_process.new_frame_available.value = 0
                            
                frame = np.asarray(self.cam_grabber_process.frame_arr).reshape(self.H,self.W,self.D)
                self.last_frame = frame
                #frame = np.asarray(self.cam_grabber_process.frame_arr, dtype=np.int32).reshape(H,W,1)
                #frame = frame.astype(np.uint8)   
                
                return frame
            else:
                if (now - self.last_new_frame_time > self.max_frame_time):
                    return None
                return self.last_frame

            
    def is_connected(self) -> bool:
        return self.cam_grabber_process.is_connected.value
    
    def is_active(self) -> bool:
        return True
        return self.cam_grabber_process.is_running.value
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        
    def stop(self):
        self.p.terminate()
        self.p.join()
        print("CamGrabber has been deleted")
    
    def __del__(self):
        if self.p.is_alive():
            self.p.terminate()
            
        try:
            self.p.join()
        except:
            pass

        
class CamGrabberProcess():
    def __init__(self, serial_number: str, H=H, W=W, D=D) -> None:
        self.serial_number = serial_number
        
        self.H = H
        self.W = W
        self.D = D
        
        self.frame_arr = multiprocessing.sharedctypes.RawArray(ctypes.c_uint8, self.H*self.W*self.D)
        self.last_frame_arr = multiprocessing.sharedctypes.RawArray(ctypes.c_uint8, self.H*self.W*self.D)
        #self.frame_arr = multiprocessing.sharedctypes.RawArray('i', H*W*1)
        self.lock = multiprocessing.Lock()
        self.new_frame_available = multiprocessing.Value('i', 0)
    
        self.camera = None
        
        self.is_running = multiprocessing.Value(ctypes.c_bool, 0)
        self.is_connected = multiprocessing.Value(ctypes.c_bool, 0)


    def run(self):
        print("-- Starting CamGrabberProcess --")
        self.h = Harvester()
        self.is_running.value = True
        
        try:
            gentl_file = self.__check_gentl_file()
        except AssertionError as e:
            print(f"[ERROR] Could not GenTL file (.cti). Expected to find: {PRODUCER_PATH}")
            return
        
        self.h.add_file(gentl_file)
        print("CTI-file added")
    
        
        last_fps_print_time = time.time()
        fps_counter = 0    
        no_cam_counter = 0
        has_cam = False
        
        try:
            while self.is_running.value:
                #time.sleep(0.001)
                
                if no_cam_counter > NO_CAM_COUNTER_MAX:
                    no_cam_counter = 0
                    print(f"NO_CAM_COUNTER exceeded {NO_CAM_COUNTER_MAX}")
                    #self.is_running.value = False
                    #continue
                    
                if not has_cam:
                    self.camera, has_cam, no_cam_counter = self.__find_cam(self.serial_number, no_cam_counter)

                if has_cam and self.camera is not None:
                    fps_counter, last_fps_print_time = self.__print_fps(fps_counter, last_fps_print_time)
                    has_cam, fps_counter = self.__try_fetch_frame(self.camera, self.lock, self.new_frame_available, self.frame_arr, fps_counter)
                    
                self.is_connected.value = has_cam
                
        except KeyboardInterrupt:
            print("CamGrabberProcess interrupted by KeyboardInterrupt")
        except Exception as e:
            print(f"CamGrabberProcess crashed ({type(e).__name__}): {e}")
               
        self.is_running.value = False    
        if self.camera:
            self.camera.stop()  
        
        self.h.reset()           

    
    def __print_fps(self, fps_counter: int ,last_print_time: float):
        if (time.time() - last_print_time) > FPS_PRINT_INTERVAL:
            last_print_time = time.time()
            print(f"CamGrabber FPS: {fps_counter/FPS_PRINT_INTERVAL}")
            fps_counter = 0
            
        return fps_counter, last_print_time
    
      
    def __reset_harvester(self):
        self.h.reset()
        self.h = Harvester()
        try:
            gentl_file = self.__check_gentl_file()
        except AssertionError as e:
            print(f"[ERROR] Could not GenTL file (.cti). Expected to find: {PRODUCER_PATH}")
            return
        
        self.h.add_file(gentl_file)  
        
        self.h.update()
      
        
    def __find_cam(self, serial_number: str, no_cam_counter: int):
        camera = None
        has_cam = False
        
        print("\n-- Searching for camera --")
        
        try:
            self.h.update()
        except Exception as e: 
            print(f"Error when updating device list: {e}")
                
        if not self.h.device_info_list:
            print(f"[ERROR] Could not find any devices")
            no_cam_counter += 1
            time.sleep(3)
        else:
            print("Found following devices:")
            for device in self.h.device_info_list:
                properties = device.property_dict
                print(f"S/N: {properties['serial_number']} | Model: {properties['model']}")
        
            print(f"\nConnecting to camera: {serial_number}")
            
            try:
                camera = self.h.create({"serial_number":serial_number}) # type:ignore
            except Exception as e:
                print(f"Exception when creating camera: {e}")
                return camera, has_cam, no_cam_counter
            
            try:
                self.__configure_camera(camera)
            except Exception as e:
                print("Exception when configuring camera: ",e)
                return camera, has_cam, no_cam_counter

            try:
                camera.start()
            except Exception as e:
                print("Exception when starting camera: ",e)
                return camera, has_cam, no_cam_counter
            
            print(f"Connected to camera and started it.")
                
            has_cam = True

        
        return camera, has_cam, no_cam_counter
  
        
    def __configure_camera(self, camera: ImageAcquirer):
        print("\n-- Configuring camera --")
        print("Current PixelFormat: ", camera.remote_device.node_map.PixelFormat.value)
        print("Current PacketSize: ", camera.remote_device.node_map.GevSCPSPacketSize.value)
        print("Current AcquisitionFrameRateEnable: ", camera.remote_device.node_map.AcquisitionFrameRateEnable.value,)
        print("Current Width: ", camera.remote_device.node_map.Width.value)
        print("Current Height: ", camera.remote_device.node_map.Height.value)
        print("")
        
        camera.remote_device.node_map.PixelFormat.value = IMAGE_FORMAT
        camera.remote_device.node_map.GevSCPSPacketSize.value = 9000
        camera.remote_device.node_map.AcquisitionFrameRateEnable.value = False
        camera.remote_device.node_map.Width.value = self.W
        camera.remote_device.node_map.Height.value = self.H
        
        print("New PixelFormat: ", camera.remote_device.node_map.PixelFormat.value)
        print("New PacketSize: ", camera.remote_device.node_map.GevSCPSPacketSize.value)
        print("New AcquisitionFrameRateEnable: ", camera.remote_device.node_map.AcquisitionFrameRateEnable.value)
        print("New Width: ", camera.remote_device.node_map.Width.value)
        print("New Height: ", camera.remote_device.node_map.Height.value)
        print("")
            
    def __check_gentl_file(self):
        #print("[->] Check gentl")
        if os.path.exists(PRODUCER_PATH):
            return PRODUCER_PATH
        else:
            assert False
    
    
    def __try_fetch_frame(self, camera: ImageAcquirer, lock: multiprocessing.Lock, new_frame_available, frame_array, fps_counter: int):
        
        has_cam = False
        frame = None
        
        try:
            with camera.fetch(timeout=1) as buffer:
            
                component = buffer.payload.components[0]            
                frame = self.__retrieve_img_from_component(component)
                
                with lock:
                    fps_counter += 1
                    new_frame_available.value = 1
                    
                    flat_frame = frame.flatten()
                    
                    ctypes.memmove(frame_array, frame.ctypes.data, frame_array._length_)
                    #frame_array[:] = flat_frame[:]
                    
                has_cam = True                
                 
        except IoException as e:
            print(f"Camera disconnected. {e}")
        
        except IndexError as e:
            print(f"Exception when reading from stream. Trying to restart. {e}")

        except TimeoutException as e:
            print(f"Fetching from camera timed out. {e}")

        except Exception as e:
            print(f"Something went wrong during fetch, {e}")          
        
        return has_cam, fps_counter
    
    
    def __retrieve_img_from_component(self, component: Component):
        #print("[->]Retrieve img")

        img = None
        data_format = component.data_format
        frame = component.data.reshape(component.height, component.width, int(component.num_components_per_pixel))

        if IMAGE_FORMAT == "Mono8":
            img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif IMAGE_FORMAT == "BayerBG8" or IMAGE_FORMAT == "BayerBG10p" or IMAGE_FORMAT == "BayerBG10":
            img = cv2.cvtColor(frame, cv2.COLOR_BayerBG2BGR)
        elif IMAGE_FORMAT == "YUV422_8" or IMAGE_FORMAT == "YUV422_YUYV_Packed":
            img = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUYV) 

        return img
        #return frame
        
        

    def __del__(self):
        self.running = False
        print("CamGrabberProcess has been deleted")
        

if __name__== "__main__":

    with CamGrabber() as cam_grabber:
        cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
        time.sleep(3)
        while cam_grabber.is_active():
            if cam_grabber.is_connected():
                frame = cam_grabber.get_newest_frame()
                
                if frame is not None:
                    cv2.cvtColor(frame, cv2.COLOR_RGB2BGR, frame)
                    cv2.imshow("Window", frame)
                    
            if cv2.waitKey(1) == "q" or cv2.getWindowProperty("Window", cv2.WND_PROP_VISIBLE) < 1:
                break

        
        cv2.destroyAllWindows()
        print("Exiting main")
    
       