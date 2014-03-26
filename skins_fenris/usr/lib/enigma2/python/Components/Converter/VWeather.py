# -*- coding: utf-8 -*-

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.
#
#
#######################################################################
#
#    AtileHD Weather for VU+
#    Coded by iMaxxx (c) 2013 mod by schomi
#    Support: www.vuplus-support.com
#
#######################################################################


from Components.Converter.Converter import Converter
from Components.config import config, ConfigText, ConfigNumber, ConfigDateTime
from Components.Element import cached

class VWeather(Converter, object):
	
	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type
			
	@cached
	def getText(self):
		if self.type == "currentLocation":
			return config.plugins.AtileHD.currentLocation.value
		if self.type == "currentWeatherTemp":
			return config.plugins.AtileHD.currentWeatherTemp.value
		elif self.type == "currentWeatherText":
			return config.plugins.AtileHD.currentWeatherText.value
		elif self.type == "currentWeatherCode":
			return config.plugins.AtileHD.currentWeatherCode.value
		elif self.type == "forecastTodayCode":
			return config.plugins.AtileHD.forecastTodayCode.value
		elif self.type == "forecastTodayTempMin":
			return config.plugins.AtileHD.forecastTodayTempMin.value + " " + self.getCF()
		elif self.type == "forecastTodayTempMax":
			return config.plugins.AtileHD.forecastTodayTempMax.value + " " + self.getCF()
		elif self.type == "forecastTodayText":
			return config.plugins.AtileHD.forecastTodayText.value
		elif self.type == "forecastTomorrowCode":
			return config.plugins.AtileHD.forecastTomorrowCode.value
		elif self.type == "forecastTomorrowTempMin":
			return config.plugins.AtileHD.forecastTomorrowTempMin.value + " " + self.getCF()
		elif self.type == "forecastTomorrowTempMax":
			return config.plugins.AtileHD.forecastTomorrowTempMax.value + " " + self.getCF()
		elif self.type == "forecastTomorrowText":
			return config.plugins.AtileHD.forecastTomorrowText.value
		elif self.type == "title":
			return self.getCF() + " | " + config.plugins.AtileHD.currentLocation.value
		elif self.type == "CF":
			return self.getCF() 
		else:
			return ""
		
	def getCF(self):
		if config.plugins.AtileHD.tempUnit.value == "Fahrenheit":
			return "°F"
		else: 
			return "°C"

	text = property(getText)