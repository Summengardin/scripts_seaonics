#  Copyright (C) 2020 Matteo Benedetto <me at enne2.net>
import time

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GObject, GstRtspServer

Gst.init(None)

port = "8554"
mount_point = "/test"

pipeline_str = "appsrc name=source is-live=true format=GST_FORMAT_TIME caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0"
pipeline_str = "appsrc name=source ! videoconvert ! x264enc ! rtph264pay name=pay0 pt=96"
pipeline = Gst.parse_launch(pipeline_str)

server = GstRtspServer.RTSPServer.new()
server.set_service(port)
mounts = server.get_mount_points()
factory = GstRtspServer.RTSPMediaFactory.new()
#factory.set_launch("videotestsrc is-live=true caps=video/x-raw(memory:NVMM) ! nvvidconv ! nvv4l2h264enc ! rtph264pay pt=96 name=pay0")
factory.set_launch(pipeline_str)
mounts.add_factory(mount_point, factory)
server.attach()

def feed_data(appsrc):
    # Get your frame data here. This is just an example using numpy and OpenCV
    # frame = get_your_frame_data_as_numpy_array()
    # data = frame.tobytes()

    # For now, let's create a dummy frame using numpy
    import numpy as np
    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    data = frame.tobytes()

    buf = Gst.Buffer.new_allocate(None, len(data), None)
    buf.fill(0, data)
    appsrc.emit('push-buffer', buf)
    
    time.sleep(0.033)
    # Return True to continue calling the feed_data function
    return True



#  start serving
print ("stream ready at rtsp://127.0.0.1:" + port + mount_point);


# Retrieve the appsrc element
appsrc = pipeline.get_by_name("source")


# Push frames every 33ms (assuming 30FPS)
GLib.timeout_add(33, feed_data, appsrc)


loop = GLib.MainLoop()
loop.run()



