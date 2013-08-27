import xml.etree.cElementTree
from Tools.Import import my_import
from Screens.Screen import Screen
from Components.Sources.Source import Source, ObsoleteSource
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from twisted.web.client import downloadPage
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import os
import traceback
import md5
import metrixDefaults
import time
from streaminghttp import register_openers
from encode import multipart_encode
import urllib2
from xml.dom.minidom import parseString
import metrixTools
import shutil
import metrixCore
import metrixConnector
import datetime

def downloadSkinPartRenderer(id):
    url = 'http://connect.mymetrix.de/store/api/?q=v2.get.xml.files&width=550&type=7&id=' + id
    downloadAdditionalFiles(url, '/usr/lib/enigma2/python/Components/Renderer/')


def downloadSkinPartConverter(id):
    url = 'http://connect.mymetrix.de/store/api/?q=v2.get.xml.files&width=550&type=8&id=' + id
    downloadAdditionalFiles(url, '/usr/lib/enigma2/python/Components/Converter/')


def downloadSkinPartImages(id):
    url = 'http://connect.mymetrix.de/store/api/?q=v2.get.xml.files&width=550&type=5&id=' + id
    downloadAdditionalFiles(url, '/usr/share/enigma2/MetrixHD/skinparts/' + id + '/')


def downloadAdditionalFiles(url, target_path):
    try:
        opener = register_openers()
        params = {}
        datagen, headers = multipart_encode(params)
        request = urllib2.Request(url, datagen, headers)
        data = urllib2.urlopen(request).read()
        dom = parseString(data)
        for design in dom.getElementsByTagName('entry'):
            url = str(design.getAttributeNode('url').nodeValue)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            metrixTools.downloadFile(url, target_path + url.split('file=')[-1])

    except:
        pass


def installSkinPart(id, type, author = '', image_id = '', image_token = '', date_modified = '', isActive = True):
    downloadurl = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinpartxml&id='
    downloadmetaurl = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinpartmeta&id='
    screenshotpath = 'http://connect.mymetrix.de/store/api/?q=get.pngresized&width=550'
    screenshotpath_v2 = 'http://connect.mymetrix.de/store/api/?q=v2.get.png&width=550&type=6'
    path = metrixDefaults.pathRoot() + 'skinparts/' + type + 's/inactive/' + type + '_' + str(id) + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    datapath = metrixTools.downloadFile(downloadurl + str(id) + '&author=' + author, path + 'data.xml', 'SKINPART/', '/usr/share/enigma2/MetrixHD/skinparts/' + id + '/')
    metapath = metrixTools.downloadFile(downloadmetaurl + str(id) + '&author=' + author, path + 'meta.xml')
    imagepath = ''
    if image_id == '':
        imagepath = metrixTools.downloadFile(screenshotpath_v2 + '&id=' + id, path + 'preview.png')
    else:
        imagepath = metrixTools.downloadFile(screenshotpath + '&image_id=' + image_id + '&token=' + image_token, path + 'preview.png')
    if isActive:
        enableSkinPart(path)
    downloadSkinPartRenderer(id)
    downloadSkinPartConverter(id)
    downloadSkinPartImages(id)


def installBundle(id, type, author = ''):
    downloadurl = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinpartbundle&id=' + id
    skinparts = str(metrixCore.getWeb(downloadurl, True, {'author': author})).split(';')
    for skinpart in skinparts:
        try:
            downloadmetaurl = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinpartmeta&id=' + skinpart
            metafile = metrixCore.getWeb(downloadmetaurl, True)
            dom = parseString(metafile)
            for design in dom.getElementsByTagName('entry'):
                id = str(design.getAttributeNode('id').nodeValue)
                name = str(design.getAttributeNode('name').nodeValue)
                type = str(design.getAttributeNode('type').nodeValue)
                image_id = str(design.getAttributeNode('image_id').nodeValue)
                image_token = str(design.getAttributeNode('image_token').nodeValue)
                author = str(design.getAttributeNode('author').nodeValue)
                installSkinPart(skinpart, type, author, image_id, image_token)

        except:
            pass


def enableSkinPart(file):
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/widgets/active'):
        os.makedirs('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/widgets/active')
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/screens/active'):
        os.makedirs('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/screens/active')
    if os.path.exists(file.replace('/inactive', '/active')):
        shutil.rmtree(file.replace('/inactive', '/active'), True)
    shutil.move(file, file.replace('/inactive', '/active'))


def disableSkinPart(file):
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/widgets/inactive'):
        os.makedirs('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/widgets/inactive')
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/screens/inactive'):
        os.makedirs('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/skinparts/screens/inactive')
    if os.path.exists(file.replace('/active', '/inactive')):
        shutil.rmtree(file.replace('/active', '/inactive'), True)
    shutil.move(file, file.replace('/active', '/inactive'))


def downloadScreenshot(item_id, image_id = '', image_token = ''):
    screenshotpath = 'http://connect.mymetrix.de/store/api/?q=get.pngresized&width=550'
    screenshotpath_v2 = 'http://connect.mymetrix.de/store/api/?q=v2.get.png&width=550&type=6'
    path = ''
    if image_id == '':
        path = metrixTools.downloadFile(screenshotpath_v2 + '&id=' + item_id, path + 'preview.png')
    else:
        path = metrixTools.downloadFile(screenshotpath + '&image_id=' + image_id + '&token=' + image_token, path + 'preview.png')
    return path


def getSkinParts(path, isactive = ''):
    dirs = listdir(path)
    for dir in dirs:
        try:
            file = open(path + '/' + dir + '/meta.xml', 'r')
            data = file.read()
            file.close()
            dom = parseString(data)
            for design in dom.getElementsByTagName('entry'):
                id = str(design.getAttributeNode('id').nodeValue)
                name = str(design.getAttributeNode('name').nodeValue)
                author = str(design.getAttributeNode('author').nodeValue)
                version = str(design.getAttributeNode('version').nodeValue)
                description = str(design.getAttributeNode('description').nodeValue)
                date = str(design.getAttributeNode('date').nodeValue)
                try:
                    date_modified = str(design.getAttributeNode('date_modified').nodeValue)
                except:
                    date_modified = date

                type = str(design.getAttributeNode('type').nodeValue)
                version = str(design.getAttributeNode('version').nodeValue)

        except:
            pass


def updateSkinParts():
    checkSkinPartUpdates(metrixDefaults.pathRoot() + 'skinparts/screens/active/')
    checkSkinPartUpdates(metrixDefaults.pathRoot() + 'skinparts/widgets/active/')
    checkSkinPartUpdates(metrixDefaults.pathRoot() + 'skinparts/screens/inactive/', False)
    checkSkinPartUpdates(metrixDefaults.pathRoot() + 'skinparts/widgets/inactive/', False)


def checkSkinPartUpdates(path, isActive = True):
    dirs = listdir(path)
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
                image_id = str(design.getAttributeNode('image_id').nodeValue)
                image_token = str(design.getAttributeNode('image_token').nodeValue)
                author = str(design.getAttributeNode('author').nodeValue)
                description = str(design.getAttributeNode('description').nodeValue)
                date = str(design.getAttributeNode('date').nodeValue)
                try:
                    date_modified = str(design.getAttributeNode('date_modified').nodeValue)
                except:
                    date_modified = date

                if isUpdateAvailable(id, date_modified):
                    installSkinPart(id, type, author, image_id, image_token, date_modified, isActive)
                    metrixConnector.showInfo(name + _(' successfully updated!'))

        except:
            pass


def isUpdateAvailable(id, local_data_modified):
    try:
        downloadmetaurl = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinpartmeta&id=' + id
        metafile = metrixCore.getWeb(downloadmetaurl, True)
        dom = parseString(metafile)
        store_date_modified = ''
        for design in dom.getElementsByTagName('entry'):
            try:
                store_date_modified = str(design.getAttributeNode('date_modified').nodeValue)
            except:
                store_date_modified = local_data_modified

        if time.strptime(local_data_modified, '%d.%m.%Y') < time.strptime(store_date_modified, '%d.%m.%Y'):
            return True
        return False
    except Exception as e:
        print '[MyMetrix] ' + str(e)
        traceback.print_exc()

    downloadSkinPartRenderer(id)
    downloadSkinPartConverter(id)
    downloadSkinPartImages(id)
