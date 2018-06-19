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

import datetime
import time
import os
import sys
import re
from random import randint, choice
from termcolor import colored, cprint
from subprocess import check_output


#####  CONSTANTS  #####
api_key = "0bd8f5fb32262aa45c4598c2f1ef5b44"
lat = 39.9936
lng = -105.0897
# exit()
number_of_LEDs = 12

# Refresh rate
# GPIO pins...


#####  CLASSES  #####

class Numpy(object):
    """
    Mimic a few simple numpy methods.
    (Since numpy is very large, and it takes hours to install from scratch.)
    """
    def add(self, lst, x):
        if type(x) == type(0) or type(x) == type(0.0):
            return map(lambda i: float(i)+x, lst)
        else:
            return map(lambda i,j: float(i)+j, lst, x)

    def subtract(self, lst, x):
        if type(x) == type(0) or type(x) == type(0.0):
            return map(lambda i: i-x, lst)
        else:
            return map(lambda i,j: float(i)-j, lst, x)

    def multiply(self, lst, x):
        if type(x) == type(0) or type(x) == type(0.0):
            return map(lambda i: float(i)*x, lst)
        else:
            return map(lambda i,j: float(i)*j, lst, x)

    def divide(self, lst, x):
        if type(x) == type(0) or type(x) == type(0.0):
            return map(lambda i: float(i)/x, lst)
        else:
            return map(lambda i,j: float(i)/j, lst, x)

    def abs(self, lst):
        return map(lambda i: abs(float(i)), lst)


class Parser(object):
    """
    Parses weather data from Dark Sky API
    """
    def __init__(self):
        # (24 hours, today and tomorrow)
        self.today_weather = {}
        self.tomorrow_weather = {}
        
        # (next 12 hours)
        self.clock_12 = {}
        self.next_12 = []

        # Current conditions
        self.current = {}

    def getWeather(self, time_window):
        # Get forecast from Dark Sky API
        forecast = forecastio.load_forecast(api_key, lat, lng, time=time_window)
        self.offset = forecast.offset()
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
            time = hourlyData.time + datetime.timedelta(hours=self.offset)
            hour = "{:02d}".format(time.hour)
            day = str(time.day)
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
        forecast = forecastio.load_forecast(api_key, lat, lng)
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

        # Find weather (0:00 - 23:00, today and tomorrow)
        self.today_weather = self.getWeather(today)
        self.tomorrow_weather = self.getWeather(tomorrow)

        # Parse into 12-hour chunks (0 - 11 O'clock)
        current_time = datetime.datetime.now().hour
        self.clock_12 = {}
        self.next_12 = []
        for i in range(number_of_LEDs):
            hour = '{:02d}'.format(current_time + i)
            hour_12 = '{:02d}'.format(int(hour) % 12)
            if int(hour) <= 23:
                self.clock_12[hour_12] = self.today_weather[hour]
            elif int(hour) > 23:
                self.clock_12[hour_12] = self.tomorrow_weather[hour_12]
            self.next_12.append( self.clock_12[hour_12] )


class Sky(object):
    """
    Handles sky-related actions
    Gets precipitation data, and sends commands to the SkyDisplayer
    
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
        self.cloudy_list    = ["cloudy", "overcast", "fog", "foggy"]
        self.snow_list      = ["snow", "sleet", "flurries"]
        self.rain_list      = ["rain", "drizzle"]
        self.thunder_list   = ["thunderstorm", "thunder"]
        self.wind_list      = ["wind", "windy", "breezy"]
        
    def set_12_Hours(self):
        next_12 = []
        for hour in Parser.next_12:
            next_12.append(hour)
        current_time = str(datetime.datetime.now())[11:13]

        for i in range(number_of_LEDs):
            this_hour = next_12.pop(0)
            HOUR_24 = str(this_hour["time"])[11:13]
            HOUR_12 = '{:02}'.format(int(HOUR_24) % 12)
            summary = this_hour["summary"]
            icon = this_hour["icon"]

            self.setHour(HOUR_12, summary, icon)

    def setHour(self, HOUR, summary, icon):
        # Search summary string for key words
        def wordsInSummary(target_words, summary):
            for target in target_words:
                for word in summary.split():
                    if word.lower() == target.lower():
                        return True
            return False
        
        # search words in summary, and direct to sequencer
        if wordsInSummary(self.clear_list, summary):
            self.clear(HOUR)

        elif wordsInSummary(self.thunder_list, summary):
            self.thunderstorm(HOUR)

        elif wordsInSummary(self.rain_list, summary):
            self.rain(HOUR)

        elif wordsInSummary(self.snow_list, summary):
            self.snow(HOUR)

        elif wordsInSummary(self.cloudy_list, summary):
            self.cloudy(HOUR)

        elif wordsInSummary(self.wind_list, summary):
            self.wind(HOUR)
        
        else:
            # If we encounter a phrase we don't know, check the icon
            # (the icons don't change, but the summaries may change a lot)
            self.unknown(HOUR)
            return
            # Check icons
            if re.search('clear', icon) is not None:
                self.clear(HOUR)
            elif re.search('cloud', icon) is not None:
                self.cloudy(HOUR)
            elif re.search('fog', icon) is not None:
                self.cloudy(HOUR)
            elif re.search('snow', icon) is not None:
                self.snow(HOUR)
            elif re.search('sleet', icon) is not None:
                self.snow(HOUR)
            elif re.search('rain', icon) is not None:
                self.rain(HOUR)
            elif re.search('wind', icon) is not None:
                self.wind(HOUR)
    

    #----------  WEATHER DISPLAY METHODS  ----------#

    def clear(self, HOUR):
        color = "yellow"
        SkyDisplayer.terminalPrint(HOUR, color)
        
    def cloudy(self, HOUR):
        color = "white"
        SkyDisplayer.terminalPrint(HOUR, color)
        
    def rain(self, HOUR):
        color = "cyan"
        SkyDisplayer.terminalPrint(HOUR, color)

    def thunderstorm(self, HOUR):
        color = "blue"
        SkyDisplayer.terminalPrint(HOUR, color)
        
    def snow(self, HOUR):
        color = "white"
        SkyDisplayer.terminalPrint(HOUR, color)

    def wind(self, HOUR):
        color = "magenta"
        SkyDisplayer.terminalPrint(HOUR, color)

    def unknown(self, HOUR):
        color = "grey"
        SkyDisplayer.terminalPrint(HOUR, color)


class SkyDisplayer(object):
    """
    Controls the LEDs (sends color commands)
    """
    def __init__(self):
        pass

    def terminalPrint(self, HOUR, color):
        global hourly_printout
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
        
        #print colored('  {}{} '.format(HOUR, ampm), color),
        hourly_printout += colored('  {}{} '.format(HOUR, ampm), color)


class Temp(object):
    """
    Handles temperature-related actions
    Gets temperature data, and sends commands to the TempDisplayer
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
        TempDisplayer.setHandPosition( HIGHEST[0], HIGHEST[1] )
        TempDisplayer.setHandPosition( MIDDLE[0] , MIDDLE[1]  )
        TempDisplayer.setHandPosition( LOWEST[0] , LOWEST[1]  )

        # Set all 3 hands
        #TempDisplayer.setHandPosition(High, self.high)
        #TempDisplayer.setHandPosition(Current, self.current)
        #TempDisplayer.setHandPosition(Low, self.low)


class TempDisplayer(object):
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
        global end_low, temp_increment, mark
        print "\r",

        # shift over to start at lowest temp (end_low)
        position -= end_low
        
        # print colored tic at position
        lead = int(position + 1)
        tic  = "{tic:>{a}.{a}}\r".format(tic='|', a=lead)
        print colored(tic, HAND),
    

class Terminal(object):
    """
    Handles printing info to the terminal
    """
    def __init__(self):
        self.width  = int(check_output(['tput', 'cols']))
        self.height = int(check_output(['tput', 'lines']))

    def print_line(self, character):
        line = character * self.width
        print line

    def print_temp_range(self):
        global end_low, temp_increment, mark
        mark = 5        # each next temperature label
        end  = mark*3   # temperature margins on each end

        temp_points     = [Temp.high, Temp.current, Temp.low]

        temp_low        = min(temp_points)
        temp_high       = max(temp_points)

        mark_low        = temp_low - (temp_low % mark)
        mark_high       = temp_high - (temp_high % mark) + mark

        end_low         = mark_low - end
        end_high        = mark_high + end

        temp_range      = end_high - end_low
        temp_increment  = 1     #1.0 * temp_range / self.width

        temp_list = [int(end_low + i*mark) for i in range(int(temp_range/mark))]

        for temp in temp_list:

            # set color for temp range
            if temp < 32:
                temp_color = 'white'
            elif temp < 50:
                temp_color = 'cyan'
            elif temp < 80:
                temp_color = 'yellow'
            else:
                temp_color = 'red'

            # print all on same line
            if temp != max(temp_list):
                a = int( (mark-1.0) / (1.0*temp_increment) )
                print colored("{:<{a}.{a}}".format(str(temp), a=a), temp_color),
            # print last number with a newline
            elif temp == max(temp_list):
                print colored("{:.{a}}".format(str(temp), a=a), temp_color)

        return end_low, temp_increment, mark



#####  SETUP  #####

# Instantiate classes
np = Numpy()
Parser = Parser()
Temp = Temp(-20, 120)
TempDisplayer = TempDisplayer()
Sky = Sky()
SkyDisplayer = SkyDisplayer()
Terminal = Terminal()


#####  MAIN  #####

Parser.parseWeather()
today = Parser.today_weather
Temp.getHighLow(today)
Temp.getCurrentTemp()

if len(sys.argv) > 1:
    if sys.argv[1] == "-v":
        # --> (next 12 hours)
        print
        for i in range(12):
            day = Parser.next_12
            time = day[i]["time"]
            hour = str(time)[11:13]
            temp =day[i]["temp"]
            summary = day[i]["summary"]
            print "{}:00  --  {:05.2f}  (degF)\t{}".format(hour, temp, summary)
        
        print "_________________________________________________"
        print
        print colored('HIGH:       {}'.format(Temp.high), 'red')
        print colored('LOW:        {}'.format(Temp.low), 'cyan')
        print colored('Currently:  {} degrees, {}'.format(Parser.current["temp"], Parser.current["summary"]), 'yellow')



Terminal.print_line("_")
print

# print Temperature scale and hands
end_low, temp_increment, mark = Terminal.print_temp_range()
Temp.setHands(today)

# print next 12 hours (colored to conditions)
hourly_printout = ''
print
Terminal.print_line(colored("-", 'white'))
Sky.set_12_Hours()
print "{hours:^{width}}".format(hours=hourly_printout, width=Terminal.width)
Terminal.print_line(colored("-", 'white'))
print 
