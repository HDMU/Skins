from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Sensors import sensors
from Poll import Poll

class vhdConvSmartInfo(Poll, Converter, object):
    SMART_LABEL = 0
    SMART_INFO_H = 1

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.type = {'ShowMe': self.SMART_LABEL,
         'ExpertInfo': self.SMART_INFO_H}[type]
        self.poll_interval = 30000
        self.poll_enabled = True
        self.ar_fec = ['Auto',
         '1/2',
         '2/3',
         '3/4',
         '5/6',
         '7/8',
         '3/5',
         '4/5',
         '8/9',
         '9/10',
         'None',
         'None',
         'None',
         'None',
         'None']
        self.ar_pol = ['H',
         'V',
         'CL',
         'CR',
         'na',
         'na',
         'na',
         'na',
         'na',
         'na',
         'na',
         'na']

    @cached
    def getText(self):
        service = self.source.service
        if service:
            info = service.info()
            return info or ''
        Ret_Text = ''
        xresol = self.type == self.SMART_INFO_H and info.getInfo(iServiceInformation.sVideoWidth)
        yresol = info.getInfo(iServiceInformation.sVideoHeight)
        feinfo = service and service.frontendInfo()
        if feinfo is not None and xresol > 0:
            if yresol > 580:
                Ret_Text = 'HD     '
            else:
                Ret_Text = 'SD     '
            if feinfo:
                frontendData = feinfo.getAll(True)
                if frontendData is not None:
                    if frontendData.get('tuner_type') == 'DVB-S' or frontendData.get('tuner_type') == 'DVB-C':
                        frequency = str(frontendData.get('frequency') / 1000) + ' MHz'
                        symbolrate = str(float(frontendData.get('symbol_rate')) / float(1000000)) + ' MS/s'
                        try:
                            if frontendData.get('tuner_type') == 'DVB-S':
                                polarisation_i = frontendData.get('polarization')
                            else:
                                polarisation_i = 0
                            fec_i = frontendData.get('fec_inner')
                            Ret_Text = Ret_Text + frequency + '  -  ' + self.ar_pol[polarisation_i] + '  -  ' + self.ar_fec[fec_i] + '  -  ' + symbolrate + '     '
                        except:
                            Ret_Text = Ret_Text + frequency + '     ' + symbolrate + '     '

                        orb_pos = ''
                        if frontendData.get('tuner_type') == 'DVB-S':
                            orbital_pos = int(frontendData['orbital_position'])
                            if orbital_pos > 1800:
                                orb_pos = str(float(3600 - orbital_pos) / 10.0) + 'W'
                            elif orbital_pos > 0:
                                orb_pos = str(float(orbital_pos) / 10.0) + 'E'
                        Ret_Text = Ret_Text + 'Pos: ' + orb_pos + '   '
                    elif frontendData.get('tuner_type') == 'DVB-T':
                        frequency = str(frontendData.get('frequency') / 1000) + ' MHz'
                        Ret_Text = Ret_Text + 'Frequency: ' + frequency
                prvd = info.getInfoString(iServiceInformation.sProvider)
                Ret_Text = self.kurz(prvd) + '     ' + Ret_Text
            maxtemp = 0
            sensotN = '?'
            try:
                templist = sensors.getSensorsList(sensors.TYPE_TEMPERATURE)
                tempcount = len(templist)
                for count in range(tempcount):
                    id = templist[count]
                    tt = sensors.getSensorValue(id)
                    if tt > maxtemp:
                        maxtemp = tt
                        sensotN = sensors.getSensorName(id)
                        if sensotN == 'undefined':
                            sensotN = 'sensor-' + str(id)

                Ret_Text = 'max. Box-Temp:  ' + str(maxtemp) + '\xb0C / ' + sensotN + '\n' + Ret_Text
            except:
                pass

            return Ret_Text
        return 'n/a'

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, what)

    def kurz(self, langTxt):
        if len(langTxt) > 23:
            retT = langTxt[:20] + '...'
            return retT
        else:
            return langTxt
