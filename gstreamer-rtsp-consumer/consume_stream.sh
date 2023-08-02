#!/bin/bash

gst-launch-1.0 -v rtspsrc location=rtsp://$1 ! application/x-rtp, payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false
#gst-launch-1.0 -v rtspsrc location=rtsp://localhost:5050/test latency=0 ! queue ! rtph264depay ! h264parse ! nvv4l2decoder ! nvvideoconvert ! video/x-raw, format=RGB ! autovideosink
