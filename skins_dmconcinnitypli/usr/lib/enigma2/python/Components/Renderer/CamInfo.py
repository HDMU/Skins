from Components.VariableText import VariableText
from enigma import eLabel
from Renderer import Renderer
from Tools.Directories import fileExists
from os import popen

class CamInfo(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.USERFILE = '/etc/clist.list'

    GUI_WIDGET = eLabel

    def changed(self, what):
        if not self.suspended:
            userLine = 'N/A'
            if fileExists(self.USERFILE):
                try:
                    myuf = 'cat ' + self.USERFILE
                    userLine = popen(myuf).readline()
                except:
                    userLine = 'No Cam'

            self.text = userLine

    def onShow(self):
        self.suspended = False
        self.changed(None)

    def onHide(self):
        self.suspended = True
