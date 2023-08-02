#!/bin/bash

wget https://www.baslerweb.com/fp-1615275631/media/downloads/software/pylon_software/pylon_6.2.0.21487-deb0_arm64.deb
sudo dpkg -i pylon_6.2.0.21487-deb0_arm64.deb
rm pylon_6.2.0.21487-deb0_arm64.deb

sudo apt remove meson ninja-build
sudo -H python3 -m pip install meson ninja --upgrade
sudo apt install -y cmake gstreamer1.0-python3-plugin-loader

export PYLON_ROOT=/opt/pylon

git clone https://github.com/basler/gst-plugin-pylon.git
cd gst-plugin-pylon
meson setup builddir --prefix /usr/

ninja -C builddir
sudo ninja -C builddir install

cd ../
rm -rf gst-plugin-pylon