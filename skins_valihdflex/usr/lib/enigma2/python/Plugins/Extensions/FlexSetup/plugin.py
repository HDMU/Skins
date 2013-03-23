#######################################################################
#
#    Flex-Control for Dreambox/Enigma-2
#    Coded by Vali (c)2011 
#
#######################################################################



from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.config import config, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists
from skin import parseColor
from os import system



config.valiflex = ConfigSubsection()
config.valiflex.Style = ConfigSelection(default="flex", choices = [
				("flex", _("Flex-Standard")),
				("warp", _("W.A.R.P.")),
				("keyred", _("Key: Red")),
				("nikes", _("Nike's line"))
				])
config.valiflex.PiG = ConfigSelection(default="noPiG", choices = [("noPiG", _("Disabled")),("PiG", _("Enabled"))])
config.valiflex.Volume = ConfigSelection(default="slider", choices = [("slider", _("Colored slider")),("digits", _("Digits")), ("thinhor", _("Thin-Horizontal"))])
config.valiflex.VolumePRZ = ConfigSelection(default="dec", choices = [("dec", _("Disabled")),("prz", _("Enabled"))])
config.valiflex.extras = ConfigSelection(default="noUsr", choices = [("noUsr", _("Disabled")),("Usr", _("Enabled"))])
config.valiflex.OledInfo = ConfigSelection(default="12", choices = [("-1", _("Disabled")),("12", _("Date-Time")),("19", _("Date-Time/Temp")),("26", _("Date-Time/Temp/CPU"))])
config.valiflex.Font = ConfigSelection(default="nemesis", choices = [("bold", _("Bold font")),("thin", _("Thin font")),("nemesis", _("Nemesis LT-font"))])
config.valiflex.TunerInfo = ConfigSelection(default="provider", choices = [("provider", _("Provider")),("tuner", _("Tuner info"))])
config.valiflex.ibOffset = ConfigInteger(default=475, limits=(400, 600))
config.valiflex.GP3 = ConfigSelection(default="noGP3", choices = [("noGP3", _("Disabled")),("GP3", _("Enabled"))])
config.valiflex.M3 = ConfigSelection(default="noM3", choices = [("noM3", _("Disabled")),("M3", _("Enabled"))])
config.valiflex.MEPG = ConfigSelection(default="noMEPG", choices = [("noMEPG", _("Disabled")),("MEPG", _("Enabled"))])
config.valiflex.button = ConfigSelection(default="noButton", choices = [("noButton", _("Disabled")),("Button", _("Enabled"))])
config.valiflex.showEinfo = ConfigSelection(default="showE", choices = [("noE", _("Disabled")),("showE", _("Enabled"))])



def main(session, **kwargs):
	session.open(Flexsetup)



def Plugins(**kwargs):
	return PluginDescriptor(name="Vali-Flex Controller", description=_("Configuration tool for Flex-skin"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)



#######################################################################




class Flexsetup(ConfigListScreen, Screen):
	skin = """
		<screen name="Flexsetup" position="center,center" size="600,476" title="Flex settings...">
			<ePixmap alphatest="blend" pixmap="Vali.HD.flex/red.png" position="45,445" size="30,30" />
			<ePixmap alphatest="blend" pixmap="Vali.HD.flex/green.png" position="300,445" size="30,30" />
			<ePixmap alphatest="blend" pixmap="Vali.HD.flex/skin_default/buttons/vali.png" position="520,445" size="50,30" />
			<eLabel font="Regular;20" halign="left" position="80,448" size="180,26" text="Cancel" transparent="1" />
			<eLabel font="Regular;20" halign="left" position="335,448" size="180,26" text="Save" transparent="1" />
			<widget itemHeight="28" name="config" position="5,160" scrollbarMode="showOnDemand" size="590,280" />
			<widget name="mystyle" position="55,5" size="500,141" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.datei = "/usr/share/enigma2/Vali.HD.flex/skin.xml"
		self.daten = "/usr/lib/enigma2/python/Plugins/Extensions/FlexSetup/data/"
		self["mystyle"] = Pixmap()
		list = []
		list.append(getConfigListEntry(_("Infobar and window style:"), config.valiflex.Style))
		list.append(getConfigListEntry(_("Enable Mini-Video-Picture(PiG):"), config.valiflex.PiG))
		list.append(getConfigListEntry(_("Volume-screen style:"), config.valiflex.Volume))
		list.append(getConfigListEntry(_("Show volume text in percent:"), config.valiflex.VolumePRZ))
		list.append(getConfigListEntry(_("Include user file:"), config.valiflex.extras))
		list.append(getConfigListEntry(_("Incude GP3.2 screens:"), config.valiflex.GP3))
		list.append(getConfigListEntry(_("Include Merlin3 screens:"), config.valiflex.M3))
		list.append(getConfigListEntry(_("Include MerlinEPG-Center screens:"), config.valiflex.MEPG))
		list.append(getConfigListEntry(_("Show colored buttons in the infobar:"), config.valiflex.button))
		list.append(getConfigListEntry(_("Tuner info field properties:"), config.valiflex.TunerInfo))
		list.append(getConfigListEntry(_("Set skin regular font to:"), config.valiflex.Font))
		list.append(getConfigListEntry(_("OLED-info properties:"), config.valiflex.OledInfo))
		list.append(getConfigListEntry(_("Infobars offset: (original=475, +down/-up)"), config.valiflex.ibOffset))
		ConfigListScreen.__init__(self, list, on_change = self.UpdateComponents)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], 
									{
									"red": self.exit, 
									"green": self.save,
									"cancel": self.exit
									}, -1)
		self.onLayoutFinish.append(self.UpdateComponents)

	def UpdateComponents(self):
		#system("tar -xzvf " + self.daten  + "data-flex.tar.gz" + " -C /")
		prev_file = self.daten + "prev-" + config.valiflex.Style.value + ".png"
		if fileExists(prev_file):
			self["mystyle"].instance.setPixmapFromFile(prev_file)

	def save(self):
		for x in self["config"].list:
			x[1].save()
		try:
			skin_lines = []
			head_file = self.daten + "head.xml"
			skFile = open(head_file, "r")
			head_lines = skFile.readlines()
			skFile.close()
			for x in head_lines:
				skin_lines.append(x)
			vol_file = self.daten + "volume-" + config.valiflex.Volume.value + ".xml"
			skFile = open(vol_file, "r")
			file_lines = skFile.readlines()
			skFile.close()
			for x in file_lines:
				skin_lines.append(x)
			skn_file = self.daten + "skin-" + config.valiflex.Style.value + ".xml"
			skFile = open(skn_file, "r")
			file_lines = skFile.readlines()
			skFile.close()
			for x in file_lines:
				skin_lines.append(x)
			skn_file = self.daten + "Infobars-" + config.valiflex.GP3.value + ".xml"
			skFile = open(skn_file, "r")
			file_lines = skFile.readlines()
			skFile.close()
			newIBoffset = config.valiflex.ibOffset.value - 475
			for x in file_lines:
				if "AUTOFIELD" in x:
					if config.valiflex.TunerInfo.value == "provider":
						x = '			<convert type="ServiceName">Provider</convert>\n'
					elif config.valiflex.TunerInfo.value == "tuner":
						x = '			<convert type="valioTunerInfo" />\n'
				if not(newIBoffset == 0) and ('name="InfoBar"' in x):
						x = '	<screen backgroundColor="transparent" flags="wfNoBorder" name="InfoBar" position="0,' + str(475 + newIBoffset) + '" size="1280,240" title="InfoBar">\n'
				if "DMM-Buttons" in x:
					if config.valiflex.button.value == "Button":
						btn_file = self.daten + "Infobar_Buttons.xml"
						btFile = open(btn_file, "r")
						file_lines = btFile.readlines()
						btFile.close()
						for y in file_lines:
							skin_lines.append(y)
				skin_lines.append(x)
			skn_file = self.daten + "serviceselction-" + config.valiflex.PiG.value + ".xml"
			skFile = open(skn_file, "r")
			file_lines = skFile.readlines()
			skFile.close()
			for x in file_lines:
				if config.valiflex.M3.value=="M3":
					if "Merlin3Image" in x:
						x = '		<widget backgroundColor="#ffffffff" position="38,37" render="MiniTV" size="400,225" source="ServiceEventReference" zPosition="1">\n'
						skin_lines.append(x)
						x = '			<convert type="MiniTVDisplay" />\n'
						skin_lines.append(x)
						x = '		</widget>\n'
				skin_lines.append(x)
			base_file = self.daten + "main.xml"
			skFile = open(base_file, "r")
			file_lines = skFile.readlines()
			skFile.close()
			for x in file_lines:
				if config.valiflex.M3.value=="M3":
					if "Merlin3Image" in x:
						x = '		<widget backgroundColor="#ffffffff" position="38,37" render="MiniTV" size="400,225" source="ServiceEventReference" zPosition="1">\n'
						skin_lines.append(x)
						x = '			<convert type="MiniTVDisplay" />\n'
						skin_lines.append(x)
						x = '		</widget>\n'
				skin_lines.append(x)
			user_file = self.daten + "user.xml"
			if config.valiflex.extras.value=="Usr" and fileExists(user_file):
				skFile = open(user_file, "r")
				file_lines = skFile.readlines()
				skFile.close()
				for x in file_lines:
					skin_lines.append(x)
			M3_file = self.daten + "merlin3.xml"
			if config.valiflex.M3.value=="M3" and fileExists(M3_file):
				skFile = open(M3_file, "r")
				file_lines = skFile.readlines()
				skFile.close()
				for x in file_lines:
					skin_lines.append(x)
			MEPG_file = self.daten + "MerlinEPGCenter.xml"
			if config.valiflex.MEPG.value=="MEPG" and fileExists(MEPG_file):
				skFile = open(MEPG_file, "r")
				file_lines = skFile.readlines()
				skFile.close()
				for x in file_lines:
					if config.valiflex.M3.value=="M3":
						if "MerlinEPGCenter-TV" in x:
							x = '		<widget backgroundColor="#ffffffff" position="880,461" render="MiniTV" size="345,165" source="ServiceEventReference" zPosition="5">\n'
							skin_lines.append(x)
							x = '			<convert type="MiniTVDisplay" />\n'
							skin_lines.append(x)
							x = '		</widget>\n'						 						  
					skin_lines.append(x)
			if int(config.valiflex.OledInfo.value) > 1:
				oled_file = self.daten + "oled-on.xml"
			else:
				oled_file = self.daten + "oled-off.xml"
			skFile = open(oled_file, "r")
			file_lines = skFile.readlines()
			skFile.close()
			for x in file_lines:
				skin_lines.append(x)
			xFile = open(self.datei, "w")
			for xx in skin_lines:
				xFile.writelines(xx)
			xFile.close()
			system("tar -xzvf " + self.daten  + "x-" + config.valiflex.Style.value + ".tar.gz -C /")
			system("tar -xzvf " + self.daten  + "x-" + config.valiflex.Font.value + ".tar.gz -C /")
		except:
			self.session.open(MessageBox, _("Error by processing the data files !!!"), MessageBox.TYPE_ERROR)
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()

	def exit(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()







