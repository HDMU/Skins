#######################################################################
#
#    MyMetrix
#    Coded by iMaxxx (c) 2013
#    KravenZeroHD by Kraven
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
gettext.bindtextdomain("KravenZeroHD", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/KravenZeroHD/locale/"))

def _(txt):
	t = gettext.dgettext("KravenZeroHD", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block


#############################################################

config.plugins.KravenZeroHD = ConfigSubsection()

                 #Image

config.plugins.KravenZeroHD.Image = ConfigSelection(default="main-custom-openatv", choices = [
				("main-custom-atemio4you", _("Atemio4You")),
				("main-custom-hdmu", _("HDMU")),
				("main-custom-openatv", _("openATV")),
				("main-custom-openhdf", _("openHDF")),
				("main-custom-openmips", _("openMIPS"))
				])

				#Color

config.plugins.KravenZeroHD.SkinColor = ConfigSelection(default="00a19181", choices = [
				("00F0A30A", _("Amber")),
				("005696d2", _("Blue")),
				("00825A2C", _("Brown")),
				("000050EF", _("Cobalt")),
				("00911d10", _("Crimson")),
				("001BA1E2", _("Cyan")),
				("00a19181", _("Kraven")),
				("00a61d4d", _("Magenta")),
				("00A4C400", _("Lime")),
				("006A00FF", _("Indigo")),
				("0070ad11", _("Green")),
				("00008A00", _("Emerald")),
				("0076608A", _("Mauve")),
				("006D8764", _("Olive")),
				("00c3461b", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("007A3B3F", _("Sienna")),
				("00647687", _("Steel")),
				("00149baf", _("Teal")),
				("006c0aab", _("Violet")),
				("00bf9217", _("Yellow"))
				])
				

config.plugins.KravenZeroHD.SelectionBackground = ConfigSelection(default="0070ad11", choices = [
				("00F0A30A", _("Amber")),
				("005696d2", _("Blue")),
				("00825A2C", _("Brown")),
				("000050EF", _("Cobalt")),
				("00911d10", _("Crimson")),
				("001BA1E2", _("Cyan")),
				("00a19181", _("Kraven")),
				("00a61d4d", _("Magenta")),
				("00A4C400", _("Lime")),
				("006A00FF", _("Indigo")),
				("0070ad11", _("Green")),
				("00008A00", _("Emerald")),
				("0076608A", _("Mauve")),
				("006D8764", _("Olive")),
				("00c3461b", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("007A3B3F", _("Sienna")),
				("00647687", _("Steel")),
				("00149baf", _("Teal")),
				("006c0aab", _("Violet")),
				("00bf9217", _("Yellow"))
				])
				
				
config.plugins.KravenZeroHD.SkinColorProgress = ConfigSelection(default="00c3461b", choices = [
	            ("00F0A30A", _("Amber")),
				("005696d2", _("Blue")),
				("00825A2C", _("Brown")),
				("000050EF", _("Cobalt")),
				("00911d10", _("Crimson")),
				("001BA1E2", _("Cyan")),
				("00a19181", _("Kraven")),
				("00a61d4d", _("Magenta")),
				("00A4C400", _("Lime")),
				("006A00FF", _("Indigo")),
				("0070ad11", _("Green")),
				("00008A00", _("Emerald")),
				("0076608A", _("Mauve")),
				("006D8764", _("Olive")),
				("00c3461b", _("Orange")),
				("00F472D0", _("Pink")),
				("00E51400", _("Red")),
				("007A3B3F", _("Sienna")),
				("00647687", _("Steel")),
				("00149baf", _("Teal")),
				("006c0aab", _("Violet")),
				("00bf9217", _("Yellow"))
				])
				
	            #General
				
config.plugins.KravenZeroHD.InfobarStyle = ConfigSelection(default="infobar-style-x1", choices = [
				("infobar-style-x1", _("X1"))
				])
				
config.plugins.KravenZeroHD.ChannelSelectionStyle = ConfigSelection(default="channelselection-style-picon", choices = [
				("channelselection-style-xpicon", _("Picon")),
				("channelselection-style-nobile", _("Nobile")),
				("channelselection-style-minitv", _("MiniTV"))
				])				

config.plugins.KravenZeroHD.InfobarShowChannelname = ConfigSelection(default="infobar-channelname-none", choices = [
				("infobar-channelname-none", _("Off")),				
				("infobar-channelname-small-x1", _("Name")),	
				("infobar-channelname-number-small-x1", _("Name and Number"))
				])				

config.plugins.KravenZeroHD.InfobarWeatherWidget = ConfigSelection(default="infobar-weather-none", choices = [
				("infobar-weather-none", _("Off")),				
				("infobar-weather-big", _("On"))
				])	

config.plugins.KravenZeroHD.InfobarClockWidget = ConfigSelection(default="infobar-clock-classic", choices = [
				("infobar-clock-classic", _("Classic"))
				])				
				
config.plugins.KravenZeroHD.InfobarECMInfo = ConfigSelection(default="infobar-ecminfo-none", choices = [
				("infobar-ecminfo-x1", _("On")),
				("infobar-ecminfo-none", _("Off"))				
                ])
#######################################################################

class KravenZeroHD(ConfigListScreen, Screen):
	skin = """
<screen name="KravenZeroHD-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
  <eLabel font="Regular; 20" foregroundColor="foreground" backgroundColor="KravenPreBlack2" halign="left" position="37,667" size="250,24" text="Cancel" transparent="1" />
  <eLabel font="Regular; 20" foregroundColor="foreground" backgroundColor="KravenPreBlack2" halign="left" position="335,667" size="250,24" text="Save" transparent="1" />
  <eLabel font="Regular; 20" foregroundColor="foreground" backgroundColor="KravenPreBlack2" halign="left" position="643,667" size="250,24" text="Reboot" transparent="1" />
  <widget name="config" position="29,14" scrollbarMode="showOnDemand" size="590,632" transparent="1" />
  <eLabel position="738,15" size="349,43" text="KravenZeroHD" font="Regular; 35" valign="center" halign="center" transparent="1" backgroundColor="KravenPreBlack2" />
  <eLabel position="738,58" size="349,43" text="Version: 1.7.1" foregroundColor="foreground" font="Regular; 35" valign="center" backgroundColor="KravenPreBlack2" transparent="1" halign="center" />
  <widget name="helperimage" position="635,173" size="550,309" zPosition="1" backgroundColor="KravenPreBlack2" />
  <eLabel backgroundColor="BackgroundKraven" position="0,0" size="1280,720" transparent="0" zPosition="-9" />
  <ePixmap position="0,0" size="1280,149" zPosition="-9" pixmap="KravenZeroHD/infobar/ibaro.png" alphatest="blend" />
  <ePixmap position="0,555" size="1280,170" zPosition="-9" pixmap="KravenZeroHD/infobar/ibar.png" alphatest="blend" />
  <ePixmap pixmap="KravenZeroHD/buttons/key_red1.png" position="32,692" size="200,5" alphatest="blend" />
  <ePixmap pixmap="KravenZeroHD/buttons/key_green1.png" position="330,692" size="200,5" alphatest="blend" />
  <ePixmap pixmap="KravenZeroHD/buttons/key_yellow1.png" position="638,692" size="200,5" alphatest="blend" />
</screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.datei = "/usr/share/enigma2/KravenZeroHD/skin.xml"
		self.dateiTMP = self.datei + ".tmp"
		self.daten = "/usr/lib/enigma2/python/Plugins/Extensions/KravenZeroHD/data/"
		self.komponente = "/usr/lib/enigma2/python/Plugins/Extensions/KravenZeroHD/comp/"
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		list = []
		list.append(getConfigListEntry(_("----------------------------- Image  --------------------------------"), ))
		list.append(getConfigListEntry(_("Image"), config.plugins.KravenZeroHD.Image))
		list.append(getConfigListEntry(_("----------------------------- Color  --------------------------------"), ))
		list.append(getConfigListEntry(_("Font"), config.plugins.KravenZeroHD.SkinColor))
		list.append(getConfigListEntry(_("Listselection"), config.plugins.KravenZeroHD.SelectionBackground))
		list.append(getConfigListEntry(_("Progress-/Volumebar"), config.plugins.KravenZeroHD.SkinColorProgress))
		list.append(getConfigListEntry(_("----------------------------- General  --------------------------------"), ))
		list.append(getConfigListEntry(_("Channel Selection"), config.plugins.KravenZeroHD.ChannelSelectionStyle))
		list.append(getConfigListEntry(_("----------------------------- InfoBar  --------------------------------"), ))
		list.append(getConfigListEntry(_("ECM Info"), config.plugins.KravenZeroHD.InfobarECMInfo))
		list.append(getConfigListEntry(_("Channel Name"), config.plugins.KravenZeroHD.InfobarShowChannelname))
		list.append(getConfigListEntry(_("Weather"), config.plugins.KravenZeroHD.InfobarWeatherWidget))

		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot, "blue": self.showInfo, "green": self.save,"cancel": self.exit}, -1)
		self.onLayoutFinish.append(self.UpdatePicture)

	def GetPicturePath(self):
		try:
			returnValue = self["config"].getCurrent()[1].value
			path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenZeroHD/images/" + returnValue + ".jpg"
			return path
		except:
			return "/usr/lib/enigma2/python/Plugins/Extensions/KravenZeroHD/images/Kravenweather.jpg"

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
			self.skinSearchAndReplace.append(["005696d2", config.plugins.KravenZeroHD.SkinColor.value])
			self.skinSearchAndReplace.append(["0070ad11", config.plugins.KravenZeroHD.SelectionBackground.value])
			self.skinSearchAndReplace.append(["00c3461b", config.plugins.KravenZeroHD.SkinColorProgress.value])
			
			
			###Header XML
			self.appendSkinFile(self.daten + "header.xml")
			
			###InfoBar
			self.appendSkinFile(self.daten + "infobar-header.xml")

			#InfobarStyle
			self.appendSkinFile(self.daten + config.plugins.KravenZeroHD.InfobarStyle.value + ".xml")
			
			#ClockWidget
			self.appendSkinFile(self.daten + config.plugins.KravenZeroHD.InfobarClockWidget.value + ".xml")
			
			#WeatherWidget
			self.appendSkinFile(self.daten + config.plugins.KravenZeroHD.InfobarWeatherWidget.value + ".xml")
            #ECMInfo
			self.appendSkinFile(self.daten + config.plugins.KravenZeroHD.InfobarECMInfo.value + ".xml")			
			#ChannelName
			self.appendSkinFile(self.daten + config.plugins.KravenZeroHD.InfobarShowChannelname.value + ".xml")	

            #Footer
			self.appendSkinFile(self.daten + "screen-footer.xml")			
			
            #Channel Selection
			self.appendSkinFile(self.daten + config.plugins.KravenZeroHD.ChannelSelectionStyle.value +".xml")	
		
			
			###Main XML
			self.appendSkinFile(self.daten + "main.xml")
			
			###plugins XML
			self.appendSkinFile(self.daten + "plugins.xml")
			
			###custom-main XML
			self.appendSkinFile(self.daten + config.plugins.KravenZeroHD.Image.value + ".xml")
			
			
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
	session.open(KravenZeroHD,"/usr/lib/enigma2/python/Plugins/Extensions/KravenZeroHD/images/kravencolors.jpg")

def Plugins(**kwargs):
	return PluginDescriptor(name="KravenZeroHD", description=_("Configuration tool for KravenZeroHD"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)