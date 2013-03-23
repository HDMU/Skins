# Happy2000
#
# RollerLcd V1.1


from Renderer import Renderer
from enigma import eLabel
from enigma import ePoint, eTimer
from Components.VariableText import VariableText
from time import strftime


class RollerLcd1(VariableText, Renderer):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)

	GUI_WIDGET = eLabel

	def connect(self, source):
		Renderer.connect(self, source)
		self.changed((self.CHANGED_DEFAULT,))


	def changed(self, what):
		if (what[0] == self.CHANGED_CLEAR):
			self.text = ''
		else:
			self.clock = strftime("  %H:%M")
			self.text = self.source.text + self.clock
		if (self.instance):
			self.c = len(self.text) * 30
			self.c = ((self.c /4) + (150))
			self.x = 1  # 130------------------------------- start positie linker punt van de tekst
			self.status = 'start'
			self.instance.move(ePoint(1, 0))
			self.moveTimerText = eTimer()
			self.moveTimerText.timeout.get().append(self.moveTimerTextRun)
			self.moveTimerText.start(2000)

	def moveTimerTextRun(self):
		self.moveTimerText.stop()
		if (self.c > 1): 
			self.instance.move(ePoint(self.x, 0))  # Y positie waar de scrollende tekst komt
			self.x = (self.x - 1)
			self.c = (self.c - 1)
		if (self.c < 2):
			self.status = 'end'
			self.changed((self.CHANGED_DEFAULT,))
		if (self.status != 'end'):
			self.moveTimerText.start(20)





