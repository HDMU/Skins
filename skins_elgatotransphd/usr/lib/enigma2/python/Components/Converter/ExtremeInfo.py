from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll
from ServiceReference import ServiceReference
from enigma import eServiceCenter, eServiceReference, iServiceInformation, iPlayableService
from string import upper
from Components.ServiceEventTracker import ServiceEventTracker
from Tools.Directories import fileExists, resolveFilename
from os import environ, listdir, remove, rename, system
import gettext

class ExtremeInfo(Poll, Converter, object):
    BETACRYPT = 0
    SECACRYPT = 1
    NAGRACRYPT = 2
    VIACRYPT = 3
    CONAXCRYPT = 4
    IRDCRYPT = 5
    CRWCRYPT = 6
    NDSCRYPT = 7
    BETAECM = 8
    SECAECM = 9
    NAGRAECM = 10
    VIAECM = 11
    CONAXECM = 12
    IRDECM = 13
    CRWECM = 14
    NDSECM = 15

    def int2hex(self, int):
        return '%x' % int

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_interval = 2000
        self.poll_enabled = True
        self.list = []
        if type == 'EcmInfo':
            self.type = self.ECMINFO
        elif type == 'CaidInfo':
            self.type = self.CAIDINFO
        elif type == 'BetaCrypt':
            self.type = self.BETACRYPT
        elif type == 'IrdCrypt':
            self.type = self.IRDCRYPT
        elif type == 'SecaCrypt':
            self.type = self.SECACRYPT
        elif type == 'NagraCrypt':
            self.type = self.NAGRACRYPT
        elif type == 'ViaCrypt':
            self.type = self.VIACRYPT
        elif type == 'ConaxCrypt':
            self.type = self.CONAXCRYPT
        elif type == 'CrwCrypt':
            self.type = self.CRWCRYPT
        elif type == 'NdsCrypt':
            self.type = self.NDSCRYPT
        elif type == 'BetaEcm':
            self.type = self.BETAECM
        elif type == 'IrdEcm':
            self.type = self.IRDECM
        elif type == 'SecaEcm':
            self.type = self.SECAECM
        elif type == 'NagraEcm':
            self.type = self.NAGRAECM
        elif type == 'ViaEcm':
            self.type = self.VIAECM
        elif type == 'ConaxEcm':
            self.type = self.CONAXECM
        elif type == 'CrwEcm':
            self.type = self.CRWECM
        elif type == 'NdsEcm':
            self.type = self.NDSECM

    @cached
    def getText(self):
        service = self.source.service
        if service:
            info = service.info()
            return info or ''
        text = ''
        return text

    text = property(getText)

    @cached
    def getBoolean(self):
        service = self.source.service
        if service:
            info = service.info()
            if not info:
                return False
            if self.type == self.BETACRYPT:
                caemm = self.getBetaCrypt()
                return caemm
            if self.type == self.SECACRYPT:
                caemm = self.getSecaCrypt()
                return caemm
            if self.type == self.NAGRACRYPT:
                caemm = self.getNagraCrypt()
                return caemm
            if self.type == self.VIACRYPT:
                caemm = self.getViaCrypt()
                return caemm
            if self.type == self.CONAXCRYPT:
                caemm = self.getConaxCrypt()
                return caemm
            if self.type == self.IRDCRYPT:
                caemm = self.getIrdCrypt()
                return caemm
            if self.type == self.CRWCRYPT:
                caemm = self.getCrwCrypt()
                return caemm
            if self.type == self.NDSCRYPT:
                caemm = self.getNdsCrypt()
                return caemm
            if self.type == self.BETAECM:
                caemm = self.getBetaEcm()
                return caemm
            if self.type == self.SECAECM:
                caemm = self.getSecaEcm()
                return caemm
            if self.type == self.NAGRAECM:
                caemm = self.getNagraEcm()
                return caemm
            if self.type == self.VIAECM:
                caemm = self.getViaEcm()
                return caemm
            if self.type == self.CONAXECM:
                caemm = self.getConaxEcm()
                return caemm
            if self.type == self.IRDECM:
                caemm = self.getIrdEcm()
                return caemm
            if self.type == self.CRWECM:
                caemm = self.getCrwEcm()
                return caemm
            caemm = self.type == self.NDSECM and self.getNdsEcm()
            return caemm
        return False

    boolean = property(getBoolean)

    def parseEcmInfoLine(self, line):
        if line.__contains__(':'):
            idx = line.index(':')
            line = line[idx + 1:]
            line = line.replace('\n', '')
            while line.startswith(' '):
                line = line[1:]

            while line.endswith(' '):
                line = line[:-1]

            return line
        else:
            return ''

    def getBetaCrypt(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids and len(caids) > 0:
                        for caid in caids:
                            caid = self.int2hex(caid)
                            if len(caid) == 3:
                                caid = '0%s' % caid
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '17':
                                return True

        return False

    def getIrdCrypt(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids and len(caids) > 0:
                        for caid in caids:
                            caid = self.int2hex(caid)
                            if len(caid) == 3:
                                caid = '0%s' % caid
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '06':
                                return True

        return False

    def getSecaCrypt(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids and len(caids) > 0:
                        for caid in caids:
                            caid = self.int2hex(caid)
                            if len(caid) == 3:
                                caid = '0%s' % caid
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '01':
                                return True

        return False

    def getNagraCrypt(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids and len(caids) > 0:
                        for caid in caids:
                            caid = self.int2hex(caid)
                            if len(caid) == 3:
                                caid = '0%s' % caid
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '18':
                                return True

        return False

    def getViaCrypt(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids and len(caids) > 0:
                        for caid in caids:
                            caid = self.int2hex(caid)
                            if len(caid) == 3:
                                caid = '0%s' % caid
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '05':
                                return True

        return False

    def getConaxCrypt(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids and len(caids) > 0:
                        for caid in caids:
                            caid = self.int2hex(caid)
                            if len(caid) == 3:
                                caid = '0%s' % caid
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '0B':
                                return True

        return False

    def getCrwCrypt(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids and len(caids) > 0:
                        for caid in caids:
                            caid = self.int2hex(caid)
                            if len(caid) == 3:
                                caid = '0%s' % caid
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '0D':
                                return True

        return False

    def getNdsCrypt(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids and len(caids) > 0:
                        for caid in caids:
                            caid = self.int2hex(caid)
                            if len(caid) == 3:
                                caid = '0%s' % caid
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '09':
                                return True

        return False

    def getBetaEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
            try:
                f = open('/tmp/ecm.info', 'r')
                content = f.read()
                f.close()
            except:
                content = ''

            contentInfo = content.split('\n')
            for line in contentInfo:
                if line.startswith('caid:'):
                    caid = self.parseEcmInfoLine(line)
                    if caid.__contains__('x'):
                        idx = caid.index('x')
                        caid = caid[idx + 1:]
                        if len(caid) == 3:
                            caid = '0%s' % caid
                        caid = caid[:2]
                        caid = caid.upper()
                        if caid == '17':
                            return True

        return False

    def getIrdEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
            try:
                f = open('/tmp/ecm.info', 'r')
                content = f.read()
                f.close()
            except:
                content = ''

            contentInfo = content.split('\n')
            for line in contentInfo:
                if line.startswith('caid:'):
                    caid = self.parseEcmInfoLine(line)
                    if caid.__contains__('x'):
                        idx = caid.index('x')
                        caid = caid[idx + 1:]
                        if len(caid) == 3:
                            caid = '0%s' % caid
                        caid = caid[:2]
                        caid = caid.upper()
                        if caid == '06':
                            return True

        return False

    def getSecaEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
            try:
                f = open('/tmp/ecm.info', 'r')
                content = f.read()
                f.close()
            except:
                content = ''

            contentInfo = content.split('\n')
            for line in contentInfo:
                if line.startswith('caid:'):
                    caid = self.parseEcmInfoLine(line)
                    if caid.__contains__('x'):
                        idx = caid.index('x')
                        caid = caid[idx + 1:]
                        if len(caid) == 3:
                            caid = '0%s' % caid
                        caid = caid[:2]
                        caid = caid.upper()
                        if caid == '01':
                            return True

        return False

    def getNagraEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
            try:
                f = open('/tmp/ecm.info', 'r')
                content = f.read()
                f.close()
            except:
                content = ''

            contentInfo = content.split('\n')
            for line in contentInfo:
                if line.startswith('caid:'):
                    caid = self.parseEcmInfoLine(line)
                    if caid.__contains__('x'):
                        idx = caid.index('x')
                        caid = caid[idx + 1:]
                        if len(caid) == 3:
                            caid = '0%s' % caid
                        caid = caid[:2]
                        caid = caid.upper()
                        if caid == '18':
                            return True

        return False

    def getViaEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
            try:
                f = open('/tmp/ecm.info', 'r')
                content = f.read()
                f.close()
            except:
                content = ''

            contentInfo = content.split('\n')
            for line in contentInfo:
                if line.startswith('caid:'):
                    caid = self.parseEcmInfoLine(line)
                    if caid.__contains__('x'):
                        idx = caid.index('x')
                        caid = caid[idx + 1:]
                        if len(caid) == 3:
                            caid = '0%s' % caid
                        caid = caid[:2]
                        caid = caid.upper()
                        if caid == '05':
                            return True

        return False

    def getConaxEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
            try:
                f = open('/tmp/ecm.info', 'r')
                content = f.read()
                f.close()
            except:
                content = ''

            contentInfo = content.split('\n')
            for line in contentInfo:
                if line.startswith('caid:'):
                    caid = self.parseEcmInfoLine(line)
                    if caid.__contains__('x'):
                        idx = caid.index('x')
                        caid = caid[idx + 1:]
                        if len(caid) == 3:
                            caid = '0%s' % caid
                        caid = caid[:2]
                        caid = caid.upper()
                        if caid == '0B':
                            return True

        return False

    def getCrwEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
            try:
                f = open('/tmp/ecm.info', 'r')
                content = f.read()
                f.close()
            except:
                content = ''

            contentInfo = content.split('\n')
            for line in contentInfo:
                if line.startswith('caid:'):
                    caid = self.parseEcmInfoLine(line)
                    if caid.__contains__('x'):
                        idx = caid.index('x')
                        caid = caid[idx + 1:]
                        if len(caid) == 3:
                            caid = '0%s' % caid
                        caid = caid[:2]
                        caid = caid.upper()
                        if caid == '0D':
                            return True

        return False

    def getNdsEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
            try:
                f = open('/tmp/ecm.info', 'r')
                content = f.read()
                f.close()
            except:
                content = ''

            contentInfo = content.split('\n')
            for line in contentInfo:
                if line.startswith('caid:'):
                    caid = self.parseEcmInfoLine(line)
                    if caid.__contains__('x'):
                        idx = caid.index('x')
                        caid = caid[idx + 1:]
                        if len(caid) == 3:
                            caid = '0%s' % caid
                        caid = caid[:2]
                        caid = caid.upper()
                        if caid == '09':
                            return True

        return False
