import time
import sys
from colors import *
from neopixel import *

# LED strip configuration:
LED_COUNT   = 24      # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor
                      # level shift)

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
# Intialize the library (must be called once before other functions).
strip.begin()

# get the color from command line (if applicable)
if len(sys.argv) > 1:
    try:
        color = eval(sys.argv[1])
    except NameError:
        color = black
else:
    color = black

# print the color value (for debuggin)
print color

# set every LED in the strip to the color
for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(color[1], color[0], color[2]) )
strip.show()

# FUTURE:  Add more command line options
#strip.setPixelColor(0, Color(color[1], color[0], color[2]) )
#strip.show()
#exit()
