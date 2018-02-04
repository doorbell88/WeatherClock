# This script will install the packages necessary to run weather_clock.py
#
# It may also in the future set up the RaspberryPi to run the script at boot,
# and clean up at shutdown.
#_______________________________________________________________________________

# get the repo's base directory
WEATHERCLOCK_BASE_DIR="$(git rev-parse --show-toplevel)"
cd $WEATHERCLOCK_BASE_DIR

#------------------------------- SETUP / CHECKS --------------------------------
# Check if being run as root
if [ "$(whoami)" != "root" ]; then
    echo "Please run as root"
    exit 1
fi

#----------------------------- RaspberryPi Setup -------------------------------
yes Y | sudo apt-get update

# Set up wpa_supplicant (for wifi networks)
WPA_SUPPLICANT_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"
WPA_SUPPLICANT_TXT="$WEATHERCLOCK_BASE_DIR/wpa_supplicant.txt"

echo "Making a copy of your wpa_supplicant.conf file..."
cp -v ${WPA_SUPPLICANT_CONF} ${WPA_SUPPLICANT_CONF}.bak
echo "Overwriting wpa_supplicant.conf with prepared contents"
sudo cat "$WPA_SUPPLICANT_TXT" > "$WPA_SUPPLICANT_CONF"
echo "Done with wpa_supplicant.  Please check for correct wifi network info."


#------------------------------- Python Modules --------------------------------
yes Y | sudo apt-get install python-pip

pip install -r "$WEATHERCLOCK_BASE_DIR/requirements.txt"


#------------------------------ WS2812 NeoPixel --------------------------------
yes Y | sudo apt-get install build-essential python-dev scons swig

cd $WEATHERCLOCK_BASE_DIR

git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons

cd python
yes Y | sudo python setup.py install


#---------------------------- Run Programs at Boot -----------------------------
sudo "$WEATHERCLOCK_BASE_DIR/add_to_run_at_boot.sh"


#----------------------- Run programs now in background ------------------------
{ sudo python "$WEATHERCLOCK_BASE_DIR/weather_clock.py" >/dev/null 2>&1 & }
{ sudo python "$WEATHERCLOCK_BASE_DIR/button_listener.py" >/dev/null 2>&1 & }


#------------------------------ NOTICES TO USER --------------------------------
tput setaf 3
echo "========================================================================="
echo "Setup complete."
echo
echo "Make sure to configure the following:"
echo "  (1) raspi-config:"
echo "        - timezone"
echo "        - hostname"
echo "        - password"
echo "  (2) /etc/wpa_supplicant/wpa_supplicant.conf"
echo "        - wifi networks and passwords"
echo "  (3) Anything else you want to change in WeatherClock/config.py"
echo
tput setaf 1
echo "PLEASE REBOOT WHEN YOU HAVE FINISHED SETUP."
echo

exit
