#!/bin/bash

bash ./install_pylon.sh
bash ./install_meson.sh

apt-get install cmake gstreamer1.0-python3-plugin-loader ninja-build -y

export PYLON_ROOT=/opt/pylon

git clone https://github.com/basler/gst-plugin-pylon.git
cd gst-plugin-pylon
meson setup builddir --prefix /usr/

ninja -C builddir
ninja -C builddir install

cd ../
rm -rf gst-plugin-pylon
