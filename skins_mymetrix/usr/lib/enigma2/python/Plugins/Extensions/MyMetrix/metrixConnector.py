from Screens.Screen import Screen
from metrixTools import getHex, getHexColor, skinPartIsCompatible
from ServiceReference import ServiceReference
from os import environ, listdir, remove, rename, system
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.EpgSelection import EPGSelection
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Screens.ChannelSelection import ChannelSelection, BouquetSelector
from Screens.TimerEntry import TimerEntry
from Plugins.Plugin import PluginDescriptor
from Screens.Standby import TryQuitMainloop
from enigma import eTimer, eDVBDB, eConsoleAppContainer
from enigma import eEPGCache, eListbox, eServiceCenter, eServiceReference
from Components.Input import Input
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.config import config
from Components.UsageConfig import preferredInstantRecordPath, defaultMoviePath
from Components.EpgList import EPGList, Rect
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.ServiceList import ServiceList
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Button import Button
from Components.config import config, ConfigClock, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry, ConfigNumber, ConfigBoolean
from uuid import getnode as get_id
from encode import multipart_encode
from streaminghttp import register_openers
from Components.ServiceList import ServiceList
import cookielib
from xml.dom.minidom import parseString
import gettext
import MultipartPostHandler
from xml.dom.minidom import parseString, parse
import os
import urllib2
import socket
import e2info
import metrixDefaults
import metrixTools
import time
import threading
import base64
import traceback
import metrixWeatherUpdater
import shutil
import metrixCore
import metrix_SkinPartTools
import metrixCloudSync
import random
import metrix_Intro
import metrixGeneral
config = metrixDefaults.loadDefaults()

def syncStart(session):
    global global_session
    global global_executer
    global_session = session
    global_executer = eConsoleAppContainer()
    config.plugins.MetrixUpdater.Reboot.value = 0
    config.plugins.MetrixUpdater.save()
    threadUpdater = threading.Thread(target=sync, args=())
    threadUpdater.daemon = True
    threadUpdater.start()
    threadUpdaterGeneral = threading.Thread(target=syncGeneral, args=())
    threadUpdaterGeneral.daemon = True
    threadUpdaterGeneral.start()
    threadActions = threading.Thread(target=syncActions, args=())
    threadActions.daemon = True
    threadActions.start()
    if config.plugins.MyMetrix.showFirstRun.value == '1':
        global_session.open(metrix_Intro.OpenScreen)


def syncGeneral():
    while 1:
        if config.plugins.MetrixConnect.auth_token.value == 'None':
            pass
        else:
            try:
                prepareInfoGeneral(global_session)
            except Exception as e:
                traceback.print_exc()

            try:
                prepareInfoSkinParts()
            except Exception as e:
                traceback.print_exc()

            try:
                if config.plugins.MyMetrix.AutoUpdate.value == '1':
                    getPackageUpdates()
            except Exception as e:
                traceback.print_exc()

            try:
                postBackup()
            except:
                traceback.print_exc()

        time.sleep(1800)


def sync():
    while 1:
        try:
            metrixWeatherUpdater.GetWeather()
        except Exception as e:
            print '[MyMetrix] MetrixWeather - ' + str(e)
            traceback.print_exc()

        if config.plugins.MetrixConnect.auth_token.value != 'None':
            try:
                prepareInfo(global_session)
            except Exception as e:
                traceback.print_exc()

            try:
                if config.plugins.MyMetrix.AutoUpdateSkinParts.value == '1':
                    metrix_SkinPartTools.updateSkinParts()
            except Exception as e:
                traceback.print_exc()

        time.sleep(3600)


def syncActions():
    syncinterval = 320
    while 1:
        if config.plugins.MetrixConnect.auth_token.value == 'None':
            pass
        else:
            try:
                getActions()
                syncinterval = getInterval()
            except:
                print 'Error getting interval'

        time.sleep(syncinterval)


def runAction(item_id, action, actiontype, param):
    checkAction(item_id)
    if action == 'install':
        if actiontype == 'SkinPart':
            installSkinPart(param, item_id)
        elif actiontype == 'MetrixColors':
            installMetrixColors(param, item_id)
        elif actiontype == 'Package':
            installPackage(param, item_id)
    elif action == 'generateSkin':
        generateSkin(item_id)
    elif action == 'disable':
        if actiontype == 'SkinPart':
            try:
                metrix_SkinPartTools.disableSkinPart('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/screens/active/screen_' + param)
                showInfo(_('Screen successfully disabled!'))
                postBackup()
            except:
                pass

            try:
                metrix_SkinPartTools.disableSkinPart('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/widgets/active/widget_' + param)
                showInfo(_('Widget successfully disabled!'))
                postBackup()
            except:
                pass

    elif action == 'enable':
        if actiontype == 'SkinPart':
            try:
                metrix_SkinPartTools.enableSkinPart('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/screens/active/screen_' + param)
                showInfo(_('Screen successfully enabled!'))
                postBackup()
            except:
                pass

            try:
                metrix_SkinPartTools.enableSkinPart('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/widgets/active/widget_' + param)
                showInfo(_('Widget successfully enabled!'))
                postBackup()
            except:
                pass

    elif action == 'generateRestart':
        generateSkin(item_id)
        time.sleep(1)
        rebootGui(item_id)
    elif action == 'restartGui':
        rebootGui(item_id)
    elif action == 'command':
        runCommand(actiontype, param, item_id)


def prepareInfo(session):
    try:
        statusinfo = e2info.getStatusInfo2(session)
        try:
            postAnonymous('program', statusinfo['currservice_name'])
            postAnonymous('channel', statusinfo['currservice_station'])
        except:
            pass

        sync_data = []
        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'General', 'inStandby', 'Standby status', statusinfo['inStandby'], 8))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Current Service', 'currservice_name', 'Program', statusinfo['currservice_name'], 1))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Current Service', 'currservice_description', 'Description', statusinfo['currservice_description'], 2))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Current Service', 'currservice_station', 'Channel', statusinfo['currservice_station'], 3))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Current Service', 'currservice_serviceref', 'ID', statusinfo['currservice_serviceref'], 4))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Current Service', 'currservice_begin', 'Begin', statusinfo['currservice_begin'], 5))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Current Service', 'currservice_end', 'End', statusinfo['currservice_end'], 6))
        except:
            pass

        metrixCloudSync.syncNow(sync_data)
    except:
        pass


def prepareInfoSkinParts():
    try:
        pass
    except:
        pass


def prepareInfoGeneral(session):
    try:
        prepareInfo(session)
    except:
        pass

    try:
        boxinfo = e2info.getInfo()
        sync_data = []
        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Software', 'mymetrix', 'MyMetrix version', metrixGeneral.getVersion(), 0))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Software', 'enigmaver', 'GUI version', boxinfo['enigmaver'], 0))
        except:
            pass

        time.sleep(1)
        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Software', 'imagever', 'Firmware version', boxinfo['imagever'], 1))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Software', 'kernelver', 'Kernel version', boxinfo['kernelver'], 2))
        except:
            pass

        try:
            for item in boxinfo['ifaces']:
                sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Network Interface ' + item['name'], item['name'] + 'dhcp', 'DHCP status', item['dhcp'], 1))
                sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Network Interface ' + item['name'], item['name'] + 'ip', 'IP address', item['ip'], 2))
                sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Network Interface ' + item['name'], item['name'] + 'mac', 'MAC address', item['mac'], 3))
                sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Network Interface ' + item['name'], item['name'] + 'mask', 'Net mask', item['mask'], 4))
                sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Network Interface ' + item['name'], item['name'] + 'gw', 'Gateway', item['gw'], 5))

        except:
            pass

        try:
            for item in boxinfo['tuners']:
                sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Tuners', item['name'], item['name'], item['type']))

        except:
            pass

        try:
            for item in boxinfo['hdd']:
                sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Hard disk ' + item['model'], 'hddcapacity', 'Capacity', item['capacity'], 1))
                sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'Hard disk ' + item['model'], 'hddfree', 'Free', item['free'], 2))

        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'General', 'brand', 'Brand', boxinfo['brand'], 2))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'General', 'model', 'Model', boxinfo['model'], 3))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'General', 'chipset', 'Chipset', boxinfo['chipset'], 4))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'General', 'mem1', 'Total memory', boxinfo['mem1'], 5))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'General', 'mem2', 'Free memory', boxinfo['mem2'], 6))
        except:
            pass

        try:
            sync_data.append(metrixCloudSync.getSyncRow('Box Info', 'General', 'uptime', 'Uptime', boxinfo['uptime'], 7))
        except:
            pass

        metrixCloudSync.syncNow(sync_data)
    except:
        pass


def postBackup():
    postSkinParts(metrixDefaults.pathRoot() + 'skinparts/widgets/active/', 'Active')
    postSkinParts(metrixDefaults.pathRoot() + 'skinparts/screens/active/', 'Active')
    postSkinParts(metrixDefaults.pathRoot() + 'skinparts/widgets/inactive/', 'Inactive')
    postSkinParts(metrixDefaults.pathRoot() + 'skinparts/screens/inactive/', 'Inactive')


def postSkinParts(path, isActive = 'Active'):
    dirs = listdir(path)
    sync_data = []
    for dir in dirs:
        try:
            file = open(path + '/' + dir + '/meta.xml', 'r')
            data = file.read()
            file.close()
            dom = parseString(data)
            for design in dom.getElementsByTagName('entry'):
                id = str(design.getAttributeNode('id').nodeValue)
                name = str(design.getAttributeNode('name').nodeValue)
                type = str(design.getAttributeNode('type').nodeValue)
                sync_data.append(metrixCloudSync.getSyncRow('SkinParts', isActive, 'skinpart_' + id, name + ' [' + type + ']', id))

        except:
            pass

    metrixCloudSync.syncNow(sync_data)


def postAnonymous(keyname = 'status', value = ''):
    try:
        url = 'http://connect.mymetrix.de/store/api/?q=connect.statistic'
        params = {'keyname': keyname,
         'value': value}
        metrixCore.getWeb(url, True, params)
    except:
        pass


def getActions(url = 'http://connect.mymetrix.de/store/api/?q=connect.actions'):
    try:
        data = metrixCore.getWeb(url, True)
        dom = parseString(data)
        for entry in dom.getElementsByTagName('entry'):
            item_id = str(entry.getAttributeNode('id').nodeValue)
            action = str(entry.getAttributeNode('action').nodeValue)
            actiontype = str(entry.getAttributeNode('type').nodeValue)
            param = str(entry.getAttributeNode('param').nodeValue)
            runAction(item_id, action, actiontype, param)

    except:
        pass


def getInterval(url = 'http://connect.mymetrix.de/store/api/?q=connect.activity'):
    try:
        data = metrixCore.getWeb(url, True)
        dom = parseString(data)
        for entry in dom.getElementsByTagName('entry'):
            return int(str(entry.getAttributeNode('interval').nodeValue))

    except:
        return 320


def installSkinPart(param, actionId):
    print '[MyMetrix] Installing skinpart: ' + param
    downloadurl = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinpartxml&id='
    downloadmetaurl = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinpartmeta&id='
    screenshotpath = 'http://connect.mymetrix.de/store/api/?q=get.pngresized&width=550'
    screenshotpath_v2 = 'http://connect.mymetrix.de/store/api/?q=v2.get.png&width=550&type=6'
    item_id = ''
    item_type = ''
    author = ''
    image_id = ''
    image_token = ''
    date_modified = ''
    try:
        data = metrixCore.getWeb(downloadmetaurl + str(param), False)
        dom = parseString(data)
        for entry in dom.getElementsByTagName('entry'):
            item_id = str(entry.getAttributeNode('id').nodeValue)
            item_name = str(entry.getAttributeNode('name').nodeValue)
            item_type = str(entry.getAttributeNode('type').nodeValue)
            author = str(entry.getAttributeNode('author').nodeValue)
            image_id = str(entry.getAttributeNode('image_id').nodeValue)
            image_token = str(entry.getAttributeNode('image_token').nodeValue)
            date = str(entry.getAttributeNode('date').nodeValue)
            try:
                date_modified = str(entry.getAttributeNode('date_modified').nodeValue)
            except:
                date_modified = date

        if item_type == 'bundle':
            metrix_SkinPartTools.installBundle(item_id, type, author)
        else:
            metrix_SkinPartTools.installSkinPart(item_id, type, author, image_id, image_token)
        showInfo(item_name + _(' successfully installed!'))
    except Exception as e:
        print '[MyMetrix] Error installing SkinPart'
        print '[MyMetrix] ' + str(e)
        traceback.print_exc()


def installMetrixColors(designname, actionId):
    print '[MyMetrix] Installing MetrixColors ' + designname
    try:
        metrixColorsUrl = 'http://connect.mymetrix.de/store/api/?q=get.xml.designs&name=' + designname
        data = metrixCore.getWeb(metrixColorsUrl, False)
        dom = parseString(data)
        for design in dom.getElementsByTagName('design'):
            name = str(design.getAttributeNode('name').nodeValue)
            title = str(design.getAttributeNode('title').nodeValue)
            if name == designname:
                try:
                    config.plugins.MyMetrix.Color.BackgroundTransparency.value = str(design.getAttributeNode('backgroundtrans').nodeValue)
                    config.plugins.MyMetrix.Color.SelectionTransparency.value = str(design.getAttributeNode('selectiontrans').nodeValue)
                    config.plugins.MyMetrix.Color.BackgroundTextTransparency.value = str(design.getAttributeNode('backgroundtexttrans').nodeValue)
                    config.plugins.MyMetrix.Color.Selection.value = str(design.getAttributeNode('selection').nodeValue)
                    config.plugins.MyMetrix.Color.ProgressBar.value = str(design.getAttributeNode('progressbars').nodeValue)
                    config.plugins.MyMetrix.Color.Background.value = str(design.getAttributeNode('background').nodeValue)
                    config.plugins.MyMetrix.Color.Background2.value = str(design.getAttributeNode('background2').nodeValue)
                    config.plugins.MyMetrix.Color.Foreground.value = str(design.getAttributeNode('foreground').nodeValue)
                    config.plugins.MyMetrix.Color.BackgroundText.value = str(design.getAttributeNode('backgroundtext').nodeValue)
                    config.plugins.MyMetrix.Color.Accent1.value = str(design.getAttributeNode('accent1').nodeValue)
                    config.plugins.MyMetrix.Color.Accent2.value = str(design.getAttributeNode('accent2').nodeValue)
                    config.plugins.MyMetrix.Color.Selection_Custom.value = toRGB(str(design.getAttributeNode('selection_custom').nodeValue))
                    config.plugins.MyMetrix.Color.Background_Custom.value = toRGB(str(design.getAttributeNode('background_custom').nodeValue))
                    config.plugins.MyMetrix.Color.Background2_Custom.value = toRGB(str(design.getAttributeNode('background2_custom').nodeValue))
                    config.plugins.MyMetrix.Color.Foreground_Custom.value = toRGB(str(design.getAttributeNode('foreground_custom').nodeValue))
                    config.plugins.MyMetrix.Color.BackgroundText_Custom.value = toRGB(str(design.getAttributeNode('backgroundtext_custom').nodeValue))
                    config.plugins.MyMetrix.Color.Accent1_Custom.value = toRGB(str(design.getAttributeNode('accent1_custom').nodeValue))
                    config.plugins.MyMetrix.Color.Accent2_Custom.value = toRGB(str(design.getAttributeNode('accent2_custom').nodeValue))
                    showInfo(title + _(' successfully installed!'))
                except:
                    print '[MyMetrix] Error installing MetrixColors'

    except:
        print '[MyMetrix] Error downloading MetrixColors'


def toRGB(text):
    rgb = []
    textar = str(text.replace('[', '').replace(']', '')).split(',')
    rgb.append(int(textar[0]))
    rgb.append(int(textar[1]))
    rgb.append(int(textar[2]))
    return rgb


def checkAction(actionId):
    if not metrixCore.getWeb('http://connect.mymetrix.de/store/api/?q=connect.actioncheck', True, {'id': actionId}):
        print '[MyMetrix] Error checking action'


def getPackageUpdates():
    try:
        updates_available = False
        data = metrixCore.getWeb('http://connect.mymetrix.de/store/api/?q=get.xml.packages&category_id=%', True)
        if not data:
            print '[MyMetrix] Error getting package updates'
        dom = parseString(data)
        for design in dom.getElementsByTagName('entry'):
            item_id = str(design.getAttributeNode('id').nodeValue)
            name = str(design.getAttributeNode('name').nodeValue)
            author = str(design.getAttributeNode('author').nodeValue)
            version = str(design.getAttributeNode('version').nodeValue)
            rating = str(design.getAttributeNode('rating').nodeValue)
            date = str(design.getAttributeNode('date_created').nodeValue)
            item_type = str(design.getAttributeNode('type').nodeValue)
            file_id = str(design.getAttributeNode('file_id').nodeValue)
            file_token = str(design.getAttributeNode('file_token').nodeValue)
            image_id = str(design.getAttributeNode('image_id').nodeValue)
            image_token = str(design.getAttributeNode('image_token').nodeValue)
            total_votes = str(design.getAttributeNode('total_votes').nodeValue)
            description = str(design.getAttributeNode('description').nodeValue)
            previouspackage = str(design.getAttributeNode('previouspackage').nodeValue)
            path = metrixDefaults.pathRoot() + 'packages/' + item_id
            if not os.path.exists(path):
                if previouspackage != '0':
                    path = metrixDefaults.pathRoot() + 'packages/' + previouspackage
                    if os.path.exists(path):
                        '[MyMetrix] Update found: ' + name + ' Version: ' + version
                        installPackage(item_id + ';' + file_id + ';' + file_token, 0)
                        updates_available = True

        if updates_available == True:
            getPackageUpdates()
    except:
        pass


def installPackage(param, actionId):
    params = param.split(';')
    packageId = params[0]
    print '[MyMetrix] Installing package ' + packageId
    downloadurl = 'http://connect.mymetrix.de/store/api/?q=get.xml.packagefile' + '&file_id=' + params[1] + '&token=' + params[2]
    localPath = '/tmp/metrixPackage.ipk'
    try:
        file_name = localPath
        u = urllib2.urlopen(downloadurl)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders('Content-Length')[0])
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
            status = 'Downloading... (%3.0f%%)' % (file_size_dl * 100.0 / file_size)
            status = status + chr(8) * (len(status) + 1)

        f.close()
        global_executer.execute('opkg install --force-overwrite ' + localPath)
        config.plugins.MetrixUpdater.Reboot.value = 1
        config.plugins.MetrixUpdater.save()
        configfile.save()
        path = metrixDefaults.pathRoot() + 'packages/' + packageId
        if not os.path.exists(path):
            os.makedirs(path)
        showInfo(_('Package successfully installed!'))
    except:
        print '[MyMetrix] Error installing package ' + params[0]


def getSkinPartsScreennames(path):
    screennames = []
    dirs = listdir(path)
    for dir in dirs:
        try:
            dom = parse(path + '/' + dir + '/data.xml')
            screen = dom.getElementsByTagName('screen')[0]
            name = str(screen.getAttributeNode('name').nodeValue)
            screennames.append(name)
        except:
            pass

    return screennames


def generateSkin(actionId):
    try:
        print '[MyMetrix] Generating Skin via web'
        showInfo(_('Generating skin!'))
        screennames = []
        screennames = getSkinPartsScreennames(metrixDefaults.pathRoot() + 'skinparts/screens/active/')
        skindom = parse(metrixDefaults.pathRoot() + 'skintemplates/' + config.plugins.MyMetrix.templateFile.value)
        skinNode = skindom.getElementsByTagName('skin')[0]
        setColor(skinNode)
        for screen in skindom.getElementsByTagName('screen'):
            screenname = str(screen.getAttributeNode('name').nodeValue)
            if screenname in screennames:
                parentNode = screen.parentNode
                parentNode.removeChild(screen)

        path = metrixDefaults.pathRoot() + 'skinparts/screens/active/'
        dirs = listdir(path)
        for dir in dirs:
            try:
                screendom = parse(path + '/' + dir + '/data.xml')
                customscreen = skindom.importNode(screendom.getElementsByTagName('screen')[0], True)
                skinNode.appendChild(customscreen)
            except:
                pass

        path = metrixDefaults.pathRoot() + 'skinparts/widgets/active/'
        dirs = listdir(path)
        for dir in dirs:
            try:
                widgetdom = parse(path + '/' + dir + '/data.xml')
                widget = widgetdom.getElementsByTagName('skinpartwidget')[0]
                widgetscreenname = str(widget.getAttributeNode('screenname').nodeValue)
                for screen in skinNode.getElementsByTagName('screen'):
                    screenname = str(screen.getAttributeNode('name').nodeValue)
                    if screenname == widgetscreenname:
                        for child in widget.childNodes:
                            childimport = skindom.importNode(child, True)
                            screen.appendChild(childimport)

                        break

            except:
                pass

        for screen in skindom.getElementsByTagName('screen'):
            screenname = str(screen.getAttributeNode('name').nodeValue)
            for widget in screen.getElementsByTagName('widget'):
                try:
                    pixmap = str(widget.getAttributeNode('pixmap').nodeValue)
                    if pixmap == 'MetrixHD/colors/00ffffff.png':
                        widget.setAttribute('pixmap', pixmap.replace('/00ffffff', '/' + config.plugins.MyMetrix.Color.ProgressBar.value.replace('#', '')))
                    elif pixmap == '%METRIX:PROGRESSBAR:COLOR:MULTI%':
                        widget.setAttribute('pixmap', 'MetrixHD/colors/' + config.plugins.MyMetrix.Color.ProgressBar.value.replace('#', '') + '.png')
                    elif pixmap == '%METRIX:PROGRESSBAR:COLOR:WHITE%':
                        widget.setAttribute('pixmap', 'MetrixHD/colors/00ffffff.png')
                except:
                    pass

        for screen in skindom.getElementsByTagName('screen'):
            screen = skinPartIsCompatible(screen)

        file = '/usr/share/enigma2/MetrixHD/skin.xml'
        path = os.path.dirname(file)
        if not os.path.exists(path):
            os.makedirs(path)
        file = open(path + '/skin.xml', 'w')
        file.write(skindom.toxml())
        file.close()
        try:
            config.skin.primary_skin.value = 'MetrixHD/skin.xml'
            config.skin.primary_skin.save()
            config.skin.primary_fallback_skin.value = True
            config.skin.primary_fallback_skin.save()
            configfile.save()
            showInfo(_('Skin successfully generated!'))
        except Exception as e:
            print '[MyMetrix] ' + str(e)
            traceback.print_exc()
            print '[MyMetrix] Error activating MetrixHD'

    except Exception as e:
        print '[MyMetrix] ' + str(e)
        traceback.print_exc()


def setColor(skinNode):
    try:
        if config.plugins.MyMetrix.Color.Selection.value == 'CUSTOM':
            _selection = getHexColor(config.plugins.MyMetrix.Color.Selection_Custom.value, config.plugins.MyMetrix.Color.SelectionTransparency.value)
        else:
            _selection = config.plugins.MyMetrix.Color.Selection.value.replace('#00', '#' + str(hex(int(config.plugins.MyMetrix.Color.SelectionTransparency.value))))
        if config.plugins.MyMetrix.Color.Background2.value == 'CUSTOM':
            _background2 = getHexColor(config.plugins.MyMetrix.Color.Background2_Custom.value, config.plugins.MyMetrix.Color.BackgroundTransparency.value)
        else:
            _background2 = config.plugins.MyMetrix.Color.Background2.value.replace('#00', '#' + getHex(config.plugins.MyMetrix.Color.BackgroundTransparency.value))
        if config.plugins.MyMetrix.Color.Background.value == 'CUSTOM':
            _background = getHexColor(config.plugins.MyMetrix.Color.Background_Custom.value, config.plugins.MyMetrix.Color.BackgroundTransparency.value)
        else:
            _background = config.plugins.MyMetrix.Color.Background.value.replace('#00', '#' + getHex(config.plugins.MyMetrix.Color.BackgroundTransparency.value))
        if config.plugins.MyMetrix.Color.BackgroundText.value == 'CUSTOM':
            _BackgroundText = getHexColor(config.plugins.MyMetrix.Color.BackgroundText_Custom.value, config.plugins.MyMetrix.Color.BackgroundTextTransparency.value)
        else:
            _BackgroundText = config.plugins.MyMetrix.Color.BackgroundText.value.replace('#00', '#' + getHex(config.plugins.MyMetrix.Color.BackgroundTextTransparency.value))
        if config.plugins.MyMetrix.Color.Foreground.value == 'CUSTOM':
            _Foreground = getHexColor(config.plugins.MyMetrix.Color.Foreground_Custom.value)
        else:
            _Foreground = config.plugins.MyMetrix.Color.Foreground.value
        if config.plugins.MyMetrix.Color.Accent1.value == 'CUSTOM':
            _Accent1 = getHexColor(config.plugins.MyMetrix.Color.Accent1_Custom.value)
        else:
            _Accent1 = config.plugins.MyMetrix.Color.Accent1.value
        if config.plugins.MyMetrix.Color.Accent2.value == 'CUSTOM':
            _Accent2 = getHexColor(config.plugins.MyMetrix.Color.Accent2_Custom.value)
        else:
            _Accent2 = config.plugins.MyMetrix.Color.Accent2.value
        if config.plugins.MyMetrix.Color.Background.value == 'CUSTOM':
            _transparent = getHexColor(config.plugins.MyMetrix.Color.Background_Custom.value, 255)
        else:
            _transparent = config.plugins.MyMetrix.Color.Background.value.replace('#00', '#ff')
        colors = skinNode.getElementsByTagName('colors')[0]
        for color in colors.getElementsByTagName('color'):
            colorname = color.getAttributeNode('name').nodeValue
            if colorname == 'metrixSelection':
                color.setAttribute('value', _selection)
            elif colorname == 'metrixBackground':
                color.setAttribute('value', _background)
            elif colorname == 'metrixBackground2':
                color.setAttribute('value', _background2)
            elif colorname == 'metrixPreTrans':
                color.setAttribute('value', _BackgroundText)
            elif colorname == 'metrixPreTrans2':
                color.setAttribute('value', _BackgroundText)
            elif colorname == 'metrixForeground':
                color.setAttribute('value', _Foreground)
            elif colorname == 'metrixAccent1':
                color.setAttribute('value', _Accent1)
            elif colorname == 'metrixAccent2':
                color.setAttribute('value', _Accent2)
            elif colorname == 'transparent':
                color.setAttribute('value', _transparent)

    except:
        pass


def rebootGui(actionId):
    print '[MyMetrix] Restarting GUI via web'
    showInfo(_('Restarting GUI!'))
    global_executer.execute('init 4 && sleep 10 && init 3')


def runCommand(type, param, actionId):
    print '[MyMetrix] Starting action via web'
    showInfo(_('Executing action!'))
    try:
        print 'command: ' + str(base64.b64decode(type) + ' ' + base64.b64decode(param))
        global_executer.execute(str(base64.b64decode(type) + ' ' + base64.b64decode(param)))
    except Exception as e:
        print '[MyMetrix] Error on action via web ' + str(e)
        traceback.print_exc()


def showInfo(text):
    try:
        global_session.open(MessageBox, _(text), type=MessageBox.TYPE_INFO, timeout=3)
    except Exception as e:
        print '[MyMetrix] ' + str(e)
        traceback.print_exc()
