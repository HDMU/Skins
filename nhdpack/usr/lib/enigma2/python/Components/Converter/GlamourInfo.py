from Components.Converter.Converter import Converter
from Components.Element import cached
from ServiceReference import ServiceReference
from enigma import eConsoleAppContainer, eServiceCenter, eServiceReference, iServiceInformation, iPlayableService, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable, eDVBFrontendParametersTerrestrial, eTimer
from time import localtime, strftime
from string import upper
from Components.ServiceEventTracker import ServiceEventTracker
from Tools.Directories import fileExists, resolveFilename
from os import environ, listdir, remove, rename, system, popen
from Components.ServiceEventTracker import ServiceEventTracker
from Components.config import config
import gettext

class GlamourInfo(Converter, object):
    TUNERINFO = 0
    ORBITAL = 1
    CAMNAME = 2
    ECMINFO = 3
    IRDCRYPT = 4
    SECACRYPT = 5
    NAGRACRYPT = 6
    VIACRYPT = 7
    CONAXCRYPT = 8
    BETACRYPT = 9
    CRWCRYPT = 10
    DREAMCRYPT = 11
    NDSCRYPT = 12
    BISSCRYPT = 13
    BULCRYPT = 14
    IRDECM = 15
    SECAECM = 16
    NAGRAECM = 17
    VIAECM = 18
    CONAXECM = 19
    BETAECM = 20
    CRWECM = 21
    DREAMECM = 22
    NDSECM = 23
    BISSECM = 24
    BULECM = 25
    CAIDINFO = 26
    FTA = 27
    EMU = 28
    CRD = 29
    NET = 30
    TUNERINFOBP = 31

    def __init__(self, type):
        Converter.__init__(self, type)
        self.list = []
        self.rescan = True
        self.DynTimer = eTimer()
        self.DynTimer.callback.append(self.doIt)
        self.interesting_events = {'EcmInfo': (self.ECMINFO, self.rescan),
         'IrdEcm': (self.IRDECM, self.rescan),
         'SecaEcm': (self.SECAECM, self.rescan),
         'NagraEcm': (self.NAGRAECM, self.rescan),
         'ViaEcm': (self.VIAECM, self.rescan),
         'ConaxEcm': (self.CONAXECM, self.rescan),
         'BetaEcm': (self.BETAECM, self.rescan),
         'CrwEcm': (self.CRWECM, self.rescan),
         'DreamEcm': (self.DREAMECM, self.rescan),
         'NdsEcm': (self.NDSECM, self.rescan),
         'BissEcm': (self.BISSECM, self.rescan),
         'BulEcm': (self.BULECM, self.rescan),
         'Emu': (self.EMU, self.rescan),
         'Crd': (self.CRD, self.rescan),
         'Net': (self.NET, self.rescan)}
        if type == 'TunerInfo':
            self.type = self.TUNERINFO
        elif type == 'Orbital':
            self.type = self.ORBITAL
        elif type == 'CamName':
            self.type = self.CAMNAME
        elif type == 'EcmInfo':
            self.type = self.ECMINFO
        elif type == 'CaidInfo':
            self.type = self.CAIDINFO
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
        elif type == 'BetaCrypt':
            self.type = self.BETACRYPT
        elif type == 'CrwCrypt':
            self.type = self.CRWCRYPT
        elif type == 'DreamCrypt':
            self.type = self.DREAMCRYPT
        elif type == 'NdsCrypt':
            self.type = self.NDSCRYPT
        elif type == 'BissCrypt':
            self.type = self.BISSCRYPT
        elif type == 'BulCrypt':
            self.type = self.BULCRYPT
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
        elif type == 'BetaEcm':
            self.type = self.BETAECM
        elif type == 'CrwEcm':
            self.type = self.CRWECM
        elif type == 'DreamEcm':
            self.type = self.DREAMECM
        elif type == 'NdsEcm':
            self.type = self.NDSECM
        elif type == 'BissEcm':
            self.type = self.BISSECM
        elif type == 'BulEcm':
            self.type = self.BULECM
        elif type == 'Fta':
            self.type = self.FTA
        elif type == 'Emu':
            self.type = self.EMU
        elif type == 'Crd':
            self.type = self.CRD
        elif type == 'Net':
            self.type = self.NET
        elif type == 'TunerInfoBP':
            self.type = self.TUNERINFOBP

    @cached
    def getText(self):
        service = self.source.service
        if service:
            info = service.info()
            if not info:
                return ''
            if info.getInfo(iServiceInformation.sIsCrypted):
                self.DynTimer.start(750)
            text = ''
            if self.type == self.TUNERINFO or self.type == self.TUNERINFOBP:
                if self.type == self.TUNERINFO:
                    self.tunertype = 'linelist'
                    tunerinfo = self.getTunerInfo(service)
                else:
                    self.tunertype = 'lineslist'
                    tunerinfo = self.getTunerInfo(service)
                text = tunerinfo
                return text
            if self.type == self.ORBITAL:
                if self.type == self.ORBITAL:
                    self.tunertype = 'linelist'
                    orbital = self.getOrbital(service)
                else:
                    self.tunertype = 'lineslist'
                    orbital = self.getOrbital(service)
                text = orbital
                return text
            camname = self.type == self.CAMNAME and self.getCamName()
            text = camname
        elif self.type == self.ECMINFO:
            ecmcam = self.getEcmCamInfo()
            text = ecmcam
        elif self.type == self.CAIDINFO:
            caidinfo = self.getCaidInfo()
            text = caidinfo
        return text

    text = property(getText)

    @cached
    def getBoolean(self):
        service = self.source.service
        if service:
            info = service.info()
            if not info:
                return False
            if info:
                self.DynTimer.start(700)
            if self.type == self.IRDCRYPT:
                caemm = self.getIrdCrypt()
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
            if self.type == self.BETACRYPT:
                caemm = self.getBetaCrypt()
                return caemm
            if self.type == self.CRWCRYPT:
                caemm = self.getCrwCrypt()
                return caemm
            if self.type == self.DREAMCRYPT:
                caemm = self.getDreamCrypt()
                return caemm
            if self.type == self.NDSCRYPT:
                caemm = self.getNdsCrypt()
                return caemm
            if self.type == self.BISSCRYPT:
                caemm = self.getBissCrypt()
                return caemm
            if self.type == self.BULCRYPT:
                caemm = self.getBulCrypt()
                return caemm
            if self.type == self.IRDECM:
                caemm = self.getIrdEcm()
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
            if self.type == self.BETAECM:
                caemm = self.getBetaEcm()
                return caemm
            if self.type == self.CRWECM:
                caemm = self.getCrwEcm()
                return caemm
            if self.type == self.DREAMECM:
                caemm = self.getDreamEcm()
                return caemm
            if self.type == self.NDSECM:
                caemm = self.getNdsEcm()
                return caemm
            if self.type == self.BISSECM:
                caemm = self.getBissEcm()
                return caemm
            if self.type == self.BULECM:
                caemm = self.getBulEcm()
                return caemm
            if self.type == self.FTA:
                caemm = self.getFta()
                return caemm
            if self.type == self.EMU:
                caemm = self.getEmu()
                return caemm
            if self.type == self.CRD:
                caemm = self.getCrd()
                return caemm
            caemm = self.type == self.NET and self.getNet()
            return caemm
        return False

    boolean = property(getBoolean)

    def changed(self, what):
        self.what = what
        if what[0] in self.interesting_events:
            Converter.changed(self, what)
        Converter.changed(self, what)

    def getFta(self):
        service = self.source.service
        if service:
            info = service.info()
            if not info:
                return False
            return info.getInfo(iServiceInformation.sIsCrypted) or True
        return False

    def getEmu(self):
        try:
            f = open('/tmp/ecm.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        for line in contentInfo:
            if line.startswith('using:') or line.startswith('source:'):
                using = self.parseEcmInfoLine(line)
                if using == 'emu':
                    return True

        return False

    def getCrd(self):
        try:
            f = open('/tmp/ecm.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        for line in contentInfo:
            if line.startswith('using:'):
                using = self.parseEcmInfoLine(line)
                if using == 'sci':
                    return True
            elif line.startswith('from:'):
                using = self.parseEcmInfoLine(line)
                if using.__contains__('local'):
                    return True

        return False

    def getNet(self):
        try:
            f = open('/tmp/ecm.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        for line in contentInfo:
            if line.startswith('using:'):
                using = self.parseEcmInfoLine(line)
                if using != 'fta' and using != 'emu' and using != 'sci':
                    return True
            elif line.startswith('source:'):
                using = self.parseEcmInfoLine(line)
                using = using[:3]
                if using == 'net':
                    return True
            elif line.startswith('from:'):
                using = self.parseEcmInfoLine(line)
                if using.__contains__('.'):
                    return True

        return False

    def getIrdEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
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
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
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
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
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
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
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
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '0B':
                                return True

        return False

    def getBetaEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '17':
                                return True

        return False

    def getCrwEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '0D':
                                return True

        return False

    def getDreamEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                            if caid == '4A':
                                return True
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '4A':
                                return True

        return False

    def getNdsEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '09':
                                return True

        return False

    def getBissEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                            if caid == '26':
                                return True
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '26':
                                return True

        return False

    def getBulEcm(self):
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    try:
                        f = open('/tmp/ecm.info', 'r')
                        content = f.read()
                        f.close()
                    except:
                        content = ''

                    contentInfo = content.split('\n')
                    return content == '' and False
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
                            if caid == '55':
                                return True
                    elif line.startswith('====='):
                        caid = self.parseInfoLine(line)
                        if caid.__contains__('x'):
                            idx = caid.index('x')
                            caid = caid[idx + 1:]
                            caid = caid[:2]
                            caid = caid.upper()
                            if caid == '55':
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

    def getDreamCrypt(self):
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
                            if caid == '4A':
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

    def getBissCrypt(self):
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
                            if caid == '26':
                                return True

        return False

    def getBulCrypt(self):
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
                            if caid == '55':
                                return True

        return False

    def int2hex(self, int):
        return '%x' % int

    def getCaidInfo(self):
        service = self.source.service
        cainfo = 'Caid(s):  '
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
                            caid = caid.upper()
                            cainfo += caid
                            cainfo += '  '

                        return cainfo
        return 'Free To Air'

    def getCamName(self):
        emu = ''
        cs = ''
        try:
            f = open('/etc/info.list', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            cas = content
            if cas.__contains__('no'):
                f.close()
            else:
                return cas
        try:
            f = open('/usr/bin/emuactive', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            emu = content
            if emu.__contains__('\n'):
                idx = emu.index('\n')
                emu = emu[:idx]
        try:
            f = open('/usr/bin/csactive', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        if content != '':
            cs = content
            if cs.__contains__('\n'):
                idx = cs.index('\n')
                cs = cs[:idx]
        if cs != '' and emu != '':
            emu += ' + '
            emu += cs
            return emu
        if cs == '' and emu != '':
            return emu
        if cs != '' and emu == '':
            return cs
        try:
            f = open('/tmp/cam.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/etc/CurrentDelCamName', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/etc/CurrentBhCamName', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/etc/clist.list', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/etc/emud/emu.default', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/etc/active_emu.list', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/tmp/gbp_cam.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/etc/init.d/current_cam.sh', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            for line in contentInfo:
                if line.startswith('EMUNAME='):
                    idex = line.index('=')
                    line = line[idex + 2:-1]
                    return line

        try:
            f = open('/etc/init.d/current_cam.sh', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            for line in contentInfo:
                if line.startswith('USERNAME='):
                    idex = line.index('=')
                    line = line[idex + 2:-1]
                    return line

        try:
            f = open('/etc/rc3.d/S98emustart', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            for line in contentInfo:
                if line.startswith('EMUNAME='):
                    idex = line.index('=')
                    line = line[idex + 2:-1]
                    return line

        try:
            f = open('/usr/LTCAM/current_CAM', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            for line in contentInfo:
                if line.startswith('CAM_'):
                    idex = line.index('_')
                    line = line[idex + 1:-3]
                    return line

        try:
            f = open('/tmp/ucm_cam.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/tmp/ucm_srv.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/etc/init.d/softcam', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            for line in contentInfo:
                if line.__contains__('usr/bin/'):
                    idex = line.index('n/')
                    line = line[idex + 2:]
                    return line

        try:
            f = open('/etc/SoftcamsAutostart', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
        try:
            f = open('/tmp/cam.check.log', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            for line in contentInfo:
                if line.__contains__(':'):
                    idex = line.index(':')
                    line = line[idex + 4:]
                    line = line.replace('running OK', '')
                    return line

        try:
            f = open('/tmp/.oscam/oscam.version', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            for line in contentInfo:
                if line.startswith('version:') or line.startswith('Version:'):
                    idex = line.index('-')
                    line = line[idex - 4:]
                    line = line.replace('-unstable_svn', '')
                    line = 'Oscam ' + line
                    return line

        return 'No/Unknown emu'

    def getEcmCamInfo(self):
        if self.getFta():
            return ' '
        ecmInfoString = ''
        using = ''
        address = ''
        prtc = ''
        osr = ''
        osfr = ''
        hops = ''
        ecmTime = ''
        ecmt = ''
        casys = ''
        state = 'Source: '
        try:
            f = open('/tmp/ecm.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        for line in contentInfo:
            if line.startswith('====='):
                castr = self.parseInfoLine(line)
                if castr.__contains__('x'):
                    idx = castr.index('x')
                    castr = castr[idx + 1:]
                    castr = castr[:4]
            if line.startswith('prov:'):
                prov = self.parseEcmInfoLine(line)
                if prov.__contains__('x'):
                    idx = prov.index('x')
                    prov = prov[idx + 1:]
                    prov = prov[:6]
                casys = 'CA: ' + castr + ':' + prov
            if line.startswith('source: net'):
                idex = line.index('(')
                line = line[idex:]
                line = line.replace('\n', '')
                if line.__contains__('cccamd'):
                    line = str(line.split(' ')[2].split())
                    line = '  Source: net \nusing: CCcam@' + line[2:-3]
                elif line.__contains__('newcamd'):
                    line = str(line.split(' ')[2].split())
                    line = '   Source: net \nusing: NewCS@' + line[2:-3]
                    if line.__contains__('127.0.0.1'):
                        line = '   Source: NewCS with local card in slot'
                ecmInfoString = casys + line + '  Ecm time: '
            if line.startswith('reader:'):
                osr = self.parseEcmInfoLine(line)
                osr = '    Source: ' + osr
            if line.startswith('from:'):
                osfr = self.parseEcmInfoLine(line)
                osfr = '@' + osfr
            if line.startswith('protocol:'):
                prtc = self.parseEcmInfoLine(line)
                prtc = '\nusing: ' + prtc
            if line.startswith('ecm'):
                ecmt = self.parseEcmInfoLine(line)
                ecmt = '   Ecm Time: ' + ecmt
                ecmInfoString = casys + osr + osfr + prtc + address + hops + ecmt
                return ecmInfoString
            if line.startswith('source: emu'):
                using = self.parseEcmInfoLine(line)
                ecmInfoString = casys + '   Source: '
                ecmInfoString += using
                return ecmInfoString
            if line.__contains__('msec -- '):
                ecmTime = line.partition(' -- ')[0]
                ecmInfoString += ecmTime
                return ecmInfoString
            if line.startswith('using:'):
                using = self.parseEcmInfoLine(line)
            elif line.startswith('provider:'):
                provider = '%s %s' % (_(' Provider:'), self.parseEcmInfoLine(line))
                if len(provider) > 48:
                    provider = '%s...' % provider[:47]
            elif line.startswith('caid:'):
                castr = self.parseEcmInfoLine(line)
                if castr.__contains__('x'):
                    idx = castr.index('x')
                    castr = castr[idx + 1:]
                    if len(castr) == 3:
                        castr = '0%s' % castr
                    castr = castr.upper()
            elif line.startswith('provid:'):
                idstr = self.parseEcmInfoLine(line)
                if idstr.__contains__('x'):
                    idx = idstr.index('x')
                    idstr = idstr[idx + 1:]
                    if len(idstr) == 3:
                        idstr = '0%s' % idstr
                    idstr = idstr.upper()
                casys = 'CA: ' + castr + ':' + idstr + '  ' + provider + '\n'
            elif line.startswith('address:'):
                address = '%s %s' % ('Address:', self.parseEcmInfoLine(line))
                if address == ' Source: /dev/sci0':
                    state = ' Source: Lower slot'
                if address == ' Source: /dev/sci1':
                    state = ' Source: Upper slot'
                if address != ' Source: /dev/sci0' and address != ' Source: /dev/sci1':
                    state = address
                if len(state) > 51:
                    state = '%s...' % state[:50]
            elif line.startswith('hops:'):
                hops = '%s %s' % (_('  Hops:'), self.parseEcmInfoLine(line))
            elif line.startswith('ecm time:'):
                ecmTime = '%s %s' % (_('  Ecm time:'), self.parseEcmInfoLine(line))

        if casys != '':
            ecmInfoString = '%s ' % casys
        if state != 'Source: ':
            ecmInfoString = '%s%s ' % (ecmInfoString, state)
        if state == 'Source: ':
            ecmInfoString += 'Source: '
            ecmInfoString = '%s%s ' % (ecmInfoString, using)
        if hops != '' and hops != ' Hops: 0':
            ecmInfoString = '%s%s ' % (ecmInfoString, hops)
        if ecmTime != '':
            ecmInfoString = '%s%s ' % (ecmInfoString, ecmTime)
        if using == '':
            return '  '
        return ecmInfoString

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

    def parseInfoLine(self, line):
        if line.__contains__('CaID'):
            idx = line.index('D')
            line = line[idx + 1:]
            line = line.replace('\n', '')
            while line.startswith(' '):
                line = line[1:]

            while line.endswith(' '):
                line = line[:-1]

            return line
        else:
            return ''

    def doIt(self):
        self.DynTimer.stop()
        if self.rescan == True:
            self.rescan = False
        ee = 1000
        self.DynTimer.start(ee, True)
        Converter.changed(self, self.what)

    def getTunerInfo(self, service):
        tunerinfo = ''
        if service:
            feinfo = service.frontendInfo()
            if feinfo is not None:
                if feinfo:
                    frontendData = feinfo.getAll(True)
                    if frontendData is not None:
                        if frontendData.get('tuner_type') == 'DVB-S' or frontendData.get('tuner_type') == 'DVB-C' or frontendData.get('tuner_type') == 'DVB-T':
                            frequency = str(frontendData.get('frequency') / 1000)
                            terra = str(frontendData.get('frequency') / 1000000)
                            symbolrate = str(int(frontendData.get('symbol_rate', 0) / 1000))
                            if frontendData.get('tuner_type') == 'DVB-S':
                                [frontendData.get('None')]
                                pol = self.tunertype == 'linelist' and {eDVBFrontendParametersSatellite.Polarisation_Horizontal: 'H',
                                 eDVBFrontendParametersSatellite.Polarisation_Vertical: 'V',
                                 eDVBFrontendParametersSatellite.Polarisation_CircularLeft: 'CL',
                                 eDVBFrontendParametersSatellite.Polarisation_CircularRight: 'CR'}[frontendData.get('polarization', eDVBFrontendParametersSatellite.Polarisation_Horizontal)]
                            else:
                                pol = {eDVBFrontendParametersSatellite.Polarisation_Horizontal: 'Horizontal',
                                 eDVBFrontendParametersSatellite.Polarisation_Vertical: 'Vertical',
                                 eDVBFrontendParametersSatellite.Polarisation_CircularLeft: 'Circular Left',
                                 eDVBFrontendParametersSatellite.Polarisation_CircularRight: 'Circular Right'}[frontendData.get('polarization', eDVBFrontendParametersSatellite.Polarisation_Horizontal)]
                            fec = {eDVBFrontendParametersSatellite.FEC_None: 'None',
                             eDVBFrontendParametersSatellite.FEC_Auto: 'Auto',
                             eDVBFrontendParametersSatellite.FEC_1_2: '1/2',
                             eDVBFrontendParametersSatellite.FEC_2_3: '2/3',
                             eDVBFrontendParametersSatellite.FEC_3_4: '3/4',
                             eDVBFrontendParametersSatellite.FEC_5_6: '5/6',
                             eDVBFrontendParametersSatellite.FEC_7_8: '7/8',
                             eDVBFrontendParametersSatellite.FEC_3_5: '3/5',
                             eDVBFrontendParametersSatellite.FEC_4_5: '4/5',
                             eDVBFrontendParametersSatellite.FEC_8_9: '8/9',
                             eDVBFrontendParametersSatellite.FEC_9_10: '9/10'}[frontendData.get('fec_inner', eDVBFrontendParametersSatellite.FEC_Auto)]
                            tunerinfo = self.tunertype == 'linelist' and 'Freq: ' + frequency + '  ' + pol + '  ' + 'SR: ' + symbolrate + '  ' + 'FEC: ' + fec
                        else:
                            tunerinfo = '\nFrequency: ' + frequency + '\nPolarisation: ' + pol + '\nSymbolrate: ' + symbolrate + '\nFEC: ' + fec
                    elif frontendData.get('tuner_type') == 'DVB-C':
                        fec = {eDVBFrontendParametersCable.FEC_None: 'None',
                         eDVBFrontendParametersCable.FEC_Auto: 'Auto',
                         eDVBFrontendParametersCable.FEC_1_2: '1/2',
                         eDVBFrontendParametersCable.FEC_2_3: '2/3',
                         eDVBFrontendParametersCable.FEC_3_4: '3/4',
                         eDVBFrontendParametersCable.FEC_5_6: '5/6',
                         eDVBFrontendParametersCable.FEC_7_8: '7/8',
                         eDVBFrontendParametersCable.FEC_8_9: '8/9'}[frontendData.get('fec_inner', eDVBFrontendParametersCable.FEC_Auto)]
                        if self.tunertype == 'linelist':
                            tunerinfo = 'Freq: ' + frequency + '  ' + 'SR: ' + symbolrate + '  ' + 'FEC: ' + fec
                        else:
                            tunerinfo = 'Frequency: ' + frequency + '\nSymbolrate: ' + symbolrate + '\nFEC: ' + fec
                    elif frontendData.get('tuner_type') == 'DVB-T':
                        [frontendData.get('None')]
                        if self.tunertype == 'linelist':
                            modulation = {eDVBFrontendParametersTerrestrial.Modulation_Auto: 'Auto',
                             eDVBFrontendParametersTerrestrial.Modulation_QPSK: 'QPSK',
                             eDVBFrontendParametersTerrestrial.Modulation_QAM16: 'QAM16',
                             eDVBFrontendParametersTerrestrial.Modulation_QAM64: 'QAM64'}[frontendData.get('constellation', eDVBFrontendParametersTerrestrial.Modulation_Auto)]
                        lp = {eDVBFrontendParametersTerrestrial.FEC_Auto: 'Auto',
                         eDVBFrontendParametersTerrestrial.FEC_1_2: '1/2',
                         eDVBFrontendParametersTerrestrial.FEC_2_3: '2/3',
                         eDVBFrontendParametersTerrestrial.FEC_3_4: '3/4',
                         eDVBFrontendParametersTerrestrial.FEC_5_6: '5/6',
                         eDVBFrontendParametersTerrestrial.FEC_7_8: '7/8'}[frontendData.get('code_rate_lp', eDVBFrontendParametersTerrestrial.FEC_Auto)]
                        hp = {eDVBFrontendParametersTerrestrial.FEC_Auto: 'Auto',
                         eDVBFrontendParametersTerrestrial.FEC_1_2: '1/2',
                         eDVBFrontendParametersTerrestrial.FEC_2_3: '2/3',
                         eDVBFrontendParametersTerrestrial.FEC_3_4: '3/4',
                         eDVBFrontendParametersTerrestrial.FEC_5_6: '5/6',
                         eDVBFrontendParametersTerrestrial.FEC_7_8: '7/8'}[frontendData.get('code_rate_hp', eDVBFrontendParametersTerrestrial.FEC_Auto)]
                        gi = {eDVBFrontendParametersTerrestrial.GuardInterval_Auto: 'Auto',
                         eDVBFrontendParametersTerrestrial.GuardInterval_1_32: '1/32',
                         eDVBFrontendParametersTerrestrial.GuardInterval_1_16: '1/16',
                         eDVBFrontendParametersTerrestrial.GuardInterval_1_8: '1/8',
                         eDVBFrontendParametersTerrestrial.GuardInterval_1_4: '1/4'}[frontendData.get('guard_interval', eDVBFrontendParametersTerrestrial.GuardInterval_Auto)]
                        if self.tunertype == 'linelist':
                            tunerinfo = 'Freq: ' + terra + ' Mhz ' + ' Mod: ' + modulation + ' LP: ' + lp + ' HP: ' + hp + ' GI: ' + gi
                        else:
                            tunerinfo = 'Frequency: ' + frequency + '\nMod: ' + modulation + '\nGI: ' + gi
                    elif self.tunertype == 'linelist':
                        tunerinfo = frequency + '  ' + symbolrate
                    else:
                        tunerinfo = 'Frequency: ' + frequency + '\nSymbolrate: ' + symbolrate
                    return tunerinfo
            else:
                return ''

    def getOrbital(self, service):
        orbital = ''
        if service:
            feinfo = service.frontendInfo()
            if feinfo is not None:
                if feinfo:
                    frontendData = feinfo.getAll(True)
                    if frontendData is not None:
                        if (frontendData.get('tuner_type') == 'DVB-S' or frontendData.get('tuner_type') == 'DVB-C' or frontendData.get('tuner_type') == 'DVB-T') and frontendData.get('tuner_type') == 'DVB-S':
                            try:
                                orb = {3592: 'Thor 5,6/Intelsat 10-02 (0.8W)',
                                 3591: 'Thor 5,6/Intelsat 10-02 (1.0W)',
                                 3590: 'Thor 5,6/Intelsat 10-02 (1.0W)',
                                 3560: 'Amos 2,3/Thor 3 (4.0W)',
                                 3557: 'Thor 3 (4.3W)',
                                 3550: 'Atlantic Bird 3 (5.0W)',
                                 3530: 'Nilesat/Atlantic Bird 4A (7.0W)',
                                 3528: 'Atlantic Bird 4A (7.2W)',
                                 3520: 'Atlantic Bird 2 (8.0W)',
                                 3490: 'Express AM44 (11.0W)',
                                 3475: 'Atlantic Bird 1 (12.5W)',
                                 3460: 'Express A4 (14.0W)',
                                 3450: 'Telstar 12 (15.0W)',
                                 3420: 'Intelsat 901 (18.0W)',
                                 3400: 'NSS 5 (20.0W)',
                                 3380: 'NSS 7 (22.0W)',
                                 3355: 'Intelsat 905 (24.5W)',
                                 3325: 'Intelsat 907 (27.5W)',
                                 3300: 'Hispasat 1C,1D (30.0W)',
                                 3285: 'Intelsat 801 (31.5W)',
                                 3255: 'Intelsat 903 (34.5W)',
                                 3225: 'NSS 10/Telstar 11N (37.5W)',
                                 3195: 'NSS 806 (40.5W)',
                                 3170: 'Intelsat 11 (43.0W)',
                                 3150: 'Intelsat 14 (45.0W)',
                                 3100: 'Intelsat 1R (50.0W)',
                                 3099: 'Intelsat 1R (50.1W)',
                                 3070: 'Intelsat  707 (53.0W)',
                                 3045: 'Intelsat 805 (55.5W)',
                                 3020: 'Intelsat 9 (58.0W)',
                                 2990: 'Amazonas (61.0W)',
                                 2985: 'Echostar 3,12 (61.5W)',
                                 2970: 'Telstar 14 (63.0W)',
                                 2950: 'Star One C1 (65.0W)',
                                 2900: 'Star One C2 (70.0W)',
                                 2880: 'AMC 6/Nahuel 1 (72.0W)',
                                 2875: 'DirecTV 1R/Nimiq 5 (72.5W)',
                                 2860: 'Horizons 2 (74.0W)',
                                 2850: 'Brasilsat B3/DirecTV 12 (75.0W)',
                                 2830: 'Echostar 1,4,8 (77.0W)',
                                 2820: 'Simon Bolivar (77.0W)',
                                 2810: 'AMC 5 (79.0W)',
                                 2780: 'Nimiq 4 (82.0W)',
                                 2770: 'AMC 9 (83.0W)',
                                 2760: 'Brasilsat B4 (84.0W)',
                                 2750: 'AMC 16 (85.0W)',
                                 2730: 'AMC 3 (87.0W)',
                                 2710: 'Galaxy 28 (89.0W)',
                                 2690: 'Galaxy 17/Nimiq 1,2 (91.0W)',
                                 2669: 'Galaxy 25 (93.1W)',
                                 2650: 'Galaxy 3C/Spaceway 3 (95.0W)',
                                 2630: 'Galaxy 19 (97.0W)',
                                 2610: 'Galaxy 16 (99.0W)',
                                 2590: 'AMC 2,4/DirecTV 4S,8 (101.0W)',
                                 2572: 'DirecTV 10/Spaceway 1 (102.8W)',
                                 2570: 'AMC 1 (103.0W)',
                                 2550: 'AMC 15/18 (105.0W)',
                                 2527: 'Anik F1,F1R (107.3W)',
                                 2500: 'DirecTV 5/EchoStar 10,11 (110.0W)',
                                 2489: 'Anik F2 (111.1W)',
                                 2470: 'SatMex 6 (113.0W)',
                                 2432: 'SatMex 5 (116.8W)',
                                 2410: 'Anik F3/DirecTV 7S/EchoStar 7 (119.0W)',
                                 2390: 'EchoStar 9/Galaxy 23 (121.0W)',
                                 2370: 'Galaxy 12,18 (123.0W)',
                                 2350: 'AMC 21/Galaxy 14 (125.0W)',
                                 2330: 'Galaxy 13/Horizons 1 (127.0W)',
                                 2310: 'Ciel 2/Galaxy 27 (129.0W)',
                                 2290: 'AMC 11 (131.0W)',
                                 2270: 'Galaxy 15 (133.0W)',
                                 2250: 'AMC 10 (135.0W)',
                                 2230: 'AMC 7 (137.0W)',
                                 2210: 'AMC 8 (139.0W)',
                                 2120: 'Echostar 2 (148.0W)',
                                 1830: 'NSS 9 (177.0W)',
                                 1800: 'Intelsat 701 (180.0E)',
                                 1720: 'GE 23 (172.0E)',
                                 1690: 'Intelsat 2,5 (169.0E)',
                                 1660: 'Intelsat 8 (166.0E)',
                                 1620: 'Superbird B2 (162.0E)',
                                 1600: 'Optus D1 (160.0E)',
                                 1560: 'Optus C1/D3 (156.0E)',
                                 1540: 'JCSAT 2A (154.0E)',
                                 1520: 'Optus D2 (152.0E)',
                                 1500: 'JCSAT 1B (150.0E)',
                                 1460: 'Agila 2 (146.0E)',
                                 1440: 'Superbird C2 (144.0E)',
                                 1380: 'Express AM3 (140.0E)',
                                 1380: 'Telstar 18 (138.0E)',
                                 1340: 'Apstar 6 (134.0E)',
                                 1320: 'JCSAT 5A/Vinasat 1 (132.0E)',
                                 1280: 'JCSAT 3A,RA (128.0E)',
                                 1250: 'Sinosat 3 (125.0E)',
                                 1240: 'JCSAT 4A (124.0E)',
                                 1222: 'AsiaSat 4 (122.2E)',
                                 1180: 'Telkom 2 (118.0E)',
                                 1160: 'Koreasat 3 (116.0E)',
                                 1155: 'Chinasat 6B (115.5E)',
                                 1130: 'Koreasat 5/Palapa D (113.0E)',
                                 1105: 'Sinosat 1 (110.5E)',
                                 1100: 'BSAT 1A,2A/N-Sat 110 (110.0E)',
                                 1080: 'NSS 11/Telkom 1 (108.0E)',
                                 1077: 'Cakrawarta 1/Indostar 2 (107.7E)',
                                 1055: 'Asiasat 3S (105.5E)',
                                 1030: 'Express A2 (103.0E)',
                                 1005: 'AsiaSat 2 (100.5E)',
                                 965: 'Express AM33 (96.5E)',
                                 950: 'NSS 6 (95.0E)',
                                 935: 'Insat 3A,4B (95.0E)',
                                 922: 'ChinaStar 9 (92.2E)',
                                 915: 'Measat 3,3A (91.5E)',
                                 900: 'Yamal 201 (90.0E)',
                                 880: 'ST1 (88.0E)',
                                 875: 'ChinaSat 5A (87.5E)',
                                 852: 'Intelsat 15 (85.2E)',
                                 850: 'Intelsat 15 (85.0E)',
                                 830: 'Insat 4A,2E,3B (83.0E)',
                                 800: 'Express MD1 (80.0E)',
                                 785: 'ThaiCom 5 (78.5E)',
                                 765: 'Apstar 2R (76.5E)',
                                 750: 'ABS 1,1B (75.0E)',
                                 740: 'Edusat (74.0E)',
                                 705: 'Eutelsat W5 (70.5E)',
                                 685: 'Intelsat 7,10 (68.5E)',
                                 660: 'Intelsat 702 (66.0E)',
                                 642: 'Intelsat 906 (64.2E)',
                                 640: 'Intelsat 906 (64.0E)',
                                 620: 'Intelsat 902 (62.0E)',
                                 600: 'Intelsat 904 (60.0E)',
                                 570: 'NSS 12 (57.0E)',
                                 560: 'Bonum 1 (56.0E)',
                                 548: 'Intelsat 709 (54.8E)',
                                 530: 'Express AM22 (53.0E)',
                                 502: 'Thaicom 2 (50.2E)',
                                 490: 'Yamal 202 (49.0E)',
                                 480: 'Eutelsat W48 (48.0E)',
                                 451: 'Galaxy 27 (45.1E)',
                                 450: 'Intelsat 12 (45.0E)',
                                 420: 'Turksat 2A,3A (42.0E)',
                                 400: 'Express AM1 (40.0E)',
                                 390: 'Hellas Sat 2 (39.0E)',
                                 380: 'Paksat 1 (38.0E)',
                                 360: 'Eutelsat W4,W7 (36.0E)',
                                 332: 'Eurobird 3 (33.2E)',
                                 330: 'Eurobird 3 (33.0E)',
                                 329: 'Intelsat 802 (32.9E)',
                                 315: 'Astra 1G (31.5E)',
                                 305: 'Arabsat 5A (30.5E)',
                                 285: 'Eurobird 1 (28.5E)',
                                 284: 'Astra 2A,2B,2D/Eurobird 1 (28.2E)',
                                 282: 'Astra 2A,2B,2D/Eurobird 1 (28.2E)',
                                 260: 'Badr 4,5,6/Eurobird 2 (26.0E)',
                                 255: 'Eurobird 2 (25.5E)',
                                 235: 'Astra 3A,3B (23.5E)',
                                 216: 'Eutelsat W6 (21.6E)',
                                 215: 'Eutelsat W6 (21.5E)',
                                 210: 'AfriStar 1 (21.0E)',
                                 202: 'Arabsat 2B (20.2E)',
                                 200: 'Arabsat 2B (20.0E)',
                                 192: 'Astra 1H/1KR/1L/1M (19.2E)',
                                 170: 'Amos 5i (17.0E)',
                                 160: 'Eurobird 16/W2M/Sesat (16.0E)',
                                 158: 'Eurobird 16/W2M/Sesat (15.8E)',
                                 130: 'HotBird 6,8,9 (13.0E)',
                                 100: 'Eutelsat W2A (10.0E)',
                                 90: 'Eurobird 9A (9.0E)',
                                 70: 'Eutelsat W3A (7.0E)',
                                 50: 'Astra 4A,1E (4.8E)',
                                 48: 'Astra 4A,1E (4.8E)',
                                 40: 'Eurobird 4A (4.0E)',
                                 30: 'Telecom 2C (3.0E)',
                                 28: 'Rascom QAF 1R (2.8E)',
                                 20: 'Astra 1C (2.0E)'}[frontendData.get('orbital_position', 'None')]
                            except:
                                orb = 'Unsupported SAT: %s' % str([frontendData.get('orbital_position', 'None')])

                            orbital = self.tunertype == 'linelist' and orb
                        else:
                            orbital = 'Satellite: ' + orb
                    elif frontendData.get('tuner_type') == 'DVB-C':
                        if self.tunertype == 'linelist':
                            orbital = 'DVB-C'
                        else:
                            orbital = ' '
                    elif frontendData.get('tuner_type') == 'DVB-T':
                        if self.tunertype == 'linelist':
                            orbital = 'DVB-T'
                        else:
                            orbital = ' '
                    return orbital
            else:
                return ''
