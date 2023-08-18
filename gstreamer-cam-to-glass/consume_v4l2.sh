#!/bin/bash

DEVICE=${1:-"/dev/video0"}

gst-launch-1.0 v4l2src device=$DEVICE ! nvv4l2decoder mjpeg=1 enable-max-performance=true disable-dpb=true ! nvvidconv ! autovideosink sync=false