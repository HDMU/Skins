from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.Directories import fileExists

class CamdInfo(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)

    @cached
    def getText(self):
        service = self.source.service
        if service:
            info = service.info()
            return info or ''
            camd = None
        if fileExists('/tmp/cam.info'):
            try:
                camdlist = open('/tmp/cam.info', 'r')
            except:
                return

        elif fileExists('/etc/active_emu.list'):
            try:
                camdlist = open('/etc/active_emu.list', 'r')
            except:
                return

        else:
            camdlist = None
        if camdlist is not None:
            for current in camdlist:
                camd = current

            camdlist.close()
            return camd
        else:
            return ''

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, what)
