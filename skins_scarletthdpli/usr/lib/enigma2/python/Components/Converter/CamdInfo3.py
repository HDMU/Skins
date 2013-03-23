from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.Directories import fileExists
import os

class CamdInfo3(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)

    @cached
    def getText(self):
        service = self.source.service
        if service:
            info = service.info()
            camd = ''
            return info or ''
        else:
            if fileExists('/tmp/.emu.info'):
                try:
                    camdlist = open('/tmp/.emu.info', 'r')
                except:
                    return

            elif fileExists('/etc/CurrentBhCamName'):
                try:
                    camdlist = open('/etc/CurrentBhCamName', 'r')
                except:
                    return

            elif fileExists('/etc/active_emu.list'):
                try:
                    camdlist = open('/etc/active_emu.list', 'r')
                except:
                    return

            elif fileExists('/tmp/egami.inf', 'r'):
                lines = open('/tmp/egami.inf', 'r').readlines()
                for line in lines:
                    item = line.split(':', 1)
                    if item[0] == 'Current emulator':
                        return item[1].strip()

            elif fileExists('/etc/init.d/softcam'):
                try:
                    camdlist = os.popen('/etc/init.d/softcam info')
                except:
                    return

            elif fileExists('/etc/init.d/cardserver'):
                try:
                    camdlist = os.popen('/etc/init.d/cardserver info')
                except:
                    return

            else:
                return
            if camdlist is not None:
                for current in camdlist.readlines():
                    camd = current

                camdlist.close()
                return camd
            return ''

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, what)
