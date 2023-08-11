import paho.mqtt.client as mqtt
from streamManager import StreamManager
import json
from paho.mqtt.client import MQTTMessage
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties
from typing import Callable

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def on_connect_fail():
    print("Connection failed")

def create_client(mqtt_host: str, system_id: str, sm: StreamManager):
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    client.on_connect_fail = on_connect_fail
    client.connect(mqtt_host)
    client.subscribe(f"{system_id}/seastream/command/request")
    client.on_message = create_consumer(system_id, sm)
    client.loop_start()
    return client

def create_consumer(system_id: str, sm: StreamManager) -> Callable[[mqtt.Client, any, MQTTMessage], None]:
    def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
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
            stream_id = sm.create_stream(parsed.get("input"))
            payload = json.dumps({'stream_id': str(stream_id)})
        elif request_type == 'list_devices':
            payload = json.dumps({'devices': sm.list_devices()})
        else:
            return

        client.publish(f"{system_id}/seastream/command/response", payload, properties=p)

    return on_message