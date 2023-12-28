#!/bin/sh

DEFAULT_ADAPTER="eth0"

if [ "$#" -ne 1 ]; then
    echo "No adapter specified. Using default: $DEFAULT_ADAPTER"
    adapter=$DEFAULT_ADAPTER
else
    adapter=$1
fi

max_mtu=`ip -d link list | grep -A 1 $adapter | sed -n -e 's/^.*maxmtu //p' | awk '{print $1}'`
echo Maximum MTU for $adapter is $max_mtu, attempting to set it.
sudo ip link set $adapter down
sudo ip link set dev $adapter mtu $max_mtu
sudo ip link set $adapter up
new_mtu=`ip link list | grep -A 1 $adapter | sed -n -e 's/^.* mtu //p' | awk '{print $1}'`
echo New MTU on $adapter is set to $new_mtu

