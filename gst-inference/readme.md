# GST-inference
This folder is for running pipelines with inference.

## Prerequisites
Most dependencies will get installed by running the setup script, but DeepStream must also be installed. This must be done through the SDKManager.

Additionally you will need a YOLOv8 net in a pytorch format and a labels.txt file. To test the networks in (examples)[../examples] can be used.
Once you have your network and label files, or examples, run the compile_model script
> bash compile_model.sh <PATH_TO_NETWORK> <PATH_TO_LABEL_FILE>