#!/bin/bash

# Install meson
sudo apt remove -y meson ninja-build
sudo apt install -y python3-pip git cmake
sudo -H python3 -m pip install meson ninja --upgrade

export PYLON_ROOT=/opt/pylon


# Install pylonsrc
git clone https://github.com/basler/gst-plugin-pylon.git
cd gst-plugin-pylon
meson setup builddir --prefix /usr/

# Build
ninja -C builddir

# Test
ninja -C builddir test

# Install
sudo ninja -C builddir install


# Add /opt/pylon/lib to LD_LIBRARY_PATH
echo ""; echo ""; echo  "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/pylon/lib" >>  ~/.bashrc