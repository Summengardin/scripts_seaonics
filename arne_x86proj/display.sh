#!/bin/bash

opt_default="camera"
dbg_default="0"

opt="${1:-$opt_default}"

dbg="${2:-$dbg_default}"

# Simplest test-stream
if [ "$opt" == "test" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 videotestsrc ! autovideosink
elif [ "$opt" == "camera" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc capture-error=keep stream::MaxNumBuffer=1 ! "video/x-raw,width=1920,height=1080,framerate=60/1,format=YUY2" ! videoconvert ! autovideosink sync=false
elif [ "$opt" == "camera-simple" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! videoconvert ! autovideosink
elif [ "$opt" == "camera-rgb" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! "video/x-raw,width=1920,height=1080,framerate=60/1,format=RGB" ! videoconvert ! autovideosink
elif [ "$opt" == "camera-yuv422" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc capture-error=keep stream::MaxNumBuffer=10 ! "video/x-raw,width=1920,height=1080,framerate=60/1,format=YUY2" ! videoconvert ! autovideosink sync=false
elif [ "$opt" == "camera-bayer" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! "video/x-bayer,framerate=60/1,format=rggb" ! bayer2rgb ! videoconvert ! autovideosink
elif [ "$opt" == "camera-tcam" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc capture-error=keep ! "video/x-bayer,framerate=60/1,format=rggb" ! tcamconvert ! video/x-raw,format=BGRx ! videoconvert ! autovideosink
elif [ "$opt" == "camera-ttest" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 videotestsrc ! "video/x-bayer,framerate=60/1,format=rggb" ! tcamconvert ! video/x-raw,format=BGRx ! videoconvert ! autovideosink
elif [ "$opt" == "camera-rgb" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! videoconvert ! video/x-raw,format=RGB ! autovideosink
elif [ "$opt" == "camera-rgb" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! videoconvert ! video/x-raw,format=RGB ! autovideosink
elif [ "$opt" == "camera-rgb" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! videoconvert ! video/x-raw,format=RGB ! autovideosink
elif [ "$opt" == "camera-rgb" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! videoconvert ! video/x-raw,format=RGB ! autovideosink
elif [ "$opt" == "camera-rgb" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! videoconvert ! video/x-raw,format=RGB ! autovideosink
elif [ "$opt" == "camera-rgb" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! videoconvert ! video/x-raw,format=RGB ! autovideosink
elif [ "$opt" == "camera-rgb" ]; then
    GST_DEBUG=$dbg gst-launch-1.0 pylonsrc ! videoconvert ! video/x-raw,format=RGB ! autovideosink
else
    echo "Unknown option: $opt"
fi