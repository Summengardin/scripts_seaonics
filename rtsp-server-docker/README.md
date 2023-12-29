
# First time setup

## Make sure to be in the correct folder
Make sure the terminal is inside the rtsp-server-docker folder


## 1. Modify setup
During setup, the network interfaces are setup with correct IP-addresses for the different interfaces. Therefore, we check this before running setup.
The network setup can be run later on as well.
- 1. Check mac address of the interfaces using:
 ```shell
sudo lshw -class network | awk '/vendor:/{vendor=$2 " " $3} /serial:/{serial=$2} vendor && serial {print "Vendor: " vendor " | MAC: " serial; vendor=""; serial=""}'
```
- 2. Edit the IP and MAC-address of './extras/configure_network.sh' according to documentation
 - Realtek (PoE) interface - for camera connection:
  - 169.254.54.20/24 (255.255.255.0)
 - Microchip interface - for switch connection:
  - Windmill: 10.1.2.81/24 (255.255.255.0)
  - Ship: 10.1.2.82/24 (255.255.255.0)
```shell
gedit ./extras/configure_network.sh
```
- 3. Save file


## 2. Run setup.sh
This will install nvidia-container-toolkit to make sure the docker container will be able to use the nvidia hardware


## 3. Load the docker image
Get the rtspserver.tar file and load it into docker
```shell
docker load -i rtspserver.tar
```

(OPTIONAL) Another option is building the image from scratch using:
```shell
docker build -t rtspserver .
```


## 4. Make the server run on startup
Make the start-script launchable using:
```shell
sudo chmod +x start_server.sh
```

Then, search for ''Startup Applications Preferences''
- Name and Comment can be anything
- set command to be ''/absolute/path/to/start_server.sh''
eg.
```shell
/home/Desktop/dev/rtsp-server-docker/start_server.sh
```

## 5. To modify the network
To modify the network later on, either:
- set the correct ip and mac inside extras/configure_network.sh and run
```shell
gedit extras/configure_network.sh
```
```shell
bash extras/configure_network.sh
```


- or use the NetworkManager
```shell
nm-connection-editor
```  




