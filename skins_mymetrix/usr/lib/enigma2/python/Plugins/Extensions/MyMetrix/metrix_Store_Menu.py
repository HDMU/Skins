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
import metrix_Store_SkinParts
import metrix_Store_MetrixColors
import metrix_Store_Packages
import threading
import time
import metrixTools
import metrixCore
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


class OpenScreen(ConfigListScreen, Screen):
    skin = '<screen name="MyMetrix-Store" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">\n<eLabel position="0,0" size="1280,720" backgroundColor="#b0ffffff" zPosition="-50" />\n<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />\n<eLabel position="660,70" size="575,580" backgroundColor="#40222222" zPosition="-1" />\n<eLabel position="644,40" size="5,60" backgroundColor="#000000ff" />\n<widget position="500,61" size="136,40" name="sort" foregroundColor="#00bbbbbb" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" />\n  \n <widget name="menu" position="671,137" selectionDisabled="1" scrollbarMode="showNever" size="549,497" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <widget position="55,55" size="438,50" name="title" foregroundColor="#00ffffff" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" />\n  \n  \n<widget name="mainmenu" position="55,125" scrollbarMode="showOnDemand" size="590,506" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <widget position="671,81" size="558,50" foregroundColor="#00ffffff" name="subtitle" font="SetrixHD; 35" valign="center" transparent="1" backgroundColor="#40000000" />\n\n<widget position="1255,121" size="546,50" name="designname" font="SetrixHD; 30" valign="center" transparent="1" backgroundColor="#40000000" />\n <widget position="1255,489" size="491,50" name="votes" foregroundColor="#00ffffff" font="Regular; 22" valign="center" halign="right" transparent="1" backgroundColor="#40000000" />\n\n<widget position="1256,173" size="341,50" name="author" foregroundColor="#00bbbbbb" font="Regular; 22" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n\n<widget name="helperimage" position="1255,230" size="500,250" zPosition="1" alphatest="blend" />\n<eLabel position="1235,110" size="45,500" backgroundColor="#40333333" zPosition="-1" />\n </screen>\n'

    def __init__(self, session, inmymetrix = 0):
        self.inmymetrix = inmymetrix
        self['title'] = Label(_('OpenStore'))
        self['subtitle'] = Label(_('OpenStore // SkinParts'))
        self['sort'] = Label()
        self.sort = 'suite'
        if self.inmymetrix == 1:
            self.url = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinparts&orderby=1%20DESC%20LIMIT%2011'
            self['sort'].setText(_('Suites'))
            self['title'].setText(_('MyMetrix // OpenStore'))
        else:
            self.url = 'http://connect.mymetrix.de/store/api/?q=get.xml.packages&orderby=1%20DESC%20LIMIT%2011'
            self['subtitle'].setText(_('OpenStore // Plugins & More'))
            self['sort'].setText(_(' '))
        self.screenshotpath = 'http://connect.mymetrix.de/designs/showscreenshot.php?name='
        Screen.__init__(self, session)
        self.session = session
        self['designname'] = Label()
        self['author'] = Label()
        self['votes'] = Label()
        self['date'] = Label()
        self.currentid = 0
        self.currentgroup = 'SkinParts'
        self.picPath = None
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['helperimage'] = Pixmap()
        self.getCatalog = True
        self['menu'] = SkinPartsList([])
        self['mainmenu'] = StoreList([])
        self.menulist = []
        self.mainmenu = []
        self.SkinPartsListEntry(0, _('Loading...'))
        self.StoreMenuEntry(_('Loading...'), 0)
        self['menu'].setList(self.menulist)
        self['mainmenu'].setList(self.mainmenu)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'right': self.pageDown,
         'left': self.pageUp,
         'up': self.keyUp,
         'upRepeated': self.keyUp,
         'ok': self.go,
         'blue': self.changeSort,
         'down': self.keyDown,
         'downRepeated': self.keyDown,
         'cancel': self.exit}, -1)
        self.onLayoutFinish.append(self.startThread)

    def startThread(self):
        thread_getDesigns = threading.Thread(target=self.threadworker, args=())
        thread_getDesigns.daemon = True
        thread_getDesigns.start()

    def threadworker(self):
        while 1:
            if self.getCatalog == True:
                self.getCatalog = False
                self.mainmenu = []
                if self.inmymetrix == 1:
                    self.mainmenu.append(self.StoreMenuEntry('MetrixColors', 'MetrixColors'))
                    self.mainmenu.append(self.StoreMenuEntry(_('Skin Extensions'), 'Extensions'))
                    self.mainmenu.append(self.StoreMenuEntry(_('All SkinParts'), 'SkinParts'))
                    if self.sort == 'suite':
                        self.getCategories('http://connect.mymetrix.de/store/api/?q=get.xml.suites')
                        self['sort'].setText(_('Suites'))
                    else:
                        self.getCategories('http://connect.mymetrix.de/store/api/?q=get.xml.screennames')
                        self['sort'].setText(_('Screens'))
                else:
                    self.mainmenu.append(self.StoreMenuEntry(_('Package Updates'), 'Updates'))
                    self.mainmenu.append(self.StoreMenuEntry(_('New '), 'New'))
                    self.getCategories('http://connect.mymetrix.de/store/api/?q=get.xml.categories')
                self.getSkinParts()
                self.UpdateComponents()
            time.sleep(1)

    def changeSort(self):
        if self.sort == 'suite':
            self.sort = 'screens'
        else:
            self.sort = 'suite'
        self.getCatalog = True

    def go(self):
        returnValue = str(self['mainmenu'].l.getCurrentSelection()[0][0])
        if returnValue is not None:
            if returnValue is 'SkinParts':
                self.session.open(metrix_Store_SkinParts.OpenScreen)
            elif returnValue is 'MetrixColors':
                self.session.open(metrix_Store_MetrixColors.OpenScreen)
            elif returnValue is 'Updates':
                self.session.open(metrix_Store_Packages.OpenScreen, '%', 'Updates', '1')
            elif returnValue is 'New':
                self.session.open(metrix_Store_Packages.OpenScreen, '%', 'New ', 'LIMIT%2011')
            elif returnValue is 'Extensions':
                self.session.open(metrix_Store_Packages.OpenScreen, '2017', 'Skin Extensions')
            elif self.inmymetrix == 1:
                if self.sort == 'suite':
                    self.session.open(metrix_Store_SkinParts.OpenScreen, '%', self['mainmenu'].l.getCurrentSelection()[0][0], self['mainmenu'].l.getCurrentSelection()[0][1])
                else:
                    self.session.open(metrix_Store_SkinParts.OpenScreen, self['mainmenu'].l.getCurrentSelection()[0][0], '%', self['mainmenu'].l.getCurrentSelection()[0][1])
            else:
                self.session.open(metrix_Store_Packages.OpenScreen, self['mainmenu'].l.getCurrentSelection()[0][0], self['mainmenu'].l.getCurrentSelection()[0][1])
        else:
            print ''

    def getSkinParts(self):
        self.menulist = []
        data = metrixCore.getWeb(self.url, True)
        dom = parseString(data)
        for design in dom.getElementsByTagName('entry'):
            id = str(design.getAttributeNode('id').nodeValue)
            name = str(design.getAttributeNode('name').nodeValue)
            rating = str(design.getAttributeNode('rating').nodeValue)
            self.menulist.append(self.SkinPartsListEntry(id, name, rating))
            self['menu'].setList(self.menulist)

    def SkinPartsListEntry(self, id, name, rating = ''):
        res = [[id, name, rating]]
        png = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/vote' + rating + '.png'
        res.append(MultiContentEntryPixmapAlphaTest(pos=(372, 6), size=(170, 32), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(3, 4), size=(380, 45), font=0, text=name))
        return res

    def StoreMenuEntry(self, name, value):
        res = [[value, name]]
        res.append(MultiContentEntryText(pos=(3, 4), size=(405, 45), font=0, text=_(name)))
        return res

    def getCategories(self, url):
        try:
            data = metrixCore.getWeb(url, True)
            dom = parseString(data)
            for entry in dom.getElementsByTagName('entry'):
                item_id = str(entry.getAttributeNode('id').nodeValue)
                name = str(entry.getAttributeNode('name').nodeValue)
                description = str(entry.getAttributeNode('description').nodeValue)
                self.mainmenu.append(self.StoreMenuEntry(name, item_id))
                self['mainmenu'].setList(self.mainmenu)

        except:
            pass

    def GetPicturePath(self):
        try:
            returnValue = str(self['menu'].l.getCurrentSelection()[0][0])
            path = metrixTools.downloadFile(self.screenshotpath + returnValue)
            return path
        except:
            pass

    def updateMeta(self):
        try:
            self['designname'].setText(_(str(self['menu'].l.getCurrentSelection()[0][1])))
            self['author'].setText(_('by ' + str(self['menu'].l.getCurrentSelection()[0][2])))
            self['votes'].setText(_(str(self['menu'].l.getCurrentSelection()[0][6])))
            self['date'].setText(_(str(self['menu'].l.getCurrentSelection()[0][4])))
            self.currentid = str(self['menu'].l.getCurrentSelection()[0][0])
        except:
            pass

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
        self.updateMeta()

    def keyDown(self):
        self['mainmenu'].instance.moveSelection(self['mainmenu'].instance.moveDown)

    def keyUp(self):
        self['mainmenu'].instance.moveSelection(self['mainmenu'].instance.moveUp)

    def pageUp(self):
        self['mainmenu'].instance.moveSelection(self['mainmenu'].instance.pageUp)

    def pageDown(self):
        self['mainmenu'].instance.moveSelection(self['mainmenu'].instance.pageDown)

    def exit(self):
        if self.inmymetrix == 0:
            if config.plugins.MetrixUpdater.Reboot.value == 1:
                restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?'), MessageBox.TYPE_YESNO)
                restartbox.setTitle(_('Restart GUI'))
            else:
                self.close()
        else:
            self.close()

    def openRating(self):
        self.session.open(metrix_Store_SubmitRating.OpenScreen, self.currentid, self.currentgroup)

    def showInfo(self, text = 'Information'):
        self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)

    def restartGUI(self, answer):
        if answer is True:
            config.plugins.MetrixUpdater.Reboot.value = 0
            config.plugins.MetrixUpdater.save()
            configfile.save()
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()


class StoreList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        self.l.setFont(0, gFont('SetrixHD', 26))
        self.l.setFont(1, gFont('Regular', 22))


class SkinPartsList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(45)
        self.l.setFont(0, gFont('SetrixHD', 24))
        self.l.setFont(1, gFont('Regular', 22))
        if 1 == 2:
            cat = _('Education')
            cat = _('Movie & Media')
            cat = _('Network & Streaming')
            cat = _('News')
            cat = _('Program Guide')
            cat = _('Social')
            cat = _('Spinners')
            cat = _('Sports')
            cat = _('Radio')
            cat = _('Tweaks')
            cat = _('Recordings')
            cat = _('Communication')
            cat = _('System Extensions')
            cat = _('Utilities')
            cat = _('Development')
            cat = _('Picons')
            cat = _('Skin Extensions')
            cat = _('SkinParts Collections')
            cat = _('Drivers')
            cat = _('Channellists')
            cat = _('Kernel Modules')
            cat = _('Language Packs')
            cat = _('Weather')
            cat = _('Various')
            cat = _('My SkinParts')
            cat = _('Default Bugfixes')
            cat = _('VTI Specific')
            cat = _('OpenPLi Specific')
            cat = _('MetrixHD Default')
