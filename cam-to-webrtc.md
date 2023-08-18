# Getting started
To stream a camera to WebRTC you need to use both the (gstreamer-rtsp-server)[./gstreamer-rtsp-server] and (rtsp-to-web)[./rtsp-to-web] folders

The reason for this is that RTSPtoWeb is used to turn an RTSP stream from Gstreamer into a WebRTC stream since no WebRTC plugins are compatible with deepstream

It is, however, possible to use webrtcbin by upgrading to Gstreamer 1.18, but doing so will break all Nvidia plugins.
Using webrtcbin without Nvidia HW acceleration is likely faster than RTSPtoWeb with HW acceleration, but I have not had the time to test it

## Starting the RTSP server
Follow the guide in (cam-to-rtsp.md)[cam-to-rtsp.md]

## Starting the RTSPtoWeb server
Follow the guide in (rtsp-to-web)[./rtsp-to-web]