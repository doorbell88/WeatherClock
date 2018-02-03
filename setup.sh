# This script will install the packages necessary to run weather_clock.py
#
# It may also in the future set up the RaspberryPi to run the script at boot,
# and clean up at shutdown.
#_______________________________________________________________________________

# get the repo's base directory
WEATHERCLOCK_BASE_DIR="$(git rev-parse --show-toplevel)"

#------------------------------- SETUP / CHECKS --------------------------------
# Check if being run as root
if [ "$(whoami)" != "root" ]; then
    echo "Please run as root"
    exit 1
fi

#----------------------------- RaspberryPi Setup -------------------------------
sudo apt-get update

# Set up wpa_supplicant (for wifi networks)
WPA_SUPPLICANT_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"
WPA_SUPPLICANT_TXT="$WEATHERCLOCK_BASE_DIR/wpa_supplicant.txt"

echo "Making a copy of your wpa_supplicant.conf file..."
cp -v $WPA_SUPPLICANT_CONF{,.bak}
echo "Overwriting wpa_supplicant.conf with prepared contents"
sudo cat "$WPA_SUPPLICANT_TXT" > "$WPA_SUPPLICANT_CONF"
echo "Done with wpa_supplicant.  Please check for correct wifi network info."


#------------------------------- Python Modules --------------------------------
sudo apt-get install python-pip

pip install -r "$WEATHERCLOCK_BASE_DIR/requirements.txt"

#pip install python-forecastio
#pip install requests[security]
#pip install gpiozero


#------------------------------ WS2812 NeoPixel --------------------------------
sudo apt-get install build-essential python-dev scons swig

git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons

cd python
sudo python setup.py install


#---------------------------- Run Programs at Boot -----------------------------
sudo "$WEATHERCLOCK_BASE_DIR/add_to_run_at_boot.sh"
