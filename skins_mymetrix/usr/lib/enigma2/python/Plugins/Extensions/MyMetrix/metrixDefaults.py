from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from twisted.web.client import downloadPage
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import urllib
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import time
import metrixTools

class ConfigMetrixBarColors(ConfigSelection):

    def __init__(self, default = '#00149baf'):
        ConfigSelection.__init__(self, default=default, choices=[('#00F0A30A', _('Amber')),
         ('#00ffffff', _('White')),
         ('#00825A2C', _('Brown')),
         ('#000050EF', _('Cobalt')),
         ('#00911d10', _('Crimson')),
         ('#001BA1E2', _('Cyan')),
         ('#00a61d4d', _('Magenta')),
         ('#00A4C400', _('Lime')),
         ('#006A00FF', _('Indigo')),
         ('#0070ad11', _('Green')),
         ('#00008A00', _('Emerald')),
         ('#0076608A', _('Mauve')),
         ('#006D8764', _('Olive')),
         ('#00c3461b', _('Orange')),
         ('#00F472D0', _('Pink')),
         ('#00E51400', _('Red')),
         ('#007A3B3F', _('Sienna')),
         ('#00647687', _('Steel')),
         ('#00149baf', _('Teal')),
         ('#006c0aab', _('Violet')),
         ('#00bf9217', _('Yellow'))])


class ConfigMetrixColors(ConfigSelection):

    def __init__(self, default = '#00000000'):
        ConfigSelection.__init__(self, default=default, choices=[('CUSTOM', _('CUSTOM')),
         ('#00000000', _('Black')),
         ('#00111111', _('PreBlack')),
         ('#00ffffff', _('White')),
         ('#00444444', _('Darkgrey')),
         ('#00bbbbbb', _('Lightgrey')),
         ('#00999999', _('Grey')),
         ('#006f0000', _('Darkred')),
         ('#00295c00', _('Darkgreen')),
         ('#006b3500', _('Darkbrown')),
         ('#00446b00', _('Darklime')),
         ('#00006b5b', _('Darkteal')),
         ('#00004c6b', _('Darkcyan')),
         ('#0000236b', _('Darkcobalt')),
         ('#0030006b', _('Darkpurple')),
         ('#006b003f', _('Darkmagenta')),
         ('#0065006b', _('Darkpink')),
         ('#00F0A30A', _('Amber')),
         ('#00825A2C', _('Brown')),
         ('#000050EF', _('Cobalt')),
         ('#00911d10', _('Crimson')),
         ('#001BA1E2', _('Cyan')),
         ('#00a61d4d', _('Magenta')),
         ('#00A4C400', _('Lime')),
         ('#006A00FF', _('Indigo')),
         ('#0070ad11', _('Green')),
         ('#00008A00', _('Emerald')),
         ('#0076608A', _('Mauve')),
         ('#006D8764', _('Olive')),
         ('#00c3461b', _('Orange')),
         ('#00F472D0', _('Pink')),
         ('#00E51400', _('Red')),
         ('#007A3B3F', _('Sienna')),
         ('#00647687', _('Steel')),
         ('#00149baf', _('Teal')),
         ('#006c0aab', _('Violet')),
         ('#00bf9217', _('Yellow'))])


def pathRoot():
    return '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/'


def loadDefaults():
    config.plugins.MyMetrix = ConfigSubsection()
    config.plugins.MyMetrix.Color = ConfigSubsection()
    config.plugins.MetrixWeather = ConfigSubsection()
    config.plugins.MetrixUpdater = ConfigSubsection()
    config.plugins.MyMetrix.Store = ConfigSubsection()
    config.plugins.MetrixConnect = ConfigSubsection()
    config.plugins.MyMetrix.templateFile = ConfigSelection(default='MetrixHD Default.xml', choices=getTemplateFiles())
    config.plugins.MyMetrix.showFirstRun = ConfigSelection(default='1', choices=[('1', _('Yes')), ('0', _('No'))])
    config.plugins.MetrixConnect.PIN = ConfigNumber()
    config.plugins.MetrixConnect.auth_session = ConfigText()
    config.plugins.MetrixConnect.auth_token = ConfigText(default='None')
    config.plugins.MetrixConnect.auth_id = ConfigText()
    config.plugins.MetrixConnect.username = ConfigText(default=_('Not connected'))
    config.plugins.MetrixUpdater.refreshInterval = ConfigSelectionNumber(10, 1440, 10, default=30)
    config.plugins.MetrixUpdater.UpdateAvailable = ConfigNumber(default=0)
    config.plugins.MetrixUpdater.Reboot = ConfigNumber(default=0)
    config.plugins.MetrixUpdater.Revision = ConfigNumber(default=1000)
    config.plugins.MyMetrix.Store.Author = ConfigText(default='Unknown', fixed_size=False)
    config.plugins.MyMetrix.Store.Designname = ConfigText(default='MyDesign', fixed_size=False)
    config.plugins.MyMetrix.Color.ProgressBar = ConfigMetrixBarColors('#00ffffff')
    config.plugins.MyMetrix.Color.Selection = ConfigMetrixColors('#00149baf')
    config.plugins.MyMetrix.Color.Background = ConfigMetrixColors('#00000000')
    config.plugins.MyMetrix.Color.Foreground = ConfigMetrixColors('#00ffffff')
    config.plugins.MyMetrix.Color.Background2 = ConfigMetrixColors('#00149baf')
    config.plugins.MyMetrix.Color.Accent1 = ConfigMetrixColors('#00bbbbbb')
    config.plugins.MyMetrix.Color.Accent2 = ConfigMetrixColors('#00999999')
    config.plugins.MyMetrix.Color.BackgroundText = ConfigMetrixColors('#00ffffff')
    config.plugins.MyMetrix.Color.Background_Custom = ConfigSequence(seperator=',', limits=[(0, 255), (0, 255), (0, 255)], default=[0, 0, 0])
    config.plugins.MyMetrix.Color.Selection_Custom = ConfigSequence(seperator=',', limits=[(0, 255), (0, 255), (0, 255)], default=[20, 155, 175])
    config.plugins.MyMetrix.Color.Background2_Custom = ConfigSequence(seperator=',', limits=[(0, 255), (0, 255), (0, 255)], default=[17, 17, 17])
    config.plugins.MyMetrix.Color.Foreground_Custom = ConfigSequence(seperator=',', limits=[(0, 255), (0, 255), (0, 255)], default=[255, 255, 255])
    config.plugins.MyMetrix.Color.BackgroundText_Custom = ConfigSequence(seperator=',', limits=[(0, 255), (0, 255), (0, 255)], default=[255, 255, 255])
    config.plugins.MyMetrix.Color.Accent1_Custom = ConfigSequence(seperator=',', limits=[(0, 255), (0, 255), (0, 255)], default=[187, 187, 187])
    config.plugins.MyMetrix.Color.Accent2_Custom = ConfigSequence(seperator=',', limits=[(0, 255), (0, 255), (0, 255)], default=[153, 153, 153])
    config.plugins.MyMetrix.Color.BackgroundTransparency = ConfigSelectionNumber(0, 255, 10, default=60, wraparound=False)
    config.plugins.MyMetrix.Color.SelectionTransparency = ConfigSelectionNumber(0, 255, 10, default=0, wraparound=False)
    config.plugins.MyMetrix.Color.BackgroundTextTransparency = ConfigSelectionNumber(0, 255, 10, default=220, wraparound=False)
    config.plugins.MetrixWeather.refreshInterval = ConfigNumber(default=10)
    config.plugins.MetrixWeather.woeid = ConfigNumber(default=640161)
    config.plugins.MetrixWeather.tempUnit = ConfigSelection(default='Celsius', choices=[('Celsius', _('Celsius')), ('Fahrenheit', _('Fahrenheit'))])
    config.plugins.MyMetrix.AutoUpdate = ConfigSelection(default='1', choices=[('1', _('On')), ('0', _('Off'))])
    config.plugins.MyMetrix.AutoUpdateSkinParts = ConfigSelection(default='1', choices=[('1', _('On')), ('0', _('Off'))])
    config.plugins.MetrixWeather = ConfigSubsection()
    config.plugins.MetrixWeather.refreshInterval = ConfigNumber(default='10')
    config.plugins.MetrixWeather.woeid = ConfigNumber(default='640161')
    config.plugins.MetrixWeather.tempUnit = ConfigSelection(default='Celsius', choices=[('Celsius', _('Celsius')), ('Fahrenheit', _('Fahrenheit'))])
    config.plugins.MetrixWeather.currentLocation = ConfigText(default='N/A')
    config.plugins.MetrixWeather.currentWeatherCode = ConfigText(default='(')
    config.plugins.MetrixWeather.currentWeatherText = ConfigText(default='N/A')
    config.plugins.MetrixWeather.currentWeatherTemp = ConfigText(default='0')
    config.plugins.MetrixWeather.forecastTodayCode = ConfigText(default='(')
    config.plugins.MetrixWeather.forecastTodayText = ConfigText(default='N/A')
    config.plugins.MetrixWeather.forecastTodayTempMin = ConfigText(default='0')
    config.plugins.MetrixWeather.forecastTodayTempMax = ConfigText(default='0')
    config.plugins.MetrixWeather.forecastTomorrowCode = ConfigText(default='(')
    config.plugins.MetrixWeather.forecastTomorrowText = ConfigText(default='N/A')
    config.plugins.MetrixWeather.forecastTomorrowTempMin = ConfigText(default='0')
    config.plugins.MetrixWeather.forecastTomorrowTempMax = ConfigText(default='0')
    config.plugins.save()
    configfile.save()
    return config


def getTemplateFiles():
    templates = []
    dirs = listdir('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skintemplates/')
    for dir in dirs:
        try:
            templates.append((dir, dir.split('/')[-1].replace('.xml', '')))
        except:
            pass

    return templates
