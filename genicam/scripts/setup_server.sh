#!/bin/bash

# NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configue docker with nvidia-ctk
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
 
# Check if the Docker service is active
if systemctl is-active --quiet docker; then
    echo "Docker OK"
else
    sudo systemctl restart docker
    if !(systemctl is-active --quiet docker;) then
        echo "Failed. Could not start docker"
        exit 1
    else
        echo "Docker OK"
    fi   
fi
