# shamelessly copied from pliExpertInfo and edit by (aslan2006)

from enigma import iServiceInformation, iPlayableService
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config
from Tools.Transponder import ConvertToHumanReadable
from Tools.ISO639 import LanguageCodes
from Poll import Poll

def addspace(text):
	if text:
		text += " "
	return text

class VAudioInfo(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.type = type
		self.poll_interval = 1000
		self.poll_enabled = True
		self.feraw = self.fedata = self.updateFEdata = None

	def createAudioCodec(self,info):
		service = self.source.service
		audio = service.audioTracks()
		if audio:
			try:
				ct = audio.getCurrentTrack()
				i = audio.getTrackInfo(ct)
				languages = i.getLanguage()
				if "ger" in languages or "german" in languages or "deu" in languages:
					languages = "Deutsch"
				elif "und" in languages:
					languages = ""
				description = i.getDescription();
				if description in languages:
					description = ""
				return description + " " + languages
			except:
				return "unbekannt"

	@cached
	def getText(self):

		service = self.source.service
		if service is None:
			return ""
		info = service and service.info()

		if not info:
			return ""

		if self.type == "AudioCodec":
			return self.createAudioCodec(info)

		return _("invalid type")

	text = property(getText)

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC:
			if what[1] in (iPlayableService.evEnd, iPlayableService.evStart, iPlayableService.evUpdatedInfo):
				self.updateFEdata = True
			Converter.changed(self, what)
		elif what[0] == self.CHANGED_POLL and self.updateFEdata is not None:
			self.updateFEdata = False
			Converter.changed(self, what)

