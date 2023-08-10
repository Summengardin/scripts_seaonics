import argparse
from mqttClientFactory import create_client
from streamManager import StreamManager
from typing import Tuple
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
from rtspStreamFactory import create_stream

loop = GLib.MainLoop()
Gst.init(None)

def parse_args() -> Tuple[str]:
    parser = argparse.ArgumentParser()
    parser.add_argument('mqtt_url')
    args = parser.parse_args()
    return args.mqtt_url

if __name__ == "__main__":
    mqtt_host = parse_args()
    mqtt = create_client(mqtt_host)
    streamManager = StreamManager()
    stream = streamManager.create_stream("baide")
    print(stream)
    loop.run()
