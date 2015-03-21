#######################################################################
#
#    MyMetrix
#    Coded by iMaxxx (c) 2013
#    SevenHD by Kraven
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
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from shutil import move
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS

#############################################################

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("SevenHD", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/SevenHD/locale/"))

def _(txt):
	t = gettext.dgettext("SevenHD", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block


#############################################################

config.plugins.SevenHD = ConfigSubsection()

config.plugins.SevenHD.Image = ConfigSelection(default="main-custom-openatv", choices = [
				("main-custom-atemio4you", _("Atemio4You")),
				("main-custom-hdmu", _("HDMU")),
				("main-custom-openatv", _("openATV")),
				("main-custom-openhdf", _("openHDF")),
				("main-custom-openmips", _("openMIPS"))
				])
				
config.plugins.SevenHD.BackgroundColorTrans = ConfigSelection(default="8C", choices = [
				("0A", _("low")),
				("4A", _("medium")),
				("8C", _("high"))
				])
				
config.plugins.SevenHD.Background = ConfigSelection(default="000000", choices = [
				("F0A30A", _("Amber")),
				("000000", _("Black")),
				("1B1775", _("Blue")),
				("7D5929", _("Brown")),
                ("0050EF", _("Cobalt")),
                ("1BA1E2", _("Cyan")),				
				("999999", _("Grey")),
				("70AD11", _("Green")),
				("0047D4", _("Medium Blue")),				
				("C3461B", _("Orange")),
				("F472D0", _("Pink")),
				("E51400", _("Red")),
				("647687", _("Steel")),
				("6C0AAB", _("Violet")),
				("EEA00A", _("Yellow")),
				("ffffff", _("White"))
				])
				
config.plugins.SevenHD.SelectionBackground = ConfigSelection(default="000050EF", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
                ("000050EF", _("Cobalt")),
                ("001BA1E2", _("Cyan")),				
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("000047D4", _("Medium Blue")),				
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00EEA00A", _("Yellow")),
				("00ffffff", _("White"))
				])
				
config.plugins.SevenHD.Font1 = ConfigSelection(default="00fffff3", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
                ("000050EF", _("Cobalt")),
				("001BA1E2", _("Cyan")),
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("000047D4", _("Medium Blue")),				
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00EEA00A", _("Yellow")),
				("00fffff3", _("White"))
				])
				
config.plugins.SevenHD.Font2 = ConfigSelection(default="00fffff4", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
                ("000050EF", _("Cobalt")),
				("001BA1E2", _("Cyan")),
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("000047D4", _("Medium Blue")),				
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00EEA00A", _("Yellow")),
				("00fffff4", _("White"))
				])
				
config.plugins.SevenHD.ButtonText = ConfigSelection(default="00fffff2", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
                ("000050EF", _("Cobalt")),
				("001BA1E2", _("Cyan")),
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("000047D4", _("Medium Blue")),				
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00EEA00A", _("Yellow")),
				("00fffff2", _("White"))
				])
				
config.plugins.SevenHD.Border = ConfigSelection(default="00fffff1", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
                ("000050EF", _("Cobalt")),
				("001BA1E2", _("Cyan")),
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("000047D4", _("Medium Blue")),				
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00EEA00A", _("Yellow")),
				("00fffff1", _("White")),
				("ff000000", _("Off"))
				])
				
config.plugins.SevenHD.Progress = ConfigSelection(default="00fffff6", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
                ("000050EF", _("Cobalt")),
				("001BA1E2", _("Cyan")),
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("000047D4", _("Medium Blue")),				
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00EEA00A", _("Yellow")),
				("00fffff6", _("White"))
				])
				
config.plugins.SevenHD.Line = ConfigSelection(default="00fffff5", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
                ("000050EF", _("Cobalt")),
				("001BA1E2", _("Cyan")),
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("000047D4", _("Medium Blue")),				
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00EEA00A", _("Yellow")),
				("00fffff5", _("White"))
				])
				
config.plugins.SevenHD.SelectionBorder = ConfigSelection(default="00ffffff", choices = [
				("00F0A30A", _("Amber")),
				("00000000", _("Black")),
				("001B1775", _("Blue")),
				("007D5929", _("Brown")),
                ("000050EF", _("Cobalt")),
				("001BA1E2", _("Cyan")),
				("00999999", _("Grey")),
				("0070AD11", _("Green")),
				("000047D4", _("Medium Blue")),				
				("00C3461B", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("00647687", _("Steel")),
				("006C0AAB", _("Violet")),
				("00EEA00A", _("Yellow")),
				("00ffffff", _("White"))
				])	
				
config.plugins.SevenHD.InfobarStyle = ConfigSelection(default="infobar-style-original", choices = [
				("infobar-style-original", _("Original")),
				("infobar-style-xpicon", _("XPicon"))
				])
				
config.plugins.SevenHD.ChannelSelectionStyle = ConfigSelection(default="channelselection-twocolumns", choices = [
				("channelselection-twocolumns", _("Two Columns")),
				("channelselection-threecolumns", _("Three Columns")),
				("channelselection-xpicon", _("XPicon"))
				])

config.plugins.SevenHD.ButtonStyle = ConfigSelection(default="buttons_white", choices = [
				("buttons_white", _("White")),
				("buttons_black", _("Black"))
				])
# .:TBX:.
config.plugins.SevenHD.ClockStyle = ConfigSelection(default="clock-standard", choices = [
				("clock-standard", _("Standard")),
				("clock-seconds", _("with Seconds")),
                ("clock-analog", _("Analog")),
				("clock-weather", _("Weather"))
				])
				
config.plugins.SevenHD.WeatherStyle = ConfigYesNo(default = False)				
#######################################################################

class SevenHD(ConfigListScreen, Screen):
	skin = """
<screen name="SevenHD-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
   <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#1A000000" halign="left" valign="center" position="64,662" size="148,48" text="Cancel" transparent="1" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#1A000000" halign="left" valign="center" position="264,662" size="148,48" text="Save" transparent="1" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#1A000000" halign="left" valign="center" position="464,662" size="148,48" text="Reboot" transparent="1" />
  <widget name="config" position="70,73" scrollbarMode="showOnDemand" size="708,574" transparent="1" />
  <eLabel position="70,12" size="708,46" text="SevenHD - Konfigurationstool" font="Regular; 35" valign="center" halign="center" transparent="1" backgroundColor="#1A000000" foregroundColor="#00ffffff" name="," />
<eLabel position="891,88" size="372,46" text="Version: 1.0" font="Regular; 35" valign="center" halign="center" transparent="1" backgroundColor="#1A000000" foregroundColor="#00ffffff" name="," />
  <widget name="helperimage" position="891,178" size="372,328" zPosition="1" backgroundColor="#1A000000" />
  <eLabel backgroundColor="#1A000000" position="0,0" size="1280,720" transparent="0" zPosition="-9" />
  <widget backgroundColor="#1A000000" font="Regular2; 34" foregroundColor="#00ffffff" position="70,12" render="Label" size="708,46" source="Title" transparent="1" halign="center" valign="center" noWrap="1" />
    <eLabel backgroundColor="#1A000000" position="6,6" size="842,708" transparent="0" zPosition="-9" foregroundColor="#00ffffff" />
    <eLabel backgroundColor="#00ffffff" position="6,6" size="842,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="6,714" size="842,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="6,6" size="2,708" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="848,6" size="2,708" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="18,64" size="816,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="18,656" size="816,2" zPosition="2" />
    <ePixmap pixmap="SevenHD/buttons/key_red1.png" position="22,670" size="32,32" backgroundColor="#1A000000" alphatest="blend" />
    <ePixmap pixmap="SevenHD/buttons/key_green1.png" position="222,670" size="32,32" backgroundColor="#1A000000" alphatest="blend" />
    <ePixmap pixmap="SevenHD/buttons/key_yellow1.png" position="422,670" size="32,32" backgroundColor="#1A000000" alphatest="blend" />
    <ePixmap pixmap="SevenHD/buttons/key_blue1.png" position="622,670" size="32,32" backgroundColor="#1A000000" alphatest="blend" />
 <widget source="global.CurrentTime" render="Label" position="1154,16" size="100,28" font="Regular;26" halign="right" backgroundColor="#1A000000" transparent="1" valign="center" foregroundColor="#00ffffff">
      <convert type="ClockToText">Default</convert>
    </widget>
    <eLabel backgroundColor="#4A000000" position="878,6" size="396,708" transparent="0" zPosition="-9" />
    <eLabel backgroundColor="#00ffffff" position="878,6" size="396,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="878,714" size="396,2" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="878,6" size="2,708" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="1274,6" size="2,708" zPosition="2" />
</screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.datei = "/usr/share/enigma2/SevenHD/skin.xml"
		self.dateiTMP = self.datei + ".tmp"
		self.daten = "/usr/lib/enigma2/python/Plugins/Extensions/SevenHD/data/"
		self.komponente = "/usr/lib/enigma2/python/Plugins/Extensions/SevenHD/comp/"
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		list = []
		list.append(getConfigListEntry(_("______________________ System __________________________________"), ))
		list.append(getConfigListEntry(_("Image"), config.plugins.SevenHD.Image))
		list.append(getConfigListEntry(_("______________________ Colors __________________________________"), ))
		list.append(getConfigListEntry(_("Background Transparency"), config.plugins.SevenHD.BackgroundColorTrans))
		list.append(getConfigListEntry(_("Background"), config.plugins.SevenHD.Background))
		list.append(getConfigListEntry(_("Border"), config.plugins.SevenHD.Border))
		list.append(getConfigListEntry(_("Line"), config.plugins.SevenHD.Line))
		list.append(getConfigListEntry(_("Listselection"), config.plugins.SevenHD.SelectionBackground))
		list.append(getConfigListEntry(_("Listselection Border"), config.plugins.SevenHD.SelectionBorder))
		list.append(getConfigListEntry(_("Progress-/Volumebar"), config.plugins.SevenHD.Progress))
		list.append(getConfigListEntry(_("Font 1"), config.plugins.SevenHD.Font1))
		list.append(getConfigListEntry(_("Font 2"), config.plugins.SevenHD.Font2))
		list.append(getConfigListEntry(_("Button Text"), config.plugins.SevenHD.ButtonText))
		list.append(getConfigListEntry(_("Button Style"), config.plugins.SevenHD.ButtonStyle))
		list.append(getConfigListEntry(_("______________________ Infobar __________________________________"), ))
		list.append(getConfigListEntry(_("Style"), config.plugins.SevenHD.InfobarStyle))
		list.append(getConfigListEntry(_("Clock"), config.plugins.SevenHD.ClockStyle))
		list.append(getConfigListEntry(_("Weather"), config.plugins.SevenHD.WeatherStyle))
                list.append(getConfigListEntry(_("______________________ ChannelSelection __________________________________"), ))
		list.append(getConfigListEntry(_("Style"), config.plugins.SevenHD.ChannelSelectionStyle))
		
		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot, "blue": self.showInfo, "green": self.save,"cancel": self.exit}, -1)
		self.onLayoutFinish.append(self.UpdatePicture)

	def GetPicturePath(self):
		try:
			returnValue = self["config"].getCurrent()[1].value
			returnValue2 = self["config"].getCurrent()[0]
                        
                        #debug
                        #f = open('/tmp/debug', "w+")
                        #f.write(str(returnValue) + ' ' + str(returnValue2) + '\n')
                        #f.close()
                        
                        if str(returnValue2) == "Weather":
                           if str(returnValue) == "True":
                              path = "/usr/lib/enigma2/python/Plugins/Extensions/SevenHD/images/weather_on.jpg"
                           else:
                              path = "/usr/lib/enigma2/python/Plugins/Extensions/SevenHD/images/weather_off.jpg"
                        else:
                           path = "/usr/lib/enigma2/python/Plugins/Extensions/SevenHD/images/" + returnValue + ".jpg"
			
                        return path
		except:
			return "/usr/lib/enigma2/python/Plugins/Extensions/SevenHD/images/Sevenweather.jpg"

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
		self.ShowPicture()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.ShowPicture()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

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
		for x in self["config"].list:
			if len(x) > 1:
					x[1].save()
			else:
					pass

		try:
		    #global tag search and replace in all skin elements
			self.skinSearchAndReplace = []
			self.skinSearchAndReplace.append(["8C", config.plugins.SevenHD.BackgroundColorTrans.value])
			self.skinSearchAndReplace.append(["000000", config.plugins.SevenHD.Background.value])
			self.skinSearchAndReplace.append(["000050EF", config.plugins.SevenHD.SelectionBackground.value])
			self.skinSearchAndReplace.append(["00fffff3", config.plugins.SevenHD.Font1.value])
			self.skinSearchAndReplace.append(["00fffff4", config.plugins.SevenHD.Font2.value])
			self.skinSearchAndReplace.append(["00fffff2", config.plugins.SevenHD.ButtonText.value])
			self.skinSearchAndReplace.append(["00fffff6", config.plugins.SevenHD.Progress.value])
			self.skinSearchAndReplace.append(["00fffff1", config.plugins.SevenHD.Border.value])
			self.skinSearchAndReplace.append(["00fffff5", config.plugins.SevenHD.Line.value])
			self.skinSearchAndReplace.append(["buttons_white", config.plugins.SevenHD.ButtonStyle.value])
			
			self.selectionbordercolor = config.plugins.SevenHD.SelectionBorder.value
			self.borset = ("borset_" + self.selectionbordercolor + ".png")
			self.skinSearchAndReplace.append(["borset.png", self.borset])
			
			### Header
			self.appendSkinFile(self.daten + "header.xml")
			
			###ChannelSelection
			self.appendSkinFile(self.daten + config.plugins.SevenHD.ChannelSelectionStyle.value + ".xml")

			###Infobar_main
			self.appendSkinFile(self.daten + config.plugins.SevenHD.InfobarStyle.value + "_main.xml")
			
			###clock-style xml
                        self.appendSkinFile(self.daten + config.plugins.SevenHD.ClockStyle.value + ".xml")
                        
                        ###weather-style xml
                        if config.plugins.SevenHD.WeatherStyle.value == True:
                           self.appendSkinFile(self.daten + "weather-on.xml")
                        
                        ###Infobar_middle
			self.appendSkinFile(self.daten + config.plugins.SevenHD.InfobarStyle.value + "_middle.xml")
                        
                        ###clock-style xml
                        self.appendSkinFile(self.daten + config.plugins.SevenHD.ClockStyle.value + ".xml")
                        
                        ###Infobar_end
			self.appendSkinFile(self.daten + config.plugins.SevenHD.InfobarStyle.value + "_end.xml")
			
                        ###Main XML
			self.appendSkinFile(self.daten + "main.xml")
			
			###Plugins XML
			self.appendSkinFile(self.daten + "plugins.xml")
			
			###custom-main XML
			self.appendSkinFile(self.daten + config.plugins.SevenHD.Image.value + ".xml")
                           
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
		except:
			self.session.open(MessageBox, _("Error creating Skin!"), MessageBox.TYPE_ERROR)

		configfile.save()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
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

	def restartGUI(self, answer):
		if answer is True:
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
	session.open(SevenHD,"/usr/lib/enigma2/python/Plugins/Extensions/SevenHD/images/Sevencolors.jpg")

def Plugins(**kwargs):
	return PluginDescriptor(name="SevenHD", description=_("Configuration tool for SevenHD"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)