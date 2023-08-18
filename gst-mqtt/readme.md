# Gst-MQTT
This is just for testing streaming over MQTT

The results were quite terrible, but in case someone wants to test / explore gstreamer over MQTT..

NOTE: Please keep in mind most MQTT GUI clients are not meant to receive raw binary video streams, thus running this pipeline on a populated 
MQTT broker will probably cause other devs' to experience crashes. 

# Usage
> bash consumer.sh <MQTT_SERVER_HOST>
> bash producer.sh <MQTT_SERVER_HOST>

Where MQTT_SERVER_HOST might be something like "dev.seaonics.com"

## Results
600x480p 5fps ~15s latency