#!/bin/bash

# Install pylon SDK
echo Installing Pylon SDK
if [ $(dpkg-query -W -f='${Status}' pylon | grep -c 'ok installed') -eq 0 ]; then
    #wget https://www2.baslerweb.com/media/downloads/software/pylon_software/pylon-7.4.0.14900_linux-x86_64_setup.tar.gz && \
    mkdir ./pylon_setup && \
    tar -C ./pylon_setup -xzf ./pylon-*_setup.tar.gz
    cd ./pylon_setup && \
    sudo mkdir -p /opt/pylon && \
    sudo tar -C /opt/pylon -xzf ./pylon-*.tar.gz
    sudo chmod 755 /opt/pylon

    if [ $(dpkg-query -W -f='${Status}' pylon | grep -c 'ok installed') -eq 0 ]; then
        echo Pylon installed
    else
        echo Failed to install Pylon
    fi
else
    echo Pylon is already installed
fi