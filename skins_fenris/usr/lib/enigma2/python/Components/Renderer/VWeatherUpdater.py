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


from Renderer import Renderer
from Components.VariableText import VariableText
#import library to do http requests:
import urllib
from enigma import eLabel
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
from Components.config import config, ConfigSubsection, configfile, ConfigText, ConfigNumber, ConfigDateTime, ConfigSelection

config.plugins.AtileHD = ConfigSubsection()
config.plugins.AtileHD.refreshInterval = ConfigNumber(default="10")
config.plugins.AtileHD.woeid = ConfigNumber(default="640161") #Location (visit yahoo.com)
config.plugins.AtileHD.tempUnit = ConfigSelection(default="Celsius", choices = [
				("Celsius", _("Celsius")),
				("Fahrenheit", _("Fahrenheit"))
				])
config.plugins.AtileHD.currentLocation = ConfigText(default="N/A")
config.plugins.AtileHD.currentWeatherCode = ConfigText(default="(")
config.plugins.AtileHD.currentWeatherText = ConfigText(default="N/A")
config.plugins.AtileHD.currentWeatherTemp = ConfigText(default="0")

config.plugins.AtileHD.forecastTodayCode = ConfigText(default="(")
config.plugins.AtileHD.forecastTodayText = ConfigText(default="N/A")
config.plugins.AtileHD.forecastTodayTempMin = ConfigText(default="0")
config.plugins.AtileHD.forecastTodayTempMax = ConfigText(default="0")

config.plugins.AtileHD.forecastTomorrowCode = ConfigText(default="(")
config.plugins.AtileHD.forecastTomorrowText = ConfigText(default="N/A")
config.plugins.AtileHD.forecastTomorrowTempMin = ConfigText(default="0")
config.plugins.AtileHD.forecastTomorrowTempMax = ConfigText(default="0")

class VWeatherUpdater(Renderer, VariableText):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self) 
		config.plugins.AtileHD.save()        
		configfile.save()
		self.woeid = config.plugins.AtileHD.woeid.value
		self.timer = 1
	GUI_WIDGET = eLabel
	
	def changed(self, what):
		if self.timer == 1:
			try:
				self.GetWeather()
			except:
				pass
		elif self.timer >= int(config.plugins.AtileHD.refreshInterval.value) * 60:
			self.timer = 0
		self.timer = self.timer + 1
			
	def onShow(self):
		self.text = config.plugins.AtileHD.currentWeatherCode.value

	def GetWeather(self):
		print "AtileHD lookup for ID " + str(self.woeid)
		url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%3D%22"+str(self.woeid)+"%22&format=xml"
		#url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%3D%22"+str(self.woeid)+"%22%20u%3Dc&format=xml"
		
		
		# where location in (select id from weather.search where query="oslo, norway")
		file = urllib.urlopen(url)
		data = file.read()
		file.close()
		
		dom = parseString(data)
		title = self.getText(dom.getElementsByTagName('title')[0].childNodes)
		config.plugins.AtileHD.currentLocation.value = str(title).split(',')[0].replace("Conditions for ","")
		
		currentWeather = dom.getElementsByTagName('yweather:condition')[0]
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.AtileHD.currentWeatherCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('temp')
		config.plugins.AtileHD.currentWeatherTemp.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.AtileHD.currentWeatherText.value = currentWeatherText.nodeValue
		
		currentWeather = dom.getElementsByTagName('yweather:forecast')[0]
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.AtileHD.forecastTodayCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('high')
		config.plugins.AtileHD.forecastTodayTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('low')
		config.plugins.AtileHD.forecastTodayTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.AtileHD.forecastTodayText.value = currentWeatherText.nodeValue
	
		currentWeather = dom.getElementsByTagName('yweather:forecast')[1]
		currentWeatherCode = currentWeather.getAttributeNode('code')
		config.plugins.AtileHD.forecastTomorrowCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('high')
		config.plugins.AtileHD.forecastTomorrowTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherTemp = currentWeather.getAttributeNode('low')
		config.plugins.AtileHD.forecastTomorrowTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
		currentWeatherText = currentWeather.getAttributeNode('text')
		config.plugins.AtileHD.forecastTomorrowText.value = currentWeatherText.nodeValue
	
	def getText(self,nodelist):
	    rc = []
	    for node in nodelist:
	        if node.nodeType == node.TEXT_NODE:
	            rc.append(node.data)
	    return ''.join(rc)
	   
	def ConvertCondition(self, c):
		c = int(c)
		condition = "("
		if c == 0 or c == 1 or c == 2:
			condition = "S"
		elif c == 3 or c == 4:
			condition = "Z"
		elif c == 5  or c == 6 or c == 7 or c == 18:
			condition = "U"
		elif c == 8 or c == 10 or c == 25:
			condition = "G"
		elif c == 9:
			condition = "Q"
		elif c == 11 or c == 12 or c == 40:
			condition = "R"
		elif c == 13 or c == 14 or c == 15 or c == 16 or c == 41 or c == 46 or c == 42 or c == 43:
			condition = "W"
		elif c == 17 or c == 35:
			condition = "X"
		elif c == 19:
			condition = "F"
		elif c == 20 or c == 21 or c == 22:
			condition = "L"
		elif c == 23 or c == 24:
			condition = "S"
		elif c == 26 or c == 44:
			condition = "N"
		elif c == 27 or c == 29:
			condition = "I"
		elif c == 28 or c == 30:
			condition = "H"
		elif c == 31 or c == 33:
			condition = "C"
		elif c == 32 or c == 34:
			condition = "B"
		elif c == 36:
			condition = "B"
		elif c == 37 or c == 38 or c == 39 or c == 45 or c == 47:
			condition = "0"
		else:
			condition = ")"
		return str(condition)
		
	def getTemp(self,temp):
		if config.plugins.AtileHD.tempUnit.value == "Fahrenheit":
			return str(int(round(float(temp),0)))
		else:
			celsius = (float(temp) - 32 ) * 5 / 9
			return str(int(round(float(celsius),0)))