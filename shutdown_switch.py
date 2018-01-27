#!/usr/bin/env python
from gpiozero import Button, LED
from signal import pause
import os, sys
import time
from config import BUTTON_PIN, BUTTON_HOLD_TIME_KILL, BUTTON_HOLD_TIME_SHUTDOWN,\
                   STATUS_LED_PIN

#--------------------------------- VARIABLES -----------------------------------
WeatherClock_dir       = "/home/pi/WeatherClock"
kill_weather_clock_sh  = "kill_weather_clock.sh"
kill_script            = "{}/{}".format(WeatherClock_dir, kill_weather_clock_sh)


#------------------------------- BUTTON ACTIONS --------------------------------
def when_pressed():
    # start blinking with 1/2 second rate
    #led.blink(on_time=0.5, off_time=0.5)
    print "pressed"

    # if held for 2 seconds, kill the weather_clock.py
    start = time.time()
    while time.time() - start < BUTTON_HOLD_TIME_KILL:
        pass
    print "calling {}".format(kill_script)
    os.system(kill_script)


def when_released():
    # be sure to turn the LEDs off if we release early
    #led.off()
    print "released"


def shutdown():
    print "SHUTTING OFF THE RASPBERRY PI NOW."
    time.sleep(1)
    os.system("sudo poweroff")


#------------------------------------ MAIN -------------------------------------
# Instantiate button and LED
led = LED(STATUS_LED_PIN)
btn = Button(BUTTON_PIN, hold_time=BUTTON_HOLD_TIME_SHUTDOWN)

# register button actions
btn.when_held     = shutdown
btn.when_pressed  = when_pressed
btn.when_released = when_released

# wait until a signal is received
pause()
