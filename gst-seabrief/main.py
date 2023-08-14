import argparse
from mqttClientFactory import create_client
from streamManager import StreamManager
from typing import Tuple
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
from ip_finder import find_ip
import os

loop = GLib.MainLoop()
Gst.init(None)

def parse_args() -> Tuple[str]:
    parser = argparse.ArgumentParser()
    parser.add_argument('mqtt_url', help='The hostname of the MQTT broker')
    parser.add_argument('system_id', help='The IMO of the vessel the device is attached to')
    parser.add_argument('--ip', help='The IP address of the device')
    parser.add_argument('--port', help='The port to launch the RTSP service on')
    args = parser.parse_args()
    return args.mqtt_url, args.system_id, args.ip, args.port

if __name__ == "__main__":
    mqtt_host, system_id, ip, port = parse_args()
    if ip is None:
        ip = find_ip()
    if port is None:
        port = 5050
    os.environ.ip = ip
    os.environ.port = port

    streamManager = StreamManager()
    
    mqtt = create_client(mqtt_host, system_id, streamManager)


    loop.run()
