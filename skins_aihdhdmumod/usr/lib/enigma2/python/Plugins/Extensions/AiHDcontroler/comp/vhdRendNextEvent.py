from Components.VariableText import VariableText
from enigma import eLabel, eEPGCache
from Renderer import Renderer
from time import localtime

class vhdRendNextEvent(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.epgcache = eEPGCache.getInstance()

    GUI_WIDGET = eLabel

    def changed(self, what):
        if not self.suspended:
            ref = self.source.service
            if ref:
                info = self.source.info
                if info is None:
                    self.text = ''
                    return
                ENext = ''
                eventNext = self.epgcache.lookupEvent(['IBDCTSERNX', (ref.toString(), 1, -1)])
                if eventNext:
                    t = eventNext[0][4] and localtime(eventNext[0][1])
                    duration = '%d min' % (eventNext[0][2] / 60)
                    ENext = '-->    %02d:%02d    %s\n%s' % (t[3],
                     t[4],
                     duration,
                     eventNext[0][4])
            self.text = ENext
