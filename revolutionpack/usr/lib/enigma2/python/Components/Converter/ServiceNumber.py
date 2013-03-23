##
##
##
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eServiceCenter, eServiceReference, iServiceInformation

class ServiceNumber(Converter, object):
	NUMBER = 3
	
	def __init__(self, type):
		Converter.__init__(self, type)
		self.SatLst  = {}		
		self.SatLst2 = {}			
		self.Bq = {}			
		self.getServList(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
		self.getServList(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
		if type == "Number":
			self.type = self.NUMBER

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return "---"		
		if self.type == self.NUMBER:
			chnl = info.getInfoString(iServiceInformation.sServiceref)
			try: 				
				if chnl.split(':')[2] == '1':
					cbq = config.tv.lastroot.value 
				elif chnl.split(':')[2] == '19' or chnl.split(':')[2] == '17': 
					cbq = config.tv.lastroot.value 
				elif chnl.split(':')[2] == '2' or chnl.split(':')[2] == '10': 
					cbq = config.radio.lastroot.value 
				else: cbq = ""
			except: 
				cbq = ""
			curr_chnl_bq = chnl + self.getBQ(cbq) 
			if curr_chnl_bq in self.SatLst: 
				num = self.SatLst[curr_chnl_bq]
				return str(num) + ". "
			else:						
				name = info.getName()
				if name in self.SatLst2: 
					num = self.SatLst2[name]
					return str(num) + ". "
			return "---"				
		
	text = property(getText)

	def getServList(self, eSRef):
		tot_num = 0  		
		hService = eServiceCenter.getInstance()
		Services = hService.list(eSRef)
		Bouquets = Services and Services.getContent("SN", True)
		for bq in Bouquets:
			curr_bq = self.getBQ(bq[0])
			self.Bq[curr_bq] = (len(self.Bq),bq[1]) 
			srv = hService.list(eServiceReference(bq[0]))
			chs = srv and srv.getContent("SN", True)
			for ch in chs:
				if not ch[0].startswith('1:64:'):	 
					tot_num = tot_num + 1
					self.SatLst[ch[0]+curr_bq] = tot_num	
					self.SatLst[ch[0]] = tot_num	
					self.SatLst2[ch[1]] = tot_num	

	def getBQ(self, bq_str = ""): 
		if bq_str == "": 
			return ""
		a = bq_str.rfind('FROM BOUQUET \"userbouquet.')
		b = bq_str.rfind('.tv\" ORDER')
		c = bq_str.rfind('.radio\" ORDER')
		if c > b: 
			b=c+5
		if bq_str.rfind('FROM SATELLITES') != -1: 
			return ""
		if (b > a) and (a != -1) and (b != -1):
			return bq_str[a+14:b+3]
		return ""          	