#!/bin/bash

if ! [ -f "$1" ]; then
    echo "The model $FILE was not found"
    exit
fi

if ! [ -f "$2" ]; then
    echo "The model $FILE was not found"
    exit
fi

if [ -d "./out" ]; then
    rm -rf ./out
fi

# Install deps
sudo apt install -y \
libssl1.1 \
libgstreamer1.0-0 \
gstreamer1.0-tools \
gstreamer1.0-plugins-good \
gstreamer1.0-plugins-bad \
gstreamer1.0-plugins-ugly \
gstreamer1.0-libav \
libgstreamer-plugins-base1.0-dev \
libgstrtspserver-1.0-0 \
libjansson4 \
libyaml-cpp-dev

sudo apt update
sudo apt install -y python3-pip
pip3 install --upgrade pip

# Clone ultralytics repo and install requirements
git clone https://github.com/ultralytics/ultralytics.git
cd ultralytics
sed -i 's/torch/# torch/' requirements.txt
pip3 install -r requirements.txt
pip3 install python-dateutil --upgrade

sudo apt-get install -y libopenblas-base libopenmpi-dev
wget https://developer.download.nvidia.com/compute/redist/jp/v50/pytorch/torch-1.12.0a0+2c916ef.nv22.3-cp38-cp38-linux_aarch64.whl -O torch-1.12.0a0+2c916ef.nv22.3-cp38-cp38-linux_aarch64.whl
pip3 install torch-1.12.0a0+2c916ef.nv22.3-cp38-cp38-linux_aarch64.whl

sudo apt install -y libjpeg-dev zlib1g-dev
git clone --branch v0.13.0 https://github.com/pytorch/vision torchvision
cd torchvision
python3 setup.py install --user
cd ../
rm -rf ./torchvision

# Clone DeepStream-YOLO
cd ../
git clone https://github.com/marcoslucianops/DeepStream-Yolo
cd DeepStream-Yolo
git checkout 68f762d5bdeae7ac3458529bfe6fed72714336ca

cp utils/gen_wts_yoloV8.py ../ultralytics
cd ../ultralytics 

# Gen model for DeepStream-YOLO
echo "Generating YOLO weights"
cp ../$1 ./model.pt
python3 gen_wts_yoloV8.py -w model.pt

echo "Building DeepStream-Yolo"
cd ../DeepStream-Yolo
mkdir ../out

cp ../ultralytics/yolov8_model.cfg ./model.cfg
cp ../ultralytics/yolov8_model.wts ./model.wts
rm ./labels.txt

rm -rf ../ultralytics

CUDA_VER=11.4 make -C nvdsinfer_custom_impl_Yolo --silent

rm deepstream_app_config.txt
rm config_infer_primary_yoloV8.txt

cd ../
cp ../config/deepstream_app_config.txt ./out
cp ../config/config_infer_primary_yoloV8.txt ./out
mv ./DeepStream-Yolo/model.cfg ./out
mv ./DeepStream-Yolo/model.wts ./out
mv ./DeepStream-Yolo/nvdsinfer_custom_impl_Yolo ./out


cp $2 ./out/labels.txt

CLASSES=$(expr $(wc -l < ./out/labels.txt) + 1)

sed -i "s/<CLASS_CT>/$CLASSES/" ./out/config_infer_primary_yoloV8.txt


rm -rf ./DeepStream-Yolo

echo cd into DeepStream-Yolo and run the pipeline with deepstream-app -c deepstream_app_config.txt