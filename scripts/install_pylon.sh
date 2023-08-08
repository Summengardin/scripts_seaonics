#!/bin/bash

if [ $(dpkg-query -W -f='${Status}' pylon | grep -c 'ok installed') -eq 0 ]; then
    wget https://www.baslerweb.com/fp-1615275631/media/downloads/software/pylon_software/pylon_6.2.0.21487-deb0_arm64.deb
    sudo dpkg -i pylon_6.2.0.21487-deb0_arm64.deb
    rm pylon_6.2.0.21487-deb0_arm64.deb
else
    echo Pylon is already installed
fi
