
# First time setup
## 1. Run setup.sh
This will install nvidia-container-toolkit to make sure the docker container will be able to use the nvidia hardware


## 2. Load the docker image
Get the rtspserver.tar file and load it into docker
```shell
docker load -i rtspserver.tar
```

(OPTIONAL) Another option is building the image from scratch using:
NB! Be sure to be in the folder of the Dockerbuild-file
```shell
cd /home/seaonics/Desktop/scripts_seaonics/rtsp-server-docker
```
```shell
docker build -t rtspserver .
```


## 3. Make the server run on startup
Make the start-script launchable using:
```shell
sudo chmod +x /home/seaonics/Desktop/scripts_seaonics/rtsp-server-docker/start_server.sh
```

Then, search for ''Startup Applications Preferences''
- Name and Comment can be anything
- set command to be ''bash absolute/path/to/start_server.sh''
eg.
```shell
bash /home/seaonics/Desktop/scripts_seaonics/rtsp-server-docker/start_server.sh
```

## 4. Modify the network interface rule
Some times the ethernet interfaces swap order and clutters the IP configuration. Therefore a udev-rule is made to make sure the order of the network interfaces stay consistent.
- 1. Check mac address of the interfaces using:
 ```shell
sudo lshw -class network | awk '/vendor:/{vendor=$2 " " $3} /serial:/{serial=$2} vendor && serial {print "Vendor: " vendor " | MAC: " serial; vendor=""; serial=""}'
```
- 2. Copy the .rules-file into the rules.d-folder using:
 ```shell
sudo cp /home/seaonics/Desktop/scripts_seaonics/rtsp-server-docker/extras/60-persistent-mac.rules /etc/udev/rules.d/60-persistent-mac.rules
```
- 3. Open the .rules-file and update the MAC-addresses accordingly
    - 'eth0' has mac address of Microchip Technology
    - 'eth1' has mac address of Realtek Semiconductor
 ```shell
sudo gedit /etc/udev/rules.d/60-persistent-mac.rules
```  
- 4. Save the file
- 5. Reload the rules using: 
 ```shell
sudo udevadm control --reload-rules
sudo udevadm trigger --type=devices --action=add
``` 

## 5. Set IP settings of the unit according to documentation
Realtek (PoE) interface - for camera connection:
- 169.254.54.20 / 255.255.255.0

Microchip interface - for switch connection:
- Windmill: 10.1.2.81 / 255.255.255.0
- Ship: 10.1.2.82 / 255.255.255.0


