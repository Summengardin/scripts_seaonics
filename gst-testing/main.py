import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

from threading import Thread
from time import sleep
Gst.init(None)

loop = GLib.MainLoop()
thread = Thread(target=loop.run)
thread.start()

pipeline = Gst.parse_launch("pylonsrc ! video/x-raw, framerate=60/1 ! autovideoconvert ! autovideosink")

pipeline.set_state(Gst.state.PLAYING)


try:    
    while True:
        sleep(0.1)
except KeyboardInterrupt:
    pass


pipeline.set_state(Gst.State.NULL)
loop.quit()
thread.join()