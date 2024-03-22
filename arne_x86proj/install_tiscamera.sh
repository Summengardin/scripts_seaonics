#!/bin/bash
sudo apt install -y git cmake

git clone https://github.com/TheImagingSource/tiscamera.git
cd tiscamera

# Install dependencies
./scripts/dependency-manager install

# Build
mkdir build
cd build
cmake ..

# Compile
make -j

# Install
source ./env.sh
sudo make install