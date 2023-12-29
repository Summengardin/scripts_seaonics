#!/bin/bash

cd /home/seaonics/Desktop/scripts_seaonics/rtsp-consumer
source ./venv/bin/activate
gnome-terminal python3 monitor_client.py
