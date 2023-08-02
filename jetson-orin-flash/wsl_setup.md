# Step 1: Install wsl
Follow this [guide](https://www.cyberithub.com/how-to-install-ubuntu-20-04-lts-on-windows-10-wsl/) to enable and install WSL with Ubuntu 20.04

# Step 2: Install sdkmanager dependencies and GUI packages

> sudo apt update && sudo apt full-upgrade
> sudo apt install libxshmfence1 libglu1 libnss3-dev libgdk-pixbuf2.0-dev libgtk-3-dev libxss-dev

# Step 3; install sdkmanager
Download the sdkmanager debian package from [Nvidia](https://developer.nvidia.com/sdk-manager) on windows browser
Install the downloaded debian package in wsl
> sudo apt install /mnt/c/Users/{username}/Downloads/sdkmanager_{version}_amd64.deb

# Step 4: Install usbipd
In windows install usbipd with the following command
> winget install usbipd

Afterwards go back to wsl and run
> sudo apt install linux-tools-generic hwdata
> sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20


To attach the device to wsl run
> usbipd list

The device should come up as either
* APX
* Remote NDIS Compatible Device, USB Serial Device (COM4), ...

Once you have found the bus-id the device is connected to, run
> usbipd wsl attach -b <BUDID> -d <WSLDISTRIBUTION> -a

usbipd should then after a couple seconds log "attached"

If usbipd does not work for whatever reason, try uninstalling and then re-installing it. In my case "Device is in Error State" was an error in usbipd which was fixed with a re-install.

# Step 5: Run sdkmanager
Run sdkmanager on wsl using the sdkmanager command and complete the setup of your Orin

To login you must use the QR-method

NOTE: After flashing the device (If you skip that step or not) use the eth connection method.
Go on your Orin and find its IPv4 address, and write it into the sdkmanager address input, but delete the pre-existing address instead of replacing the last couple sequences.
For some reason, replacing the 55.0 in 192.168.55.0 did not work for me, but backspacing the whole string and writing the ip from scratch worked.

# Step 6: Add nvcc to path
If the 
> nvcc --version
command doesn't work on the Orin, append the following to the Orins ~/.bashrc file
> export PATH="/usr/local/cuda-{version}/bin:$PATH"
> export LD_LIBRARY_PATH="/usr/local/cuda-{version}/lib64:$LD_LIBRARY_PATH"