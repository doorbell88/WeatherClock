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
import pdb
import pudb

import datetime
import time
import os
import sys
import re
#import numpy as np
from random import randint, choice
from copy import copy, deepcopy
from termcolor import colored, cprint
from term_colors import rgb, print_color, set_color, format_color
"""
from neopixel import *
import wiringpi
# import RPi.GPIO as GPIO ?
# I2C ?
"""


#####  CONSTANTS  #####
api_key = "0bd8f5fb32262aa45c4598c2f1ef5b44"
lat = 40.0150
lng = -105.2705

number_of_LEDs = 12

# Refresh rate
# GPIO pins...

# COLORS
red  			=	(255, 0, 0)
magenta 		=	(255, 0, 255)
orange 			= 	(255, 125, 0)
yellow 			= 	(255, 255, 0)
light_yellow	= 	(200, 200, 100)
green 			=	(0, 255, 0)
blue  			=	(0, 0, 255)
dark_blue		=	(0, 0, 100)
light_blue		=	(120, 150, 255)
gray_blue		=	(70, 70, 190)
cyan  			=	(0, 255, 255)
indigo  		=	(75, 0, 130)
violet 			= 	(148, 0, 211)
white 			= 	(255, 255, 255)
light_gray		= 	(200, 200, 200)
gray 			= 	(80, 80, 80)
black 			= 	(0, 0, 0)






#####  CLASSES  #####

class Numpy(object):
	"""
	Mimic a few simple numpy methods.
	(Since numpy is very large, and it takes hours to install from scratch.)
	"""
	def add(self, lst, x):
		result = []
		for i in range(len(lst)):
			if type(x) == type(0):
				result.append(lst[i] + x)
			else:
				result.append(lst[i] + x[i])
		return result

	def subtract(self, lst, x):
		result = []
		for i in range(len(lst)):
			if type(x) == type(0):
				result.append(lst[i] - x)
			else:
				result.append(lst[i] - x[i])
		return result

	def multiply(self, lst, x):
		result = []
		for i in range(len(lst)):
			if type(x) == type(0):
				result.append(lst[i] * x)
			else:
				result.append(lst[i] * x[i])
		return result

	def divide(self, lst, x):
		result = []
		for i in range(len(lst)):
			if type(x) == type(0):
				result.append(lst[i] / x)
			else:
				result.append(lst[i] / x[i])
		return result

	def abs(self, lst):
		result = []
		for i in list(lst):
			result.append(abs(i))
		return result


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
		self.next_12 = []

		# Current conditions
		self.current = {}

	def getWeather(self, time_window):
		# Get forecast from Dark Sky API
		forecast = forecastio.load_forecast(api_key, lat, lng, time=time_window)
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
					destination_dict[hour] = day1["05"]		#Daylight Savings
				i+=1
			i=7
			while i <= 23:
				hour = '{:02d}'.format(i)
				try:
					destination_dict[hour] = day2[hour]
				except KeyError:
					destination_dict[hour] = day2["22"]		#Daylight Savings
				i+=1
	
		# Parse into 24-hour chunks (0 - 23 hour)
		# (Today)
		parse24(	self.today_24,
					self.yesterday_weather,
					self.today_weather)
		# (Tomorrow)
		parse24(	self.tomorrow_24,
					self.today_weather,
					self.tomorrow_weather)

		# Parse into 12-hour chunks (0 - 11 O'clock)
		current_time = int( str(today)[11:13] )
		self.clock_12 = {}
		self.next_12 = []
		for i in range(number_of_LEDs):
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
	clear-day				Clear
	clear-night
	cloudy					Cloudy
	partly-cloudy-day
	partly-cloudy-night
	fog
	snow					Snow
	sleet
	rain					Rain
	wind					Wind
	"""
	def __init__(self):
		self.clear_list 	= ["sunny", "clear"]
		self.cloudy_list 	= ["cloudy", "clouds", "overcast", "fog", "foggy"]
		self.snow_list 		= ["snow", "sleet", "flurries"]
		self.rain_list 		= ["rain", "drizzle", "mist", "misty"]
		self.thunder_list 	= ["thunderstorm", "thunderstorms", "thunder", "lightning"]
		self.wind_list 		= ["wind", "windy", "breezy", "gust", "gusts", "gusty"]

		# Static display colors (if desired)
		self.clear_static 			= yellow
		self.cloudy_static 			= gray
		self.partly_cloudy_static 	= light_yellow
		self.snow_static 			= white
		self.rain_static 			= light_blue
		self.thunder_static 		= violet
		self.wind_static 			= cyan
		self.unknown_static 		= red

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
		if wordsInSummary(self.clear_list, summary):
			weather_type = 'clear'

		elif wordsInSummary(self.thunder_list, summary):
			weather_type = 'thunderstorm'

		elif wordsInSummary(self.rain_list, summary):
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
		
		else:
			# If we encounter a phrase we don't know, check the icon
			# (the icons don't change, but the summaries may change a lot)
			#self.unknown(HOUR)
			#return
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

		for i in range(number_of_LEDs):
			# Get HOUR, summary, and icon for current LED
			this_hour = next_12.pop(0)
			HOUR_24 = str(this_hour["time"])[11:13]
			HOUR_12 = '{:02}'.format(int(HOUR_24) % 12)
			summary = this_hour["summary"]
			icon = this_hour["icon"]

			self.setHour(HOUR_12, summary, icon, display_type)
			
			# Reset color values to pure (undimmed, unadjusted) color
			LED_status = LedHandler.LED_status[HOUR_12]
			RGB_now = LED_status["RGB"]["now"]
			RGB_now = LedHandler.capRGB(RGB_now)
			LED_status["RGB"]["dimmed"] 	= RGB_now
			LED_status["RGB"]["adjusted"] 	= RGB_now

			# Dim each hour after current a little more
			if i == 0:
				LedHandler.setLEDBrightness(HOUR_12, 0)
			#LedHandler.setLEDBrightness(HOUR_12, 1.00**i)

			"""LedHandler.strip.show()"""

	def setHour(self, HOUR, summary, icon, display_type):
		weather_type = self.determineWeather(HOUR, summary, icon)
		if display_type == 'unique':
			self.setHourUnique(HOUR, weather_type)
		elif display_type == 'uniform':
			self.setHourUniform(HOUR, weather_type)
		elif display_type == 'static':
			self.setHourStatic(HOUR, weather_type)

		"""LedHandler.updateLED(HOUR)"""

	def setHourUnique(self, HOUR, weather_type):
		# search words in summary, and direct to sequencer
		if weather_type == 'clear':
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
		
		else:
			RGB_final = self.unknown(HOUR)
		
		LedHandler.LED_status[HOUR]["RGB"]["now"] 		= RGB_final
		LedHandler.LED_status[HOUR]["RGB"]["dimmed"] 	= RGB_final
		LedHandler.LED_status[HOUR]["RGB"]["adjusted"] 	= RGB_final
	
	def setHourUniform(self, HOUR, weather_type):
		# search words in summary, and direct to sequencer
		if weather_type == 'clear':
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
		
		else:
			RGB_final = LedHandler.LED_status["unknown"]["RGB"]["now"]
		
		LedHandler.LED_status[HOUR]["RGB"]["now"] 		= RGB_final
		LedHandler.LED_status[HOUR]["RGB"]["dimmed"] 	= RGB_final
		LedHandler.LED_status[HOUR]["RGB"]["adjusted"] 	= RGB_final

	def setHourStatic(self, HOUR, weather_type):
		# search words in summary, and direct to sequencer
		if weather_type == 'clear':
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
		
		else:
			RGB_final = self.unknown_static
		
		LedHandler.LED_status[HOUR]["RGB"]["now"] 		= RGB_final
		LedHandler.LED_status[HOUR]["RGB"]["dimmed"] 	= RGB_final
		LedHandler.LED_status[HOUR]["RGB"]["adjusted"] 	= RGB_final
	

	#----------  WEATHER HELPER FUNCTIONS  ----------#

	def _uniformDisplay(self):
		self.clear("clear")
		self.cloudy("cloudy")
		self.partlyCloudy("partly cloudy")
		self.rain("rain")
		self.thunderstorm("thunderstorm")
		self.snow("snow")
		self.wind("wind")
		self.unknown("unknown")
		
	def lightningSetup(self, HOUR):
		LED_status = LedHandler.LED_status[HOUR]
		
		# Lists of color choices
		dim_whites 	= [tuple(np.divide(white,x)) for x in range(2,8)]
		warm_colors = [red, magenta, violet, yellow, light_yellow]
		cool_colors = [blue, indigo, cyan]
		end_colors 	= dim_whites + warm_colors + cool_colors
		
		# Lists of time intervals
		up_intervals 	= [5,7,10]
		down_intervals 	= [10,15,20]
		up_interval 	= choice(up_intervals)
		down_interval 	= choice(down_intervals)
		
		# Final definition of lightning variables
		entry_color = LED_status["RGB"]["now"]
		brightest 	= white
		dimmest 	= choice(end_colors)
		intervals 	= (up_interval, down_interval)
		
		# Set into lightning dictionary
		LED_status["lightning"]["status"]       = "start"
		LED_status["lightning"]["entry_color"]  = entry_color
		LED_status["lightning"]["brightest"]    = brightest
		LED_status["lightning"]["dimmest"]      = dimmest
		LED_status["lightning"]["intervals"]    = intervals


	#----------  WEATHER DISPLAY METHODS  ----------#

	def clear(self, HOUR):
		color = yellow
		LedHandler.LED_status[HOUR]["RGB"]["now"] = color
		return

		color = "yellow"
		LedHandler.terminalPrint(HOUR, color)
		
	def partlyCloudy(self, HOUR):
		color1 = yellow
		color2 = light_yellow
		time_constant = 10
		fluxuation = 10
		LedHandler.flicker(HOUR, color1, color2, time_constant, fluxuation)
		return

		color = light_yellow
		LedHandler.LED_status[HOUR]["RGB"]["now"] = color
		return

		color = "white"
		LedHandler.terminalPrint(HOUR, color)
		
	def cloudy(self, HOUR):
		color = gray
		LedHandler.LED_status[HOUR]["RGB"]["now"] = color
		return

		color = "white"
		LedHandler.terminalPrint(HOUR, color)
		
	def rain(self, HOUR):
		color1 = gray_blue
		color2 = light_blue

		color1 = (120, 150, 255)
		color2 = (110, 140, 255)
		time_constant = 1
		fluxuation = 1

		LedHandler.flicker(HOUR, color1, color2, time_constant, fluxuation)
		return

		color = "cyan"
		LedHandler.terminalPrint(HOUR, color)

	def thunderstorm(self, HOUR):
		LED_status = LedHandler.LED_status[HOUR]
		
		# If it is currently in a lightning bolt, keep going (with current values)
		#if LED_status["lightning"]["status"] == True:
		if LED_status["lightning"]["status"] in ("start",True):
			RGB_final = LedHandler.lightning(HOUR)
			#print "LIGHTNING"
	
			if randint(1, 30) == 1:
				LED_status["lightning"]["status"] = "start"
				#RGB_now = LED_status["RGB"]["now"]
				#LED_status["lightning"]["entry_color"] = RGB_now
				RGB_final = LedHandler.lightning(HOUR)
		
		# RANDOM LIGHTNING STRIKE
		elif randint(1, 70) == 1:
			self.lightningSetup(HOUR)
			RGB_final = LedHandler.lightning(HOUR)
	
		# Otherwise, bounce / flicker
		else:
			interval = 80
			fluxuation = 10
			#RGB_final = LedHandler.bounce(HOUR, dark_blue, indigo, interval)
			#print "bounce"
			RGB_final = LedHandler.flicker(HOUR, violet, indigo, interval, fluxuation)
		return

		color = "blue"
		LedHandler.terminalPrint(HOUR, color)
		
	def snow(self, HOUR):
		color1 = white
		color2 = light_gray
		time_constant = 1
		fluxuation = 1

		#LedHandler.LED_status[HOUR]["RGB"]["now"] = color1
		LedHandler.flicker(HOUR, color1, color2, time_constant, fluxuation)
		return

		color = "white"
		LedHandler.terminalPrint(HOUR, color)

	def wind(self, HOUR):
		color = cyan
		LedHandler.LED_status[HOUR]["RGB"]["now"] = color
		return

		color = "magenta"
		LedHandler.terminalPrint(HOUR, color)

	def unknown(self, HOUR):
		color = red
		LedHandler.LED_status[HOUR]["RGB"]["now"] = color
		return

		color = "grey"
		LedHandler.terminalPrint(HOUR, color)


class LedHandler(object):
	"""
	Controls the LEDs (sends color commands)
	"""
	def __init__(self):
		# Memory for certain data about each LED's state
		self.LED_status = {}
		for i in range(number_of_LEDs):
			HOUR = '{:02d}'.format(i)
			self.LED_status[HOUR] = {}
			self.LED_status[HOUR]["RGB"] = {}
			self.LED_status[HOUR]["RGB"]["now"]			= (0,0,0)
			self.LED_status[HOUR]["RGB"]["dimmed"] 		= (0,0,0)
			self.LED_status[HOUR]["RGB"]["adjusted"] 	= (0,0,0)

			self.LED_status[HOUR]["drift"] = {}
			self.LED_status[HOUR]["drift"]["status"] 	= False
			self.LED_status[HOUR]["drift"]["direction"] = (0,0,0)

			self.LED_status[HOUR]["lightning"] = {}
			self.LED_status[HOUR]["lightning"]["status"] 		= False
			self.LED_status[HOUR]["lightning"]["entry_color"] 	= (0,0,0)
			self.LED_status[HOUR]["lightning"]["brightest"] 	= (0,0,0)
			self.LED_status[HOUR]["lightning"]["dimmest"] 		= (0,0,0)
			self.LED_status[HOUR]["lightning"]["intervals"] 	= [1,1]

		# Memory for uniform shows
		self.LED_status["clear"] 			= deepcopy(self.LED_status["00"])
		self.LED_status["cloudy"] 			= deepcopy(self.LED_status["00"])
		self.LED_status["partly cloudy"]	= deepcopy(self.LED_status["00"])
		self.LED_status["snow"] 			= deepcopy(self.LED_status["00"])
		self.LED_status["rain"] 			= deepcopy(self.LED_status["00"])
		self.LED_status["thunderstorm"] 	= deepcopy(self.LED_status["00"])
		self.LED_status["wind"] 			= deepcopy(self.LED_status["00"])
		self.LED_status["unknown"] 			= deepcopy(self.LED_status["00"])

		LED_COUNT = 12			# Number of LED NeoPixels
		LED_PIN = 18			# GPIO pin (must support PWM)
		LED_FREQ_HZ = 800000  	# LED signal frequency (usually 800khz)
		LED_DMA = 5				# DMA channel to use for generating signal
		LED_INVERT = False		# True when using NPN transistor level shift
		"""	
		# Create NeoPixel object with appropriate configuration.
		self.strip = Adafruit_NeoPixel(	LED_COUNT, LED_PIN, LED_FREQ_HZ,
										LED_DMA, LED_INVERT)
		# Intialize the library (must be called once before other functions).
		self.strip.begin()
		"""


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
		
		clock = '\n\
		        {00}          \n\
		   {11}        {01}   \n\
		 {10}            {02} \n\
		                      \n\
		{09}              {03}\n\
		                      \n\
		 {08}            {04} \n\
		   {07}        {05}   \n\
		        {06}          \n'\
		.format(format_color('  ', bg=rgb(c0r, c0g, c0b)),
				format_color('  ', bg=rgb(c1r, c1g, c1b)),
				format_color('  ', bg=rgb(c2r, c2g, c2b)),
				format_color('  ', bg=rgb(c3r, c3g, c3b)),
				format_color('  ', bg=rgb(c4r, c4g, c4b)),
				format_color('  ', bg=rgb(c5r, c5g, c5b)),
				format_color('  ', bg=rgb(c6r, c6g, c6b)),
				format_color('  ', bg=rgb(c7r, c7g, c7b)),
				format_color('  ', bg=rgb(c8r, c8g, c8b)),
				format_color('  ', bg=rgb(c9r, c9g, c9b)),
				format_color('  ', bg=rgb(c10r, c10g, c10b)),
				format_color('  ', bg=rgb(c11r, c11g, c11b)))

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
		led = self.strip
		led.setPixelColorRGB(HOUR, G, R, B)
		led.show()
	
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
		RGB_now = self.LED_status[HOUR]["RGB"]["now"]
		RGB_dimmed = self.LED_status[HOUR]["RGB"]["dimmed"]
		RGB_adjusted = self.LED_status[HOUR]["RGB"]["adjusted"]
		
		color = RGB_adjusted
		self.setColor(HOUR, color)
	

	#----------  COMPLEX METHODS  ----------#

	def drift(self, HOUR, color1, color2, interval):
		RGB_now = self.LED_status[HOUR]["RGB"]["now"]
		self.LED_status[HOUR]["drift"]["direction"] = color2
		self.LED_status[HOUR]["drift"]["status"] = True

		# Drift initially, before checking end conditions
		dRGB_dt = self._dRGB_dt(color1, color2, interval)
		RGB_final = tuple(np.add(RGB_now, dRGB_dt))
		self.LED_status[HOUR]["RGB"]["now"] = RGB_final
		self.LED_status[HOUR]["drift"]["status"] = True

		# Check if current color is outside of drift range
		dRGB1 	= sum(np.abs(self._dRGB(color1, RGB_now)))		# d(now-to-2)
		d12 	= sum(np.abs(self._dRGB(color1, color2)))		# d(1-to-2)
		dRGB2 	= sum(np.abs(self._dRGB(color2, RGB_now)))		# d(now-to-2)
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
		RGB_now 	= self.LED_status[HOUR]["RGB"]["now"]
		direction 	= self.LED_status[HOUR]["drift"]["direction"]
		status 		= self.LED_status[HOUR]["drift"]["status"]
		
		if direction == color2:
			if status == True:
				self.drift(HOUR, color1, color2, interval)
			else:
				self.LED_status[HOUR]["drift"]["status"] 	= True
				self.LED_status[HOUR]["drift"]["direction"] = tuple(color1)
				self.drift(HOUR, color2, color1, interval)
		
		elif direction == color1:
			if status == True:
				self.drift(HOUR, color2, color1, interval)
			else:
				self.LED_status[HOUR]["drift"]["status"] 	= True
				self.LED_status[HOUR]["drift"]["direction"] = tuple(color2)
				self.drift(HOUR, color1, color2, interval)

		else:
			self.LED_status[HOUR]["RGB"]["now"] 		= tuple(color1)
			self.LED_status[HOUR]["drift"]["status"] 	= True
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
		LED_status 		= self.LED_status[HOUR]
		RGB_now 		= LED_status["RGB"]["now"]
		up_interval 	= intervals[0]		# Faster
		down_interval 	= intervals[1]	# Slower
		drift_status 	= LED_status["drift"]["status"]
	
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

		# If getting dimmer, drift dimmer
		elif tuple(LED_status["drift"]["direction"]) == tuple(dimmest):

			# (randomly can do a multiple bolts in a single strike
			if randint(1,20) == 1:
				LED_status["lightning"]["status"] = "start"
				entry_color = LED_status["RGB"]["now"]
				RGB_final = self.thunderBolt(HOUR, entry_color, brightest, dimmest, intervals)

			# drift dimmer	
			if LED_status["drift"]["status"] == True:
				RGB_final = self.drift(HOUR, brightest, dimmest, down_interval)
			else:
				LED_status["lightning"]["status"] = False
				RGB_final = dimmest

		else:
			RGB_final = LED_status["RGB"]["now"]

		LED_status["RGB"]["now"] = RGB_final
		return RGB_final

	def lightning(self, HOUR):
		LED_status = self.LED_status[HOUR]

		status	 	= LED_status["lightning"]["status"]
		entry_color = LED_status["lightning"]["entry_color"]
		brightest 	= LED_status["lightning"]["brightest"]
		dimmest 	= LED_status["lightning"]["dimmest"]
		intervals 	= LED_status["lightning"]["intervals"]

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




#####  SETUP  #####

# Instantiate classes
np = Numpy()
Parser = Parser()
Temp = Temp(-20, 120)
MotorHandler = MotorHandler()
Sky = Sky()
LedHandler = LedHandler()
"""
# Set up RPi GPIO pins
GPIO.setmode(GPIO.BOARD)
# Servomotor pins
GPIO.setup(MOTOR_CTRL_1, GPIO.OUT)
GPIO.setup(MOTOR_CTRL_2, GPIO.OUT)
GPIO.setup(MOTOR_CTRL_3, GPIO.OUT)
# LED controller pins
GPIO.setup(LED_CTRL_1, GPIO.OUT)
GPIO.setup(LED_CTRL_2, GPIO.OUT)
"""


#####  MAIN  #####

#pudb.set_trace()

Parser.parseWeather()
#Parser.next_12[3]["summary"] = "thunderstorm"
#Parser.next_12[4]["summary"] = "thunderstorm"
#Parser.next_12[5]["summary"] = "thunderstorm"

counter=0
while True:
	os.system('clear')

	#Sky.set_12_Hours("unique")
	Sky.set_12_Hours("uniform")
	#Sky.set_12_Hours("static")
	LedHandler.terminalClock()

	counter+=1
	if counter >= 3000:
		Parser.parseWeather()
		counter=0

	time.sleep(0.05)

#pdb.set_trace()

HOUR = "05"
HOURS = ["05", "06"]

#pudb.set_trace()
#pdb.set_trace()
while True:
	os.system('clear')
	for HOUR in HOURS:
		Sky.thunderstorm(HOUR)

		LED_status = LedHandler.LED_status[HOUR]
		RGB_now = LED_status["RGB"]["now"]
		RGB_dimmed = LED_status["RGB"]["dimmed"]
		LedHandler.setColor(HOUR, RGB_now)
	
		entry_color = LED_status["lightning"]["entry_color"] 	
		brightest 	= LED_status["lightning"]["brightest"] 	
		dimmest 	= LED_status["lightning"]["dimmest"] 		
		intervals 	= LED_status["lightning"]["intervals"] 	
	
		print "brightest\t",
		R, G, B = brightest
		print_color('  ', bg=rgb(R/50, G/50, B/50))  
		print "dimmest\t\t",
		R, G, B = dimmest
		print_color('  ', bg=rgb(R/50, G/50, B/50))  
		print "entry_color\t",
		R, G, B = entry_color
		print_color('  ', bg=rgb(R/50, G/50, B/50))  
		print "-"*64
	
	time.sleep(0.1)

