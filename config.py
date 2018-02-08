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
CLOCK_BRIGHTNESS  = 5       # Overall brightness of the clock (0-255)
DIM_BY_HOUR       = False   # If True, each hour after current hour dims
DIM_BY_HOUR_VALUE = 0.50    # (If DIM_BY_HOUR is True, dims each hour by this
                            #  amount successively.)

CURSOR_COLOR       = black      # cursor color if weather is up-to-date
CURSOR_COLOR_API   = cyan       # cursor color if weather is calling API
CURSOR_COLOR_ERROR = red        # cursor color if weather API call fails

DISPLAY_TYPE       = "uniform"  #  "static", "uniform", or "unique"
LATENCY            = 0.01       # time between LED update (frame length)

SLEEP_AT_NIGHT     = True       # If True clock doesn't light during sleep hours
SLEEP_START        = '10:00pm'  # Time to sleep clock (24-hr format - 'HH:MM')
SLEEP_STOP         = '6:30am'   # Time to wake clock up (24-hr format - 'HH:MM')


#------------------------------- OTHER HARDWARE --------------------------------
BUTTON_PIN                = 23  # GPIO pin for button (2nd button contact = GND)
BUTTON_HOLD_TIME_KILL     = 1   # Seconds to hold down button to kill Clock
BUTTON_HOLD_TIME_REBOOT   = 3   # Seconds to hold down button for reboot
BUTTON_HOLD_TIME_SHUTDOWN = 6   # Seconds to hold down button for shutoff

STATUS_LED_PIN            = 16  # A simple status LED (if you have one).
                                # Provides feedback for button presses.
