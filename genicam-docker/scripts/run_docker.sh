#!/bin/bash

docker run -it --network host -p 8554:8554  first-cam-docker

# Interactive mode, remove container when done
#docker run -itd -rm --network "host" -p 8554:8554  first-cam-docker