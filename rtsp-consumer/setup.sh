echo Installing dependencies
bash ../scripts/install_gstreamer.sh

sudo apt-get install -y \
libcairo2-dev \
libxt-dev \
libgirepository1.0-dev \
python3-pip \
python3-venv

echo Creating python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install pycairo PyGObject

