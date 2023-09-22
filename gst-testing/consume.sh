#!/bin/bash

GST_DEBUG=2  gst-launch-1.0 pylonsrc cam::GevSCPSPacketSize=8000 capture-error=skip ! video/x-raw, framerate=60/1 ! autovideoconvert  ! autovideosink