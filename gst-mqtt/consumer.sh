#!/bin/bash

gst-launch-1.0 mqttsrc host=$1 sub-topic=sys1/seastream/streams/123 ! video/x-raw,format=RGB,width=640,height=480,framerate=5/1 ! videoconvert ! ximagesink sync=false