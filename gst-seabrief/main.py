import argparse
from mqttClientFactory import create_client
from streamManager import StreamManager
from typing import Tuple
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

loop = GLib.MainLoop()
Gst.init(None)

def parse_args() -> Tuple[str]:
    parser = argparse.ArgumentParser()
    parser.add_argument('mqtt_url')
    parser.add_argument('system_id')
    args = parser.parse_args()
    return args.mqtt_url, args.system_id

if __name__ == "__main__":
    streamManager = StreamManager()
    
    mqtt_host, system_id = parse_args()
    mqtt = create_client(mqtt_host, system_id, streamManager)


    loop.run()
