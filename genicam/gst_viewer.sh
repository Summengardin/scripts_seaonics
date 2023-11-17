#!/bin/bash

#gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test latency=0 ! rtph264depay ! h264parse ! nvv4l2decoder enable-max-performance=0 ! nvvidconv ! autovideosink sync=0

gst-launch-1.0 rtspsrc location=rtsp://169.254.54.69:8554/test latency=0 protocols=udp-mcast+udp ! rtph265depay ! h265parse ! decodebin ! videoconvert ! autovideosink sync=0
