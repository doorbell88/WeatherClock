#!usr/bin/env python
"""
WEATHER CLOCK

A RaspberryPi-powered display, which displays weather data in a format that
resembles an analog clock interface.

The High, Low, and Current temperatures will be represented by three clock
hands in the middle of the clock.

The Precipitation / Sky Conditions will be represented by colored LEDs 
on the outside of the clock.  Each LED will be placed at each hour.  The 
current conditions will be the brightest LED, and will be located at the
current hour on the clock.
"""

import forecastio
import logging
logging.captureWarnings(True)

import json
import datetime
import time
import os
import sys
import re
import signal
#import numpy as np
from random import randint, choice
from copy import copy, deepcopy
#from termcolor import colored, cprint
#from term_colors import rgb, print_color, set_color, format_color
from colors import *
from neopixel import *

from config import LATITUDE, LONGITUDE, DARK_SKY_API_KEY, \
                   LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, \
                   ACTIVE_LEDS


#===============================================================================
#--------------------------------- CONSTANTS -----------------------------------
#===============================================================================

#----------------------------------- colors ------------------------------------
# (now imports all colors from colors.py)


#------------------------------- other options ---------------------------------
NUMBER_OF_HOURS = 12
cursor_color    = red


#===============================================================================
#---------------------------------- CLASSES ------------------------------------
#===============================================================================

class Numpy(object):
    """
    Mimic a few simple numpy methods.
    (Since numpy is very large, and it takes hours to install from scratch.)
    """
    def add(self, lst, x):
        if type(x) == type(0) or type(x) == type(0.0):
            return map(lambda i: i+x, lst)
        else:
            return map(lambda i,j: i+j, lst, x)

    def subtract(self, lst, x):
        if type(x) == type(0) or type(x) == type(0.0):
            return map(lambda i: i-x, lst)
        else:
            return map(lambda i,j: i-j, lst, x)

    def multiply(self, lst, x):
        if type(x) == type(0) or type(x) == type(0.0):
            return map(lambda i: i*x, lst)
        else:
            return map(lambda i,j: i*j, lst, x)

    def divide(self, lst, x):
        if type(x) == type(0) or type(x) == type(0.0):
            return map(lambda i: i/x, lst)
        else:
            return map(lambda i,j: i/j, lst, x)

    def abs(self, lst):
        return map(lambda i: abs(i), lst)


class Parser(object):
    """
    Parses weather data from Dark Sky API
    """
    def __init__(self):
        # (7am - 6am next day)
        self.today_weather = {}
        self.tomorrow_weather = {}
        self.yesterday_weather = {}
        
        # (0 - 23 hour)
        self.today_24 = {}
        self.tomorrow_24 = {}

        # (next 12 hours)
        self.clock_12 = {}
        self.next_12  = []

        # populate self.next_12
        clock_item = { "icon"    : "",
                       "summary" : "",
                       "temp"    : 0,
                       "time"    : "" }
        current_time = datetime.datetime.now().hour
        for i in range(NUMBER_OF_HOURS):
            HOUR = int((current_time+i) % 12)
            next_item    = deepcopy(clock_item)
            two_digit_hr = "{:0>2}".format(HOUR)
            next_item["time"] = "xxxx-xx-xx {}:00:00".format(two_digit_hr)
            self.next_12.append(next_item)

        # Current conditions
        self.current = {}

    def getWeather(self, time_window):
        # Get forecast from Dark Sky API
        forecast = forecastio.load_forecast(DARK_SKY_API_KEY, LATITUDE, LONGITUDE,
                                            time=time_window)
        byHour = forecast.hourly()
        
        current_conditions = forecast.currently()
        temp = current_conditions.temperature
        summary = current_conditions.summary
        self.current["temp"] = temp
        self.current["summary"] = summary

        # Get weather into hourly list (24 hours -- 7am-6am)
        i=0
        Hours = {}
        # Get temp and summary for the hour
        for hourlyData in byHour.data:
            time = str(hourlyData.time)
            hour = str(hourlyData.time)[11:13]
            day = str(hourlyData.time)[8:10]
            temp = hourlyData.temperature
            summary = '{}'.format(hourlyData.summary)
            icon = '{}'.format(hourlyData.icon)

            # put temp and summary into this Hour's dictionary
            Hours[hour] = {}
            Hours[hour]["time"] = time
            Hours[hour]["temp"] = temp
            Hours[hour]["summary"] = summary
            Hours[hour]["icon"] = icon
            i+=1
        return Hours

    def getCurrentConditions(self):
        current_time = datetime.datetime.now()
        current_hour = str(current_time)[11:13]
        forecast = forecastio.load_forecast(DARK_SKY_API_KEY, LATITUDE, LONGITUDE)
        current_conditions = forecast.currently()
        temp = current_conditions.temperature
        summary = current_conditions.summary
        self.current["temp"] = temp
        self.current["summary"] = summary
        return temp, summary

    def parseWeather(self):
        # Set time points
        today = datetime.datetime.now()
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today + datetime.timedelta(days=-1)

        # Find weather (7am - 6am next day)
        self.today_weather = self.getWeather(today)
        self.tomorrow_weather = self.getWeather(tomorrow)
        self.yesterday_weather = self.getWeather(yesterday)

        unknown_hour_dict = {"time": "", "temp": "", "summary": "", "icon": ""}

        # Get current conditions
        #self.getCurrentConditions()
        
        def parse24(destination_dict, day1, day2):
            # Parse into 24-hour chunks (0 - 23 hour)
            i=0
            while i < 7:
                hour = '{:02d}'.format(i)
                try:
                    destination_dict[hour] = day1[hour]
                except KeyError:
                    destination_dict[hour] = day1["05"]     #Daylight Savings
                i+=1
            i=7
            while i <= 23:
                hour = '{:02d}'.format(i)
                try:
                    destination_dict[hour] = day2[hour]
                except KeyError:
                    destination_dict[hour] = day2["22"]     #Daylight Savings
                i+=1
    
        # Parse into 24-hour chunks (0 - 23 hour)
        # (Today)
        parse24(    self.today_24,
                    self.yesterday_weather,
                    self.today_weather)
        # (Tomorrow)
        parse24(    self.tomorrow_24,
                    self.today_weather,
                    self.tomorrow_weather)

        # Parse into 12-hour chunks (0 - 11 O'clock)
        current_time = int( str(today)[11:13] )
        self.clock_12 = {}
        self.next_12 = []
        for i in range(NUMBER_OF_HOURS):
            hour = '{:02d}'.format(current_time + i)
            hour_12 = '{:02d}'.format(int(hour) % 12)
            if int(hour) <= 23:
                self.clock_12[hour_12] = self.today_24[hour]
            elif int(hour) > 23:
                self.clock_12[hour_12] = self.tomorrow_24[hour_12]
            self.next_12.append( self.clock_12[hour_12] )


class Sky(object):
    """
    Handles sky-related actions
    Gets precipitation data, and sends commands to the LedHandler
    
    icons:
    ------
    clear-day               Clear
    clear-night
    cloudy                  Cloudy
    partly-cloudy-day
    partly-cloudy-night
    fog
    snow                    Snow
    sleet
    rain                    Rain
    wind                    Wind
    """
    def __init__(self):
        self.clear_list     = ["sunny", "clear"]
        self.cloudy_list    = ["cloudy", "clouds", "overcast", "fog", "foggy"]
        self.snow_list      = ["snow", "sleet", "flurries"]
        self.rain_list      = ["rain", "drizzle", "mist", "misty"]
        self.thunder_list   = ["thunderstorm", "thunderstorms", "thunder", "lightning"]
        self.wind_list      = ["wind", "windy", "breezy", "gust", "gusts", "gusty"]

        # Static display colors (if desired)
        self.start_up_static        = green
        self.clear_static           = yellow
        self.cloudy_static          = gray
        self.partly_cloudy_static   = light_yellow
        self.snow_static            = white
        self.rain_static            = light_blue
        self.thunder_static         = violet
        self.wind_static            = cyan
        self.unknown_static         = red
        self.cursor_static          = cursor_color

    def determineWeather(self, HOUR, summary, icon):
        # Search summary string for key words
        def wordsInSummary(target_words, summary):
            for target in target_words:
                for word in summary.split():
                    if word.lower() == target.lower():
                        return True
            return False
        
        weather_type = ''
        # search words in summary, and direct to sequencer
        if wordsInSummary(["start_up"], summary):
            weather_type = 'start_up'

        elif wordsInSummary(self.clear_list, summary):
            weather_type = 'clear'

        elif wordsInSummary(self.thunder_list, summary):
            weather_type = 'thunderstorm'

        #elif wordsInSummary(self.rain_list, summary):
        #    if wordsInSummary(["heavy"], summary):
        #        weather_type = 'thunderstorm'
        #    else:
        #        weather_type = 'rain'
        elif wordsInSummary(self.rain_list, summary):
            if summary.lower() in ["heavy rain", "rain"]:
                weather_type = 'thunderstorm'
            else:
                weather_type = 'rain'

        elif wordsInSummary(self.snow_list, summary):
            weather_type = 'snow'

        elif wordsInSummary(self.cloudy_list, summary):
            if wordsInSummary(["partly"], summary):
                weather_type = 'partly cloudy'
            else:
                weather_type = 'cloudy'

        elif wordsInSummary(self.wind_list, summary):
            weather_type = 'wind'

        elif summary == 'cursor':
            weather_type = 'cursor'
        
        # If we encounter a phrase we don't know, check the icon
        # (the icons don't change, but the summaries may change a lot)
        else:
            # Check icons
            if re.search('clear', icon) is not None:
                weather_type = 'clear'
            elif re.search('cloud', icon) is not None:
                RGB_final = self.cloudy(HOUR)
            elif re.search('fog', icon) is not None:
                weather_type = 'cloudy'
            elif re.search('snow', icon) is not None:
                weather_type = 'snow'
            elif re.search('sleet', icon) is not None:
                weather_type = 'snow'
            elif re.search('rain', icon) is not None:
                weather_type = 'rain'
            elif re.search('wind', icon) is not None:
                weather_type = 'wind'
            else:
                weather_type = 'unknown'
    
        return weather_type

    def set_12_Hours(self, display_type):
        next_12 = []
        for hour in Parser.next_12:
            next_12.append(hour)
        current_time = str(datetime.datetime.now())[11:13]
        
        # Run Uniform display show for each weather type
        self._uniformDisplay()

        # update cursor
        cursor_now = LedHandler.LED_status["cursor"]["RGB"]["now"]
        LedHandler.LED_status["cursor"]["RGB"]["dimmed"]     = cursor_now
        LedHandler.LED_status["cursor"]["RGB"]["adjusted"]   = cursor_now

        for i in range(NUMBER_OF_HOURS):
            # Get HOUR, summary, and icon for current LED
            this_hour   = next_12.pop(0)
            HOUR_24     = str(this_hour["time"])[11:13]
            HOUR_12     = '{:02}'.format(int(HOUR_24) % 12)
            summary     = this_hour["summary"]
            icon        = this_hour["icon"]

            # set the hour
            self.setHour(HOUR_12, summary, icon, display_type)
            
            # Reset color values to pure (undimmed, unadjusted) color
            LED_status  = LedHandler.LED_status[HOUR_12]
            RGB_now     = LED_status["RGB"]["now"]
            RGB_now     = LedHandler.capRGB(RGB_now)
            LED_status["RGB"]["dimmed"]     = RGB_now
            LED_status["RGB"]["adjusted"]   = RGB_now

            # Dim each hour after current a little more
            if i == 0:
                #LedHandler.setLEDBrightness(HOUR_12, 0)
                summary     = "cursor"
                icon        = "cursor"
                self.setHour(HOUR_12, summary, icon, display_type)
            else:
                LedHandler.setLEDBrightness(HOUR_12, 0.65**i)
                pass

            LedHandler.updateLED(HOUR_12)

    def setHour(self, HOUR, summary, icon, display_type):
        weather_type = self.determineWeather(HOUR, summary, icon)
        if display_type == 'unique':
            self.setHourUnique(HOUR, weather_type)
        elif display_type == 'uniform':
            self.setHourUniform(HOUR, weather_type)
        elif display_type == 'static':
            self.setHourStatic(HOUR, weather_type)

    def setHourUnique(self, HOUR, weather_type):
        # start_up is a special light show, while starting up
        if weather_type == 'start_up':
            #RGB_final = LedHandler.LED_status["start_up"]["RGB"]["now"]
            RGB_final = self.start_up(HOUR)

        # search words in summary, and direct to sequencer
        elif weather_type == 'clear':
            RGB_final = self.clear(HOUR)

        elif weather_type == 'thunderstorm':
            RGB_final = self.thunderstorm(HOUR)

        elif weather_type == 'rain':
            RGB_final = self.rain(HOUR)

        elif weather_type == 'snow':
            RGB_final = self.snow(HOUR)

        elif weather_type == 'cloudy':
            RGB_final = self.cloudy(HOUR)

        elif weather_type == 'partly cloudy':
            RGB_final = self.partlyCloudy(HOUR)

        elif weather_type == 'wind':
            RGB_final = self.wind(HOUR)
        
        elif weather_type == 'unknown':
            RGB_final = self.unknown(HOUR)
        
        elif weather_type == 'cursor':
            RGB_final = self.cursor(HOUR)
        
        else:
            RGB_final = self.unknown(HOUR)
        
        LedHandler.LED_status[HOUR]["RGB"]["now"]       = RGB_final
        LedHandler.LED_status[HOUR]["RGB"]["dimmed"]    = RGB_final
        LedHandler.LED_status[HOUR]["RGB"]["adjusted"]  = RGB_final
    
    def setHourUniform(self, HOUR, weather_type):
        # start_up is a special light show, while starting up
        if weather_type == 'start_up':
            RGB_final = LedHandler.LED_status["start_up"]["RGB"]["now"]

        # search words in summary, and direct to sequencer
        elif weather_type == 'clear':
            RGB_final = LedHandler.LED_status["clear"]["RGB"]["now"]

        elif weather_type == 'thunderstorm':
            RGB_final = LedHandler.LED_status["thunderstorm"]["RGB"]["now"]

        elif weather_type == 'rain':
            RGB_final = LedHandler.LED_status["rain"]["RGB"]["now"]

        elif weather_type == 'snow':
            RGB_final = LedHandler.LED_status["snow"]["RGB"]["now"]

        elif weather_type == 'cloudy':
            RGB_final = LedHandler.LED_status["cloudy"]["RGB"]["now"]

        elif weather_type == 'partly cloudy':
            RGB_final = LedHandler.LED_status["partly cloudy"]["RGB"]["now"]

        elif weather_type == 'wind':
            RGB_final = LedHandler.LED_status["wind"]["RGB"]["now"]
        
        elif weather_type == 'unknown':
            RGB_final = LedHandler.LED_status["unknown"]["RGB"]["now"]
        
        elif weather_type == 'cursor':
            RGB_final = LedHandler.LED_status["cursor"]["RGB"]["now"]
        
        else:
            RGB_final = LedHandler.LED_status["unknown"]["RGB"]["now"]
        
        LedHandler.LED_status[HOUR]["RGB"]["now"]       = RGB_final
        LedHandler.LED_status[HOUR]["RGB"]["dimmed"]    = RGB_final
        LedHandler.LED_status[HOUR]["RGB"]["adjusted"]  = RGB_final

    def setHourStatic(self, HOUR, weather_type):
        # start_up is a special light show, while starting up
        if weather_type == 'start_up':
            #RGB_final = LedHandler.LED_status["start_up"]["RGB"]["now"]
            RGB_final = self.start_up

        # search words in summary, and direct to sequencer
        elif weather_type == 'clear':
            RGB_final = self.clear_static

        elif weather_type == 'thunderstorm':
            RGB_final = self.thunder_static

        elif weather_type == 'rain':
            RGB_final = self.rain_static

        elif weather_type == 'snow':
            RGB_final = self.snow_static

        elif weather_type == 'cloudy':
            RGB_final = self.cloudy_static

        elif weather_type == 'partly cloudy':
            RGB_final = self.partly_cloudy_static

        elif weather_type == 'wind':
            RGB_final = self.wind_static
        
        elif weather_type == 'unknown':
            RGB_final = self.unknown_static
        
        elif weather_type == 'cursor':
            RGB_final = self.cursor_static
        
        else:
            RGB_final = self.unknown_static
        
        LedHandler.LED_status[HOUR]["RGB"]["now"]       = RGB_final
        LedHandler.LED_status[HOUR]["RGB"]["dimmed"]    = RGB_final
        LedHandler.LED_status[HOUR]["RGB"]["adjusted"]  = RGB_final
    

    #----------  WEATHER HELPER FUNCTIONS  ----------#

    def _uniformDisplay(self):
        self.start_up("start_up")
        self.clear("clear")
        self.cloudy("cloudy")
        self.partlyCloudy("partly cloudy")
        self.rain("rain")
        self.thunderstorm("thunderstorm")
        self.snow("snow")
        self.wind("wind")
        self.unknown("unknown")
        self.cursor("cursor")
        
    def lightningSetup(self, HOUR):
        LED_status = LedHandler.LED_status[HOUR]
        
        # Lists of color choices
        dim_whites  = [tuple(np.divide(white,x)) for x in range(5,10)]
        warm_colors = [red, orange, magenta, violet, yellow, light_yellow]
        cool_colors = [blue, indigo, cyan]
        end_colors  = dim_whites + warm_colors + cool_colors
        
        # Lists of time intervals
        up_intervals    = [5,7,10,15,20]
        down_intervals  = [10,15,20,30]
        up_interval     = choice(up_intervals)
        down_interval   = choice(down_intervals)
        
        # Final definition of lightning variables
        entry_color = LED_status["RGB"]["now"]
        brightest   = white
        dimmest     = choice(end_colors)
        intervals   = (up_interval, down_interval)
        
        # Set into lightning dictionary
        LED_status["lightning"]["status"]       = "start"
        LED_status["lightning"]["entry_color"]  = entry_color
        LED_status["lightning"]["brightest"]    = brightest
        LED_status["lightning"]["dimmest"]      = dimmest
        LED_status["lightning"]["intervals"]    = intervals


    #----------  WEATHER DISPLAY METHODS  ----------#

    def start_up(self, HOUR):
        color1   = black
        color2   = green
        interval = 50

        LedHandler.bounce(HOUR, color1, color2, interval)

    def clear(self, HOUR):
        color = yellow

        LedHandler.LED_status[HOUR]["RGB"]["now"] = color
        
    def partlyCloudy(self, HOUR):
        color1          = yellow
        color2          = light_yellow
        time_constant   = 30
        fluxuation      = 10
        LedHandler.flicker(HOUR, color1, color2, time_constant, fluxuation)
        
    def cloudy(self, HOUR):
        color = gray
        LedHandler.LED_status[HOUR]["RGB"]["now"] = color
        
    def rain(self, HOUR):
        color1          = gray_blue
        color2          = light_blue
        time_constant   = 10
        fluxuation      = 5

        LedHandler.flicker(HOUR, color1, color2, time_constant, fluxuation)

    def thunderstorm(self, HOUR):
        LED_status = LedHandler.LED_status[HOUR]
        
        # If it is currently in a lightning bolt, keep going (with current values)
        if LED_status["lightning"]["status"] in ("start",True):
            RGB_final = LedHandler.lightning(HOUR)
    
            if randint(1, 80) == 1:
                LED_status["lightning"]["status"] = "start"
                RGB_now = LED_status["RGB"]["now"]
                LED_status["lightning"]["entry_color"] = RGB_now
                RGB_final = LedHandler.lightning(HOUR)
        
        # RANDOM LIGHTNING STRIKE
        elif randint(1, 100) == 1:
            self.lightningSetup(HOUR)
            RGB_final = LedHandler.lightning(HOUR)
    
        # Otherwise, bounce / flicker
        else:
            interval    = 20
            fluxuation  = 7
            RGB_final   = LedHandler.bounce(HOUR, dark_blue, indigo, interval)
            #RGB_final   = LedHandler.flicker(HOUR, violet, indigo, interval, fluxuation)
        
    def snow(self, HOUR):
        color1          = gray
        color2          = light_gray
        time_constant   = 6
        fluxuation      = 4

        LedHandler.flicker(HOUR, color1, color2, time_constant, fluxuation)

    def wind(self, HOUR):
        color           = green
        LedHandler.LED_status[HOUR]["RGB"]["now"] = color

    def unknown(self, HOUR):
        color           = orange
        LedHandler.LED_status[HOUR]["RGB"]["now"] = color

    def cursor(self, HOUR):
        color           = cursor_color
        LedHandler.LED_status[HOUR]["RGB"]["now"] = color


class LedHandler(object):
    """
    Controls the LEDs (sends color commands)
    """
    def __init__(self):
        # Memory for certain data about each LED's state
        self.LED_status = {}
        for i in range(NUMBER_OF_HOURS):
            HOUR = '{:02d}'.format(i)
            self.LED_status[HOUR] = {}
            self.LED_status[HOUR]["RGB"] = {}
            self.LED_status[HOUR]["RGB"]["now"]         = (0,0,0)
            self.LED_status[HOUR]["RGB"]["dimmed"]      = (0,0,0)
            self.LED_status[HOUR]["RGB"]["adjusted"]    = (0,0,0)

            self.LED_status[HOUR]["drift"] = {}
            self.LED_status[HOUR]["drift"]["status"]    = False
            self.LED_status[HOUR]["drift"]["direction"] = (0,0,0)

            self.LED_status[HOUR]["lightning"] = {}
            self.LED_status[HOUR]["lightning"]["status"]        = False
            self.LED_status[HOUR]["lightning"]["entry_color"]   = (0,0,0)
            self.LED_status[HOUR]["lightning"]["brightest"]     = (0,0,0)
            self.LED_status[HOUR]["lightning"]["dimmest"]       = (0,0,0)
            self.LED_status[HOUR]["lightning"]["intervals"]     = [1,1]

        # Memory for uniform shows
        self.LED_status["start_up"]         = deepcopy(self.LED_status["00"])
        self.LED_status["clear"]            = deepcopy(self.LED_status["00"])
        self.LED_status["cloudy"]           = deepcopy(self.LED_status["00"])
        self.LED_status["partly cloudy"]    = deepcopy(self.LED_status["00"])
        self.LED_status["snow"]             = deepcopy(self.LED_status["00"])
        self.LED_status["rain"]             = deepcopy(self.LED_status["00"])
        self.LED_status["thunderstorm"]     = deepcopy(self.LED_status["00"])
        self.LED_status["wind"]             = deepcopy(self.LED_status["00"])
        self.LED_status["unknown"]          = deepcopy(self.LED_status["00"])
        self.LED_status["cursor"]           = deepcopy(self.LED_status["00"])

        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel( LED_COUNT, LED_PIN, LED_FREQ_HZ,
                                        LED_DMA, LED_INVERT )
        # Intialize the library (must be called once before other functions).
        self.strip.begin()


    #----------  CONVENIENCE FUNCTIONS  ----------#

    def _dRGB(self, color1, color2):
        R1, G1, B1 = color1
        R2, G2, B2 = color2
        dR = R2-R1
        dG = G2-G1
        dB = B2-B1
        return (dR, dG, dB)

    def _dRGB_dt(self, color1, color2, dt):
        (dR, dG, dB) = self._dRGB(color1, color2)

        # get direction of dC (since negative numbers can otherwise be offset by -1)
        if dR == 0:
            dir_dR = 1
        else:
            dir_dR = (dR/abs(dR))
        if dG == 0:
            dir_dG = 1
        else:
            dir_dG = (dG/abs(dG))
        if dB == 0:
            dir_dB = 1
        else:
            dir_dB = (dB/abs(dB))

        dR_dt = (abs(dR) / dt) * dir_dR
        dG_dt = (abs(dG) / dt) * dir_dG
        dB_dt = (abs(dB) / dt) * dir_dB
        return (dR_dt, dG_dt, dB_dt)
    
    def capRGB(self, color):
        # Make sure (R, G, B) values are int's from 0-255
        RGB = []
        for i in color:
            if i < 0:
                x = 0
            elif i > 255:
                x = 255
            else:
                x = i
            RGB.append( int(x) )
        R, G, B = RGB
        return (R,G,B)

    def dim(self, color, decimal):
        RGB_dimmed_floats = tuple(np.multiply(color, decimal))
        r, g, b = RGB_dimmed_floats
        RGB_dimmed = (int(r), int(g), int(b))
        return RGB_dimmed


    #----------  TERMINAL PRINTING  ----------#

    def terminalPrint(self, HOUR, color):
        current_hour = str(datetime.datetime.now())[11:13]
        # If it's morning (am)
        if int(current_hour) < 12:
            if int(HOUR) < int(current_hour) % 12:
                ampm = "pm"
            else:
                ampm = "am"
        # If it's afternoon (pm)
        elif int(current_hour) >= 12:
            if int(HOUR) < int(current_hour) % 12:
                ampm = "am"
            else:
                ampm = "pm"
        # Make single digits nice, and 0:00 = 12:00
        if int(HOUR) < 10:
            HOUR = HOUR[1]
        if int(HOUR) == 0:
            HOUR = "12"
        
        print colored('  {}{} '.format(HOUR, ampm), color),

    def terminalRGB(self, HOUR, color):
        R = color[0]
        G = color[1]
        B = color[2]
        print colored('HOUR -- {}:00'.format(HOUR), "white")
        print colored('\t{:<3} {}{}'.format(R, (" " * (int(R)/5)), "|"), "red")
        print colored('\t{:<3} {}{}'.format(G, (" " * (int(G)/5)), "|"), "green")
        print colored('\t{:<3} {}{}'.format(B, (" " * (int(B)/5)), "|"), "blue")
        print
        print_color('         ', bg=rgb(R/43, G/43, B/43))  
        print_color('         ', bg=rgb(R/43, G/43, B/43))  
        print_color('         ', bg=rgb(R/43, G/43, B/43))  
        print
        return
    
    def terminalClock(self):
        global circle
        current_time = int(str(datetime.datetime.now())[11:13])%12
        current_hour = '{:02d}'.format(current_time)
        c = LedHandler.LED_status
        divisor = 50
        
        c0r,  c0g,  c0b  = tuple(np.divide(c["00"]["RGB"]["dimmed"], divisor))
        c1r,  c1g,  c1b  = tuple(np.divide(c["01"]["RGB"]["dimmed"], divisor))
        c2r,  c2g,  c2b  = tuple(np.divide(c["02"]["RGB"]["dimmed"], divisor))
        c3r,  c3g,  c3b  = tuple(np.divide(c["03"]["RGB"]["dimmed"], divisor))
        c4r,  c4g,  c4b  = tuple(np.divide(c["04"]["RGB"]["dimmed"], divisor))
        c5r,  c5g,  c5b  = tuple(np.divide(c["05"]["RGB"]["dimmed"], divisor))
        c6r,  c6g,  c6b  = tuple(np.divide(c["06"]["RGB"]["dimmed"], divisor))
        c7r,  c7g,  c7b  = tuple(np.divide(c["07"]["RGB"]["dimmed"], divisor))
        c8r,  c8g,  c8b  = tuple(np.divide(c["08"]["RGB"]["dimmed"], divisor))
        c9r,  c9g,  c9b  = tuple(np.divide(c["09"]["RGB"]["dimmed"], divisor))
        c10r, c10g, c10b = tuple(np.divide(c["10"]["RGB"]["dimmed"], divisor))
        c11r, c11g, c11b = tuple(np.divide(c["11"]["RGB"]["dimmed"], divisor))
        #c12r, c12g, c12b = tuple(np.divide(c[current_hour]["RGB"]["dimmed"], divisor))
        c12r, c12g, c12b = tuple(np.divide(c["cursor"]["RGB"]["dimmed"], divisor))
        
        clock = '\n'+\
        '        {}        \n'  .format(format_color(circle, fg=rgb(c0r, c0g, c0b)))    +\
        '   {}         {}   \n' .format(format_color(circle, fg=rgb(c11r, c11g, c11b)),
                                        format_color(circle, fg=rgb(c1r, c1g, c1b)))    +\
        ' {}             {} \n' .format(format_color(circle, fg=rgb(c10r, c10g, c10b)),
                                        format_color(circle, fg=rgb(c2r, c2g, c2b)))    +\
        '                 \n'+\
        '{}       {}       {}\n'.format(format_color(circle, fg=rgb(c9r, c9g, c9b)),
                                        format_color(circle, fg=rgb(c12r, c12g, c12b)),
                                        format_color(circle, fg=rgb(c3r, c3g, c3b)))    +\
        '                 \n'+\
        ' {}             {} \n' .format(format_color(circle, fg=rgb(c8r, c8g, c8b)),
                                        format_color(circle, fg=rgb(c4r, c4g, c4b)))    +\
        '   {}         {}   \n' .format(format_color(circle, fg=rgb(c7r, c7g, c7b)),
                                        format_color(circle, fg=rgb(c5r, c5g, c5b)))    +\
        '        {}        '    .format(format_color(circle, fg=rgb(c6r, c6g, c6b)))
        #.format(format_color(circle, fg=rgb(c0r, c0g, c0b)),
        #        format_color(circle, fg=rgb(c1r, c1g, c1b)),
        #        format_color(circle, fg=rgb(c2r, c2g, c2b)),
        #        format_color(circle, fg=rgb(c3r, c3g, c3b)),
        #        format_color(circle, fg=rgb(c4r, c4g, c4b)),
        #        format_color(circle, fg=rgb(c5r, c5g, c5b)),
        #        format_color(circle, fg=rgb(c6r, c6g, c6b)),
        #        format_color(circle, fg=rgb(c7r, c7g, c7b)),
        #        format_color(circle, fg=rgb(c8r, c8g, c8b)),
        #        format_color(circle, fg=rgb(c9r, c9g, c9b)),
        #        format_color(circle, fg=rgb(c10r, c10g, c10b)),
        #        format_color(circle, fg=rgb(c11r, c11g, c11b)),
        #        format_color(circle, fg=rgb(c12r, c12g, c12b)))

        print clock


    #----------  SPECIFIC LED  ----------#

    def getColor(self, HOUR):
        led = self.strip
        color = led.getPixelColor(HOUR)
        self.LED_status[HOUR]["RGB"]["now"] = color
        return color

    def setColor(self, HOUR, color):
        capRGB = self.capRGB(color)
        R, G, B = capRGB
        self.setColorRGB(HOUR, R, G, B)

    def setColorRGB(self, HOUR, R, G, B):
        step          = (LED_COUNT / ACTIVE_LEDS)
        LEDs_per_step = (LED_COUNT / 12)
        n             = int(HOUR) * LEDs_per_step

        # set pixel(s)
        self.strip.setPixelColorRGB(n, G, R, B)
        if step == 1:
            self.strip.setPixelColorRGB(n + 1, G, R, B)
        self.strip.show()
    
    def setLEDBrightness(self, HOUR, brightness):
        RGB_now = self.LED_status[HOUR]["RGB"]["now"]
        RGB_dimmed = self.dim(RGB_now, brightness)
        self.LED_status[HOUR]["RGB"]["dimmed"]   = RGB_dimmed
        self.LED_status[HOUR]["RGB"]["adjusted"] = RGB_dimmed
        return RGB_dimmed

    def setClockBrightness(self, brightness):
        led = self.strip
        led.setBrightness(brightness)

    def updateLED(self, HOUR):
        RGB_now      = self.LED_status[HOUR]["RGB"]["now"]
        RGB_dimmed   = self.LED_status[HOUR]["RGB"]["dimmed"]
        RGB_adjusted = self.LED_status[HOUR]["RGB"]["adjusted"]
        
        #color = RGB_dimmed
        color = RGB_adjusted
        self.setColor(HOUR, color)
    

    #----------  COMPLEX METHODS  ----------#
    def turn_off_all_LEDs(self):
        for i in range(LED_COUNT):
            self.setColorRGB(i, 0,0,0)

    def start_up(self, start_up_time, latency):
        for item in Parser.next_12:
            item["summary"] = "start_up"

        start = time.time()
        while time.time() - start  < start_up_time:
            Sky.set_12_Hours("uniform")
            LedHandler.strip.show()
            time.sleep(latency)

    def drift(self, HOUR, color1, color2, interval):
        RGB_now = self.LED_status[HOUR]["RGB"]["now"]
        self.LED_status[HOUR]["drift"]["direction"] = color2
        self.LED_status[HOUR]["drift"]["status"] = True

        # Drift initially, before checking end conditions
        dRGB_dt = self._dRGB_dt(color1, color2, interval)
        RGB_final = tuple(np.add(RGB_now, dRGB_dt))
        self.LED_status[HOUR]["RGB"]["now"] = RGB_final
        self.LED_status[HOUR]["drift"]["status"] = True

        #-------------------------------------------------------------------------------
        #             CHECK THINGS THAT CAN CAUSE A STALL IN DRIFTING
        #-------------------------------------------------------------------------------
        # Check if current color is trying to drift to outside of range (0-255)
        if filter(lambda x: x<0 or x>255, RGB_final):
            self.LED_status[HOUR]["drift"]["status"] = False
            return RGB_final
        # Check if current color can't drift because of the interval
        if dRGB_dt == (0,0,0):
            self.LED_status[HOUR]["drift"]["status"] = False
            return RGB_final
        #-------------------------------------------------------------------------------

        # Check if current color is outside of drift range
        dRGB1   = sum(np.abs(self._dRGB(color1, RGB_now)))      # d(now-to-1)
        d12     = sum(np.abs(self._dRGB(color1, color2)))       # d(1-to-2)
        dRGB2   = sum(np.abs(self._dRGB(color2, RGB_now)))      # d(now-to-2)
        # if RGB has passed color2, set RGB_now to color2 and stop drifting
        if dRGB1 >= d12:
            RGB_final = color2
            self.LED_status[HOUR]["RGB"]["now"] = RGB_final
            self.LED_status[HOUR]["drift"]["status"] = False
        # if RGB is outside of color1, set RGB_now to color1 and drift
        elif dRGB2 > d12:
            RGB_final = color1
            self.LED_status[HOUR]["RGB"]["now"] = RGB_final
            self.LED_status[HOUR]["drift"]["status"] = True

        return RGB_final
    
    def bounce(self, HOUR, color1, color2, interval):
        RGB_now     = self.LED_status[HOUR]["RGB"]["now"]
        direction   = self.LED_status[HOUR]["drift"]["direction"]
        status      = self.LED_status[HOUR]["drift"]["status"]
        
        if direction == color2:
            if status == True:
                self.drift(HOUR, color1, color2, interval)
            else:
                self.LED_status[HOUR]["drift"]["status"]    = True
                self.LED_status[HOUR]["drift"]["direction"] = tuple(color1)
                self.drift(HOUR, color2, color1, interval)
        
        elif direction == color1:
            if status == True:
                self.drift(HOUR, color2, color1, interval)
            else:
                self.LED_status[HOUR]["drift"]["status"]    = True
                self.LED_status[HOUR]["drift"]["direction"] = tuple(color2)
                self.drift(HOUR, color1, color2, interval)

        else:
            self.LED_status[HOUR]["RGB"]["now"]         = tuple(color1)
            self.LED_status[HOUR]["drift"]["status"]    = True
            self.LED_status[HOUR]["drift"]["direction"] = tuple(color2)
            self.bounce(HOUR, color1, color2, interval)

        RGB_final = self.LED_status[HOUR]["RGB"]["now"]
        return RGB_final

    def flicker(self, HOUR, color1, color2, time_constant, fluxuation):
        RGB_now = self.LED_status[HOUR]["RGB"]["now"]
        lower_time_const = time_constant - fluxuation
        upper_time_const = time_constant + fluxuation
        interval = 0
        while interval == 0:
            interval = randint(lower_time_const, upper_time_const)

        RGB_final = self.bounce(HOUR, color1, color2, interval)

        self.LED_status[HOUR]["RGB"]["now"] = RGB_final
        return RGB_final

    def thunderBolt(self, HOUR, entry_color, brightest, dimmest, intervals):
        LED_status      = self.LED_status[HOUR]
        RGB_now         = LED_status["RGB"]["now"]
        up_interval     = intervals[0]      # Faster
        down_interval   = intervals[1]  # Slower
        drift_status    = LED_status["drift"]["status"]
    
        # Initialize thunder bolt
        if LED_status["lightning"]["status"] == "start":
            LED_status["lightning"]["status"] = True
            LED_status["drift"]["direction"] = brightest
            LED_status["RGB"]["now"] = entry_color
            RGB_final = entry_color
            return RGB_final

        # If getting bright, drift brighter
        if tuple(LED_status["drift"]["direction"]) == tuple(brightest):
            if LED_status["drift"]["status"] == True:
                RGB_final = self.drift(HOUR, entry_color, brightest, up_interval)
            else:
                LED_status["drift"]["direction"] = dimmest
                LED_status["drift"]["status"] = True
                RGB_final = brightest
                #RGB_final = self.drift(HOUR, brightest, dimmest, up_interval)

        # If getting dimmer, drift dimmer
        elif tuple(LED_status["drift"]["direction"]) == tuple(dimmest):

            # (randomly can do multiple bolts in a single strike)
            if randint(1,20) == 1:
                LED_status["lightning"]["status"] = "start"
                entry_color = LED_status["RGB"]["now"]
                RGB_final = self.thunderBolt(HOUR, entry_color, brightest, dimmest, intervals)

            # drift dimmer  
            if LED_status["drift"]["status"] == True:
                RGB_final = self.drift(HOUR, brightest, dimmest, down_interval)
            else:
                LED_status["lightning"]["status"] = False
                LED_status["drift"]["status"] == True
                RGB_final = self.drift(HOUR, brightest, dimmest, down_interval)

        else:
            RGB_final = LED_status["RGB"]["now"]

        LED_status["RGB"]["now"] = RGB_final
        return RGB_final

    def lightning(self, HOUR):
        LED_status = self.LED_status[HOUR]

        status      = LED_status["lightning"]["status"]
        entry_color = LED_status["lightning"]["entry_color"]
        brightest   = LED_status["lightning"]["brightest"]
        dimmest     = LED_status["lightning"]["dimmest"]
        intervals   = LED_status["lightning"]["intervals"]

        if status in (True, "start"):
            RGB_final = self.thunderBolt(HOUR, entry_color, brightest, dimmest, intervals)
            LED_status["RGB"]["now"] = RGB_final
            return RGB_final
        else:
            return False


class Temp(object):
    """
    Handles temperature-related actions
    Gets temperature data, and sends commands to the MotorHandler
    """
    def __init__(self, minTemp, maxTemp):
        self.minTemp = minTemp
        self.maxTemp = maxTemp
        self.high = 100
        self.low = 0
        self.current =50
    
    def getHighLow(self, time_range):
        # Get high and low temperatures for a given time_range
        hottest_hour = max(time_range, key=lambda key: time_range[key]["temp"])
        coldest_hour = min(time_range, key=lambda key: time_range[key]["temp"])
        self.high = time_range[ str(hottest_hour) ]["temp"]
        self.low = time_range[ str(coldest_hour) ]["temp"]

    def getCurrentTemp(self):
        #current_time = datetime.datetime.now()
        #current_hour = str(current_time)[11:13]
        #self.current = Parser.today_24[current_hour]["temp"]
        self.current = Parser.current["temp"]

    def setHands(self, time_range):
        # Update temperatures
        self.getCurrentTemp()
        self.getHighLow(time_range)
        
        Low = "cyan"
        High = "red"
        Current = "yellow"

        highest = max(self.high, self.current)
        lowest = min(self.current, self.low)

        if highest == self.high:
            HIGHEST = (High, self.high)
            MIDDLE = (Current, self.current)
        else:
            HIGHEST = (Current, self.current)
            MIDDLE = (High, self.high)
        
        if lowest == self.current:
            LOWEST = (Current, self.current)
            MIDDLE = (Low, self.low)
        else:
            LOWEST = (Low, self.low)

        # Set all 3 hands
        MotorHandler.setHandPosition( HIGHEST[0], HIGHEST[1] )
        MotorHandler.setHandPosition( MIDDLE[0] , MIDDLE[1]  )
        MotorHandler.setHandPosition( LOWEST[0] , LOWEST[1]  )

        # Set all 3 hands
        #MotorHandler.setHandPosition(High, self.high)
        #MotorHandler.setHandPosition(Current, self.current)
        #MotorHandler.setHandPosition(Low, self.low)


class MotorHandler(object):
    """
    Controls the motors which drive the 3 "hands" which display temperature
    """
    def __init__(self):
        pass

    def setHandPosition(self, HAND, position):
        # Get HAND current position
        # Map motor position to Temperature position
        # Move hand to destination position
    
        # print for debugging
        self.terminalPrint(HAND, position)
    
    def terminalPrint(self, HAND, position):
        print "\r",
        print " " * int(position + 10),
        print colored("|\r", HAND),
    

class UIHandler(object):
    """
    Handles input from any buttons etc. in the interface
    """
    # Hours each unique
    # Hours all uniform
    # dimmer over 12 hours
    # no flashing (static)
    # 12-24 hours later
    # next 60 minutes
    # simple clock
    # shows temperature changes over each hour
    pass


#===============================================================================
#----------------------------------- SETUP -------------------------------------
#===============================================================================
# Instantiate classes
np = Numpy()
Parser = Parser()
Temp = Temp(-20, 120)
MotorHandler = MotorHandler()
Sky = Sky()
LedHandler = LedHandler()

#.................................................
# register interrupt handler
def signal_handler(signum, frame):
    # set all LEDs to black (off)
    LedHandler.turn_off_all_LEDs()
    sys.exit()
signal.signal(signal.SIGINT, signal_handler)
#.................................................


#===============================================================================
#------------------------------------ MAIN -------------------------------------
#===============================================================================
# turn on LEDs right away
start_up_time = 6.5
latency       = 0.01
#LedHandler.start_up(start_up_time, latency)
#print "done with startup LED show"
#time.sleep(1)


for item in Parser.next_12:
    #item["summary"] = "start_up"
    #item["summary"] = "clear"
    #item["summary"] = "cloudy"
    #item["summary"] = "partly cloudy"
    #item["summary"] = "light rain"
    item["summary"] = "thunderstorm"
    #item["summary"] = "snow"
    #item["summary"] = "wind"
    #item["summary"] = "unknown"
    #item["summary"] = "cursor"

while True:
    Sky.set_12_Hours("uniform")
    LedHandler.strip.show()
    time.sleep(latency)
    os.system('clear')
    print json.dumps(LedHandler.LED_status['thunderstorm'], sort_keys=True, indent=4)

#-------------------------------------------------------------------------------
# Get weather data and start displaying
#Parser.parseWeather()

while True:
    # Update weather data
    Parser.parseWeather()

    # show LEDs
    t_a     = time.time()
    period  = 60            # seconds between weather API calls
    latency = 0.01
    while time.time() - t_a < period:
        Sky.set_12_Hours("uniform")
        LedHandler.strip.show()
        time.sleep(latency)
