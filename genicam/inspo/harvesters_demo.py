"""
NOTE-TO-SELF 13.10.23

Stream er oppe å kjører med open-cv. Kan også veksle mellom ulike pixel-formats.
Siste "gjennombruddet" var at CTI-fila som fulgte hadde en trial-periode på seg. 
Byttet til pylon sin CTI-fil, og da virket det over lengre tid.

Neste nå blir enten å få til å sende over rtsp, eller å bygge ut biblioteket på Emil-vis

"""



import numpy as np
import cv2
import time

from harvesters.core import Harvester

#PRODUCER_PATH = '/opt/mvIMPACT_Acquire/lib/arm64/mvGenTLProducer.cti'
PRODUCER_PATH = "/opt/pylon/lib/gentlproducer/gtl/ProducerGEV.cti"
SERIAL_NUMBER_ACE2 = "24595666"


# Create a Harvester instance and set the path of the GenTL producer library.
h = Harvester()
h.add_file(PRODUCER_PATH)
print(h.files)

# Update list of available cameras:
h.update()

# To get a list of available devices:
#print(h.device_info_list)
"""
Available device info:
['access_status', 'display_name', 'id_', 'model', 'parent',
'serial_number', 'tl_type', 'user_defined_name', 'vendor', 'version']

for the ace2 (on my desk):
{'access_status': 1, 'display_name': 'Basler acA1300-75gc(00:30:53:46:1f:d2)', 
'id_': 'acA1300-75gc(00:30:53:46:1f:d2)', 'model': 'acA1300-75gc', 
'parent': <genicam.gentl.Interface; proxy of <Swig Object of type 'std::shared_ptr< GenTLCpp::TLInterface > *' at 0xffff8e128a50> >, 
'serial_number': '24595666', 'tl_type': 'GEV', 'user_defined_name': 'gangway_ace2', 
'vendor': 'Basler', 'version': '106757-23'}
"""

# Create an image acquirer for device with specified serial number:
image_acq = h.create({'serial_number': SERIAL_NUMBER_ACE2})

# Set PixelFormat
print("Previous PixelFormat:")
print(image_acq.remote_device.node_map.PixelFormat.value)
#image_acq.remote_device.node_map.PixelFormat.value = 'Mono8'
image_acq.remote_device.node_map.PixelFormat.value = 'BayerBG8'
#image_acq.remote_device.node_map.PixelFormat.value = 'BayerBG10p'
#image_acq.remote_device.node_map.PixelFormat.value = 'YUV422_YUYV_Packed'
print("New PixelFormat:")
print(image_acq.remote_device.node_map.PixelFormat.value)

#Start camera-connection
image_acq.start()
#time.sleep(1)

try:
    img_2d = None
    while True:
        with image_acq.try_fetch(timeout=3) as buffer:
            if buffer:
                component = buffer.payload.components[0]
                data_format = component.data_format
                print(component)
                
                frame = component.data.reshape(component.height, component.width, int(component.num_components_per_pixel))
 
                if data_format == "Mono8":
                    img_2d = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                elif data_format == "BayerBG8" or data_format == "BayerBG10p" or data_format == "BayerBG10":
                    img_2d = cv2.cvtColor(frame, cv2.COLOR_BayerBG2RGB)
                elif data_format == "YUV422_8":
                    img_2d = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUYV)              

        if img_2d is not None:
            cv2.imshow('Converted Image', img_2d)
            if cv2.waitKey(1) == ord('q'):
                break
                 
except KeyboardInterrupt:
    print("Ctrl-C")

except Exception as e:
    print(e)
    
cv2.destroyAllWindows()

image_acq.stop()

h.reset()