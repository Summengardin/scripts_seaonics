# Running DeepStream pipeline with YOLO-inference

## Requirements

* JetPack 5.1.1 host computer
* DeepStream sdk 6.2
* Yolov8 pytorch model with labels (Example ResNet and Landing models & labels are provided)

## Compiling and running

Run the [compile model script](./compile_model.sh)
> bash compile_model.sh <model_path> <labels_path>

Example:
> bash compile_model.sh examples/resnet/yolov8s.pt examples/resnet/labels.txt


Once compilation of the model is complete, cd into the out directory and run 
> deepstream-app -c deepstream_app_config.txt