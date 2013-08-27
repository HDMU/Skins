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
from metrixTools import getHex, getHexColor
from xml.dom.minidom import parseString, parse
import os
import urllib2
import socket
import e2info
import threading
import time
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
    skin = '\n<screen name="MyMetrix-Menu" position="0,0" size="1200,640" flags="wfNoBorder" backgroundColor="transparent">\n    <eLabel position="264,51" zPosition="-1" size="340,320" backgroundColor="#40000000" transparent="0" />\n    <!-- /*ClockWidget-->\n    <widget source="global.CurrentTime" foregroundColor="#00ffffff" render="Label" position="450,401" size="169,80" font="SetrixHD; 60" halign="left" backgroundColor="#40000000" transparent="1" valign="top">\n      <convert type="ClockToText">Default</convert>\n    </widget>\n    <widget source="global.CurrentTime" render="Label" position="290,444" size="148,29" font="SetrixHD; 20" halign="right" backgroundColor="#40000000" foregroundColor="#00bbbbbb" transparent="1">\n      <convert type="ClockToText">Format:%e. %B</convert>\n    </widget>\n    <widget source="global.CurrentTime" render="Label" position="313,415" size="125,30" font="SetrixHD; 20" halign="right" backgroundColor="#40000000" foregroundColor="#00bbbbbb" transparent="1">\n      <convert type="ClockToText">Format:%A</convert>\n    </widget>\n    <eLabel position="265,410" zPosition="-1" size="340,70" backgroundColor="#40000000" transparent="0" />\n    <!--ClockWidget */-->\n    \n<widget name="menu" position="636,60" size="430,555" scrollbarMode="showNever" itemHeight="60" enableWrapAround="1" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000">\n    </widget>\n    <eLabel name="" position="645,51" zPosition="-19" size="412,565" backgroundColor="#40000000" foregroundColor="#40000000" />\n    <ePixmap position="310,85" size="256,256" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/mymetrix.png" alphatest="blend" />\n</screen>\n'

    def __init__(self, session, args = None):
        self.version = 'v2.0a'
        Screen.__init__(self, session)
        self.session = session
        self.list = []
        self.list.append(self.MetrixListEntry(_('OpenStore'), 'OpenStore'))
        self.list.append(self.MetrixListEntry(_('SkinPart Settings'), 'SkinParts'))
        self.list.append(self.MetrixListEntry(_('MetrixColors Settings'), 'metrixColors'))
        self.list.append(self.MetrixListEntry(_('General Settings'), 'general'))
        self.list.append(self.MetrixListEntry(_('Save My Skin'), 'generate'))
        self['menu'] = MetrixList([])
        self['menu'].setList(self.list)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'ok': self.go,
         'red': self.exit,
         'yellow': self.reboot,
         'green': self.save,
         'cancel': self.exit}, -1)

    def MetrixListEntry(self, _name, _value):
        entry = [[_value, _name]]
        entry.append(MultiContentEntryText(pos=(30, 5), size=(405, 50), font=0, text=_name))
        return entry

    def go(self):
        returnValue = str(self['menu'].l.getCurrentSelection()[0][0])
        if returnValue is not None:
            if returnValue is 'metrixColors':
                self.session.open(metrixColors.OpenScreen)
            elif returnValue is 'OpenStore':
                self.session.open(metrix_Store_Menu.OpenScreen, 1)
            elif returnValue is 'SkinParts':
                self.session.open(metrix_Settings_SkinParts.OpenScreen)
            elif returnValue is 'general':
                self.session.open(metrixGeneral.OpenScreen)
            elif returnValue is 'generate':
                self.session.open(metrix_GenerateSkin.OpenScreen)
        else:
            print ''

    def reboot(self):
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('Do you really want to reboot now?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI'))

    def showInfo(self):
        self.session.open(MessageBox, _('Information'), MessageBox.TYPE_INFO, 3)

    def exit(self):
        self.close()

    def save(self):
        self.close()


class MetrixList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(60)
        self.l.setFont(0, gFont('SetrixHD', 30))
        self.l.setFont(1, gFont('Regular', 22))
