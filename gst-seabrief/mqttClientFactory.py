from streamManager import StreamManager
import json
from paho.mqtt.client import MQTTMessage, Client, MQTTv5
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties
from typing import Callable
import os

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def on_connect_fail():
    print("Connection failed")

def create_client(mqtt_host: str, system_id: str, sm: StreamManager):
    client = Client(protocol=MQTTv5)
    client.on_connect_fail = on_connect_fail
    client.connect(mqtt_host)
    client.subscribe(f"{system_id}/seastream/command/request")
    client.on_message = create_consumer(system_id, sm)
    client.loop_start()
    return client

def create_consumer(system_id: str, sm: StreamManager) -> Callable[[Client, any, MQTTMessage], None]:
    def on_message(client: Client, userdata, msg: MQTTMessage):
        # Ignore messages without correlation data
        p =  Properties(PacketTypes.PUBLISH)
        try:
            p.CorrelationData = msg.properties.CorrelationData
        except:
            return

        parsed = json.loads(msg.payload)

        # Ignore messages without a specified request type
        try:
            request_type = parsed['request_type']
        except:
            return
        
        print(msg.topic+" "+str(parsed))
        if request_type == 'start_stream':
            try:
                source = parsed.get("source")
                device = parsed.get("device")
                stream_id = sm.create_stream(source, device)
                payload = json.dumps({'stream_id': str(stream_id), 'url': f'rtsp://{os.environ.ip}:{os.environ.port}/{stream_id}'})
            except Exception as e:
                payload = json.dumps({'error': str(e)})
        elif request_type == 'list_devices':
            payload = json.dumps({'basler_devices': sm.list_basler_devices(), 'v4l_devices': sm.list_v4l_devices()})
        elif request_type == 'ping':
            stream_id = parsed.get("stream_id")
            success = sm.ping_stream(stream_id) if stream_id is not None else False
            payload = "pong" if success else "Stream has ended"
        else:
            return

        client.publish(f"{system_id}/seastream/command/response", payload, properties=p)

    return on_message