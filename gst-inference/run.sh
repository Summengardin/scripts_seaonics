#!/bin/bash

if ! [ -d "out" ]; then
    echo "You have to compile the model"
    exit 
fi
cd out


gst-launch-1.0 pylonsrc ! "video/x-raw,width=1920,height=1080,framerate=51/1,format=YUY2" ! nvvideoconvert ! m.sink_0 nvstreammux name=m batch-size=1 width=1920 height=1080 ! nvinfer config-file-path=./config_infer_primary_yoloV8.txt batch-size=1 unique-id=1 ! nvvideoconvert ! nvdsosd ! nvegltransform ! nveglglessink sync=0
# To addgst-shark tracing run the following line instead
# GST_DEBUG="GST_TRACER:7" GST_TRACERS="proctime;scheduletime;bitrate;buffer;queuelevel" gst-launch-1.0 pylonsrc ! "video/x-raw,width=1920,height=1080,framerate=51/1,format=YUY2" ! nvvideoconvert ! m.sink_0 nvstreammux name=m batch-size=1 width=1920 height=1080 ! nvinfer config-file-path=./config_infer_primary_yoloV8.txt batch-size=1 unique-id=1 ! nvvideoconvert ! nvdsosd ! nvegltransform ! nveglglessink sync=0