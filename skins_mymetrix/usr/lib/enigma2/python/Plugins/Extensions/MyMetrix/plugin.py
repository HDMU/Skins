from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from uuid import getnode as get_id
from Screens.Console import Console
import cookielib
from xml.dom.minidom import parseString
import gettext
import MultipartPostHandler
from enigma import eListboxPythonMultiContent, gFont, eTimer, eDVBDB, getDesktop
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.MenuList import MenuList
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad, eListboxPythonMultiContent, gFont, addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixConnector
import metrixColors
import metrixDefaults
import metrixInfobar
import metrix_Store_MetrixColors
import metrix_Store_SkinParts
import metrix_Settings_SkinParts
import metrix_GenerateSkin
import metrix_Store_Menu
import metrixSecondInfobar
import metrix_Store_ConnectDevice
import metrixGeneral
import metrixStore
from enigma import addFont
from metrixTools import getHex, getHexColor
from xml.dom.minidom import parseString, parse
import os
import urllib2
import socket
import e2info
import threading
import time
import metrix_MainMenu
addFont('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/setrixHD.ttf', 'SetrixHD', 100, False)
addFont('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/meteocons.ttf', 'Meteo', 100, False)

def startMetrixDeamon(reason, **kwargs):
    metrixConnector.syncStart(global_session)


def startSession(reason, session):
    global global_session
    global_session = session


config = metrixDefaults.loadDefaults()
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('MyMetrix', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MyMetrix/locale/'))

def _(txt):
    t = gettext.dgettext('MyMetrix', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def translateBlock(block):
    for x in TranslationHelper:
        if block.__contains__(x[0]):
            block = block.replace(x[0], x[1])

    return block


def main(session, **kwargs):
    session.open(metrix_MainMenu.OpenScreen)


def openStore(session, **kwargs):
    session.open(metrix_Store_Menu.OpenScreen)


def Plugins(**kwargs):
    return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=startSession),
     PluginDescriptor(where=[PluginDescriptor.WHERE_NETWORKCONFIG_READ], fnc=startMetrixDeamon),
     PluginDescriptor(name='MyMetrix', description=_('Metrify Your Vu+'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main),
     PluginDescriptor(name='OpenStore', description=_('Explore The Variety Of Your Vu+'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='plugin-store.png', fnc=openStore)]
