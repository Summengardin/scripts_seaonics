import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GstRtspServer


def create_stream():
        pipeline = "videotestsrc ! x264enc ! rtph264pay pt=96 name=pay0"

        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(pipeline)
        factory.set_shared(True)

        return factory