#!/usr/bin/env python
from gpiozero import Button, LED
from signal import pause
import os, sys
import time
from config import BUTTON_PIN, BUTTON_HOLD_TIME_KILL, BUTTON_HOLD_TIME_SHUTDOWN,\
                   BUTTON_HOLD_TIME_REBOOT, STATUS_LED_PIN

#--------------------------------- VARIABLES -----------------------------------
WeatherClock_dir       = "/home/pi/WeatherClock"
weather_clock_py       = "weather_clock.py"
kill_weather_clock_sh  = "kill_weather_clock.sh"
LED_shutdown_sequence  = "LED_shutdown_sequence.py"
LED_reboot_sequence    = "LED_reboot_sequence.py"
weather_clock_script   = "{}/{}".format(WeatherClock_dir, weather_clock_py)
kill_script            = "{}/{}".format(WeatherClock_dir, kill_weather_clock_sh)
LED_shutdown_script    = "{}/{}".format(WeatherClock_dir, LED_shutdown_sequence)
LED_reboot_script      = "{}/{}".format(WeatherClock_dir, LED_reboot_sequence)


stage = ""      # keeps track of what stage of a button hold you're in

#------------------------------- BUTTON ACTIONS --------------------------------
def when_pressed():
    global stage
    # start blinking with 1/2 second rate
    #led.blink(on_time=0.5, off_time=0.5)
    print "pressed"

    # start recording how long buton has been held down for
    start_time = time.time()

    # if held for X seconds, do different actions
    while btn.is_pressed:
        elapsed_time = time.time() - start_time

        if BUTTON_HOLD_TIME_KILL <= elapsed_time < BUTTON_HOLD_TIME_REBOOT:
            action = "KILL_SCRIPT" 
            if action not in stage:
                stage = action
                print "calling kill script --> ({})".format(kill_script)
                os.system(kill_script)

        elif BUTTON_HOLD_TIME_REBOOT <= elapsed_time < BUTTON_HOLD_TIME_SHUTDOWN:
            action = "REBOOT" 
            if action not in stage:
                stage = action
                print "STAGING FOR REBOOT"
                os.system("sudo python {}".format(LED_reboot_script))
                #reboot()

        elif (time.time() - start_time) >= BUTTON_HOLD_TIME_SHUTDOWN:
            action = "SHUTDOWN" 
            if action not in stage:
                stage = action
                print "STAGING FOR SHUTDOWN"
                os.system("sudo python {}".format(LED_shutdown_script))


def when_released():
    global stage
    # be sure to turn the LEDs off if we release early
    #led.off()
    print "released"

    if not stage:
        start_weather_clock()

    elif ("REBOOT" in stage) and ("SHUTDOWN" not in stage):
        reboot()

    # (SHUTDOWN happens through btn.when_held, so it is not needed here)
    elif ("SHUTDOWN" in stage):
        shutdown()

    # reset list of actions done
    stage = ""


def start_weather_clock():
    os.system(kill_script)
    print "STARTING THE WEATHER CLOCK"
    os.system("sudo python {} &".format(weather_clock_script))


def reboot():
    time.sleep(1)
    print "REBOOTING THE RASPBERRY PI NOW."
    os.system("sudo reboot")


def shutdown():
    time.sleep(1)
    print "SHUTTING OFF THE RASPBERRY PI NOW."
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
