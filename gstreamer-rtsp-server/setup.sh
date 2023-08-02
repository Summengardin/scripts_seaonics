#!/bin/bash

echo Installing dependencies
sudo apt-get install -y \
libgstreamer1.0-dev \
libgstreamer-plugins-base1.0-dev \
libgstreamer-plugins-bad1.0-dev \
gstreamer1.0-plugins-base \
gstreamer1.0-plugins-good \
gstreamer1.0-plugins-bad \
gstreamer1.0-plugins-ugly \
gstreamer1.0-libav \
gstreamer1.0-tools \
gstreamer1.0-x \
gstreamer1.0-alsa \
gstreamer1.0-gl \
gstreamer1.0-gtk3 \
gstreamer1.0-qt5 \
gstreamer1.0-pulseaudio \
libcairo2-dev \
libxt-dev \
libgirepository1.0-dev \
gir1.2-gst-rtsp-server-1.0

echo Creating python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install pycairo PyGObject