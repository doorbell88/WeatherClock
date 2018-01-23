import time
from neopixel import *
#from pi_clock.py import *

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

black           =   (0, 0, 0)
white           =   (255, 255, 255)
red             =   (255, 0, 0)
green           =   (0, 255, 0)
blue            =   (0, 0, 255)
cyan            =   (0, 255, 255)
magenta         =   (255, 0, 255)
yellow          =   (255, 255, 0)
orange          =   (255, 50, 0)
indigo          =   (70, 0, 255)
violet          =   (100, 0, 255)
light_yellow    =   (100, 100, 30)
light_green     =   (75, 255, 75)
dark_green      =   (0, 100, 0)
light_blue      =   (100, 120, 255)
dark_blue       =   (0, 0, 100)
gray_blue       =   (50, 50, 150)
light_gray      =   (100, 100, 100)
gray            =   (80, 80, 80)

color = black

#strip.setPixelColor(0, Color(color[1], color[0], color[2]) )
#strip.show()
#exit()

for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(color[1], color[0], color[2]) )
strip.show()
