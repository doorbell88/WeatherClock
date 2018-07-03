#!/usr/bin/env python
from gpiozero import Button, LED
import signal
import os, sys
import subprocess
import time
from config import BUTTON_PIN, STATUS_LED_PIN, \
                   BUTTON_QUICK_PRESS, BUTTON_HOLD_TIME_KILL, \
                   BUTTON_HOLD_TIME_SHUTDOWN, BUTTON_HOLD_TIME_REBOOT

#--------------------------------- VARIABLES -----------------------------------
WeatherClock_dir       = "/home/pi/WeatherClock"
weather_clock_py       = "weather_clock.py"
kill_weather_clock_sh  = "kill_weather_clock.sh"
get_weather_clock_pid  = "get_weather_clock_pid.sh"
LED_shutdown_sequence  = "LED_shutdown_sequence.py"
LED_reboot_sequence    = "LED_reboot_sequence.py"
LED_strip              = "LED_strip.py"
weather_clock_script   = "{}/{}".format(WeatherClock_dir, weather_clock_py)
kill_script            = "{}/{}".format(WeatherClock_dir, kill_weather_clock_sh)
get_weather_clock_pid  = "{}/{}".format(WeatherClock_dir, get_weather_clock_pid)
LED_shutdown_script    = "{}/{}".format(WeatherClock_dir, LED_shutdown_sequence)
LED_reboot_script      = "{}/{}".format(WeatherClock_dir, LED_reboot_sequence)
LED_strip_script       = "{}/{}".format(WeatherClock_dir, LED_strip)


stage = ""      # keeps track of what stage of a button hold you're in
quick_press_start  = 0.0
quick_press_counter = 0 # keeps track of how many times button has been pressed quickly

#------------------------------- BUTTON ACTIONS --------------------------------
def when_pressed():
    global stage
    global quick_press_start
    global quick_press_counter
    # start blinking with 1/2 second rate
    #led.blink(on_time=0.5, off_time=0.5)
    print "pressed"

    # clear the quick_press variables if a long time has passed
    if time.time() - quick_press_start > BUTTON_QUICK_PRESS:
        quick_press_start = time.time()
        quick_press_counter = 0

    # start recording how long button has been held down for (this press only)
    start_time = time.time()

    # if held for X seconds, do different actions
    while btn.is_pressed:
        elapsed_time = time.time() - start_time

        if elapsed_time <= BUTTON_QUICK_PRESS:
            if quick_press_start == 0.0:
                quick_press_start = time.time()

        #if BUTTON_HOLD_TIME_KILL <= elapsed_time < BUTTON_HOLD_TIME_REBOOT:
        #    action = "KILL_SCRIPT" 
        #    if action not in stage:
        #        stage = action
        #        print "calling kill script --> ({})".format(kill_script)
        #        os.system(kill_script)
        #        os.system("sudo python {}".format(LED_strip_script))

        elif BUTTON_HOLD_TIME_REBOOT <= elapsed_time < BUTTON_HOLD_TIME_SHUTDOWN:
            action = "REBOOT" 
            if action not in stage:
                stage = action
                print "STAGING FOR REBOOT"
                os.system("sudo python {}".format(LED_reboot_script))

        elif (time.time() - start_time) >= BUTTON_HOLD_TIME_SHUTDOWN:
            action = "SHUTDOWN" 
            if action not in stage:
                stage = action
                print "STAGING FOR SHUTDOWN"
                os.system("sudo python {}".format(LED_shutdown_script))


def when_released():
    global stage
    global quick_press_start
    global quick_press_counter
    print "released"

    if time.time() - quick_press_start < BUTTON_QUICK_PRESS:
        quick_press_counter += 1

        if quick_press_counter == 1:
            toggle_mode()

        elif quick_press_counter >=2:
            toggle_weather_clock()
            quick_press_counter = 0
            quick_press_start = 0.0

    elif stage == "REBOOT":
        reboot()

    # (SHUTDOWN happens through btn.when_held, so it is not needed here)
    #elif stage == "SHUTDOWN"
    #    shutdown()

    # reset list of actions done
    stage = ""


def toggle_mode():
    # toggle between "sky" and "temp" modes
    print "Sending SIGINT to toggle mode on weather clock"
    weather_clock_pid = subprocess.check_output(get_weather_clock_pid)
    try:
        weather_clock_pid = int(weather_clock_pid)
    except:
        start_weather_clock()
    else:
        os.kill(weather_clock_pid, signal.SIGTERM)


def toggle_weather_clock():
    #exit_status = os.WEXITSTATUS(os.system(kill_script))
    ##if successfull, then the weather clock was just killed
    #if exit_status == 0:
    #    return
    ## if unsuccessful, there was no weather clock process --> start one
    #elif exit_status == 1:
    #    start_weather_clock()

    weather_clock_pid = subprocess.check_output(get_weather_clock_pid)
    if weather_clock_pid:
        kill_weather_clock()
    else:
        start_weather_clock()


def kill_weather_clock():
    print "calling kill script --> ({})".format(kill_script)
    os.system(kill_script)
    os.system("sudo python {}".format(LED_strip_script))


def start_weather_clock():
    os.system(kill_script)
    print "STARTING THE WEATHER CLOCK"
    os.system("sudo python {} &".format(weather_clock_script))


def reboot():
    time.sleep(1)
    print "REBOOTING THE RASPBERRY PI NOW."
    #os.system("sudo reboot")


def shutdown():
    time.sleep(1)
    print "SHUTTING OFF THE RASPBERRY PI NOW."
    #os.system("sudo poweroff")



#------------------------------------ MAIN -------------------------------------
# Instantiate button and LED
led = LED(STATUS_LED_PIN)
btn = Button(BUTTON_PIN, hold_time=BUTTON_HOLD_TIME_SHUTDOWN)

# register button actions
btn.when_held     = shutdown
btn.when_pressed  = when_pressed
btn.when_released = when_released

# wait until a signal is received
signal.pause()
