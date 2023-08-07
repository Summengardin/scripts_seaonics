#!/bin/bash

sudo apt remove -y meson ninja-build

wget https://www.baslerweb.com/fp-1615275631/media/downloads/software/pylon_software/pylon_6.2.0.21487-deb0_arm64.deb
sudo dpkg -i pylon_6.2.0.21487-deb0_arm64.deb
rm pylon_6.2.0.21487-deb0_arm64.deb

wget http://ports.ubuntu.com/pool/universe/m/meson/meson_0.61.2-1_all.deb
sudo dpkg -i meson_0.61.2-1_all.deb
rm meson_0.61.2-1_all.deb

sudo apt install -y cmake gstreamer1.0-python3-plugin-loader ninja-build

export PYLON_ROOT=/opt/pylon

git clone https://github.com/basler/gst-plugin-pylon.git
cd gst-plugin-pylon
meson setup builddir --prefix /usr/

ninja -C builddir
sudo ninja -C builddir install

cd ../
rm -rf gst-plugin-pylon