from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.Directories import fileExists

class TSCamdInfo(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)

    @cached
    def getText(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return ''
        camd = None
        if fileExists('/tmp/cam.info'):
            try:
                camdlist = open('/tmp/cam.info', 'r')
            except:
                return

        elif fileExists('/etc/clist.list'):
            try:
                camdlist = open('/etc/clist.list', 'r')
            except:
                return

        elif fileExists('/usr/lib/enigma2/python/Plugins/Bp/geminimain/lib/libgeminimain.so'):
            try:
                from Plugins.Bp.geminimain.plugin import GETCAMDLIST
                from Plugins.Bp.geminimain.lib import libgeminimain
                camdl = libgeminimain.getPyList(GETCAMDLIST)
                camd = None
                for x in camdl:
                    if x[1] == 1:
                        camd = x[2]

                return camd
            except:
                return

        else:
            camdlist = None
        if camdlist is not None:
            for current in camdlist:
                camd = current

            camdlist.close()
            return camd
        elif camd is not None:
            return camd
        else:
            return ''

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, what)
