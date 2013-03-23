from Components.VariableText import VariableText
from enigma import eLabel, iServiceInformation
from Renderer import Renderer

class vhdRendVideoSize(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)

    GUI_WIDGET = eLabel

    def changed(self, what):
        service = self.source.service
        if service:
            info = service.info()
            if info is None:
                self.text = ''
                return
            xresol = info.getInfo(iServiceInformation.sVideoWidth)
            yresol = info.getInfo(iServiceInformation.sVideoHeight)
            self.text = xresol > 0 and str(xresol) + 'x' + str(yresol)
        else:
            self.text = '---'
