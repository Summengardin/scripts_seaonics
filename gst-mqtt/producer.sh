#!/bin/bash

gst-launch-1.0 v4l2src device=/dev/video0 ! videoconvert ! video/x-raw,format=RGB,width=640,height=480,framerate=5/1 ! mqttsink host=$1 pub-topic=sys1/seastream/streams/123

