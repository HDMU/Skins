from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
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
import urllib
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixColors
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


def main(session, **kwargs):
    session.open(MyMetrixSecondInfobarWindow)


class MyMetrixSecondInfobarWindow(ConfigListScreen, Screen):
    skin = '\n<screen name="MyMetrix-Setup" position="40,40" size="1200,640" flags="wfNoBorder" backgroundColor="#40000000">\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="37,605" size="250,33" text="Discard" transparent="1" />\n <widget name="config" itemHeight="30"  position="21,77" scrollbarMode="showOnDemand" size="590,506" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <eLabel position="20,15" size="348,50" text="MyMetrix" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />\n  <eLabel position="223,15" size="349,50" text="SecondInfobar" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n  <eLabel position="20,600" size="5,40" backgroundColor="#00ff0000" />\n  <widget name="helperimage" position="629,81" size="550,500" zPosition="1" />\n</screen>\n'

    def __init__(self, session, args = None, picPath = None):
        self.skin_lines = []
        Screen.__init__(self, session)
        self.session = session
        self.picPath = picPath
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['helperimage'] = Pixmap()
        self['rect'] = Label()
        list = []
        list.append(getConfigListEntry(_('Clock Widget'), config.plugins.MyMetrix.SecondInfobarClockWidget))
        list.append(getConfigListEntry(_('Info Widget'), config.plugins.MyMetrix.SecondInfobarInfoWidget))
        list.append(getConfigListEntry(_('Health Widget'), config.plugins.MyMetrix.SecondInfobarHealthWidget))
        list.append(getConfigListEntry(_('Weather Widget'), config.plugins.MyMetrix.SecondInfobarWeatherWidget))
        list.append(getConfigListEntry(_('EPG Widget'), config.plugins.MyMetrix.SecondInfobarEPGWidget))
        list.append(getConfigListEntry(_('Style'), config.plugins.MyMetrix.SecondInfobarStyle))
        list.append(getConfigListEntry(_('Channel name'), config.plugins.MyMetrix.SecondInfobarShowChannelname))
        list.append(getConfigListEntry(_('Show tuner info'), config.plugins.MyMetrix.SecondInfobarTunerInfo))
        list.append(getConfigListEntry(_('Show resolution info'), config.plugins.MyMetrix.SecondInfobarResolutionInfo))
        list.append(getConfigListEntry(_('Show crypt info'), config.plugins.MyMetrix.SecondInfobarCryptInfo))
        ConfigListScreen.__init__(self, list)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'left': self.keyLeft,
         'down': self.keyDown,
         'up': self.keyUp,
         'right': self.keyRight,
         'red': self.exit,
         'cancel': self.save}, -1)
        self.onLayoutFinish.append(self.UpdateComponents)

    def GetPicturePath(self):
        config.plugins.MyMetrix.Color.save()
        try:
            print str(self['config'].getCurrent())
            returnValue = self['config'].getCurrent()[1].value
            path = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/' + returnValue + '.png'
            return path
        except:
            return '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/metrixweather.png'

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        self.PicLoad.setPara([self['helperimage'].instance.size().width(),
         self['helperimage'].instance.size().height(),
         self.Scale[0],
         self.Scale[1],
         0,
         1,
         '#002C2C39'])
        self.PicLoad.startDecode(self.GetPicturePath())

    def DecodePicture(self, PicInfo = ''):
        ptr = self.PicLoad.getData()
        self['helperimage'].instance.setPixmap(ptr)

    def UpdateComponents(self):
        self.UpdatePicture()

    def keyLeft(self):
        self['rect'].instance.setBackgroundColor(parseColor(config.plugins.MyMetrix.Color.Selection.value))
        ConfigListScreen.keyLeft(self)
        self.ShowPicture()

    def keyRight(self):
        self['rect'].instance.setBackgroundColor(parseColor(config.plugins.MyMetrix.Color.Foreground.value))
        ConfigListScreen.keyRight(self)
        self.ShowPicture()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.ShowPicture()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.ShowPicture()

    def reboot(self):
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('Do you really want to reboot now?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI'))

    def showInfo(self):
        self.session.open(MessageBox, _('Information'), MessageBox.TYPE_INFO)

    def save(self):
        for x in self['config'].list:
            if len(x) > 1:
                x[1].save()

        configfile.save()
        self.close()

    def restartGUI(self, answer):
        if answer is True:
            config.plugins.MetrixUpdater.Reboot.value = 0
            config.plugins.MetrixUpdater.save()
            configfile.save()
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def getHexColor(self, rgbColor, alpha = 0):
        return ('#' + str(hex(alpha).zfill(2)) + str(hex(rgbColor[0]).zfill(2)) + str(hex(rgbColor[1]).zfill(2)) + str(hex(rgbColor[2]).zfill(2))).replace('0x', '')

    def getHex(self, number):
        return str(hex(int(number)).zfill(2)).replace('0x', '')

    def appendSkinFile(self, appendFileName):
        skFile = open(appendFileName, 'r')
        file_lines = skFile.readlines()
        skFile.close()
        for x in file_lines:
            self.skin_lines.append(x)

    def exit(self):
        for x in self['config'].list:
            if len(x) > 1:
                x[1].cancel()

        self.close()
