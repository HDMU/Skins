#######################################################################
#
#    MyMetrix
#    Coded by iMaxxx (c) 2013
#    KravenSE by Kraven
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.
#
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from shutil import move
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad, getDesktop, eConsoleAppContainer
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
#############################################################

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("KravenSE", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/KravenSE/locale/"))

def _(txt):
	t = gettext.dgettext("KravenSE", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block


#############################################################

config.plugins.KravenSE = ConfigSubsection()
config.plugins.KravenSE.weather_city = ConfigNumber(default="924938")

config.plugins.KravenSE.Image = ConfigSelection(default="main-custom-openatv", choices = [
				("main-custom-atemio4you", _("Atemio4You")),
				("main-custom-hdmu", _("HDMU")),
				("main-custom-openatv", _("openATV")),
				("main-custom-openhdf", _("openHDF")),
				("main-custom-openmips", _("openMIPS")),
				("main-custom-opennfr", _("openNFR"))
				])
				
config.plugins.KravenSE.Header = ConfigSelection(default="header-seven", choices = [
				("header-seven", _("SevenHD")),
				("header-zero", _("ZeroHD")),
				("header-kravenhd", _("KravenHD")),
				("header-kravense", _("KravenSE"))
				])
				
config.plugins.KravenSE.Volume = ConfigSelection(default="volume-border", choices = [
				("volume-original", _("Original")),
				("volume-border", _("with Border")),
				("volume-left", _("left")),
				("volume-right", _("right")),
				("volume-top", _("top")),
				("volume-center", _("center"))
				])
				
config.plugins.KravenSE.BackgroundColorTrans = ConfigSelection(default="0A", choices = [
				("0A", _("low")),
				("4A", _("medium")),
				("8C", _("high"))
				])
				
config.plugins.KravenSE.Background = ConfigSelection(default="000000", choices = [
				("F0A30A", _("Amber")),
				("B27708", _("Amber Dark")),
				("000000", _("Black")),
				("1B1775", _("Blue")),
				("0E0C3F", _("Blue Dark")),
				("7D5929", _("Brown")),
				("3F2D15", _("Brown Dark")),
				("0050EF", _("Cobalt")),
				("001F59", _("Cobalt Dark")),
				("1BA1E2", _("Cyan")),
				("0F5B7F", _("Cyan Dark")),
				("999999", _("Grey")),
				("3F3F3F", _("Grey Dark")),
				("70AD11", _("Green")),
				("213305", _("Green Dark")),
				("6D8764", _("Olive")),
				("313D2D", _("Olive Dark")),
				("C3461B", _("Orange")),
				("892E13", _("Orange Dark")),
				("F472D0", _("Pink")),
				("723562", _("Pink Dark")),
				("E51400", _("Red")),
				("330400", _("Red Dark")),
				("647687", _("Steel")),
				("262C33", _("Steel Dark")),
				("6C0AAB", _("Violet")),
				("1F0333", _("Violet Dark")),
				("ffffff", _("White"))
				])
				
config.plugins.KravenSE.SkinColorInfobar = ConfigSelection(default="001B1775", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00ffffff", _("White"))
				])
				
config.plugins.KravenSE.SelectionBackground = ConfigSelection(default="000050EF", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00ffffff", _("White"))
				])
				
config.plugins.KravenSE.Font1 = ConfigSelection(default="00fffff3", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00fffff3", _("White"))
				])
				
config.plugins.KravenSE.Font2 = ConfigSelection(default="00fffff4", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00fffff4", _("White"))
				])
				
config.plugins.KravenSE.SelectionFont = ConfigSelection(default="00fffff7", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00fffff7", _("White"))
				])
				
config.plugins.KravenSE.ButtonText = ConfigSelection(default="00fffff2", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00fffff2", _("White"))
				])
				
config.plugins.KravenSE.Border = ConfigSelection(default="00fffff1", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00fffff1", _("White")),
				("ff000000", _("Off"))
				])
				
config.plugins.KravenSE.Progress = ConfigSelection(default="00fffff6", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00fffff6", _("White"))
				])
				
config.plugins.KravenSE.Line = ConfigSelection(default="00fffff5", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00fffff5", _("White"))
				])
				
config.plugins.KravenSE.SelectionBorder = ConfigSelection(default="00ffffff", choices = [
				("00F0A30A", _("Amber")),
				("00B27708", _("Amber Dark")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("000E0C3F", _("Blue Dark")),
				("007D5929", _("Brown")),
				("003F2D15", _("Brown Dark")),
				("000050EF", _("Cobalt")),
				("00001F59", _("Cobalt Dark")),
				("001BA1E2", _("Cyan")),
				("000F5B7F", _("Cyan Dark")),
				("00999999", _("Grey")),
				("003F3F3F", _("Grey Dark")),
				("0070AD11", _("Green")),
				("00213305", _("Green Dark")),
				("006D8764", _("Olive")),
				("00313D2D", _("Olive Dark")),
				("00C3461B", _("Orange")),
				("00892E13", _("Orange Dark")),
				("00F472D0", _("Pink")),
				("00723562", _("Pink Dark")),
				("00E51400", _("Red")),
				("00330400", _("Red Dark")),
				("00647687", _("Steel")),
				("00262C33", _("Steel Dark")),
				("006C0AAB", _("Violet")),
				("001F0333", _("Violet Dark")),
				("00ffffff", _("White"))
				])
				
config.plugins.KravenSE.AnalogStyle = ConfigSelection(default="00999999", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
				("000050EF", _("Cobalt")),
				("001BA1E2", _("Cyan")),
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00ffffff", _("White"))
				])
				
config.plugins.KravenSE.InfobarStyle = ConfigSelection(default="infobar-style-original", choices = [
				("infobar-style-original", _("Original")),
				("infobar-style-zpicon", _("ZPicon")),
				("infobar-style-xpicon", _("XPicon")),
				("infobar-style-zzpicon", _("ZZPicon")),
				("infobar-style-zzzpicon", _("ZZZPicon"))
				])
				
config.plugins.KravenSE.InfobarStyle2 = ConfigSelection(default="infobar-style-xpicon", choices = [
				("infobar-style-zpicon", _("ZPicon")),
				("infobar-style-xpicon", _("XPicon")),
				("infobar-style-zzpicon", _("ZZPicon")),
				("infobar-style-zzzpicon", _("ZZZPicon"))
				])
				
config.plugins.KravenSE.ChannelSelectionStyle = ConfigSelection(default="channelselection-twocolumns", choices = [
				("channelselection-twocolumns", _("Two Columns")),
				("channelselection-threecolumns", _("Three Columns")),
				("channelselection-zpicon", _("ZPicon")),
				("channelselection-xpicon", _("XPicon")),
				("channelselection-zzpicon", _("ZZPicon")),
				("channelselection-zzzpicon", _("ZZZPicon")),
				("channelselection-minitv", _("MiniTV"))
				])
				
config.plugins.KravenSE.NumberZapExt = ConfigSelection(default="numberzapext-none", choices = [
				("numberzapext-none", _("Off")),
				("numberzapext-zpicon", _("ZPicons")),
				("numberzapext-xpicon", _("XPicons")),
				("numberzapext-zzpicon", _("ZZPicons")),
				("numberzapext-zzzpicon", _("ZZZPicons"))
				])
				
config.plugins.KravenSE.CoolTVGuide = ConfigSelection(default="cooltv-minitv", choices = [
				("cooltv-minitv", _("MiniTV")),
				("cooltv-picon", _("Picon"))
				])
				
config.plugins.KravenSE.EMCStyle = ConfigSelection(default="emc-bigcover", choices = [
				("emc-nocover", _("No Cover")),
				("emc-smallcover", _("Small Cover")),
				("emc-bigcover", _("Big Cover")),
				("emc-verybigcover", _("Very Big Cover"))
				])
				
config.plugins.KravenSE.RunningText = ConfigSelection(default="movetype=running", choices = [
				("movetype=running", _("On")),
				("movetype=none", _("Off"))
				])
				
config.plugins.KravenSE.ButtonStyle = ConfigSelection(default="buttons_seven_white", choices = [
				("buttons_seven_white", _("SevenHD white")),
				("buttons_seven_black", _("SevenHD black")),
				("buttons_kravenhd", _("KravenHD")),
				("buttons_kravense", _("KravenSE")),
				("buttons_zero", _("ZeroHD")),
				("buttons_stony", _("stony"))
				])
# .:TBX:.
config.plugins.KravenSE.ClockStyle = ConfigSelection(default="clock-standard", choices = [
				("clock-standard", _("Standard")),
				("clock-seconds", _("with Seconds")),
				("clock-weekday", _("with Weekday")),
				("clock-analog", _("Analog")),
				("clock-weather", _("Weather")),
				("clock-android", _("Android"))
				])
				
config.plugins.KravenSE.ClockStyle2 = ConfigSelection(default="clock-standard2", choices = [
				("clock-standard2", _("Standard")),
				("clock-seconds2", _("with Seconds"))
				])
				
config.plugins.KravenSE.WeatherStyle = ConfigSelection(default="weather-off", choices = [
                ("weather-off", _("Off")),
				("weather-big", _("Big")),
				("weather-small", _("Small"))
				])
				
config.plugins.KravenSE.FontStyle = ConfigSelection(default="campton", choices = [
				("handel", _("HandelGotD")),
				("campton", _("Campton")),
				("proxima", _("Proxima Nova")),
				("opensans", _("OpenSans"))
				])
config.plugins.KravenSE.SatInfo = ConfigSelection(default="satinfo-off", choices = [
				("satinfo-off", _("Off")),
				("satinfo-on", _("On"))
				])
				
config.plugins.KravenSE.ECMInfo = ConfigSelection(default="ecminfo-off", choices = [
				("ecminfo-off", _("Off")),
				("ecminfo-on", _("On"))
				])
				
#######################################################################

class KravenSE(ConfigListScreen, Screen):
	skin = """
<screen name="KravenSE-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
   <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" valign="center" position="64,662" size="148,48" text="Cancel" transparent="1" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" valign="center" position="264,662" size="148,48" text="Save" transparent="1" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" valign="center" position="464,662" size="148,48" text="Reboot" transparent="1" />
  <widget name="config" position="18,72" size="816,575" transparent="1" zPosition="1" backgroundColor="#00000000" />
  <eLabel position="70,12" size="708,46" text="KravenSE - Konfigurationstool" font="Regular; 35" valign="center" halign="center" transparent="1" backgroundColor="#00000000" foregroundColor="#00ffffff" name="," />
<eLabel position="891,657" size="372,46" text="Thanks to http://www.gigablue-support.org/" font="Regular; 12" valign="center" halign="center" transparent="1" backgroundColor="#00000000" foregroundColor="#00ffffff" name="," />
  <widget name="helperimage" position="891,178" size="372,328" zPosition="1" backgroundColor="#00000000" />
  <eLabel backgroundColor="#00000000" position="0,0" size="1280,720" transparent="0" zPosition="-9" />
  <widget backgroundColor="#00000000" font="Regular2; 34" foregroundColor="#00ffffff" position="70,12" render="Label" size="708,46" source="Title" transparent="1" halign="center" valign="center" noWrap="1" />
    <eLabel backgroundColor="#00000000" position="6,6" size="842,708" transparent="0" zPosition="-9" foregroundColor="#00ffffff" />
    <eLabel backgroundColor="#00ffffff" position="6,6" size="842,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="6,714" size="842,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="6,6" size="2,708" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="848,6" size="2,708" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="18,64" size="816,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="18,656" size="816,2" zPosition="2" />
    <ePixmap pixmap="KravenSE/buttons/key_red1.png" position="22,670" size="32,32" backgroundColor="#00000000" alphatest="blend" />
    <ePixmap pixmap="KravenSE/buttons/key_green1.png" position="222,670" size="32,32" backgroundColor="#00000000" alphatest="blend" />
    <ePixmap pixmap="KravenSE/buttons/key_yellow1.png" position="422,670" size="32,32" backgroundColor="#00000000" alphatest="blend" />
    <ePixmap pixmap="KravenSE/buttons/key_blue1.png" position="622,670" size="32,32" backgroundColor="#00000000" alphatest="blend" />
 <widget source="global.CurrentTime" render="Label" position="1154,16" size="100,28" font="Regular;26" halign="right" backgroundColor="#00000000" transparent="1" valign="center" foregroundColor="#00ffffff">
      <convert type="ClockToText">Default</convert>
    </widget>
    <eLabel backgroundColor="#00000000" position="878,6" size="396,708" transparent="0" zPosition="-9" />
    <eLabel backgroundColor="#00ffffff" position="878,6" size="396,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="878,714" size="396,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="878,6" size="2,708" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="1274,6" size="2,708" zPosition="2" />
<eLabel position="891,88" size="372,46" text="Version: 1.6" font="Regular; 35" valign="center" halign="center" transparent="1" backgroundColor="#00000000" foregroundColor="#00ffffff" name="," />
</screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.datei = "/usr/share/enigma2/KravenSE/skin.xml"
		self.dateiTMP = self.datei + ".tmp"
		self.daten = "/usr/lib/enigma2/python/Plugins/Extensions/KravenSE/data/"
		self.komponente = "/usr/lib/enigma2/python/Plugins/Extensions/KravenSE/comp/"
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		
		list = []
		ConfigListScreen.__init__(self, list)
		
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot, "blue": self.showInfo, "green": self.save,"cancel": self.exit}, -1)
		self.UpdatePicture()
		self.onLayoutFinish.append(self.mylist)

	def mylist(self):
		list = []
		list.append(getConfigListEntry(_("______________________ System __________________________________"), ))
		list.append(getConfigListEntry(_("Image"), config.plugins.KravenSE.Image))
		list.append(getConfigListEntry(_("Style"), config.plugins.KravenSE.Header))
		list.append(getConfigListEntry(_("Font Style"), config.plugins.KravenSE.FontStyle))
		list.append(getConfigListEntry(_("Button Style"), config.plugins.KravenSE.ButtonStyle))
		list.append(getConfigListEntry(_("Running Text"), config.plugins.KravenSE.RunningText))
		list.append(getConfigListEntry(_("Background Transparency"), config.plugins.KravenSE.BackgroundColorTrans))
		list.append(getConfigListEntry(_("Weather ID"), config.plugins.KravenSE.weather_city))
		list.append(getConfigListEntry(_("______________________ Colors __________________________________"), ))
		list.append(getConfigListEntry(_("Line"), config.plugins.KravenSE.Line))

		if config.plugins.KravenSE.Header.value == "header-kravense" or config.plugins.KravenSE.Header.value == "header-kravenhd":
			list.append(getConfigListEntry(_("Infobar"), config.plugins.KravenSE.SkinColorInfobar))

		list.append(getConfigListEntry(_("Background"), config.plugins.KravenSE.Background))
		if config.plugins.KravenSE.Header.value == "header-seven":
			list.append(getConfigListEntry(_("Border"), config.plugins.KravenSE.Border))
		list.append(getConfigListEntry(_("Listselection"), config.plugins.KravenSE.SelectionBackground))
		list.append(getConfigListEntry(_("Listselection Border"), config.plugins.KravenSE.SelectionBorder))
		list.append(getConfigListEntry(_("Progress-/Volumebar"), config.plugins.KravenSE.Progress))
		list.append(getConfigListEntry(_("Font 1"), config.plugins.KravenSE.Font1))
		list.append(getConfigListEntry(_("Font 2"), config.plugins.KravenSE.Font2))
		list.append(getConfigListEntry(_("Selection Font"), config.plugins.KravenSE.SelectionFont))
		list.append(getConfigListEntry(_("Button Text"), config.plugins.KravenSE.ButtonText))
		list.append(getConfigListEntry(_("______________________ Infobar __________________________________"), ))
		if config.plugins.KravenSE.Header.value == "header-seven" or config.plugins.KravenSE.Header.value == "header-zero":
			list.append(getConfigListEntry(_("Style"), config.plugins.KravenSE.InfobarStyle))
		elif config.plugins.KravenSE.Header.value == "header-kravenhd" or config.plugins.KravenSE.Header.value == "header-kravense":
			list.append(getConfigListEntry(_("Style"), config.plugins.KravenSE.InfobarStyle2))
		if config.plugins.KravenSE.Header.value == "header-zero":
			list.append(getConfigListEntry(_("Clock"), config.plugins.KravenSE.ClockStyle2))
		elif config.plugins.KravenSE.Header.value == "header-kravenhd" or config.plugins.KravenSE.Header.value == "header-kravense" or config.plugins.KravenSE.Header.value == "header-seven":
			list.append(getConfigListEntry(_("Clock"), config.plugins.KravenSE.ClockStyle))
		if config.plugins.KravenSE.ClockStyle.value == "clock-analog":
			list.append(getConfigListEntry(_("Clock Analog Color"), config.plugins.KravenSE.AnalogStyle))
		list.append(getConfigListEntry(_("Weather"), config.plugins.KravenSE.WeatherStyle))
		list.append(getConfigListEntry(_("Sat-Info"), config.plugins.KravenSE.SatInfo))
		list.append(getConfigListEntry(_("ECM-Info"), config.plugins.KravenSE.ECMInfo))
		list.append(getConfigListEntry(_("______________________ General __________________________________"), ))
		list.append(getConfigListEntry(_("Channel Selection"), config.plugins.KravenSE.ChannelSelectionStyle))
		list.append(getConfigListEntry(_("EMC"), config.plugins.KravenSE.EMCStyle))
		list.append(getConfigListEntry(_("ExtNumberZap"), config.plugins.KravenSE.NumberZapExt))
		list.append(getConfigListEntry(_("Volume Style"), config.plugins.KravenSE.Volume))
		list.append(getConfigListEntry(_("CoolTVGuide"), config.plugins.KravenSE.CoolTVGuide))
		
		self["config"].list = list
		self["config"].l.setList(list)
		
		self.ShowPicture()

	def GetPicturePath(self):
		try:
			returnValue = self["config"].getCurrent()[1].value
			path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenSE/images/" + returnValue + ".jpg"
			if fileExists(path):
				return path
			else:
				## colors
				return "/usr/lib/enigma2/python/Plugins/Extensions/KravenSE/images/colors.jpg"
		except:
			## weather
			return "/usr/lib/enigma2/python/Plugins/Extensions/KravenSE/images/924938.jpg"

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#002C2C39"])
		self.PicLoad.startDecode(self.GetPicturePath())

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.mylist()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.mylist()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.mylist()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.mylist()

	def reboot(self):
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("Do you really want to reboot now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def getDataByKey(self, list, key):
		for item in list:
			if item["key"] == key:
				return item
		return list[0]

	def getFontStyleData(self, key):
		return self.getDataByKey(channelselFontStyles, key)

	def getFontSizeData(self, key):
		return self.getDataByKey(channelInfoFontSizes, key)

	def save(self):
		if fileExists("/tmp/KravenSEweather.xml"):
			remove('/tmp/KravenSEweather.xml')

		for x in self["config"].list:
			if len(x) > 1:
					x[1].save()
			else:
					pass

		try:
			#global tag search and replace in all skin elements
			self.set_font()
			self.skinSearchAndReplace = []
			self.skinSearchAndReplace.append(["0A", config.plugins.KravenSE.BackgroundColorTrans.value])
			self.skinSearchAndReplace.append(["000000", config.plugins.KravenSE.Background.value])
			self.skinSearchAndReplace.append(["000050EF", config.plugins.KravenSE.SelectionBackground.value])
			self.skinSearchAndReplace.append(["00fffff3", config.plugins.KravenSE.Font1.value])
			self.skinSearchAndReplace.append(["00fffff4", config.plugins.KravenSE.Font2.value])
			self.skinSearchAndReplace.append(["00fffff7", config.plugins.KravenSE.SelectionFont.value])
			self.skinSearchAndReplace.append(["00fffff2", config.plugins.KravenSE.ButtonText.value])
			self.skinSearchAndReplace.append(["00fffff6", config.plugins.KravenSE.Progress.value])
			self.skinSearchAndReplace.append(["00fffff1", config.plugins.KravenSE.Border.value])
			self.skinSearchAndReplace.append(["00fffff5", config.plugins.KravenSE.Line.value])
			self.skinSearchAndReplace.append(["buttons_seven", config.plugins.KravenSE.ButtonStyle.value])
			self.skinSearchAndReplace.append(["movetype=running", config.plugins.KravenSE.RunningText.value])
			
			self.selectionbordercolor = config.plugins.KravenSE.SelectionBorder.value
			self.borset = ("borset_" + self.selectionbordercolor + ".png")
			self.skinSearchAndReplace.append(["borset.png", self.borset])
			
			self.skincolorinfobarcolor = config.plugins.KravenSE.SkinColorInfobar.value
			self.ibar = ("ibar_" + self.skincolorinfobarcolor + ".png")
			self.skinSearchAndReplace.append(["ibar.png", self.ibar])
			
			self.skincolorinfobarcolor = config.plugins.KravenSE.SkinColorInfobar.value
			self.ibar = ("ibaro_" + self.skincolorinfobarcolor + ".png")
			self.skinSearchAndReplace.append(["ibaro.png", self.ibar])
			
			self.skincolorinfobarcolor = config.plugins.KravenSE.SkinColorInfobar.value
			self.ibar = ("ibaro2_" + self.skincolorinfobarcolor + ".png")
			self.skinSearchAndReplace.append(["ibaro2.png", self.ibar])
			
			self.skincolorinfobarcolor = config.plugins.KravenSE.SkinColorInfobar.value
			self.ibar = ("ibaro3_" + self.skincolorinfobarcolor + ".png")
			self.skinSearchAndReplace.append(["ibaro3.png", self.ibar])
			
			self.skincolorinfobarcolor = config.plugins.KravenSE.SkinColorInfobar.value
			self.ibar = ("ibaro4_" + self.skincolorinfobarcolor + ".png")
			self.skinSearchAndReplace.append(["ibaro4.png", self.ibar])
			
			self.analogstylecolor = config.plugins.KravenSE.AnalogStyle.value
			self.analog = ("analog_" + self.analogstylecolor + ".png")
			self.skinSearchAndReplace.append(["analog.png", self.analog])
			
			### Header
			self.appendSkinFile(self.daten + config.plugins.KravenSE.Header.value + ".xml")
			
			### Volume
			self.appendSkinFile(self.daten + config.plugins.KravenSE.Volume.value + ".xml")
			
			###ChannelSelection
			self.appendSkinFile(self.daten + config.plugins.KravenSE.ChannelSelectionStyle.value + ".xml")

			###Infobar_main
			if config.plugins.KravenSE.Header.value == "header-seven" or config.plugins.KravenSE.Header.value == "header-zero":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.InfobarStyle.value + "_main.xml")
			elif config.plugins.KravenSE.Header.value == "header-kravenhd" or config.plugins.KravenSE.Header.value == "header-kravense":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.InfobarStyle2.value + "_main.xml")

			###clock-style xml
			if config.plugins.KravenSE.Header.value == "header-zero":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.ClockStyle2.value + ".xml")
			elif config.plugins.KravenSE.Header.value == "header-kravenhd" or config.plugins.KravenSE.Header.value == "header-kravense" or config.plugins.KravenSE.Header.value == "header-seven":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.ClockStyle.value + ".xml")

			###sat-info
			self.appendSkinFile(self.daten + config.plugins.KravenSE.SatInfo.value + ".xml")

			###ecm-info
			self.appendSkinFile(self.daten + config.plugins.KravenSE.ECMInfo.value + ".xml")

			###weather-style
			self.appendSkinFile(self.daten + config.plugins.KravenSE.WeatherStyle.value + ".xml")

			###Infobar_middle
			if config.plugins.KravenSE.Header.value == "header-seven" or config.plugins.KravenSE.Header.value == "header-zero":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.InfobarStyle.value + "_middle.xml")
			elif config.plugins.KravenSE.Header.value == "header-kravenhd" or config.plugins.KravenSE.Header.value == "header-kravense":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.InfobarStyle2.value + "_middle.xml")

			###clock-style xml
			if config.plugins.KravenSE.Header.value == "header-zero":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.ClockStyle2.value + ".xml")
			elif config.plugins.KravenSE.Header.value == "header-kravenhd" or config.plugins.KravenSE.Header.value == "header-kravense" or config.plugins.KravenSE.Header.value == "header-seven":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.ClockStyle.value + ".xml")

			###Infobar_end
			if config.plugins.KravenSE.Header.value == "header-seven" or config.plugins.KravenSE.Header.value == "header-zero":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.InfobarStyle.value + "_end.xml")
			elif config.plugins.KravenSE.Header.value == "header-kravenhd" or config.plugins.KravenSE.Header.value == "header-kravense":
				self.appendSkinFile(self.daten + config.plugins.KravenSE.InfobarStyle2.value + "_end.xml")

			###Main XML
			self.appendSkinFile(self.daten + "main.xml")

			###Plugins XML
			self.appendSkinFile(self.daten + "plugins.xml")

			#EMCSTYLE
			self.appendSkinFile(self.daten + config.plugins.KravenSE.EMCStyle.value +".xml")			

			#NumberZapExtStyle
			self.appendSkinFile(self.daten + config.plugins.KravenSE.NumberZapExt.value + ".xml")

			###custom-main XML
			self.appendSkinFile(self.daten + config.plugins.KravenSE.Image.value + ".xml")

			###cooltv XML
			self.appendSkinFile(self.daten + config.plugins.KravenSE.CoolTVGuide.value + ".xml")

			###skin-user
			try:
				self.appendSkinFile(self.daten + "skin-user.xml")
			except:
				pass
			###skin-end
			self.appendSkinFile(self.daten + "skin-end.xml")

			xFile = open(self.dateiTMP, "w")
			for xx in self.skin_lines:
				xFile.writelines(xx)
			xFile.close()

			move(self.dateiTMP, self.datei)

			#system('rm -rf ' + self.dateiTMP)
			
			console1 = eConsoleAppContainer()
			console2 = eConsoleAppContainer()
			console3 = eConsoleAppContainer()
			console4 = eConsoleAppContainer()
			console5 = eConsoleAppContainer()
			
			#volume
			console1.execute("rm -rf /usr/share/enigma2/KravenSE/volume/*.*; rm -rf /usr/share/enigma2/KravenSE/volume; wget -q http://www.gigablue-support.org/skins/KravenSE/%s.tar.gz -O /tmp/%s.tar.gz; tar xf /tmp/%s.tar.gz -C /usr/share/enigma2/KravenSE/" % (str(config.plugins.KravenSE.Volume.value), str(config.plugins.KravenSE.Volume.value), str(config.plugins.KravenSE.Volume.value)))
			#buttons
			console2.execute("rm -rf /usr/share/enigma2/KravenSE/buttons/*.*; rm -rf /usr/share/enigma2/KravenSE/buttons; wget -q http://www.gigablue-support.org/skins/KravenSE/%s.tar.gz -O /tmp/%s.tar.gz; tar xf /tmp/%s.tar.gz -C /usr/share/enigma2/KravenSE/" % (str(config.plugins.KravenSE.ButtonStyle.value), str(config.plugins.KravenSE.ButtonStyle.value), str(config.plugins.KravenSE.ButtonStyle.value)))
			#infobar
			console3.execute("wget -q http://www.gigablue-support.org/skins/KravenSE/%s.tar.gz -O /tmp/%s.tar.gz; tar xf /tmp/%s.tar.gz -C /usr/share/enigma2/KravenSE/" % (str(config.plugins.KravenSE.Header.value), str(config.plugins.KravenSE.Header.value), str(config.plugins.KravenSE.Header.value)))
			#weather
			console4.execute("rm -rf /usr/share/enigma2/KravenSE/WetterIcons/*.*; rm -rf /usr/share/enigma2/KravenSE/WetterIcons; wget -q http://www.gigablue-support.org/skins/KravenSE/%s.tar.gz -O /tmp/%s.tar.gz; tar xf /tmp/%s.tar.gz -C /usr/share/enigma2/KravenSE/" % (str(config.plugins.KravenSE.WeatherStyle.value), str(config.plugins.KravenSE.WeatherStyle.value), str(config.plugins.KravenSE.WeatherStyle.value)))
			#clock
			console5.execute("rm -rf /usr/share/enigma2/KravenSE/clock/*.*; rm -rf /usr/share/enigma2/KravenSE/clock; wget -q http://www.gigablue-support.org/skins/KravenSE/%s.tar.gz -O /tmp/%s.tar.gz; tar xf /tmp/%s.tar.gz -C /usr/share/enigma2/KravenSE/" % (str(config.plugins.KravenSE.ClockStyle.value), str(config.plugins.KravenSE.ClockStyle.value), str(config.plugins.KravenSE.ClockStyle.value)))
						
		except:
			self.session.open(MessageBox, _("Error creating Skin!"), MessageBox.TYPE_ERROR)

		self.restart()

	def restart(self):
		configfile.save()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to download files and apply a new skin.\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))

	def appendSkinFile(self, appendFileName, skinPartSearchAndReplace=None):
		"""
		add skin file to main skin content

		appendFileName:
		 xml skin-part to add

		skinPartSearchAndReplace:
		 (optional) a list of search and replace arrays. first element, search, second for replace
		"""
		skFile = open(appendFileName, "r")
		file_lines = skFile.readlines()
		skFile.close()

		tmpSearchAndReplace = []

		if skinPartSearchAndReplace is not None:
			tmpSearchAndReplace = self.skinSearchAndReplace + skinPartSearchAndReplace
		else:
			tmpSearchAndReplace = self.skinSearchAndReplace

		for skinLine in file_lines:
			for item in tmpSearchAndReplace:
				skinLine = skinLine.replace(item[0], item[1])
			self.skin_lines.append(skinLine)

	def set_font(self):
		'''header-kraven.xml; header-seven; header-zero
		handel = 97
		campton= 93
		opensans= 93
		proxima = 103'''
		#config.plugins.KravenSE.Header.value
		new_font = config.plugins.KravenSE.FontStyle.value
		if new_font == "campton":
			new_scale = 'scale="93"'
			new_font_name1 = 'Campton Light.otf'
			new_font_name2 = 'Campton Medium.otf'
		elif new_font == "handel":
			new_scale = 'scale="97"'
			new_font_name1 = 'HandelGotD.ttf'
			new_font_name2 = 'HandelGotDBol.ttf'
		elif new_font == "proxima":
			new_scale = 'scale="103"'
			new_font_name1 = 'Proxima Nova Regular.otf'
			new_font_name2 = 'Proxima Nova Bold.otf'
		elif new_font == "opensans":
			new_scale = 'scale="93"'
			new_font_name1 = 'setrixHD.ttf'
			new_font_name2 = 'OpenSans-Regular.ttf'
			
		old_xml = self.daten + config.plugins.KravenSE.Header.value + ".xml"
		new_xml = self.daten + config.plugins.KravenSE.Header.value + ".xml_new"
		
		fin = open(old_xml)
		fout = open(new_xml, "wt")
		
		for line in fin.readlines():
			if line.find('Campton Light.otf')>= 0:
				fout.write( line.replace('Campton Light.otf', new_font_name1).replace('scale="93"', new_scale))
			elif line.find('Campton Medium.otf')>= 0:
				fout.write( line.replace('Campton Medium.otf', new_font_name2).replace('scale="93"', new_scale))
			elif line.find('HandelGotD.ttf')>= 0:
				fout.write( line.replace('HandelGotD.ttf', new_font_name1).replace('scale="97"', new_scale))
			elif line.find('HandelGotDBol.ttf')>= 0:
				fout.write( line.replace('HandelGotDBol.ttf', new_font_name2).replace('scale="97"', new_scale))
			elif line.find('Proxima Nova Regular.otf')>= 0:
				fout.write( line.replace('Proxima Nova Regular.otf', new_font_name1).replace('scale="103"', new_scale))
			elif line.find('Proxima Nova Bold.otf')>= 0: 
				fout.write( line.replace('Proxima Nova Bold.otf', new_font_name2).replace('scale="103"', new_scale)) 
			elif line.find('setrixHD.ttf')>= 0:
				fout.write( line.replace('setrixHD.ttf', new_font_name1).replace('scale="93"', new_scale))
			elif line.find('OpenSans-Regular.ttf')>= 0: 
				fout.write( line.replace('OpenSans-Regular.ttf', new_font_name2).replace('scale="93"', new_scale))
			else:
				fout.write( line )
		
		fin.close()
		fout.close()
		
		remove(old_xml)
		rename(new_xml, old_xml)
		

	def restartGUI(self, answer):
		if answer is True:
			config.skin.primary_skin.setValue("KravenSE/skin.xml")
			config.skin.save()
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
					pass
		self.close()

#############################################################

def main(session, **kwargs):
	session.open(KravenSE,"/usr/lib/enigma2/python/Plugins/Extensions/KravenSE/images/kravencolors.jpg")

def Plugins(**kwargs):
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		return [PluginDescriptor(name="KravenSE", description=_("Configuration tool for KravenSE"), where = PluginDescriptor.WHERE_PLUGINMENU, icon='pluginfhd.png', fnc=main)]
	else:
		return [PluginDescriptor(name="KravenSE", description=_("Configuration tool for KravenSE"), where = PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main)]