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
LED_shutdown_sequence  = "LED_shutdown_sequence.py"
LED_shutdown_script    = "{}/{}".format(WeatherClock_dir, LED_shutdown_sequence)


#------------------------------- BUTTON ACTIONS --------------------------------
def when_pressed():
    # start blinking with 1/2 second rate
    #led.blink(on_time=0.5, off_time=0.5)
    print "pressed"

    # start recording how long buton has been held down for
    start_time = time.time()

    # if held for 2 seconds, kill the weather_clock.py
    while btn.is_pressed:
        if (time.time() - start_time) >= BUTTON_HOLD_TIME_KILL: 
            print "calling killl script --> ({})".format(kill_script)
            os.system(kill_script)
            break


def when_released():
    # be sure to turn the LEDs off if we release early
    #led.off()
    print "released"


def shutdown():
    print "SHUTTING OFF THE RASPBERRY PI NOW."
    os.system("sudo python {}".format(LED_shutdown_script))
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
