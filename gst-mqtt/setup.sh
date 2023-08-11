#!/bin/bash

bash ../scripts/install_gstreamer.sh

sudo add-apt-repository ppa:nnstreamer/ppa
sudo apt install -y nnstreamer-edge nnstreamer-misc