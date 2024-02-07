

## Terminology

Terminology in terms of the RTSP stream:
**Client**: The viewer
**Server**: The sender (camera)


## Getting started

Complete installation guide for Harvesters can be found on their [GitHub](https://github.com/genicam/harvesters#getting-started-with-harvester). 
In short you need a GenTL producer.


That GenTL producer can be downloaded and installed from this [link](http://static.matrix-vision.com/mvIMPACT_Acquire/). 
Scroll down to find the latest version, and then download the correct version for your system.


## Required Packages
Activate the venv using 
```shell
# Activate virtualenv
$ source venv/bin/activate
```
(If you haven't created a virtual environment do so:)

```shell
# Install pyvenv and create virtaulenv called <venv>
$ pip3 install pyvenv
$ python3 -m venv venv
```

Install the required packages using :
```shell
# Install packages from requirements.txt
$ pip3 install -r requirements.txt
```


## Automagical restarting
As a hacky solution for automatic restart, two extra python scripts are made: One for the server [monitor_server.py](monitor_server.py) and one for the client [monitor_client.py](monitor_server.py)


