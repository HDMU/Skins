from Components.Converter.Converter import Converter
from Components.Element import cached
from ServiceReference import ServiceReference
from enigma import eServiceCenter, eServiceReference, iServiceInformation, iPlayableService, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable, eTimer
from string import upper
from Components.ServiceEventTracker import ServiceEventTracker
from Tools.Directories import fileExists, resolveFilename
from os import environ, listdir, remove, rename, system
from Components.ServiceEventTracker import ServiceEventTracker
from Components.config import config
import gettext

class ExtremeInfo(Converter, object):
    TUNERINFO = 0
    CAMNAME = 1
    NUMBER = 2
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
    IRDECM = 13
    SECAECM = 14
    NAGRAECM = 15
    VIAECM = 16
    CONAXECM = 17
    BETAECM = 18
    CRWECM = 19
    DREAMECM = 20
    NDSECM = 21
    CAIDINFO = 22
    FTA = 23
    EMU = 24
    CRD = 25
    NET = 26
    TUNERINFOBP = 27
    TUNERTYPE = 28

    def __init__(self, type):
        Converter.__init__(self, type)
        self.list = []
        self.rescan = False
        self.getLists()
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
         'Emu': (self.EMU, self.rescan),
         'Crd': (self.CRD, self.rescan),
         'Net': (self.NET, self.rescan)}
        if type == 'TunerInfo':
            self.type = self.TUNERINFO
        elif type == 'CamName':
            self.type = self.CAMNAME
        elif type == 'Number':
            self.type = self.NUMBER
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
        elif type == 'TunerType':
            self.type = self.TUNERTYPE

    @cached
    def getText(self):
        service = self.source.service
        if service:
            info = service.info()
            if not info:
                return ''
            if info.getInfo(iServiceInformation.sIsCrypted):
                self.DynTimer.start(3000)
            text = ''
            if self.type == self.TUNERINFO or self.type == self.TUNERINFOBP or self.type == self.TUNERTYPE:
                if self.type == self.TUNERINFO:
                    self.tunertype = 'linelist'
                    tunerinfo = self.getTunerInfo(service)
                elif self.type == self.TUNERINFOBP:
                    self.tunertype = 'lineslist'
                    tunerinfo = self.getTunerInfo(service)
                elif self.type == self.TUNERTYPE:
                    self.tunertype = 'tunertype'
                    tunerinfo = self.getTunerInfo(service)
                text = tunerinfo
                return text
            if self.type == self.NUMBER:
                name = info.getName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                number = self.getServiceNumber(name, info.getInfoString(iServiceInformation.sServiceref))
                text = number
                return text
            if config.skin.primary_skin.value == 'hd_glass13/skin.xml':
                if config.plugins.Glass12Setup.par4.value != '0':
                    return ''
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

    def doIt(self):
        self.DynTimer.stop()
        if self.rescan == True:
            self.rescan = False
        if config.skin.primary_skin.value == 'hd_glass13/skin.xml':
            ee = int(config.plugins.Glass12Setup.par6.value) * 1000
        else:
            ee = 10000
        self.DynTimer.start(ee, True)
        Converter.changed(self, self.what)

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

    def int2hex(self, int):
        return '%x' % int

    def getCaidInfo(self):
        service = self.source.service
        cainfo = 'Caid:  '
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
        return 'No CA info available'

    def getCamName(self):
        emu = ''
        cs = ''
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
            f = open('/tmp/gbp_cam.info', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            return content
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
            tmp = 'xxx'
            from enigma import Cbptools
            camdStatus = Cbptools.getInstance().CamdCommandPY(Cbptools.GET_CAMD_STATE)
            tmp = camdStatus[1]
        except:
            pass

        if tmp != 'xxx':
            return tmp
        try:
            f = open('/etc/CurrentDelCamName', 'r')
            content = f.read()
            f.close()
        except:
            content = ''

        contentInfo = content.split('\n')
        if content != '':
            tmp = str(contentInfo)
            return tmp[2:-2]
        return 'None'

    def getEcmCamInfo(self):
        if self.getFta():
            return 'Free to Air'
        ecmInfoString = ''
        using = ''
        address = ''
        hops = ''
        ecmTime = ''
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
                casys = 'Caid: ' + castr
            if line.startswith('source: net'):
                idex = line.index('(')
                line = line[idex:]
                line = line.replace('\n', '')
                if line.__contains__('cccamd'):
                    line = str(line.split(' ')[2].split())
                    line = ', Source: Net, CCcam: ' + line[2:-3]
                elif line.__contains__('newcamd'):
                    line = str(line.split(' ')[2].split())
                    line = ', Source: Net, NewCS: ' + line[2:-3]
                    if line.__contains__('127.0.0.1'):
                        line = ', Source: NewCS with local card in slot'
                ecmInfoString = casys + line
                return ecmInfoString
            if line.startswith('source: emu'):
                using = self.parseEcmInfoLine(line)
                ecmInfoString = casys + ', Source: '
                ecmInfoString += using
                return ecmInfoString
            if line.startswith('using:'):
                using = self.parseEcmInfoLine(line)
            elif line.startswith('caid:'):
                castr = self.parseEcmInfoLine(line)
                if castr.__contains__('x'):
                    idx = castr.index('x')
                    castr = castr[idx + 1:]
                    if len(castr) == 3:
                        castr = '0%s' % castr
                    castr = castr.upper()
                casys = 'Caid: ' + castr
            elif line.startswith('address:'):
                address = '%s %s' % (_(' Source:'), self.parseEcmInfoLine(line))
                if address == ' Source: /dev/sci0':
                    state = ' Source: Lower slot'
                if address == ' Source: /dev/sci1':
                    state = ' Source: Upper slot'
                if address != ' Source: /dev/sci0' and address != ' Source: /dev/sci1':
                    state = address
                if len(state) > 28:
                    state = '%s...' % state[:25]
            elif line.startswith('hops:'):
                hops = '%s %s' % (_(' Hops:'), self.parseEcmInfoLine(line))
            elif line.startswith('ecm time:'):
                ecmTime = '%s %s' % (_(' Time:'), self.parseEcmInfoLine(line))

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
            return 'No info from emu or FTA'
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

    def getServiceNumber(self, name, ref):
        list = []
        if ref.startswith('1:0:2'):
            list = self.radio_list
        elif ref.startswith('1:0:1'):
            list = self.tv_list
        number = '---'
        if name in list:
            for idx in range(1, len(list)):
                if name == list[idx - 1]:
                    number = str(idx)
                    break

        return number

    def getListFromRef(self, ref):
        list = []
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(ref)
        bouquets = services and services.getContent('SN', True)
        for bouquet in bouquets:
            services = serviceHandler.list(eServiceReference(bouquet[0]))
            channels = services and services.getContent('SN', True)
            for channel in channels:
                if not channel[0].startswith('1:64:'):
                    list.append(channel[1].replace('\xc2\x86', '').replace('\xc2\x87', ''))

        return list

    def getLists(self):
        self.tv_list = self.getListFromRef(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
        self.radio_list = self.getListFromRef(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))

    def getTunerInfo(self, service):
        tunerinfo = ''
        feinfo = service and service.frontendInfo()
        if feinfo is not None and feinfo:
            frontendData = feinfo.getAll(True)
            if frontendData is not None:
                if frontendData.get('tuner_type') == 'DVB-S' or frontendData.get('tuner_type') == 'DVB-C':
                    frequency = str(frontendData.get('frequency') / 1000) + ' MHz'
                    symbolrate = str(int(frontendData.get('symbol_rate', 0) / 1000))
                    if frontendData.get('tuner_type') == 'DVB-S':
                        try:
                            orb = {3590: 'Thor/Intelsat (1.0W)',
                             3560: 'Amos (4.0W)',
                             3550: 'Atlantic Bird (5.0W)',
                             3530: 'Nilesat/Atlantic Bird (7.0W)',
                             3520: 'Atlantic Bird (8.0W)',
                             3475: 'Atlantic Bird (12.5W)',
                             3460: 'Express (14.0W)',
                             3450: 'Telstar (15.0W)',
                             3420: 'Intelsat (18.0W)',
                             3380: 'Nss (22.0W)',
                             3355: 'Intelsat (24.5W)',
                             3325: 'Intelsat (27.5W)',
                             3300: 'Hispasat (30.0W)',
                             3285: 'Intelsat (31.5W)',
                             3170: 'Intelsat (43.0W)',
                             3150: 'Intelsat (45.0W)',
                             3070: 'Intelsat (53.0W)',
                             3045: 'Intelsat (55.5W)',
                             3020: 'Intelsat 9 (58.0W)',
                             2990: 'Amazonas (61.0W)',
                             2900: 'Star One (70.0W)',
                             2880: 'AMC 6 (72.0W)',
                             2875: 'Echostar 6 (72.7W)',
                             2860: 'Horizons (74.0W)',
                             2810: 'AMC5 (79.0W)',
                             2780: 'NIMIQ 4 (82.0W)',
                             2690: 'NIMIQ 1 (91.0W)',
                             3592: 'Thor/Intelsat (0.8W)',
                             2985: 'Echostar 3,12 (61.5W)',
                             2830: 'Echostar 8 (77.0W)',
                             2630: 'Galaxy 19 (97.0W)',
                             2500: 'Echostar 10,11 (110.0W)',
                             2502: 'DirectTV 5 (110.0W)',
                             2410: 'Echostar 7 Anik F3 (119.0W)',
                             2391: 'Galaxy 23 (121.0W)',
                             2390: 'Echostar 9 (121.0W)',
                             2412: 'DirectTV 7S (119.0W)',
                             2310: 'Galaxy 27 (129.0W)',
                             2311: 'Ciel 2 (129.0W)',
                             2120: 'Echostar 2 (148.0W)',
                             1100: 'BSat 1A,2A (110.0E)',
                             1101: 'N-Sat 110 (110.0E)',
                             1131: 'KoreaSat 5 (113.0E)',
                             1440: 'SuperBird 7,C2 (144.0E)',
                             1006: 'AsiaSat 2 (100.5E)',
                             1030: 'Express A2 (103.0E)',
                             1056: 'Asiasat 3S (105.5E)',
                             1082: 'NSS 11 (108.2E)',
                             881: 'ST1 (88.0E)',
                             900: 'Yamal 201 (90.0E)',
                             917: 'Mesat (91.5E)',
                             950: 'Insat 4B (95.0E)',
                             951: 'NSS 6 (95.0E)',
                             765: 'Telestar (76.5E)',
                             785: 'ThaiCom 5 (78.5E)',
                             800: 'Express (80.0E)',
                             830: 'Insat 4A (83.0E)',
                             850: 'Intelsat 709 (85.2E)',
                             750: 'Abs (75.0E)',
                             720: 'Intelsat (72.0E)',
                             705: 'Eutelsat W5 (70.5E)',
                             685: 'Intelsat (68.5E)',
                             620: 'Intelsat 902 (62.0E)',
                             600: 'Intelsat 904 (60.0E)',
                             570: 'Nss (57.0E)',
                             530: 'Express AM22 (53.0E)',
                             480: 'Eutelsat 2F2 (48.0E)',
                             450: 'Intelsat (45.0E)',
                             420: 'Turksat 2A (42.0E)',
                             400: 'Express AM1 (40.0E)',
                             390: 'Hellas Sat 2 (39.0E)',
                             380: 'Paksat 1 (38.0E)',
                             360: 'Eutelsat Sesat (36.0E)',
                             335: 'Astra 1M (33.5E)',
                             330: 'Eurobird 3 (33.0E)',
                             328: 'Galaxy 11 (32.8E)',
                             315: 'Astra 5A (31.5E)',
                             310: 'Turksat (31.0E)',
                             305: 'Arabsat (30.5E)',
                             285: 'Eurobird 1 (28.5E)',
                             284: 'Eurobird/Astra (28.2E)',
                             282: 'Eurobird/Astra (28.2E)',
                             1220: 'AsiaSat (122.0E)',
                             1380: 'Telstar 18 (138.0E)',
                             260: 'Badr 3/4 (26.0E)',
                             255: 'Eurobird 2 (25.5E)',
                             235: 'Astra 1E (23.5E)',
                             215: 'Eutelsat (21.5E)',
                             216: 'Eutelsat W6 (21.6E)',
                             210: 'AfriStar 1 (21.0E)',
                             192: 'Astra 1F (19.2E)',
                             160: 'Eutelsat W2 (16.0E)',
                             130: 'Hot Bird 6,7A,8 (13.0E)',
                             100: 'Eutelsat W1 (10.0E)',
                             90: 'Eurobird 9 (9.0E)',
                             70: 'Eutelsat W3A (7.0E)',
                             50: 'Sirius 4 (5.0E)',
                             48: 'Sirius 4 (4.8E)',
                             30: 'Telecom 2 (3.0E)'}[frontendData.get('orbital_position', 'None')]
                        except:
                            orb = 'Unsupported SAT: %s' % str([frontendData.get('orbital_position', 'None')])

                        if self.tunertype == 'linelist':
                            pol = {eDVBFrontendParametersSatellite.Polarisation_Horizontal: 'H',
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
                        system = {eDVBFrontendParametersSatellite.System_DVB_S: 'DVB-S',
                         eDVBFrontendParametersSatellite.System_DVB_S2: 'DVB-S2'}[frontendData.get('system', eDVBFrontendParametersSatellite.System_DVB_S)]
                        modulation = {eDVBFrontendParametersSatellite.Modulation_Auto: 'Auto',
                         eDVBFrontendParametersSatellite.Modulation_QPSK: 'QPSK',
                         eDVBFrontendParametersSatellite.Modulation_8PSK: '8PSK',
                         eDVBFrontendParametersSatellite.Modulation_QAM16: 'QAM16'}[frontendData.get('modulation', eDVBFrontendParametersSatellite.Modulation_Auto)]
                        if self.tunertype == 'linelist':
                            tunerinfo = frequency + '  ' + pol + '  ' + fec + '  ' + symbolrate + '  ' + orb
                        elif self.tunertype == 'tunertype':
                            tunerinfo = system + '  ' + modulation
                        elif self.tunertype == 'lineslist':
                            tunerinfo = 'Satellite: ' + orb + '\nFrequency: ' + frequency + '\nPolarisation: ' + pol + '\nSymbolrate: ' + symbolrate + '\nFEC: ' + fec
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
                            tunerinfo = frequency + '  ' + fec + '  ' + symbolrate
                        elif self.tunertype == 'tunertype':
                            tunerinfo = 'DVB-C'
                        elif self.tunertype == 'lineslist':
                            tunerinfo = 'Frequency: ' + frequency + '\nSymbolrate: ' + symbolrate + '\nFEC: ' + fec
                    elif self.tunertype == 'linelist':
                        tunerinfo = frequency + '  ' + symbolrate
                    elif self.tunertype == 'tunertype':
                        tunerinfo = 'DVB-T'
                    elif self.tunertype == 'lineslist':
                        tunerinfo = 'Frequency: ' + frequency + '\nSymbolrate: ' + symbolrate
                    return tunerinfo
            else:
                return ''
