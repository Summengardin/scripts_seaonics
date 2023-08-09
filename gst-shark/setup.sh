#!/bin/bash
cd ../scripts
bash install_meson.sh
cd ../gst-shark

if [ -d "./gst-shark" ]; then
    rm -rf ./gst-shark
fi

sudo apt install -y graphviz libgraphviz-dev octave epstool babeltrace gtk-doc-tools ninja-build

git clone https://github.com/RidgeRun/gst-shark/
cd gst-shark

meson builddir --prefix /usr/
ninja -C builddir

sudo ninja install -C builddir

cd ../
#rm -rf gst-shark