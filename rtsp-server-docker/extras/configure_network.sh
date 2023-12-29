#!/bin/bash

# Ethernet interface of camera connection (PoE port) - Realtek Semiconductor
eth_camera_mac="48:b0:2d:d8:cd:0a"
eth_camera_ip="169.254.54.20/24"

# Ethernet interface of client connection - Microchip Technology
eth_server_mac="2c:f7:f1:20:e9:fd"
eth_server_ip="10.1.2.82/24"


# Setup connections
if nmcli con show "eth-server" &> /dev/null; then
	nmcli connection delete "eth-server"
fi
nmcli connection add type ethernet con-name "eth-server" ifname "*" mac $eth_server_mac ip4 $eth_server_ip

if nmcli con show "eth-camera" &> /dev/null; then
	nmcli connection delete "eth-camera"
fi 
nmcli connection add type ethernet con-name "eth-camera" ifname "*" mac $eth_camera_mac ip4 $eth_camera_ip


# Delete the default connections
if nmcli con show "Wired connection 1" &> /dev/null; then
	nmcli connection delete "Wired connection 1"
fi 
if nmcli con show "Wired connection 2" &> /dev/null; then
	nmcli connection delete "Wired connection 2"
fi 


# Restart networking
nmcli networking off
nmcli networking on

echo "Networking was restarted"
