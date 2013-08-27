import metrixDefaults
import random
import metrixCore
import traceback
config = metrixDefaults.loadDefaults()

def getSyncRow(area, category, keyname, keydescription, value, order = 0):
    row = []
    row.append(area)
    row.append(category)
    row.append(keyname)
    row.append(keydescription)
    row.append(value)
    row.append(order)
    return row


def syncNow(sync_data):
    try:
        url = 'http://connect.mymetrix.de/store/api/?q=v2.set.info'
        params = {'data': sync_data}
        metrixCore.getWeb(url, True, params)
    except:
        print '[MetrixCloudSync] Error sending data'
