import platform
import os, sys
import cv2
import time
import threading
import numpy as np
import typing
import logging
from datetime import datetime
import multiprocessing
import multiprocessing.sharedctypes
import ctypes
import traceback

print("starting")
print(time.strftime("%Y-%m-%d %H:%M", time.gmtime()))
logger = logging.getLogger('my_logger')

from harvesters.core import Harvester
import harvesters.core
# import mjpeg_stream
# import psutil


from genicam.gentl import TimeoutException #type:ignore

start_time_string = datetime.utcnow().strftime('%Y-%m-%d-%H.%M.%S.%f')[:-3]

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
        path += os.path.sep + name
        if os.path.exists(path):
            return path
    return ""

def save_img(img: np.ndarray[typing.Any, np.dtype[typing.Any]] | None):
        cwd = os.getcwd()
        try:
            os.mkdir(cwd+"/saved-images/")
        except Exception as e: # type: ignore
            pass
        foldername = cwd+"/saved-images/"+start_time_string+"/"
        print (foldername)
        try:
            os.mkdir(foldername)
        except Exception as e: # type: ignore
            pass

        ts = datetime.utcnow().strftime('%Y-%m-%d-%H.%M.%S.%f')[:-3]
    
        if img is not None and ts != '':
            _, jpg_img = cv2.imencode('.jpg', img) #type:ignore
            filename = foldername+ts+"_img_"+".jpeg"
            f = open(filename, 'wb')
            f.write(jpg_img) #type:ignore
            f.close()


class CamGrabber():
    def __init__(self, save_video: bool, undistort_img: bool, lower_right_serial_number: str, lower_left_serial_number: str, right_serial_number: str, dummy_imgs: bool=False) -> None:

        # H, W, D = 544, 728, 3
        # self.frame: np.ndarray[typing.Any, np.dtype[typing.Any]] = np.empty((H,W,D))
        self.dummy_imgs = dummy_imgs
        self.example_img:np.ndarray[typing.Any, np.dtype[typing.Any]] = cv2.imread("./example_img.jpeg", cv2.IMREAD_UNCHANGED) # type:ignore

        self.camGrabberProcess = CamGrabberProcess(save_video, undistort_img, lower_right_serial_number, lower_left_serial_number, right_serial_number)

        if not dummy_imgs:
            p = multiprocessing.Process(target=self.camGrabberProcess.run, args=())
            p.daemon = True
            p.start()
        

    def get_new_frame_lower_right(self) -> np.ndarray[typing.Any, np.dtype[typing.Any]] | None:
        if self.dummy_imgs:
            return self.example_img
        else:
            with self.camGrabberProcess.lock_lower_right:
                if self.camGrabberProcess.new_frame_lower_right.value: # type:ignore
                    self.camGrabberProcess.new_frame_lower_right.value = 0 # type:ignore
                    H, W, D = 544, 728, 3
                    frame = np.asarray(self.camGrabberProcess.frame_arr_lower_right).reshape(H,W,D)
                    return frame

    def get_most_recent_frame_right(self) -> np.ndarray[typing.Any, np.dtype[typing.Any]] | None:
        if self.dummy_imgs:
            return self.example_img
        else:
            with self.camGrabberProcess.lock_right: #TODO add image age check. return None if too old
                H, W, D = 500, 728, 3
                frame = np.asarray(self.camGrabberProcess.frame_arr_right).reshape(H,W,D)
                return frame
    
    def get_most_recent_frame_lower_left(self) -> np.ndarray[typing.Any, np.dtype[typing.Any]] | None:
        if self.dummy_imgs:
            H, W, D = 544, 728, 3
            tmp = np.zeros((H,W,D))
            tmp[:,100::,:] = self.example_img[:, :-100:, :]
            return tmp
        else:
            with self.camGrabberProcess.lock_lower_left: #TODO add image age check. return None if too old
                H, W, D = 544, 728, 3
                frame = np.asarray(self.camGrabberProcess.frame_arr_lower_left).reshape(H,W,D)
                return frame
    
        


class CamGrabberProcess():
    def __init__(self, save_video: bool, undistort_img: bool, lower_right_serial_number: str, lower_left_serial_number: str, right_serial_number: str) -> None:
        
        self.undistort_img = undistort_img
        if undistort_img:
            try:
                cv_file = cv2.FileStorage("./cal.xml", cv2.FILE_STORAGE_READ)
            except:
                cv_file = cv2.FileStorage("cal.xml", cv2.FILE_STORAGE_READ)
            self.cam_matrix = cv_file.getNode("camera_matrix").mat()
            self.distortion_coefficients = cv_file.getNode("distortion_coefficients").mat()
            print(self.cam_matrix)

        H, W, D = 544, 728, 3
        # self.frame_arr = multiprocessing.Array(ctypes.c_double, W*H*D)
        self.frame_arr_lower_right = multiprocessing.sharedctypes.RawArray(ctypes.c_double, W*H*D)
        self.frame_arr_lower_left = multiprocessing.sharedctypes.RawArray(ctypes.c_double, W*H*D)
        H_right = 500
        self.frame_arr_right = multiprocessing.sharedctypes.RawArray(ctypes.c_double, W*H_right*D)

        self.lock_lower_right = multiprocessing.Lock()
        self.lock_lower_left = multiprocessing.Lock()
        self.lock_right = multiprocessing.Lock()
        # self.frame = np.frombuffer(self.frame_arr.get_obj()).reshape(H,W,D)

        # self.frame: None | np.ndarray[typing.Any, np.dtype[typing.Any]] = None
        self.new_frame_lower_right = multiprocessing.Value('i', 0)
        self.new_frame_lower_left = multiprocessing.Value('i', 0)
        self.new_frame_right = multiprocessing.Value('i', 0)
        # self.x = Value('i', 20)
        self.first_run = True
        self.running = True

        self.lower_right_serial_number = lower_right_serial_number
        self.lower_left_serial_number = lower_left_serial_number
        self.right_serial_number = right_serial_number



    def run(self):
        print("init cam grabber")
        self.connected = False
        # self.save_video = save_video
        
        self.h = Harvester()


        # Location of the Basler blaze GenTL producer.
        if platform.system() == "Windows" or platform.system() == "Linux":
            gentl_file = find_producer("mvGenTLProducer.cti")
        else:
            print(f"{platform.system()} is not supported.")
            assert False

        # gentl_file = r"C:\Program Files\MATRIX VISION\mvIMPACT Acquire\bin\x64\mvGenTLProducer.cti"

        # assert os.path.exists(path_to_blaze_cti)
        print("assert")
        assert os.path.exists(gentl_file)
        print("assert done")
        self.has_cam_lower_right = False
        self.has_cam_lower_left = False
        self.has_cam_right = False
        self.h.add_file(gentl_file)
        print("added gentl file")
        # Update device list.
        self.h.update()
        print("update done")
        print("Starting cam grabber for")
        global logger
        logger.warning("Starting cam grabber at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

        last_print_time_lower_right = time.time()
        last_print_time_lower_left = time.time()
        last_print_time_right = time.time()

        lower_right_fps_counter = 0
        lower_left_fps_counter = 0
        right_fps_counter = 0

        lower_right_timeout_counter = 0
        lower_left_timeout_counter = 0
        right_timeout_counter = 0

        self.mapx = None
        self.mapy = None

        no_cam_counter = 0
        # newcameramtx, roi = cv.getOptimalNewCameraMatrix(cal.cameraMatrix, cal.distortionCoefficients, (w,h), 1, (w,h))
        lower_right_cam = None
        lower_left_cam = None
        right_cam = None
        # cap = None
        while self.running:
            time.sleep(0.001)
            if no_cam_counter > 20:
                logger.warning("No cam counter exceeded")
                # self.running = False
            if not self.has_cam_lower_right:
                lower_right_cam, self.has_cam_lower_right, no_cam_counter = self.find_cam(self.lower_right_serial_number, self.has_cam_lower_right, no_cam_counter)

            if not self.has_cam_right:
                right_cam, self.has_cam_right, no_cam_counter = self.find_cam(self.right_serial_number, self.has_cam_right, no_cam_counter)

            if not self.has_cam_lower_left:
                lower_left_cam, self.has_cam_lower_left, no_cam_counter = self.find_cam(self.lower_left_serial_number, self.has_cam_lower_left, no_cam_counter)

            if self.has_cam_lower_right and lower_right_cam is not None:
                lower_right_fps_counter = self.print_fps(last_print_time_lower_right, lower_right_fps_counter)

                lower_right_fps_counter, lower_right_timeout_counter, self.has_cam_lower_right = self.try_to_fetch_cam(lower_right_cam, lower_right_fps_counter, lower_right_timeout_counter, 
                                                                                 self.lock_lower_right, self.new_frame_lower_right, self.frame_arr_lower_right)
                    
            if self.has_cam_right and right_cam is not None:
                right_fps_counter = self.print_fps(last_print_time_right, right_fps_counter)
                right_fps_counter, right_timeout_counter, self.has_cam_right = self.try_to_fetch_cam(right_cam, right_fps_counter, right_timeout_counter, 
                                                                                 self.lock_right, self.new_frame_right, self.frame_arr_right, 500)
                
            if self.has_cam_lower_left and lower_left_cam is not None:
                lower_left_fps_counter = self.print_fps(last_print_time_lower_left, lower_left_fps_counter)
                lower_left_fps_counter, lower_left_timeout_counter, self.has_cam_lower_left = self.try_to_fetch_cam(lower_left_cam, lower_left_fps_counter, lower_left_timeout_counter, 
                                                                                 self.lock_lower_left, self.new_frame_lower_left, self.frame_arr_lower_left)
                    
                
    def find_cam(self, cam_SN: str, has_cam_bool: bool, no_cam_counter: int):
        the_cam = None
        print("looking for cam: ",cam_SN)
        try: #H2386410
            # self.h.update()
            dev_info = next((d for d in self.h.device_info_list if str(d.serial_number).startswith(cam_SN)), None) #type:ignore
            print(dev_info)
            print(self.h.device_info_list)
            if dev_info is not None:
                the_cam = self.h.create({"model":dev_info.model, "serial_number":dev_info.serial_number}) # type:ignore
                # cam = self.h.create(0)
                try:
                    the_cam.start()
                except Exception as e:
                    print("Exception when starting cam: ",e)
                has_cam_bool = True
                print("Got connection to cam")
                no_cam_counter = 0
            else:
                print("Didnt find camera. sleeping a bit before looking again")
                # time.sleep(2)
                no_cam_counter += 1
        except Exception as e:
            print("Exception finding cam: ",e)
            traceback.print_exc()
            # time.sleep(1)
            no_cam_counter += 1

        return the_cam, has_cam_bool, no_cam_counter


    def print_fps(self, last_print_time: float, fps_counter: int):
        if time.time()-last_print_time > 10:
            last_print_time = time.time()
            print("Avg fps last 10 sec: ",fps_counter/10)
            logger.warning("Avg fps last 10 sec: " +str(fps_counter/10))
            fps_counter = 0
        return fps_counter

    def try_to_fetch_cam(self, cam: harvesters.core.ImageAcquirer, fps_counter: int, timeout_counter: int, lock, new_frame, array_to_place, img_height=544):
        has_cam = True
        try:
            with cam.fetch(timeout=1) as buffer:
                component = buffer.payload.components[0]
                # print(component)
                _2d_new = component.data.reshape(component.height,component.width,int(component.num_components_per_pixel))
                # _2d_new = cv2.cvtColor(_2d_new , cv2.COLOR_RGB2BGR)
                img_2d = cv2.cvtColor(_2d_new, cv2.COLOR_BayerRG2RGB) 
                if self.undistort_img:
                    if self.first_run:
                        self.first_run = False
                        h, w = img_2d.shape[:2]
                        self.mapx, self.mapy = cv2.initUndistortRectifyMap(self.cam_matrix, self.distortion_coefficients, None, self.cam_matrix, (w, h), cv2.CV_32FC1)
                    img_2d = cv2.remap(img_2d, self.mapx, self.mapy, cv2.INTER_LINEAR)

                with lock: 
                    new_frame.value = 1 #type:ignore

                    fps_counter += 1

                    img_2d = cv2.resize(img_2d, (728,img_height), cv2.INTER_AREA)
                    array_to_place[:] = img_2d.flatten()[:]
                    timeout_counter = 0


        except IndexError as e:
            print("Exception when reading from stream. trying to restart. ",e)
            has_cam = False

        except TimeoutException as e:
            timeout_counter += 1
            if timeout_counter > 100:
                print("Cam fetch timed out. Trying to get new cam")
                # self.frame = None
                has_cam = False

        except TimeoutError as e:
            print("Cam fetch timed out. Trying to get new cam")
            has_cam = False
        
        return fps_counter, timeout_counter, has_cam

    # def get_frame(self):
    #     with self.lock:
    #         return self.frame
        
    # def get_new_frame(self, blocking: bool = False):
    #     with self.lock:
    #         if self.new_frame.value: #type:ignore
    #             self.new_frame.value = 0 #type:ignore
    #             return self.frame
    #     if blocking:
    #         while True:
    #             time.sleep(0.1)
    #             with self.lock:
    #                 if self.new_frame.value: #type:ignore
    #                     self.new_frame.value = 0 #type:ignore
    #                     return self.frame
                    

