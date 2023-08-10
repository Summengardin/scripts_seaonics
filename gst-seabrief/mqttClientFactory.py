import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def on_connect_fail():
    print("Connection failed")

def create_client(mqtt_host: str):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_connect_fail = on_connect_fail

    client.connect(mqtt_host)
    return client
