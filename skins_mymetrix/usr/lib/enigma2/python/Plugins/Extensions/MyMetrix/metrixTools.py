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
import metrixCore

def getHexColor(rgbColor, alpha = 0):
    return '#' + getHex(alpha) + getHex(rgbColor[0]) + getHex(rgbColor[1]) + getHex(rgbColor[2])


def getHex(number):
    return str(hex(int(number))).replace('0x', '').zfill(2)


def skinPartIsCompatible(dom):
    isvalid = True
    try:
        for widget in dom.getElementsByTagName('widget'):
            isvalid = True
            renderer = None
            try:
                renderer = str(widget.getAttributeNode('render').nodeValue)
            except:
                pass

            if renderer is not None:
                try:
                    renderer_class = my_import('.'.join(('Components', 'Renderer', renderer))).__dict__.get(renderer)
                    for convert in dom.getElementsByTagName('convert'):
                        ctype = None
                        try:
                            ctype = str(convert.getAttributeNode('type').nodeValue)
                        except:
                            pass

                        if ctype is not None:
                            try:
                                converter_class = my_import('.'.join(('Components', 'Converter', ctype))).__dict__.get(ctype)
                            except:
                                isvalid = False
                                print "[MetrixGSP] Missing converter '" + ctype + "'"
                                break

                except:
                    print "[MetrixGSP] Missing renderer '" + renderer + "'"
                    isvalid = False

            if isvalid == False:
                dom.removeChild(widget)
                print '[MetrixGSP] Widget removed!'

    except:
        pass

    return dom


def downloadFile(storePath, localPath = '/tmp/metrixPreview.tmp', searchpattern = '', replacepattern = ''):
    try:
        webFile = urllib2.urlopen(storePath)
        localFile = open(localPath, 'w')
        if searchpattern == '':
            localFile.write(webFile.read())
        else:
            for line in webFile:
                localFile.write(line.replace(searchpattern, replacepattern))

        webFile.close()
        localFile.close()
        return localPath
    except Exception as e:
        print '[MyMetrix] ' + str(e)
        traceback.print_exc()


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
        data = metrixCore.getWeb(url, True)
        dom = parseString(data)
        for design in dom.getElementsByTagName('entry'):
            url = str(design.getAttributeNode('url').nodeValue)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            downloadFile(url, target_path + url.split('file=')[-1])

    except:
        pass
