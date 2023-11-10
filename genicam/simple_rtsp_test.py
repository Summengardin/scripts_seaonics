#  Copyright (C) 2020 Matteo Benedetto <me at enne2.net>

# TO DISPLAY: gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test ! decodebin ! nvvidconv ! videoconvert ! autovideosink





import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GObject, GstRtspServer

Gst.init(None)

port = "8554"
mount_point = "/test"

server = GstRtspServer.RTSPServer.new()
server.set_service(port)
mounts = server.get_mount_points()
factory = GstRtspServer.RTSPMediaFactory.new()
factory.set_launch("videotestsrc is-live=true ! videoconvert ! theoraenc ! queue ! rtptheorapay name=pay0")
mounts.add_factory(mount_point, factory)
server.attach()

#  start serving
print ("stream ready at rtsp://127.0.0.1:" + port + mount_point);

loop = GLib.MainLoop()
loop.run()