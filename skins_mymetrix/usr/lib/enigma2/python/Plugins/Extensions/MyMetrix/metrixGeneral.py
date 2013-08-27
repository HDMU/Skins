from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
import socket
import base64
from encode import multipart_encode
from streaminghttp import register_openers
import cookielib
from xml.dom.minidom import parseString
import gettext
import MultipartPostHandler
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
import urllib
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixColors
import metrix_Store_ConnectDevice
import metrix_Store_DisconnectDevice
import metrixDefaults
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


def getVersion():
    return '2.0.14'


class OpenScreen(ConfigListScreen, Screen):
    skin = '\n<screen name="MyMetrix-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#b0ffffff">\n    <eLabel position="40,40" size="620,640" backgroundColor="#40000000" zPosition="-1" />\n  <eLabel position="660,71" size="575,575" backgroundColor="#40111111" zPosition="-1" />\n<widget name="metrixVersion" position="52,521" size="590,46" font="Regular; 20" backgroundColor="#40000000" transparent="1" />\n<eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="75,641" size="250,33" text="%s" transparent="1" />\n <widget name="config" position="54,110" itemHeight="30" scrollbarMode="showOnDemand" size="590,340" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <eLabel position="54,51" size="348,50" text="MyMetrix" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />\n  <eLabel position="273,48" size="349,50" text="General" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n  <eLabel position="62,639" size="5,40" backgroundColor="#00ff0000" />\n  <ePixmap position="671,152" size="550,310" zPosition="3" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/mymetrix-de.png" />\n<eLabel position="671,86" size="541,50" text="OpenStore Account" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n<widget name="avatar" position="1109,496" size="96,96" />\n<widget name="metrixUpdate" position="52,575" size="590,52" backgroundColor="#40000000" foregroundColor="#00ffffff" transparent="1" font="Regular; 20" />\n<eLabel position="53,459" size="349,50" text="Information" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n<widget name="username" position="692,518" size="400,50" font="Regular; 30" transparent="1" halign="right" backgroundColor="#40000000" foregroundColor="#00ffffff"  />\n<eLabel position="711,606" size="5,40" backgroundColor="#000000ff" />\n<widget name="connectbutton" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="721,605" size="250,33" transparent="1" /></screen>\n' % _('Discard')

    def __init__(self, session, args = None, picPath = None):
        self.skin_lines = []
        Screen.__init__(self, session)
        self.session = session
        self.version = 'v' + getVersion()
        self.picPath = picPath
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['avatar'] = Pixmap()
        self['connectbutton'] = Label()
        self['username'] = Label()
        self['metrixVersion'] = Label(_(self.version + ' - open-store.net'))
        self['metrixUpdate'] = Label(_(' '))
        if config.plugins.MetrixUpdater.Reboot.value == 1:
            self['metrixVersion'] = Label(_(self.version + ' - live.mymetrix.de (Reboot required)'))
        self['metrixUpdate'] = Label(_(' '))
        list = []
        list.append(getConfigListEntry(_('Automatic Updates ----------------------------------------------------------------------')))
        list.append(getConfigListEntry(_('MyMetrix, OpenStore and plugins'), config.plugins.MyMetrix.AutoUpdate))
        list.append(getConfigListEntry(_('SkinParts'), config.plugins.MyMetrix.AutoUpdateSkinParts))
        list.append(getConfigListEntry(_(' ')))
        list.append(getConfigListEntry(_('Skin -----------------------------------------------------------------------------------')))
        list.append(getConfigListEntry(_('Show intro page'), config.plugins.MyMetrix.showFirstRun))
        list.append(getConfigListEntry(_('Skin template'), config.plugins.MyMetrix.templateFile))
        list.append(getConfigListEntry(_(' ')))
        list.append(getConfigListEntry(_('Weather --------------------------------------------------------------------------------')))
        list.append(getConfigListEntry(_('MetrixWeather ID'), config.plugins.MetrixWeather.woeid))
        list.append(getConfigListEntry(_('Unit'), config.plugins.MetrixWeather.tempUnit))
        ConfigListScreen.__init__(self, list)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'down': self.keyDown,
         'up': self.keyUp,
         'blue': self.connect,
         'red': self.exit,
         'cancel': self.save}, -1)
        self.onLayoutFinish.append(self.UpdateComponents)

    def connect(self):
        if config.plugins.MetrixConnect.auth_token.value == 'None':
            self.session.open(metrix_Store_ConnectDevice.OpenScreen)
        else:
            self.session.open(metrix_Store_DisconnectDevice.OpenScreen)
        self.updateAccountData()

    def updateAccountData(self):
        self['connectbutton'].setText(_('Connect to OpenStore'))
        if config.plugins.MetrixConnect.auth_token.value == 'None':
            self['connectbutton'].setText(_('Connect to OpenStore'))
        else:
            self['connectbutton'].setText(_('Disconnect'))
        self['username'].setText(_(config.plugins.MetrixConnect.username.value))

    def GetPicturePath(self):
        path = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/user.png'
        return path

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        self.PicLoad.setPara([self['avatar'].instance.size().width(),
         self['avatar'].instance.size().height(),
         self.Scale[0],
         self.Scale[1],
         0,
         1,
         '#30000000'])
        self.PicLoad.startDecode(self.GetPicturePath())

    def DecodePicture(self, PicInfo = ''):
        ptr = self.PicLoad.getData()
        self['avatar'].instance.setPixmap(ptr)

    def UpdateComponents(self):
        self.UpdatePicture()
        self.updateAccountData()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.ShowPicture()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.ShowPicture()

    def showInfo(self):
        self.session.open(MessageBox, _('Information'), MessageBox.TYPE_INFO)

    def save(self):
        for x in self['config'].list:
            if len(x) > 1:
                x[1].save()

        configfile.save()
        self.close()

    def exit(self):
        for x in self['config'].list:
            if len(x) > 1:
                x[1].cancel()

        self.close()
