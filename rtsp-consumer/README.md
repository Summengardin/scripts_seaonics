## 1. Run setup.sh
This will install gstreamer libraries, set python virtual environment and install pip libraries.

## 2. Edit IPs (if needed)
Set the IP of the unit to match documentation. 
It is currently set at 10.1.2.80


Edit the IP of the camera servers to match documentation.
This is done inside [config.yaml](config.yaml)


Port must be the same as the server is setup at (8554 is default)


Mount must be the same as the server is setup at (/cam is default)


## 3. Make the start-script executable
Right click the start_consumer.sh file an check 'Allow executing file as program'
