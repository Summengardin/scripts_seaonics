echo Creating python virtual environment
python3 -m venv venv

echo Activating python virtual environment
source venv/bin/activate

echo Installing python dependencies
pip install -r requirements.txt

echo Updating apt
sudo apt update

echo Installing gstreamer
sudo apt-get install gstreamer1.0-tools gstreamer1.0-alsa \
     gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
     gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
     gstreamer1.0-libav

echo Installing gstreamer development libraries
sudo apt-get install libgstreamer1.0-dev \
     libgstreamer-plugins-base1.0-dev \
     libgstreamer-plugins-good1.0-dev \
     libgstreamer-plugins-bad1.0-dev