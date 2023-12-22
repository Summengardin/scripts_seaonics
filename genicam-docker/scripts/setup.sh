echo Creating python virtual environment
sudo apt install -y         python3-pip
python3 -m venv venv

echo Activating python virtual environment
source venv/bin/activate

echo Installing python dependencies
pip install -r requirements.txt

echo Updating apt
sudo apt update

echo Installing gstreamer
cd ../scripts
bash install_gstreamer.sh
