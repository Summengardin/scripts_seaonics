#!/bin/bash

cd /home/seaonics/Desktop/scripts_seaonics/genicam/scripts
bash setmaxMTU.sh eth0 #POE port
bash setmaxMTU.sh docker0


cd /home/seaonics/Desktop/scripts_seaonics/genicam
source ./venv/bin/activate
gnome-terminal -- python3 monitor_server.py
