#!/bin/bash

#gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test latency=0 ! rtph264depay ! h264parse ! nvv4l2decoder enable-max-performance=0 ! nvvidconv ! autovideosink sync=0


# Working H264 launch_str_4
#gst-launch-1.0 rtspsrc location=rtsp://169.254.54.69:8554/test latency=0 ! rtph264depay ! h264parse ! decodebin ! videoconvert ! autovideosink sync=0


# H265
gst-launch-1.0 rtspsrc location=rtsp://169.254.54.69:8554/test latency=0 ! rtph265depay ! h265parse ! decodebin ! videoconvert ! autovideosink sync=0