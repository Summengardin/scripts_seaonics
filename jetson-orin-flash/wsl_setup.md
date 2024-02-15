# Step 1: Install wsl
Follow this [guide](https://www.cyberithub.com/how-to-install-ubuntu-20-04-lts-on-windows-10-wsl/) to enable and install WSL with Ubuntu 20.04

# Step 2: Install sdkmanager dependencies and GUI packages

> sudo apt update && sudo apt full-upgrade
> 
> sudo apt install libxshmfence1 libglu1 libnss3-dev libgdk-pixbuf2.0-dev libgtk-3-dev libxss-dev

# Step 3; install sdkmanager
Download the sdkmanager debian package from [Nvidia](https://developer.nvidia.com/sdk-manager) on Windows-browser
Install the downloaded debian package in wsl
> sudo apt install /mnt/c/Users/{username}/Downloads/sdkmanager_{version}-{build}_amd64.deb

# Step 4: Install usbipd
In windows install usbipd with the following command
> winget install usbipd

Afterwards go back to wsl and run
> sudo apt install linux-tools-generic hwdata
> 
> sudo update-alternatives --install /usr/local/bin/usbip usbip `ls /usr/lib/linux-tools/*/usbip | tail -n1` 20


# Step 5; attach the device to wsl
This [link](https://learn.microsoft.com/en-us/windows/wsl/connect-usb#attach-a-usb-device) explains everything.

In a Windows terminal, do
> usbipd list
The device should come up as either
* APX
* Remote NDIS Compatible Device, USB Serial Device ...

Note the BUSID of the device.

Once you have found the bus-id the device is connected to, run these commands in a Windows Terminal with admin privileges.
> usbipd bind --busid {BUSID}
>
> usbipd attach --wsl --busid {BUSID}

usbipd should then after a couple seconds log "attached"

If usbipd does not work for whatever reason, try uninstalling and then re-installing it. In my case "Device is in Error State" was an error in usbipd which was fixed with a re-install.

# Step 6: Run sdkmanager
Run sdkmanager on wsl using the sdkmanager command and complete the setup of your Orin

To login you must use the QR-method

NOTE: After flashing the device (If you skip that step or not) use the eth connection method.
Go on your Orin and find its IPv4 address, and write it into the sdkmanager address input, but delete the pre-existing address instead of replacing the last couple sequences.
For some reason, replacing the 55.0 in 192.168.55.0 did not work for me, but backspacing the whole string and writing the ip from scratch worked.

# Step 7: Add nvcc to path
If the 
> nvcc --version
command doesn't work on the Orin, append the following to the Orins ~/.bashrc file
> export PATH="/usr/local/cuda-{version}/bin:$PATH"
> export LD_LIBRARY_PATH="/usr/local/cuda-{version}/lib64:$LD_LIBRARY_PATH"

# Step 8: gst environment configs
Append
> export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1  
to ~/.bashrc, then run 
> source ~/.bashrc
or reboot

# Step 9: Power mode
In the upper right hand corner of the Orin UI change the power-mode to 50W and reboot

# Troubleshooting
## Terminal won't open
If the terminal won't open after flashing and installing jetpack on the orin go into language settings and change the language.
For some reason the locale settings seem to be corrupted during flashing

If that doesn't work, ssh into the Orin and update the /usr/bin/gnome-terminal file to point to the correct python version
If `python3 --version` says ex. 3.9.1 change the hashbang to python3.9 on the first line

## avdec_h264 element not found
Ensure that you have done step 7
Then try running [the purge cache script](../scripts/purge_cache.sh)
