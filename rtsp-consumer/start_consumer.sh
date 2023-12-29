#!/bin/bash

cd /home/seaonics/Desktop/scripts_seaonics/rtsp-consumer
source ./venv/bin/activate
gnome-terminal -- python3 rtsp_multiview.py
