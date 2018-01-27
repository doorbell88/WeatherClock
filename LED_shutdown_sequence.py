import time
from copy import deepcopy
from neopixel import *
from config import LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, \
                   ACTIVE_LEDS

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


color   = green
(R,G,B) = color
(r,g,b) = deepcopy(color)

latency = 0.01
dimming = 0.01
while (R>0) or (G>0) or (B>0):
    r -= (R * dimming)
    g -= (G * dimming)
    b -= (B * dimming)
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(int(g), int(r), int(b)) )
    strip.show()
    print "showing"
    time.sleep(0.01)
