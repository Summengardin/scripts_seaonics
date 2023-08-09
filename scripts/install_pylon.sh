#!/bin/bash

if [ $(dpkg-query -W -f='${Status}' pylon | grep -c 'ok installed') -eq 0 ]; then
    wget https://www.baslerweb.com/fp-1682511084/media/downloads/software/pylon_software/pylon_7.3.0.27189_linux-aarch64_debs.tar.gz
    tar -xzf pylon_7.3.0.27189_linux-aarch64_debs.tar.gz ./pylon_7.3.0.27189-deb0_arm64.deb
    rm pylon_7.3.0.27189_linux-aarch64_debs.tar.gz
    sudo dpkg -i pylon_7.3.0.27189-deb0_arm64.deb
    rm pylon_7.3.0.27189-deb0_arm64.deb
else
    echo Pylon is already installed
fi
