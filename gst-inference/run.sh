#!/bin/bash

gst-launch-1.0 pylonsrc ! "video/x-raw,width=1280,height=720,framerate=51/1,format=YUY2" ! nvvideoconvert ! m.sink_0 nvstreammux name=m batch-size=1 width=1280 height=720 ! nvinfer config-file-path=/media/seaonics/D/scripts_seaonics/gst-inference/config_infer_primary_yoloV8.txt batch-size=1 unique-id=1 ! nvvideoconvert ! nvdsosd ! nvegltransform ! nveglglessink sync=0