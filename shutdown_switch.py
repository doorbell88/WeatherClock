#!/usr/bin/env python
from gpiozero import Button, LED
from signal import pause
import os, sys
import time

offGPIO  = int(sys.argv[1]) if len(sys.argv) >= 2 else 21
holdTime = int(sys.argv[2]) if len(sys.argv) >= 3 else 6
ledGPIO  = int(sys.argv[3]) if len(sys.argv) >= 4 else 16

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
    os.system("/home/pi/WeatherClock/kill_weather_clock.sh {}".format("pi_clock.py"))
    os.system("sudo python /home/pi/WeatherClock/turn_off_LED_array.py")
    time.sleep(1)
    os.system("sudo poweroff")

led = LED(ledGPIO)
btn = Button(offGPIO, hold_time=holdTime)
btn.when_held     = shutdown
btn.when_pressed  = when_pressed
btn.when_released = when_released
pause()
