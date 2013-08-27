import threading
from encode import multipart_encode
from streaminghttp import register_openers
import cookielib
from xml.dom.minidom import parseString
import gettext
import MultipartPostHandler
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from twisted.web.client import downloadPage
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSequence, ConfigSubsection, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from uuid import getnode as get_mac
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import os
from enigma import loadPNG
import urllib
from xml.dom.minidom import parseString
import gettext
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad, eListboxPythonMultiContent, gFont, addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixDefaults
import metrix_Store_SubmitRating
import time
import shutil
import metrixTools
import metrix_SkinPartTools
import traceback
import metrixCore
import metrix_GenerateSkin
import metrix_MainMenu
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


class OpenScreen(Screen):
    skin = '\n<screen name="MyMetrix-Intro" position="0,0" size="1278,720" flags="wfNoBorder" backgroundColor="#99ffffff">\n  <eLabel position="40,40" size="1195,113" backgroundColor="#40000000" zPosition="-1" />\n  <eLabel position="62,153" size="1151,521" backgroundColor="#40149baf" zPosition="-1" />\n<widget name="left" position="84,317" size="262,59" foregroundColor="foreground" font="Regular; 23" valign="center" transparent="1" backgroundColor="#40149baf" halign="center" />\n<ePixmap position="194,281" size="36,36" zPosition="10" pixmap="MetrixHD/left.png" transparent="1" alphatest="blend" />\n<widget name="helperimage" position="361,161" size="550,310" zPosition="1" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/metrixhddefault.png" />\n<ePixmap position="1039,281" size="36,36" zPosition="10" pixmap="MetrixHD/right.png" transparent="1" alphatest="blend" />\n<widget name="right" position="929,318" size="262,59" foregroundColor="foreground" font="Regular; 23" valign="center" transparent="1" backgroundColor="#40149baf" halign="center" />\n  <widget name="description" position="75,479" size="1127,189" transparent="1" halign="left" foregroundColor="foreground" backgroundColor="#40149baf" font="Regular; 30" valign="center" />\n  <widget position="57,58" size="1162,85" foregroundColor="foreground" name="title" font="SetrixHD; 60" valign="center" transparent="1" backgroundColor="background" />\n</screen>\n'

    def __init__(self, session):
        self['title'] = Label(_('Welcome to MyMetrix and OpenStore!'))
        self['description'] = Label(_('MyMetrix brings your set-top box experience onto a whole new level!\nPress left button to start the easy setup which generates the default MetrixHD feeling. Alternatively press right button to explore great SkinParts in OpenStore and customize your user interface how ever you want!'))
        Screen.__init__(self, session)
        self.session = session
        self['right'] = Label(_('Customize'))
        self['left'] = Label(_('Easy setup'))
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['helperimage'] = Pixmap()
        config.plugins.MyMetrix.showFirstRun.value = '0'
        config.plugins.MyMetrix.showFirstRun.save()
        configfile.save()
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'right': self.keyRight,
         'left': self.keyLeft,
         'cancel': self.exit}, -1)

    def keyLeft(self):
        self.session.open(metrix_GenerateSkin.OpenScreen)
        self.exit()

    def keyRight(self):
        self.session.open(metrix_MainMenu.OpenScreen)
        self.exit()

    def exit(self):
        self.close()

    def showInfo(self, text = 'Information'):
        self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)
