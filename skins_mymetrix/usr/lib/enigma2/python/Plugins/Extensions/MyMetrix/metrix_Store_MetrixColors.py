import thread
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
import urllib2
import urllib
from xml.dom.minidom import parseString
import gettext
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad, eListboxPythonMultiContent, gFont, addFont, loadPic, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixColors
import metrixDefaults
import metrix_Store_SubmitRating
import threading
import time
import metrixTools
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
    skin = '\n<screen name="MyMetrix-Store-Browse" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">\n<eLabel position="0,0" size="1280,720" backgroundColor="#b0ffffff" zPosition="-50" />\n<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />\n<eLabel position="660,70" size="575,580" backgroundColor="#40222222" zPosition="-1" />\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="695,608" size="250,33" text="%s" transparent="1" />\n <widget name="menu" position="55,122" scrollbarMode="showNever" size="605,555" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <widget position="55,55" size="558,50" name="title" foregroundColor="#00ffffff" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" />\n  \n  <eLabel position="681,610" size="5,40" backgroundColor="#0000ff00" />\n<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/star.png" position="1177,549" size="32,34" zPosition="1" alphatest="blend" />\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="1009,608" size="200,33" text="%s" transparent="1" />\n<widget name="helperimage" position="671,206" size="550,310" zPosition="1" alphatest="blend" />\n<widget position="674,82" size="546,50" name="designname" foregroundColor="#00ffffff" font="SetrixHD; 35" valign="center" transparent="1" backgroundColor="#40000000" />\n <widget position="679,542" size="491,50" name="votes" foregroundColor="#00ffffff" font="Regular; 30" valign="center" halign="right" transparent="1" backgroundColor="#40000000" />\n<eLabel position="995,610" zPosition="1" size="5,40" backgroundColor="#00ffff00" />\n<widget position="675,142" size="341,50" name="author" foregroundColor="#00bbbbbb" font="Regular; 28" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n<widget position="1019,145" size="200,40" name="date" foregroundColor="#00999999" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" zPosition="1" />\n<eLabel position="0,10" size="40,700" backgroundColor="#30000000" zPosition="-1" />\n\n </screen>\n' % (_('Install '), _('Vote'))

    def __init__(self, session, args = None):
        self['title'] = Label(_('OpenStore // MetrixColors'))
        self.url = 'http://connect.mymetrix.de/store/api/?q=get.xml.designs'
        self.screenshotpath = 'http://connect.mymetrix.de/store/api/?q=get.pngresizedColors&width=550&name='
        Screen.__init__(self, session)
        self.session = session
        self['designname'] = Label()
        self['author'] = Label()
        self['votes'] = Label()
        self['date'] = Label()
        self.currentid = 1
        self.currentgroup = 'DesignStore_'
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['helperimage'] = Pixmap()
        self.getCatalog = True
        self.getEntry = True
        self.initPicture = True
        self['menu'] = SkinPartsList([])
        self.menulist = []
        self.menulist.append(self.DesignsListEntry('-', _('loading, please wait...'), '', '0', '0', '0'))
        self['menu'].setList(self.menulist)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'up': self.keyUp,
         'ok': self.selectItem,
         'down': self.keyDown,
         'green': self.applyDesign,
         'yellow': self.openRating,
         'right': self.pageDown,
         'left': self.pageUp,
         'cancel': self.save}, -1)
        self.onLayoutFinish.append(self.startThread)

    def startThread(self):
        thread_getDesigns = threading.Thread(target=self.threadworker, args=())
        thread_getDesigns.daemon = True
        thread_getDesigns.start()

    def threadworker(self):
        while 1:
            if self.getCatalog == True:
                self.getCatalog = False
                self.getDesigns()
            if self.initPicture == True:
                self.initPicture = False
                self.UpdatePicture()
                self.updateMeta()
            if self.getEntry == True:
                self.getEntry = False
                self.updateMeta()
                self.ShowPicture()
            time.sleep(1)

    def getDesigns(self):
        try:
            self.menulist = []
            file = urllib2.urlopen(self.url)
            data = file.read()
            file.close()
            dom = parseString(data)
            for design in dom.getElementsByTagName('design'):
                name = str(design.getAttributeNode('name').nodeValue)
                title = str(design.getAttributeNode('title').nodeValue)
                author = str(design.getAttributeNode('author').nodeValue)
                rating = str(design.getAttributeNode('rating').nodeValue)
                date = str(design.getAttributeNode('date').nodeValue)
                total_votes = str(design.getAttributeNode('total_votes').nodeValue)
                self.menulist.append(self.DesignsListEntry(name, title, author, rating, date, total_votes))

            self['menu'].setList(self.menulist)
            self.updateMeta()
            self.ShowPicture()
        except:
            pass

    def DesignsListEntry(self, name, title, author, rating, date, total_votes):
        res = [[name,
          title,
          author,
          rating,
          date,
          total_votes]]
        png = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/vote' + rating + '.png'
        pngtype = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/brush.png'
        res.append(MultiContentEntryPixmapAlphaTest(pos=(412, 9), size=(170, 32), png=loadPNG(png)))
        res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 7), size=(32, 32), png=loadPNG(pngtype)))
        res.append(MultiContentEntryText(pos=(40, 4), size=(367, 45), font=0, text=title))
        return res

    def GetPicturePath(self):
        try:
            returnValue = str(self['menu'].l.getCurrentSelection()[0][0])
            path = metrixTools.downloadFile(self.screenshotpath + returnValue)
            return path
        except:
            pass

    def updateMeta(self):
        try:
            self['designname'].setText(str(self['menu'].l.getCurrentSelection()[0][1]))
            self['author'].setText(_('by ' + str(self['menu'].l.getCurrentSelection()[0][2])))
            self['votes'].setText(str(self['menu'].l.getCurrentSelection()[0][5]))
            self['date'].setText(str(self['menu'].l.getCurrentSelection()[0][4]))
            self.currentid = 1
            self.currentgroup = 'DesignStore_' + str(self['menu'].l.getCurrentSelection()[0][0])
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
         '#30000000'])
        self.PicLoad.startDecode(self.GetPicturePath())

    def DecodePicture(self, PicInfo = ''):
        ptr = self.PicLoad.getData()
        self['helperimage'].instance.setPixmap(ptr)

    def UpdateComponents(self):
        self.UpdatePicture()

    def selectItem(self):
        self.getEntry = True

    def keyDown(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveDown)
        self.getEntry = True

    def keyUp(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveUp)
        self.getEntry = True

    def save(self):
        config.plugins.MyMetrix.Color.save()
        configfile.save()
        self.close()

    def exit(self):
        self.close()

    def applyDesign(self):
        try:
            designname = self['menu'].l.getCurrentSelection()[0][0]
            file = urllib2.urlopen(self.url)
            data = file.read()
            file.close()
            dom = parseString(data)
            for design in dom.getElementsByTagName('design'):
                name = str(design.getAttributeNode('name').nodeValue)
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
                        config.plugins.MyMetrix.Color.Selection_Custom.value = self.toRGB(str(design.getAttributeNode('selection_custom').nodeValue))
                        config.plugins.MyMetrix.Color.Background_Custom.value = self.toRGB(str(design.getAttributeNode('background_custom').nodeValue))
                        config.plugins.MyMetrix.Color.Background2_Custom.value = self.toRGB(str(design.getAttributeNode('background2_custom').nodeValue))
                        config.plugins.MyMetrix.Color.Foreground_Custom.value = self.toRGB(str(design.getAttributeNode('foreground_custom').nodeValue))
                        config.plugins.MyMetrix.Color.BackgroundText_Custom.value = self.toRGB(str(design.getAttributeNode('backgroundtext_custom').nodeValue))
                        config.plugins.MyMetrix.Color.Accent1_Custom.value = self.toRGB(str(design.getAttributeNode('accent1_custom').nodeValue))
                        config.plugins.MyMetrix.Color.Accent2_Custom.value = self.toRGB(str(design.getAttributeNode('accent2_custom').nodeValue))
                        screenshot = str(design.getAttributeNode('screenshot').nodeValue)
                        self.showInfo('Design successfully downloaded!\nSave MetrixHD to apply!')
                    except:
                        self.showInfo('Design corrupt!')

        except:
            self.showInfo('Design corrupt!')

    def openRating(self):
        self.session.open(metrix_Store_SubmitRating.OpenScreen, self.currentid, self.currentgroup)

    def toRGB(self, text):
        rgb = []
        textar = str(text.replace('[', '').replace(']', '')).split(',')
        rgb.append(int(textar[0]))
        rgb.append(int(textar[1]))
        rgb.append(int(textar[2]))
        return rgb

    def showInfo(self, text = 'Information'):
        self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)

    def pageUp(self):
        self['menu'].instance.moveSelection(self['menu'].instance.pageUp)

    def pageDown(self):
        self['menu'].instance.moveSelection(self['menu'].instance.pageDown)


class SkinPartsList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        self.l.setFont(0, gFont('SetrixHD', 26))
        self.l.setFont(1, gFont('Regular', 22))
