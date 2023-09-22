import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GLib, Gtk

Gst.init(None)

class CameraViewer:
    def __init__(self):
        self.pipeline = Gst.Pipeline()

        # Create elements
        self.pylonsrc = Gst.ElementFactory.make("pylonsrc")
        self.videoconvert = Gst.ElementFactory.make("videoconvert")
        self.autovideosink = Gst.ElementFactory.make("autovideosink")

        if not self.pipeline or not self.pylonsrc or not self.videoconvert or not self.autovideosink:
            print("Not all elements could be created.")
            exit(-1)

        # Set camera properties (replace with your camera's values)
        #self.pylonsrc.set_property("camera-ip", "192.168.0.1")
        #self.pylonsrc.set_property("camera-idx", 0)

        # Add elements to the pipeline
        self.pipeline.add(self.pylonsrc)
        self.pipeline.add(self.videoconvert)
        self.pipeline.add(self.autovideosink)

        # Link elements
        if not self.pylonsrc.link(self.videoconvert):
            print("Elements could not be linked.")
            exit(-1)

        if not self.videoconvert.link(self.autovideosink):
            print("Elements could not be linked.")
            exit(-1)

    def run(self):
        # Set up a main loop
        loop = GLib.MainLoop()
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        # Start the pipeline
        self.pipeline.set_state(Gst.State.PLAYING)

        try:
            loop.run()
        except KeyboardInterrupt:
            pass

        # Stop the pipeline
        self.pipeline.set_state(Gst.State.NULL)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR:
            err, debug_info = message.parse_error()
            print("Error: %s" % err, debug_info)
            Gtk.main_quit()
        elif t == Gst.MessageType.EOS:
            print("End-Of-Stream reached")
            Gtk.main_quit()
        elif t == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print(f"Pipeline state changed from {old_state.value_nick.upper()} to {new_state.value_nick.upper()}")

if __name__ == '__main__':
    viewer = CameraViewer()
    viewer.run()
