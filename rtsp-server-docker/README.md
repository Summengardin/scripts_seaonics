
# First time setup
## 1. Run setup.sh
This will install nvidia-container-toolkit to make sure the docker container will be able to use the nvidia hardware


## 2. Load the docker image
Get the rtspserver.tar file and load it into docker
```shell
docker load -i rtspserver.tar
```

(OPTIONAL) Another option is building the image from scratch using:
```shell
docker build -t rtspserver .
```


## 3. Make the server run on startup
- Search for ''Startup Applications Preferences''
- Name and Comment can be anything
- set command to be ''bash absolute/path/to/start_server.sh''
eg.
```shell
bash /home/seaonics/dev/rtsp-server-docker/start_server.sh
```


## 4. Set IP settings of the unit according to documentation
Realtek (PoE) interface - for camera connection:
- 169.254.54.20 / 255.255.255.0

Microchip interface - for switch connection:
- Windmill: 10.1.2.81 / 255.255.255.0
- Ship: 10.1.2.82 / 255.255.255.0

