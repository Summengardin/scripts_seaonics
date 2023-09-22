## Crash due to "The buffer was incompletely grabbed"
By default, the pipeline is setup to stop on capturing errors.
By adding ```capture-error=skip``` after ```pylonsrc``` will allow skipping such errors.

e.g:
```console
$ gst-launch-1.0 pylonsrc capture-error=skip ! ...
``` 

## Laggy stream
The message log shows that lots of frames were still missed because of "The buffer was incompletely grabbed". This caused the video stream to appear laggy. Increasing the **packet-size** (default is 1500) fixed this. Increasing this is done in Pylon Viewer under **Transport Layer Control** -> **Packet Size**.

Setting the the packet size using PIPELINE-DESCRIPTION is done with ```cam::GevSCPSPacketSize```

e.g:
```console
$ gst-launch-1.0 pylonsrc cam::GevSCPSPacketSize=8000 ! ...
``` 
<br>

> **Note:** Maximum Transfer Unit (MTU) of network adapters are often default at 1500 as well. Therefore, check the MTU of the network adapter to make sure it can allow for higher packet size.
```console 
$ ifconfig # To check the current MTU values
$ sudo ifconfig eth0 mtu 8192 # To set MTU of eth0 to 8192 
```

More info at [imaginghub](imaginghub.com/forum/posts/696-losing-frames-pylon-for-linux-on-pc)