#!/bin/bash

#bash /home/seaonics/Desktop/scripts_seaonics/genicam/scripts/setmaxMTU.sh eth0 #POE port
#bash /home/seaonics/Desktop/scripts_seaonics/genicam/scripts/setmaxMTU.sh docker0
#nmcli connection up eth-server
gnome-terminal -- docker run -it --rm --net=host --runtime nvidia --gpus all \
                    -v /tmp/argus_socket:/tmp/argus_socket \
                    -v /home/seaonics/Desktop/scripts_seaonics/rtsp-server-docker/config.yaml:/app/config.yaml \
                    -v /home/seaonics/Desktop/scripts_seaonics/rtsp-server-docker/log:/app/log\
                    rtspserver
