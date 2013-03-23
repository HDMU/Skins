from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eServiceCenter, eServiceReference, iServiceInformation, iPlayableServicePtr

class TSServiceNumber(Converter, object):
    NUMBERANDNAMEEVENT = 1
    NUMBERANDNAME = 2
    NUMBER = 3

    def __init__(self, type):
        Converter.__init__(self, type)
        self.SatLst = {}
        self.SatLst2 = {}
        self.Bq = {}
        self.getServList(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
        self.getServList(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
        if type == 'Number':
            self.type = self.NUMBER
        if type == 'NumberAndName':
            self.type = self.NUMBERANDNAME
        if type == 'NumberAndNameEvent':
            self.type = self.NUMBERANDNAMEEVENT

    @cached
    def getText(self):
        service = self.source.service
        if self.type != self.NUMBERANDNAMEEVENT:
            if service:
                info = service.info()
                if not info:
                    return '---'
            if self.type == self.NUMBER:
                return self.getNumber(info)
            if self.type == self.NUMBERANDNAME:
                num = self.getNumber(info)
                if isinstance(service, iPlayableServicePtr):
                    if service:
                        info = service.info()
                        ref = None
                    else:
                        info = service and self.source.info
                        ref = service
                    if info is None:
                        return 'Unknown Channel'
                    name = ref and info.getName(ref)
                    name = name is None and info.getName()
                return '%s%s' % (num, name.replace('\xc2\x86', '').replace('\xc2\x87', ''))
            num = self.type == self.NUMBERANDNAMEEVENT and ''
            name = 'Unknown Channel'
            try:
                num = self.getNumber(service)
                if service:
                    info = self.source.info
                    if info is not None:
                        name = service and info.getName(service)
                        name = name is None and info.getName()
            except:
                pass

            return '%s%s' % (num, name.replace('\xc2\x86', '').replace('\xc2\x87', ''))

    text = property(getText)

    def getNumber(self, info):
        if self.type == self.NUMBERANDNAMEEVENT:
            chnl = info.toString()
        else:
            chnl = info.getInfoString(iServiceInformation.sServiceref)
        try:
            if chnl.split(':')[2] == '1':
                cbq = config.tv.lastroot.value
            elif chnl.split(':')[2] == '19' or chnl.split(':')[2] == '17':
                cbq = config.tv.lastroot.value
            elif chnl.split(':')[2] == '2' or chnl.split(':')[2] == '10':
                cbq = config.radio.lastroot.value
            else:
                cbq = ''
        except:
            cbq = ''

        curr_chnl_bq = chnl + self.getBQ(cbq)
        if curr_chnl_bq in self.SatLst:
            num = self.SatLst[curr_chnl_bq]
            return str(num) + ' '
        name = info.getName()
        if name in self.SatLst2:
            num = self.SatLst2[name]
            return str(num) + ' '
        if self.type == self.NUMBERANDNAMEEVENT:
            if chnl in self.SatLst:
                num = self.SatLst[chnl]
                return str(num) + ' '
        return ''

    def getServList(self, eSRef):
        tot_num = 0
        hService = eServiceCenter.getInstance()
        Services = hService.list(eSRef)
        Bouquets = Services and Services.getContent('SN', True)
        for bq in Bouquets:
            curr_bq = self.getBQ(bq[0])
            self.Bq[curr_bq] = (len(self.Bq), bq[1])
            srv = hService.list(eServiceReference(bq[0]))
            chs = srv and srv.getContent('SN', True)
            for ch in chs:
                if not ch[0].startswith('1:64:'):
                    tot_num = tot_num + 1
                    self.SatLst[ch[0] + curr_bq] = tot_num
                    self.SatLst[ch[0]] = tot_num
                    self.SatLst2[ch[1]] = tot_num

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
