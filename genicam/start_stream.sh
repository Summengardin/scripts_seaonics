#!/bin/bash

cd /home/seaonics/Desktop/scripts_seaonics/genicam
source ./venv/bin/activate
gnome-terminal -- python3 monitor_server.py
