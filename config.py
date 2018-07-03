# This configuration file is where you set all the variables that may be
# different depending on your own personal setup, location, hardware, etc.
#
# Your Dark Sky API key must be configured here before the Weather Clock can 
# access weather data.  Your latitude and longitude also bust be set here.
#   --> Getting a Dark Sky API key is free!  Just go to the website below and 
#       click on [TRY FOR FREE].  You will register and receive your own
#       personal API key in an email:
#       
#               https://darksky.net/dev
#
# I hope you enjoy your Weather Clock!
#
#                                       Date Created:   (1/27/2018)
#                                       Created by:     Kevin Klinkel
#                                       GitHub:         doorbell88
#
# NOTE: All Pin numbers refer to the RPi's GPIO pin number, (which is different
#       from the physical pin number)!

from colors import *

#--------------------------- WEATHER & LOCALIZATION ----------------------------
LATITUDE            = 39.9936
LONGITUDE           = -105.0897
DARK_SKY_API_KEY    = "0bd8f5fb32262aa45c4598c2f1ef5b44"


#----------------------------- LED CONFIGURATION -------------------------------
LED_COUNT   = 24            # Number of LED NeoPixels
LED_PIN     = 18            # GPIO pin (must support PWM)
LED_FREQ_HZ = 800000        # LED signal frequency (usually 800khz)
LED_DMA     = 5             # DMA channel to use for generating signal
LED_INVERT  = False         # True when using NPN transistor level shift

NUMBER_OF_HOURS = 12        # Number of hours displayed in the clock

ACTIVE_LEDS     = 12        # (If you have 24 LEDs, but only want one lit up for
                            #  each hour, you would set ACTIVE_LEDS = 12)
                            #   --> Currently only works with 12 or 24 LEDs


#------------------------------- CUSTOMIZATION ---------------------------------
CURSOR_COLOR_SKY   = red        # Cursor color if weather is up-to-date
CURSOR_COLOR_TEMP  = violet     # Cursor color if weather is up-to-date
CURSOR_COLOR_API   = black      # Cursor color if weather is calling API
CURSOR_COLOR_ERROR = black      # Cursor color if weather API call fails
DISPLAY_MINUTE     = False      # True will display the minute hand. False won't
MINUTE_CURSOR_DIM  = 0.5        # Amount to dim minute cursor

CLOCK_BRIGHTNESS  = DIMMEST # Overall brightness of the clock (0-255)
DIM_BY_HOUR       = False   # If True, each hour after current hour dims
DIM_BY_HOUR_VALUE = 0.70    # (If DIM_BY_HOUR is True, dims each hour by this
                            #  amount successively.)

SLEEP_AT_NIGHT = True       # If True clock doesn't light during sleep hours
SLEEP_START    = '9:00pm'   # Time to sleep clock (24-hr format - 'HH:MM')
SLEEP_STOP     = '6:30am'   # Time to wake clock up (24-hr format - 'HH:MM')

DISPLAY_TYPE   = "uniform"  #  "static", "uniform", "unique", or "temp"
DISPLAY_MODE   = "sky"      # "sky" or "temp"
LATENCY        = 0.05       # time between LED update (frame length)


#------------------------------- OTHER HARDWARE --------------------------------
BUTTON_PIN                = 23  # GPIO pin for button (2nd button contact = GND)
BUTTON_HOLD_TIME_KILL     = 1   # Seconds to hold down button to kill Clock
BUTTON_HOLD_TIME_REBOOT   = 3   # Seconds to hold down button for reboot
BUTTON_HOLD_TIME_SHUTDOWN = 5   # Seconds to hold down button for shutoff

STATUS_LED_PIN            = 16  # A simple status LED (if you have one).
                                # Provides feedback for button presses.


#---------------------------------- PROFILES -----------------------------------
# Profiles with set characteristics, to make it easy to change the appearance
# and functionality without having to change all the associated values
#
#    "disk"
#    "dim disk"
#    "faded disk"
#    "clock"
#    "dim clock"
#    "faded clock"

PROFILE = "dim clock"

if PROFILE == "disk":
    ACTIVE_LEDS                = LED_COUNT
    CLOCK_BRIGHTNESS           = 255
    DIM_BY_HOUR                = False
elif PROFILE == "dim disk":
    ACTIVE_LEDS                = LED_COUNT
    CLOCK_BRIGHTNESS           = DIMMEST
    DIM_BY_HOUR                = False
elif PROFILE == "faded disk":
    ACTIVE_LEDS                = LED_COUNT
    CLOCK_BRIGHTNESS           = 255
    DIM_BY_HOUR                = True
    DIM_BY_HOUR_VALUE          = 0.70
elif PROFILE == "clock":
    ACTIVE_LEDS                = NUMBER_OF_HOURS
    CLOCK_BRIGHTNESS           = 255
    DIM_BY_HOUR                = False
elif PROFILE == "dim clock":
    ACTIVE_LEDS                = NUMBER_OF_HOURS
    CLOCK_BRIGHTNESS           = DIMMEST
    DIM_BY_HOUR                = False
elif PROFILE == "faded clock":
    ACTIVE_LEDS                = NUMBER_OF_HOURS
    CLOCK_BRIGHTNESS           = 255
    DIM_BY_HOUR                = True
    DIM_BY_HOUR_VALUE          = 0.70
else:
    pass
