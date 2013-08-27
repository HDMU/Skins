from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from uuid import getnode as get_id
import gettext
from e2info import getInfo as e2getInfo
from streaminghttp import register_openers
from encode import multipart_encode
import urllib2
import metrixDefaults
import md5
import time
import metrixCore
import metrixTools
import socket
import traceback
config = metrixDefaults.loadDefaults()

def getWeb(url, login = False, parameters = {}):
    try:
        opener = register_openers()
        if login and config.plugins.MetrixConnect.auth_token.value != 'None' and config.plugins.MetrixConnect.auth_token.value != '':
            params = {'auth_id': config.plugins.MetrixConnect.auth_id.value,
             'device_id': getDeviceID(),
             'auth_token': config.plugins.MetrixConnect.auth_token.value}
            params.update(parameters)
        else:
            params = parameters
        datagen, headers = multipart_encode(params)
        request = urllib2.Request(url, datagen, headers)
        data = urllib2.urlopen(request).read()
        return data
    except Exception as e:
        print '[MetrixCore] Error getting web: ' + url
        return False


def connectDevice(pin):
    model = e2getInfo()['model']
    params = {'pin': pin,
     'device_id': metrixCore.getDeviceID(),
     'device_name': socket.gethostname(),
     'device_type': model}
    data = metrixCore.getWeb('http://connect.mymetrix.de/store/api/?q=connect.device', False, params)
    if not data:
        print '[MyMetrix] Error connecting to server!'
    return data


def getDeviceID():
    device_id = 'open'
    try:
        if config.plugins.MetrixConnect.auth_session.value == None or config.plugins.MetrixConnect.auth_session.value == '':
            config.plugins.MetrixConnect.auth_session.value = str(md5.new(str(int(time.time()))).hexdigest())
            config.plugins.MetrixConnect.auth_session.save()
            configfile.save()
        device_id = str(md5.new(config.plugins.MetrixConnect.auth_session.value + str(get_id())).hexdigest())
    except:
        pass

    return device_id
