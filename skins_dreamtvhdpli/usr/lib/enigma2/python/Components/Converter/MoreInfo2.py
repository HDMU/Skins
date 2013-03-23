from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.CurrentService import CurrentService
from Components.config import config
from Components.PluginComponent import plugins
from enigma import iServiceInformation, iFrontendInformation, iPlayableService, iPlayableServicePtr
from enigma import eServiceCenter, eServiceReference, eConsoleAppContainer, eDVBFrontendParametersSatellite
from Poll import Poll
from Screens.Standby import inStandby
from ServiceReference import ServiceReference
from xml.etree.cElementTree import parse
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import fileExists
from Tools.Transponder import ConvertToHumanReadable
from time import time, localtime
try:
    from enigma import Cbptools
except:
    Cbptools = None

VERSION = 'MoreInfo v.2.6R1'
SatLst = {}
SatLst2 = {}
SatLst2inv = {}
SatNameLst = {}
Bq = {}
camdlist = {}
isAllSatDataReady = False
AllSkinUsage = '----- Used in skin: -----\n'
btrt = None
START_BR = 1
SAY_BR = 2
STOP_BR = 3
WAIT = 4

def AboutMain(session, **kwargs):
    try:
        from Components.Converter.MoreInfo2 import VERSION, AllSkinUsage
        from Screens.MessageBox import MessageBox
        session.open(MessageBox, '%s *** (c)2010 by SatCat\n%s' % (VERSION, AllSkinUsage), MessageBox.TYPE_INFO)
    except:
        pass


def About(menuid):
    if menuid != 'system':
        return []
    try:
        from Components.Converter.MoreInfo2 import AboutMain
        return [('About MoreInfo',
          AboutMain,
          'About_MoreInfo',
          None)]
    except:
        return []


class Bitrate:

    def __init__(self):
        self.pauseBR = False
        if not fileExists('/usr/bin/bitrate'):
            self.noBitrateExc = True
            return
        self.unused = ''
        self.strng = ''
        self.noBitrateExc = False
        self.store_rf = None
        self.store_time = None
        self.isBRstarted = False
        self.clrVal()
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.stop)
        self.container.dataAvail.append(self.BRgenerated)

    def clrVal(self):
        self.vmin = 0
        self.vmax = 0
        self.vavg = 0
        self.vcur = 0
        self.amin = 0
        self.amax = 0
        self.aavg = 0
        self.acur = 0

    def start(self, info, service):
        if self.isBRstarted:
            return
        if service:
            demux = 0
            try:
                stream = service.stream()
                if stream:
                    stream
                    demux = str(stream.getStreamingData().get('demux', 0))
            except:
                pass

            vpid = info.getInfo(iServiceInformation.sVideoPID)
            apid = info.getInfo(iServiceInformation.sAudioPID)
            cmd = 'bitrate ' + str(demux) + ' ' + str(vpid) + ' ' + str(apid)
            self.isBRstarted = True
            self.container.execute(cmd)

    def stop(self, rval = None):
        self.container.kill()
        self.isBRstarted = False
        self.clrVal()
        self.unused = ''

    def BRgenerated(self, strng):
        self.clrVal()
        if inStandby:
            self.stop()
        try:
            self.strng = self.unused + strng
            datalines = self.strng.split('\n')
            i = len(datalines[3:])
            if i == 1:
                self.unused = datalines[-1] + '\n'
            elif i == 2:
                self.unused = '%s\n%s\n' % (datalines[-2], datalines[-1])
            else:
                self.unused = ''
            m = datalines[0].split(' ')
            if len(m) == 4:
                self.vmin, self.vmax, self.vavg, self.vcur = m
            m = datalines[1].split(' ')
            if len(m) == 4:
                self.amin, self.amax, self.aavg, self.acur = m
        except:
            self.clrVal()

    def wUp(self, rf):
        if not self.store_rf:
            self.store_rf = rf
            self.store_time = time()
            return WAIT
        if self.store_rf == rf:
            if self.pauseBR:
                return WAIT
            elif self.isBRstarted:
                return SAY_BR
            elif time() - self.store_time > 8:
                return START_BR
            else:
                return WAIT
        else:
            if self.pauseBR:
                self.pauseBR = False
            self.store_rf = rf
            self.store_time = time()
            return STOP_BR

    def get(self, info, tpi, chnl, cbq, param, service):
        if self.noBitrateExc:
            return 'No /usr/bin/bitrate!'
        ret = self.wUp(chnl)
        if ret == START_BR:
            self.start(info, service)
        elif ret == STOP_BR:
            self.stop()
        elif ret == SAY_BR:
            try:
                if int(self.vcur) < 1 and int(self.acur) < 1:
                    return '%Hide'
                if int(self.vcur) < 1 and int(self.acur) > 1:
                    return 'A: ' + str(self.acur) + 'kb/s'
                return 'V: ' + str(self.vcur) + 'kb/s, A: ' + str(self.acur) + 'kb/s'
            except:
                pass

        return '%Hide'


class MoreInfo2(Poll, Converter, object):
    IB = 0
    CS = 1
    ALL = 0
    FREQ = 1
    SR = 2
    POLAR = 3
    FEC = 4
    VER = 5
    SERVNUM = 6
    SATNAME = 7
    SERVREF = 8
    TST = 9
    BQ = 10
    SID = 11
    VPID = 12
    APID = 13
    TSID = 14
    ONID = 15
    SERVNAME = 16
    HIDE = 18
    CAID = 20
    CANAME = 21
    BITRATE = 22
    PROV = 23
    MOD = 24
    SYS = 25
    FPS = 26
    CAMDNAME = 27
    REALTP = 28
    TP = {}
    ECM = {}
    ECMtype = 0

    def __init__(self, type):
        global AllSkinUsage
        global isAllSatDataReady
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_enabled = False
        self.ECMtype = 0
        self.type = type
        AllSkinUsage = AllSkinUsage + '%s\n' % type
        if self.type.find('%ECM') != -1 or self.type.find('%Bitr') != -1:
            self.poll_enabled = True
            self.poll_interval = 1000
        if not isAllSatDataReady:
            self.getServList(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
            self.getServList(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
            self.CreateSatList()
            isAllSatDataReady = True
            try:
                plugins.addPlugin(PluginDescriptor(name='About MoreInfo', description='About MoreInfo', where=PluginDescriptor.WHERE_MENU, fnc=About))
            except:
                pass

        self.i = 0

    def getBQ(self, bq_str = ''):
        if bq_str == '':
            return ''
        a = bq_str.rfind('FROM BOUQUET "userbouquet.')
        b = bq_str.rfind('.tv" ORDER')
        c = bq_str.rfind('.radio" ORDER')
        if c > b:
            b = c + 5
        if bq_str.rfind('FROM SATELLITES') != -1:
            return ''
        if b > a and a != -1 and b != -1:
            return bq_str[a + 14:b + 3]
        return ''

    def getServList(self, eSRef):
        tot_num = 0
        hService = eServiceCenter.getInstance()
        Services = hService.list(eSRef)
        Bouquets = Services and Services.getContent('SN', True)
        for bq in Bouquets:
            curr_bq = self.getBQ(bq[0])
            Bq[curr_bq] = (len(Bq), bq[1])
            srv = hService.list(eServiceReference(bq[0]))
            chs = srv and srv.getContent('SN', True)
            for ch in chs:
                if not ch[0].startswith('1:64:'):
                    tot_num = tot_num + 1
                    SatLst[ch[0] + curr_bq] = tot_num
                    SatLst[ch[0]] = tot_num
                    SatLst2[ch[1]] = tot_num
                    SatLst2inv[tot_num] = ch[1]

    def CAName(self, cid):
        caID = '%04X' % cid
        if caID == '2600':
            syID = 'Biss'
        elif caID >= '0600' and caID <= '06FF':
            syID = 'Irdeto'
        elif caID >= '0500' and caID <= '05FF':
            syID = 'Viaccess'
        elif caID == '4AE0':
            syID = 'DRE-Crypt'
        elif caID == '4AE1':
            syID = 'DRE-Crypt MP4/HD'
        elif caID >= '1800' and caID <= '18FF':
            syID = 'Nagravision'
        elif caID == 'A101':
            syID = 'Rosscrypt'
        elif caID >= '0100' and caID <= '01FF':
            syID = 'Seca Mediaguard'
        elif caID >= '0900' and caID <= '09FF':
            syID = 'NDS Videoguard'
        elif caID == '4A70':
            syID = 'DreamCrypt'
        elif caID >= '0B00' and caID <= '0BFF':
            syID = 'Conax'
        elif caID >= '0700' and caID <= '07FF':
            syID = 'DigiCipher 2'
        elif caID >= '0D00' and caID <= '0DFF':
            syID = 'Cryptoworks'
        elif caID >= '1700' and caID <= '17FF':
            syID = 'BetaCrypt'
        elif caID == '0E00':
            syID = 'PowerVu'
        elif caID == '2200':
            syID = 'Codicrypt'
        else:
            syID = ''
        return '%s(%04X)' % (syID, cid)

    def CreateSatList(self):
        XmlLst = parse('/etc/tuxbox/satellites.xml').getroot()
        if XmlLst != None:
            for s in XmlLst.findall('sat'):
                sname = s.get('name')
                spos = s.get('position')
                SatNameLst[spos] = sname

    def getTPinfo(self, tpi):
        self.TP = {'All': 'n/a',
         'Freq': '0',
         'SR': '0',
         'Polar': 'n/a',
         'FEC': 'n/a',
         'Mod': 'n/a',
         'Sys': 'n/a',
         'Trans': 'n/a',
         'CodeRateLP': 'n/a',
         'Guard': 'n/a'}
        if tpi.has_key('frequency'):
            self.TP['Freq'] = str(int(tpi['frequency']) / 1000)
        if tpi.has_key('polarization'):
            polar = str(tpi['polarization'])
            if len(polar) > 1:
                if len(polar) < 11:
                    self.TP['Polar'] = tpi['polarization'][0]
                else:
                    self.TP['Polar'] = tpi['polarization'][9]
            elif polar == '0':
                self.TP['Polar'] = 'H'
            elif polar == '1':
                self.TP['Polar'] = 'V'
            elif polar == '2':
                self.TP['Polar'] = 'CL'
            elif polar == '3':
                self.TP['Polar'] = 'CR'
            else:
                self.TP['Polar'] = '?'
        if tpi.has_key('symbol_rate'):
            self.TP['SR'] = str(int(tpi['symbol_rate']) / 1000)
        elif tpi.has_key('symbolrate'):
            self.TP['SR'] = str(int(tpi['symbolrate']) / 1000)
        if tpi.has_key('modulation'):
            self.TP['Mod'] = {0: 'Auto',
             1: 'QPSK',
             2: '8PSK',
             3: 'QAM16'}[tpi['modulation']]
        if tpi.has_key('system'):
            self.TP['Sys'] = {0: 'DVB-S',
             1: 'DVB-S2'}[tpi['system']]
        if tpi.has_key('fec_inner'):
            fec = str(tpi['fec_inner'])
            if fec == '0':
                fec = 'AUTO'
            elif fec == '1':
                fec = '1/2'
            elif fec == '2':
                fec = '2/3'
            elif fec == '3':
                fec = '3/4'
            elif fec == '4':
                fec = '5/6'
            elif fec == '5':
                fec = '7/8'
            elif fec == '6':
                fec = '8/9'
            elif fec == '7':
                fec = '3/5'
            elif fec == '8':
                fec = '4/5'
            elif fec == '9':
                fec = '9/10'
            elif fec == '15':
                fec = 'None'
            else:
                fec = '?'
            self.TP['FEC'] = fec
        elif tpi.has_key('fec inner'):
            self.TP['FEC'] = tpi['fec inner']
        if self.TP['Freq'] != 0:
            self.TP['All'] = '%s %s %s %s' % (self.TP['Freq'],
             self.TP['Polar'],
             self.TP['SR'],
             self.TP['FEC'])
        if tpi.has_key('transmission_mode'):
            self.TP['Sys'] = 'DVB-T'
            self.TP['Trans'] = {0: _('Auto'),
             1: '2k',
             2: '8k'}[tpi['transmission_mode']]
            if tpi.has_key('constellation'):
                self.TP['Mod'] = {0: _('Auto'),
                 1: 'QPSK',
                 2: 'QAM16',
                 3: 'QAM64'}[tpi['constellation']]
            if tpi.has_key('frequency'):
                self.TP['Freq'] = str(int(tpi['frequency']) / 1000000) + 'Mhz'
                try:
                    frq = int(tpi['frequency']) / 1000000
                    if frq >= 474:
                        self.TP['Freq'] += '(%d)' % (21 + (frq - 474) / 8)
                    elif 178 <= frq <= 226:
                        self.TP['Freq'] += '(%d)' % (6 + (frq - 178) / 8)
                    elif 80 <= frq <= 96:
                        self.TP['Freq'] += '(%d)' % (3 + (frq - 80) / 8)
                    elif frq == 52:
                        self.TP['Freq'] += '(1)'
                    elif frq == 62:
                        self.TP['Freq'] += '(2)'
                except:
                    pass

            if tpi.has_key('code_rate_lp'):
                self.TP['CodeRateLP'] = {0: _('Auto'),
                 1: '1/2',
                 2: '2/3',
                 3: '3/4',
                 4: '5/6',
                 5: '7/8'}[tpi['code_rate_lp']]
            if tpi.has_key('guard_interval'):
                self.TP['Guard'] = {0: _('Auto'),
                 1: '1/32',
                 2: '1/16',
                 3: '1/8',
                 4: '1/4'}[tpi['guard_interval']]
            self.TP['All'] = '%s %s %s %s' % (self.TP['Freq'],
             self.TP['CodeRateLP'],
             self.TP['Trans'],
             self.TP['Guard'])

    def GetECMInfo(self, fname):
        try:
            f = open(fname, 'r')
            lns = f.readlines()
            f.close()
            a = []
            for l in lns:
                for s in l.split():
                    a.append(s)

            if 'source:' in a and 'prov:' in a and 'msec' in a:
                return 1
            if 'provid:' in a and 'time:' in a and 'caid:' in a:
                return 2
            if 'FROM:' in a and 'CW0:' in a and 'CAID' in a:
                return 3
        except:
            pass

        return 0

    def ECMParam(self, info):
        self.ECM = {'ECMTime': '%Hide',
         'ECMHost': '%Hide',
         'ECMProv': '%Hide',
         'ECMKey': '%Hide',
         'ECMCaid': '%Hide',
         'ECMPid': '%Hide'}
        caid = info.getInfoObject(iServiceInformation.sCAIDs)
        if caid and len(caid) > 0 and caid[0] != 9728:
            if self.ECMtype == 0:
                self.ECMtype = self.GetECMInfo('/tmp/ecm.info')
                if self.ECMtype == 0:
                    return
            try:
                f = open('/tmp/ecm.info', 'r')
                lns = f.readlines()
                f.close()
                if len(lns) < 3:
                    self.ECMtype = 0
                    return
            except:
                self.ECMtype = 0
                return

            self.ECM = {'ECMTime': '',
             'ECMHost': 'n/a',
             'ECMProv': 'n/a',
             'ECMKey': 'n/a',
             'ECMCaid': '',
             'ECMPid': ''}
            try:
                if self.ECMtype == 1:
                    for l in lns:
                        if l.find(' CaID ') > 10:
                            m = l.split()
                            if len(m) > 5:
                                self.ECM['ECMCaid'] = m[5].strip(',')
                        if l.find(' pid ') > 10:
                            m = l.split()
                            if len(m) >= 7:
                                self.ECM['ECMPid'] = m[7].strip(',')
                        if l.find('caid:') == 0:
                            self.ECM['ECMCaid'] = l[8:].strip()
                        if l.find('pid:') == 0:
                            self.ECM['ECMPid'] = l[7:].strip()
                        if l.find('msec') > 2:
                            self.ECM['ECMTime'] = l.split()[0] + ' ms'
                        if l.find('source:') == 0:
                            self.ECM['ECMHost'] = l.rstrip()[l.find(' at ') + 4:].rstrip(')')
                        if l.find('cw0: ') == 0:
                            cw0 = l[4:].strip()
                        if l.find('cw1: ') == 0:
                            cw1 = l[4:].strip()
                        if l.find('prov: ') == 0:
                            self.ECM['ECMProv'] = l[6:].strip()

                    if len(cw0) > 1 and len(cw1) > 1:
                        self.ECM['ECMKey'] = (cw0 + cw1).replace(' ', '')
                elif self.ECMtype == 2:
                    for l in lns:
                        if l.find('address:') == 0:
                            m = l.split()
                            if len(m) >= 2:
                                self.ECM['ECMHost'] = m[1]
                        if l.find('pid:') == 0:
                            m = l.split()
                            if len(m) >= 2:
                                self.ECM['ECMPid'] = m[1]
                        if l.find('caid:') == 0:
                            m = l.split()
                            if len(m) >= 2:
                                self.ECM['ECMCaid'] = m[1]
                        if l.find('ecm time:') == 0:
                            self.ECM['ECMTime'] = l.split()[2] + ' s'
                        if l.find('provid:') == 0:
                            self.ECM['ECMProv'] = l[8:].strip()

                elif self.ECMtype == 3:
                    for l in lns:
                        if l.find(' PID ') > 0:
                            m = l.split()
                            if len(m) >= 4:
                                self.ECM['ECMPid'] = m[3].strip(',')
                        if l.find('CAID ') == 0:
                            m = l.split()
                            if len(m) >= 2:
                                self.ECM['ECMCaid'] = m[1].strip(',')
                        if l.find('FROM:') == 0:
                            self.ECM['ECMHost'] = l.rstrip()[6:]
                        if l.find('PROVIDER') > 1:
                            self.ECM['ECMProv'] = l.rstrip()[l.find('PROVIDER') + 11:]
                        if l.find('CW0: ') == 0:
                            cw0 = l[4:].strip()
                        if l.find('CW1: ') == 0:
                            cw1 = l[4:].strip()

                    if len(cw0) > 1 and len(cw1) > 1:
                        self.ECM['ECMKey'] = (cw0 + cw1).replace(' ', '')
                if self.ECM['ECMCaid'] == '':
                    self.ECMtype = 0
            except:
                pass

    def GetParam(self, info, tpi, chnl, cbq, param, rf = None):
        global btrt
        if param == self.VER:
            return VERSION
        if param == self.SERVNUM:
            curr_chnl_bq = chnl + self.getBQ(cbq)
            if curr_chnl_bq in SatLst:
                num = SatLst[curr_chnl_bq]
                return str(num)
            name = info.getName()
            if name in SatLst2:
                num = SatLst2[name]
                return str(num)
            return '00'
        if param == self.SERVNAME:
            if rf == None:
                return info.getName()
            else:
                return info.getName(rf)
        else:
            if param == self.SATNAME:
                try:
                    orb = str(tpi['orbital_position'])
                except:
                    return '---'

                if orb in SatNameLst:
                    return SatNameLst[orb]
                if int(orb) >= 1800:
                    orb = str(int(orb) - 3600)
                    if len(orb) == 2 and orb[0:1] == '-':
                        orb = '-0' + orb[1:2]
                    if orb in SatNameLst:
                        return SatNameLst[orb]
                return '--'
            if param == self.BITRATE:
                if not btrt:
                    btrt = Bitrate()
                    return ''
                service = self.source.service
                return btrt.get(info, tpi, chnl, cbq, param, service)
            if param == self.SERVREF:
                if len(chnl) > 5:
                    if chnl.find('::') != -1:
                        return str(chnl)[:chnl.find('::') + 1]
                    else:
                        return str(chnl)
                else:
                    return ''
            elif param == self.BQ:
                try:
                    return Bq[self.getBQ(cbq)][1]
                except:
                    return ''

            elif param == self.PROV:
                try:
                    return str(info.getInfoString(iServiceInformation.sProvider))
                except:
                    return ''

            elif param == self.SID:
                try:
                    return '%X' % info.getInfo(iServiceInformation.sSID)
                except:
                    return ''

            elif param == self.VPID:
                try:
                    return '%X' % info.getInfo(iServiceInformation.sVideoPID)
                except:
                    return ''

            elif param == self.APID:
                try:
                    return '%X' % info.getInfo(iServiceInformation.sAudioPID)
                except:
                    return ''

            elif param == self.TSID:
                try:
                    return '%X' % info.getInfo(iServiceInformation.sTSID)
                except:
                    return ''

            elif param == self.ONID:
                try:
                    return '%X' % info.getInfo(iServiceInformation.sONID)
                except:
                    return ''

            elif param == self.CAID:
                cid = info.getInfoObject(iServiceInformation.sCAIDs)
                if cid and int(cid[0]) > 0:
                    if len(cid) == 1:
                        return '%04X' % int(cid[0])
                    else:
                        retval = ''
                        for c in cid:
                            retval = retval + ', %04X' % c

                        return retval[2:]
                else:
                    return '%Hide'
            elif param == self.CANAME:
                cid = info.getInfoObject(iServiceInformation.sCAIDs)
                if cid and int(cid[0]) > 0:
                    if len(cid) == 1:
                        return self.CAName(cid[0])
                    else:
                        retval = ''
                        for c in cid:
                            retval = retval + ', %s' % self.CAName(c)

                        return retval[2:]
                else:
                    return '%Hide'
            else:
                if param == self.CAMDNAME:
                    if Cbptools and len(camdlist) == 0:
                        try:
                            for c in Cbptools.getInstance().CamdCommandPY(Cbptools.GET_CAMD_LIST):
                                camdlist[c[0]] = c[1]

                        except:
                            return 'ERR: Bad Cbptools'

                    if Cbptools and len(camdlist) > 0:
                        return camdlist.get(Cbptools.getInstance().CamdCommandPY(Cbptools.GET_CAMD_STATE)[0], '<get camdname error>')
                    return 'ERR: No BP Camd (non Gemini image?)'
                if param == self.FPS:
                    try:
                        return str((info.getInfo(iServiceInformation.sFrameRate) + 500) / 1000)
                    except:
                        return ''

                elif param == self.TST:
                    service = self.source.service
                    if service:
                        feinfo = service.frontendInfo()
                        return feinfo and '<tpi>:' + str(tpi) + '<TD>:' + str(feinfo.getTransponderData(True)) + '<FS>:' + str(feinfo.getFrontendStatus())
                    else:
                        return '<tpi>:' + str(tpi) + '<stop>'
                elif param == self.REALTP:
                    service = self.source.service
                    feinfo = service and service.frontendInfo()
                    if feinfo:
                        return '<TD:>' + str(feinfo.getTransponderData(True)) + '<FS:>' + str(feinfo.getFrontendStatus())
                    return 'n/a'
                    tinfo = info.getInfoObject(iServiceInformation.sTransponderData)
                    if tinfo:
                        return str(ConvertToHumanReadable(self.tinfo))
                    else:
                        return 'n/a'

    @cached
    def getText(self):
        retval = self.type
        ref = None
        t = localtime()
        mStr = [u'\u044f\u043d\u0432\u0430\u0440\u044f',
         u'\u0444\u0435\u0432\u0440\u0430\u043b\u044f',
         u'\u043c\u0430\u0440\u0442\u0430',
         u'\u0430\u043f\u0440\u0435\u043b\u044f',
         u'\u043c\u0430\u044f',
         u'\u0438\u044e\u043d\u044f',
         u'\u0438\u044e\u043b\u044f',
         u'\u0430\u0432\u0433\u0443\u0441\u0442\u0430',
         u'\u0441\u0435\u043d\u0442\u044f\u0431\u0440\u044f',
         u'\u043e\u043a\u0442\u044f\u0431\u0440\u044f',
         u'\u043d\u043e\u044f\u0431\u0440\u044f',
         u'\u0434\u0435\u043a\u0430\u0431\u0440\u044f']
        dStr = [u'\u041f\u043e\u043d\u0435\u0434\u0435\u043b\u044c\u043d\u0438\u043a',
         u'\u0412\u0442\u043e\u0440\u043d\u0438\u043a',
         u'\u0421\u0440\u0435\u0434\u0430',
         u'\u0427\u0435\u0442\u0432\u0435\u0440\u0433',
         u'\u041f\u044f\u0442\u043d\u0438\u0446\u0430',
         u'\u0421\u0443\u0431\u0431\u043e\u0442\u0430',
         u'\u0412\u043e\u0441\u043a\u0440\u0435\u0441\u0435\u043d\u044c\u0435']
        dStrSh = [u'\u041f\u043d',
         u'\u0412\u0442',
         u'\u0421\u0440',
         u'\u0427\u0442',
         u'\u041f\u0442',
         u'\u0421\u0431',
         u'\u0412\u0441']
        self.i = self.i + 1
        if isinstance(self.source, CurrentService):
            use_in = self.IB
        elif isinstance(self.source, ServiceEvent):
            use_in = self.CS
        else:
            return ''
        if not isAllSatDataReady:
            return ''
        if use_in == self.IB:
            service = self.source.service
            if service:
                info = service.info()
                if not info:
                    return ''
                tpi = info.getInfoObject(iServiceInformation.sTransponderData)
                chnl = info.getInfoString(iServiceInformation.sServiceref)
            elif use_in == self.CS:
                service = self.source.service
                if isinstance(service, iPlayableServicePtr):
                    if service:
                        info = service.info()
                        ref = None
                    else:
                        info = service and self.source.info
                        ref = service
                    return info or ''
                tpi = ref and info.getInfoObject(ref, iServiceInformation.sTransponderData)
                chnl = str(ServiceReference(info.getInfoString(ref, iServiceInformation.sServiceref)))
                chnl = chnl[1:]
            else:
                return ''
            if tpi is not None and isinstance(tpi, dict):
                self.getTPinfo(tpi)
                retval = retval.replace('%All', self.TP['All'])
                retval = retval.replace('%Freq', self.TP['Freq'])
                retval = retval.replace('%SR', self.TP['SR'])
                retval = retval.replace('%Polar', self.TP['Polar'])
                retval = retval.replace('%FEC', self.TP['FEC'])
                retval = retval.replace('%Mod', self.TP['Mod'])
                retval = retval.replace('%Sys', self.TP['Sys'])
            if retval.find('%All') != -1:
                return ''
            if retval.find('%Freq') != -1:
                return ''
            cbq = ''
            if retval.find('%Ver') != -1:
                retval = retval.replace('%Ver', self.GetParam(info, tpi, chnl, cbq, self.VER))
            if retval.find('%Tst') != -1:
                retval = retval.replace('%Tst', self.GetParam(info, tpi, chnl, cbq, self.TST))
            if retval.find('%WDay') != -1:
                retval = retval.replace('%WDay', dStr[t.tm_wday].encode('utf_8'))
            if retval.find('%ShWDay') != -1:
                retval = retval.replace('%ShWDay', dStrSh[t.tm_wday].encode('utf_8'))
            if retval.find('%Month') != -1:
                retval = retval.replace('%Month', mStr[t.tm_mon - 1].encode('utf_8'))
            if retval.find('%Day') != -1:
                retval = retval.replace('%Day', str(t.tm_mday))
            if retval.find('%Year') != -1:
                retval = retval.replace('%Year', str(t.tm_year))
            if use_in == self.CS:
                return retval
            try:
                if chnl.split(':')[2] == '1':
                    cbq = config.tv.lastroot.value
                elif chnl.split(':')[2] == '19' or chnl.split(':')[2] == '17':
                    cbq = config.tv.lastroot.value
                elif chnl.split(':')[2] == '2' or chnl.split(':')[2] == '10':
                    cbq = config.radio.lastroot.value
            except:
                cbq = ''

            if retval.find('%ECM') != -1:
                self.ECMParam(info)
                retval = retval.replace('%ECMTime', self.ECM['ECMTime'])
                retval = retval.replace('%ECMHost', self.ECM['ECMHost'])
                retval = retval.replace('%ECMProv', self.ECM['ECMProv'])
                retval = retval.replace('%ECMKey', self.ECM['ECMKey'])
                retval = retval.replace('%ECMCaid', self.ECM['ECMCaid'])
                retval = retval.replace('%ECMPid', self.ECM['ECMPid'])
                if retval.find('%Hide') != -1:
                    return ''
            if retval.find('%ServRef') != -1:
                retval = retval.replace('%ServRef', self.GetParam(info, tpi, chnl, cbq, self.SERVREF))
            if retval.find('%RealTP') != -1:
                retval = retval.replace('%RealTP', self.GetParam(info, tpi, chnl, cbq, self.REALTP))
            if retval.find('%ServName') != -1:
                retval = retval.replace('%ServName', self.GetParam(info, tpi, chnl, cbq, self.SERVNAME))
            if retval.find('%Prov') != -1:
                retval = retval.replace('%Prov', self.GetParam(info, tpi, chnl, cbq, self.PROV))
            if retval.find('%SID') != -1:
                retval = retval.replace('%SID', self.GetParam(info, tpi, chnl, cbq, self.SID))
            if retval.find('%VPID') != -1:
                retval = retval.replace('%VPID', self.GetParam(info, tpi, chnl, cbq, self.VPID))
            if retval.find('%APID') != -1:
                retval = retval.replace('%APID', self.GetParam(info, tpi, chnl, cbq, self.APID))
            if retval.find('%TSID') != -1:
                retval = retval.replace('%TSID', self.GetParam(info, tpi, chnl, cbq, self.TSID))
            if retval.find('%ONID') != -1:
                retval = retval.replace('%ONID', self.GetParam(info, tpi, chnl, cbq, self.ONID))
            if retval.find('%ServNum') != -1:
                retval = retval.replace('%ServNum', self.GetParam(info, tpi, chnl, cbq, self.SERVNUM))
            if retval.find('%SatName') != -1:
                retval = retval.replace('%SatName', self.GetParam(info, tpi, chnl, cbq, self.SATNAME))
            if retval.find('%BqName') != -1:
                retval = retval.replace('%BqName', self.GetParam(info, tpi, chnl, cbq, self.BQ))
            if retval.find('%CAID') != -1:
                retval = retval.replace('%CAID', self.GetParam(info, tpi, chnl, cbq, self.CAID))
            if retval.find('%CAName') != -1:
                retval = retval.replace('%CAName', self.GetParam(info, tpi, chnl, cbq, self.CANAME))
            if retval.find('%Fps') != -1:
                retval = retval.replace('%Fps', self.GetParam(info, tpi, chnl, cbq, self.FPS))
            if retval.find('%Bitrate') != -1:
                retval = retval.replace('%Bitrate', self.GetParam(info, tpi, chnl, cbq, self.BITRATE))
            if retval.find('%CamdName') != -1:
                retval = retval.replace('%CamdName', self.GetParam(info, tpi, chnl, cbq, self.CAMDNAME))
            return retval.find('%Hide') != -1 and ''
        return retval

    text = property(getText)
