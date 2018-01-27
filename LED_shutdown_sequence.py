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
while (r>0) or (g>0) or (b>0):
    # dim each color
    r -= (R * dimming)
    g -= (G * dimming)
    b -= (B * dimming)
    
    # make sure each value doesn't become negative
    r = 0 if r<0 else r
    g = 0 if g<0 else g
    b = 0 if b<0 else b

    # set the new display
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(int(g), int(r), int(b)) )
    strip.show()
    time.sleep(0.01)

# finally, set to black
(r,g,b) = (0,0,0)
strip.setPixelColor(i, Color(0,0,0) )
