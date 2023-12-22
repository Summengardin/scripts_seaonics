

## Terminology

Terminology in terms of the RTSP stream:
**Client**: The viewer
**Server**: The sender (camera)


## Getting started

Install Harvesters following [this](https://github.com/genicam/harvesters#getting-started-with-harvester) link.

For the GenTL producer follow the link in the Harvesters guide. Or click [here](http://static.matrix-vision.com/mvIMPACT_Acquire/). 
Then scroll down to find the latest version, and the download the correct version for your system.


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
As a hacky solution for automatic restart, two  extra python scripts are made: One for the server [monitor_server.py](monitor_server.py) and one for the client [monitor_client.py](monitor_server.py)