# Getting Started
To create a stream from your camera straight to the monitor the (gstreamer-basler-consumer)[../gstreamer-cam-to-glass] subfolder includes everything needed
to stream from a Basler IP camera, v4l2 device and test source, including all software.

Before streaming can start you must however configure the network settings for your Orin and the camera such that the devices are on the same network.
This can be done using the Pylon IP configurator which is installed in the setup script. You can also use the Pylon viewer, also installed under setup, to test if the camera is configured correctly.

Currently the only model tested and confirmed working is the Basler Ace2 a2A1920-51gcPRO


# Configuration
No configuration is needed, however, when running the v4l2 script you can override the default /dev/video0 device by giving a new device name as the 1st parameter