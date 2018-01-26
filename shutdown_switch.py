#!/usr/bin/env python
from gpiozero import Button, LED
from signal import pause
import os, sys
import time
from config import BUTTON_PIN, BUTTON_HOLD_TIME, STATUS_LED_PIN

#--------------------------------- VARIABLES -----------------------------------
weather_clock_file = "weather_clock.py"


#------------------------------- BUTTON ACTIONS --------------------------------
def when_pressed():
    # start blinking with 1/2 second rate
    #led.blink(on_time=0.5, off_time=0.5)
    print "pressed"

def when_released():
    # be sure to turn the LEDs off if we release early
    #led.off()
    print "released"

def shutdown():
    print "Yay!"
    os.system("/home/pi/WeatherClock/kill_weather_clock.sh {}".format(weather_clock_file))
    os.system("sudo python /home/pi/WeatherClock/turn_off_LED_array.py")
    time.sleep(1)
    os.system("sudo poweroff")


#------------------------------------ MAIN -------------------------------------
# Instantiate button and LED
led = LED(STATUS_LED_PIN)
btn = Button(BUTTON_PIN, hold_time=BUTTON_HOLD_TIME)

# register button actions
btn.when_held     = shutdown
btn.when_pressed  = when_pressed
btn.when_released = when_released

# wait until a signal is received
pause()
