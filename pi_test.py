import time
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

#color = orange
#brightness = 24
#
#dimmest_divisor    = reduce(lambda i,j: min(i,j), filter(lambda x: x>0, color))
#dimmest_decimal    = 1.0/dimmest_divisor
#dimmest_brightness = 255/dimmest_divisor
#
#print "  {} / {}...".format(color, dimmest_divisor)
#print "  dimmest brightness: {}".format(dimmest_brightness)
#print "  dimmest decimal: {}".format(dimmest_decimal)
#print "  {}".format(tuple( map(lambda x: x/dimmest_divisor, color) ))


color = (180, 255, 0)
decimal = 1
dimmed_color = tuple( map(lambda x: int(x*decimal) or (x and 1), color) )
#divisor = int(1/decimal)
#dimmed_color = tuple( map(lambda x: int(x/divisor or (x and 1)), color) )

print "  {} * {}...".format(color, decimal)
print "  {}".format(dimmed_color)

color = dimmed_color

#strip.setBrightness(dimmest_brightness)
for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(color[1], color[0], color[2]) )
strip.show()

#strip.setPixelColor(0, Color(color[1], color[0], color[2]) )
#strip.show()
#exit()
