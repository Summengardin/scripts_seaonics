#!/bin/bash

GST_DEBUG=5 gst-launch-1.0 pylonsrc ! video/x-raw, framerate=60/1 ! autovideoconvert ! autovideosink