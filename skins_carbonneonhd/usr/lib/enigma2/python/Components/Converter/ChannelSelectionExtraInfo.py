from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr
from enigma import eServiceCenter
from enigma import eEPGCache, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable, eServiceReference
from time import localtime

class ChannelSelectionExtraInfo(Converter, object):
    Reference = 1
    NextEventTitle = 2
    NextEventStartStopTime = 3
    NextEventStartTime = 4
    NextEventStopTime = 5
    NextEventDuration = 6
    NextEventFull = 7
    TInfoFrequency = 9
    TInfoPolaryzation = 10
    TInfoFec = 11
    TInfoSr = 12
    TInfoOrb = 13
    TInfoFull = 14

    def __init__(self, type):
        Converter.__init__(self, type)
        self.type = {'Reference': self.Reference,
         'NextEventTitle': self.NextEventTitle,
         'NextEventStartStopTime': self.NextEventStartStopTime,
         'NextEventStartTime': self.NextEventStartTime,
         'NextEventStopTime': self.NextEventStopTime,
         'NextEventDuration': self.NextEventDuration,
         'NextEventFull': self.NextEventFull,
         'TInfoFrequency': self.TInfoFrequency,
         'TInfoPolaryzation': self.TInfoPolaryzation,
         'TInfoFec': self.TInfoFec,
         'TInfoSR': self.TInfoSr,
         'TInfoOrbit': self.TInfoOrb,
         'TInfoFull': self.TInfoFull}[type]
        self.epgcache = eEPGCache.getInstance()

    def getServiceInfoValue(self, info, what, ref = None):
        if not (ref and info.getInfo(ref, what)):
            v = info.getInfo(what)
            return v != iServiceInformation.resIsString and 'N/A'
        return ref and info.getInfoString(ref, what) or info.getInfoString(what)

    @cached
    def getText(self):
        service = self.source.service
        print 'Test source='
        print self.source
        print 'Test service= %s' % service
        if service is None:
            return ''
        print 'Flags'
        marker = service.flags & eServiceReference.isMarker == eServiceReference.isMarker
        print marker
        if self.type == self.Reference:
            if marker:
                return ''
            refId = ''
            sname = service.toString()
            pos = sname.rfind(':')
            if pos != -1:
                refId = '' + sname[:-1]
            return refId
        if self.type >= self.NextEventTitle and self.type <= self.NextEventFull:
            eventNext = ''
            list = self.epgcache.lookupEvent(['IBDCTSERNX', (service.toString(), 1, -1)])
            print '---------- ChannelSelectionExtraInfo ----------'
            print list
            if len(list) > 0:
                eventNext = list[0]
                print eventNext
                if eventNext[4]:
                    if self.type == self.NextEventTitle:
                        return str(eventNext[4])
                    t_start = localtime(eventNext[1])
                    t_stop = localtime(eventNext[1] + eventNext[2])
                    eventStartTime = '%02d:%02d' % (t_start.tm_hour, t_start.tm_min)
                    eventStopTime = '%02d:%02d' % (t_stop.tm_hour, t_stop.tm_min)
                    duration = '%d min' % (eventNext[2] / 60)
                    if self.type == self.NextEventStartTime:
                        return eventStartTime
                    if self.type == self.NextEventStopTime:
                        return eventStopTime
                    if self.type == self.NextEventStartStopTime:
                        return eventStartTime + ' - ' + eventStopTime
                    if self.type == self.NextEventDuration:
                        return duration
                    if self.type == self.NextEventFull:
                        return '%s  %s\n%s' % (eventStartTime, duration, eventNext[4])
            else:
                return ' '
        elif self.type >= self.TInfoFrequency and self.type <= self.TInfoFull:
            info = eServiceCenter.getInstance().info(service)
            print 'TInfo'
            print info
            if info:
                transponderData = info.getInfoObject(service, iServiceInformation.sTransponderData)
                fq = pol = fec = sr = orb = ''
                print transponderData
                try:
                    if transponderData.has_key('frequency'):
                        tmp = int(transponderData['frequency']) / 1000
                        fq = str(tmp)
                    if transponderData.has_key('polarization'):
                        try:
                            pol = {eDVBFrontendParametersSatellite.Polarisation_Horizontal: 'H  ',
                             eDVBFrontendParametersSatellite.Polarisation_Vertical: 'V  ',
                             eDVBFrontendParametersSatellite.Polarisation_CircularLeft: 'CL  ',
                             eDVBFrontendParametersSatellite.Polarisation_CircularRight: 'CR  '}[transponderData['polarization']]
                        except:
                            pol = 'N/A'

                    if transponderData.has_key('fec_inner'):
                        try:
                            fec = {eDVBFrontendParametersSatellite.FEC_None: _('None  '),
                             eDVBFrontendParametersSatellite.FEC_Auto: _('Auto  '),
                             eDVBFrontendParametersSatellite.FEC_1_2: '1/2  ',
                             eDVBFrontendParametersSatellite.FEC_2_3: '2/3  ',
                             eDVBFrontendParametersSatellite.FEC_3_4: '3/4  ',
                             eDVBFrontendParametersSatellite.FEC_5_6: '5/6  ',
                             eDVBFrontendParametersSatellite.FEC_7_8: '7/8  ',
                             eDVBFrontendParametersSatellite.FEC_3_5: '3/5  ',
                             eDVBFrontendParametersSatellite.FEC_4_5: '4/5  ',
                             eDVBFrontendParametersSatellite.FEC_8_9: '8/9  ',
                             eDVBFrontendParametersSatellite.FEC_9_10: '9/10  '}[transponderData['fec_inner']]
                        except:
                            fec = 'N/A'

                        if fec == 'N/A':
                            try:
                                fec = {eDVBFrontendParametersCable.FEC_None: _('None  '),
                                 eDVBFrontendParametersCable.FEC_Auto: _('Auto  '),
                                 eDVBFrontendParametersCable.FEC_1_2: '1/2  ',
                                 eDVBFrontendParametersCable.FEC_2_3: '2/3  ',
                                 eDVBFrontendParametersCable.FEC_3_4: '3/4  ',
                                 eDVBFrontendParametersCable.FEC_5_6: '5/6  ',
                                 eDVBFrontendParametersCable.FEC_7_8: '7/8  ',
                                 eDVBFrontendParametersCable.FEC_8_9: '8/9  '}[transponderData['fec_inner']]
                            except:
                                fec = 'N/A'

                    if transponderData.has_key('symbol_rate'):
                        tmp = int(transponderData['symbol_rate']) / 1000
                        sr = str(tmp)
                    if transponderData.has_key('orbital_position'):
                        try:
                            orb = {3590: ' (1.0W)',
                             3592: ' (0.8W)',
                             3560: ' (4.0W)',
                             3550: ' (5.0W)',
                             3530: ' (7.0W)',
                             3520: ' (8.0W)',
                             3475: ' (12.5W)',
                             3460: ' (14.0W)',
                             3450: ' (15.0W)',
                             3420: ' (18.0W)',
                             3380: ' (22.0W)',
                             3355: ' (24.5W)',
                             3325: ' (27.5W)',
                             3300: ' (30.0W)',
                             3285: ' (31.5W)',
                             3170: ' (43.0W)',
                             3150: ' (45.0W)',
                             3070: ' (53.0W)',
                             3045: ' (55.5W)',
                             3020: ' (58.0W)',
                             2990: ' (61.0W)',
                             2900: ' (70.0W)',
                             2880: ' (72.0W)',
                             2875: ' (72.7W)',
                             2860: ' (74.0W)',
                             2810: ' (79.0W)',
                             2780: ' (82.0W)',
                             2690: ' (91.0W)',
                             3592: ' (0.8W)',
                             2985: ' (61.5W)',
                             2830: ' (77.0W)',
                             2630: ' (97.0W)',
                             2500: ' (110.0W)',
                             2502: ' (110.0W)',
                             2410: ' (119.0W)',
                             2391: ' (121.0W)',
                             2390: ' (121.0W)',
                             2412: ' (119.0W)',
                             2310: ' (129.0W)',
                             2311: ' (129.0W)',
                             2120: ' (148.0W)',
                             1100: ' (110.0E)',
                             1101: ' (110.0E)',
                             1131: ' (113.0E)',
                             1440: ' (144.0E)',
                             1006: ' (100.5E)',
                             1030: ' (103.0E)',
                             1056: ' (105.5E)',
                             1082: ' (108.2E)',
                             881: ' (88.0E)',
                             900: ' (90.0E)',
                             917: ' (91.5E)',
                             950: ' (95.0E)',
                             951: ' (95.0E)',
                             765: ' (76.5E)',
                             785: ' (78.5E)',
                             800: ' (80.0E)',
                             830: ' (83.0E)',
                             850: ' (85.2E)',
                             750: ' (75.0E)',
                             720: ' (72.0E)',
                             705: ' (70.5E)',
                             685: ' (68.5E)',
                             620: ' (62.0E)',
                             600: ' (60.0E)',
                             570: ' (57.0E)',
                             530: ' (53.0E)',
                             480: ' (48.0E)',
                             450: ' (45.0E)',
                             420: ' (42.0E)',
                             400: ' (40.0E)',
                             390: ' (39.0E)',
                             380: ' (38.0E)',
                             360: ' (36.0E)',
                             335: ' (33.5E)',
                             330: ' (33.0E)',
                             328: ' (32.8E)',
                             315: ' (31.5E)',
                             310: ' (31.0E)',
                             305: ' (30.5E)',
                             285: ' (28.5E)',
                             284: ' (28.2E)',
                             282: ' (28.2E)',
                             1220: ' (122.0E)',
                             1380: ' (138.0E)',
                             260: ' (26.0E)',
                             255: ' (25.5E)',
                             235: ' (23.5E)',
                             215: ' (21.5E)',
                             216: ' (21.6E)',
                             210: ' (21.0E)',
                             192: ' (19.2E)',
                             160: ' (16.0E)',
                             130: ' (13.0E)',
                             100: ' (10.0E)',
                             90: ' (9.0E)',
                             70: ' (7.0E)',
                             50: ' (5.0E)',
                             48: ' (4.8E)',
                             30: ' (3.0E)'}[transponderData['orbital_position']]
                        except:
                            orb = ''

                except:
                    pass

                print self.type
                print fq
                print pol
                print fec
                print sr
                print orb
                if self.type == self.TInfoFrequency:
                    return fq
                if self.type == self.TInfoPolaryzation:
                    return pol
                if self.type == self.TInfoFec:
                    return fec
                if self.type == self.TInfoSr:
                    return sr
                if self.type == self.TInfoOrb:
                    return orb
                if self.type == self.TInfoFull:
                    return '%s %s %s %s %s' % (fq,
                     pol,
                     fec,
                     sr,
                     orb)
        return ''

    text = property(getText)

    def changed(self, what):
        print 'Test what'
        print what
        if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart,):
            Converter.changed(self, what)
