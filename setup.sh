# This script will install the packages necessary to run weather_clock.py
#
# It may also in the future set up the RaspberryPi to run the script at boot,
# and clean up at shutdown.
#_______________________________________________________________________________

#------------------------------- SETUP / CHECKS --------------------------------
# Check if being run as root
if (whoami != root) then
    echo "Please run as root"
    exit 1
fi

#----------------------------- RaspberryPi Setup -------------------------------
sudo cat ./wpa_supplicant.txt > /etc/wpa_supplicant/wpa_supplicant.conf


#------------------------------- Python Modules --------------------------------
sudo apt-get install python-pip

pip install python-forecastio
pip install requests[security]
pip install gpiozero


#------------------------------ WS2812 NeoPixel --------------------------------
sudo apt-get update
sudo apt-get install build-essential python-dev scons swig

git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons

cd python
sudo python setup.py install
