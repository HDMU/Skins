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
import metrixDefaults
import metrixTools
addFont('/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/setrixHD.ttf', 'SetrixHD', 100, False)
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
    session.open(MyMetrixStoreWindow)


class MyMetrixStoreWindow(ConfigListScreen, Screen):
    skin = '\n<screen name="MyMetrix-DesignStore" position="40,40" size="1200,640" flags="wfNoBorder" backgroundColor="#40000000">\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="317,600" size="250,33" text="Apply Design" transparent="1" />\n <widget name="menu" position="21,77" scrollbarMode="showOnDemand" size="590,506" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <eLabel position="20,15" size="348,50" text="MyMetrix" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" />\n  <eLabel position="223,15" size="349,50" text="Design Store" foregroundColor="#00ffffff" font="SetrixHD; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n  <eLabel position="300,600" size="5,40" backgroundColor="#0000ff00" />\n<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/vote.png" position="1137,534" size="32,32" zPosition="1" alphatest="blend" />\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="662,600" size="250,33" text="Vote Design" transparent="1" />\n<widget name="helperimage" position="623,211" size="550,310" zPosition="1" alphatest="blend" />\n<widget position="625,77" size="550,50" name="designname" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" />\n <widget position="639,527" size="491,50" name="votes" font="Regular; 30" valign="center" halign="right" transparent="1" backgroundColor="#40000000" />\n<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/vote.png" position="622,600" size="32,32" zPosition="1" alphatest="blend" />\n<widget position="624,142" size="349,50" name="author" foregroundColor="#00bbbbbb" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n<widget position="974,145" size="200,40" name="date" foregroundColor="#00999999" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" zPosition="1" />\n </screen>\n'

    def __init__(self, session, args = None, picPath = None):
        self.url = 'http://connect.mymetrix.de/designs/designs.php'
        self.likeurl = 'http://connect.mymetrix.de/designs/likedesign.php'
        self.screenshotpath = 'http://connect.mymetrix.de/designs/showscreenshot.php?name='
        self.skin_lines = []
        Screen.__init__(self, session)
        self.session = session
        self['designname'] = Label()
        self['author'] = Label()
        self['votes'] = Label()
        self['date'] = Label()
        self.picPath = picPath
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['helperimage'] = Pixmap()
        self['menu'] = StoreList([])
        self.menulist = []
        self.getDesigns()
        self['menu'].setList(self.menulist)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'left': self.keyLeft,
         'right': self.keyRight,
         'up': self.keyUp,
         'down': self.keyDown,
         'green': self.applyDesign,
         'yellow': self.likeDesign,
         'cancel': self.save}, -1)
        self.onLayoutFinish.append(self.UpdateComponents)

    def getDesigns(self):
        file = urllib2.urlopen(self.url)
        data = file.read()
        file.close()
        dom = parseString(data)
        for design in dom.getElementsByTagName('design'):
            name = str(design.getAttributeNode('name').nodeValue)
            title = str(design.getAttributeNode('title').nodeValue)
            author = str(design.getAttributeNode('author').nodeValue)
            likes = str(design.getAttributeNode('likes').nodeValue)
            date = str(design.getAttributeNode('date').nodeValue)
            self.menulist.append(self.DesignsListEntry(name, title, author, likes, date))

    def DesignsListEntry(self, name, title, author, likes, date):
        res = [[name,
          title,
          author,
          likes,
          date]]
        png = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/vote.png'
        res.append(MultiContentEntryPixmapAlphaTest(pos=(552, 9), size=(32, 32), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(3, 4), size=(380, 45), font=0, text=title))
        res.append(MultiContentEntryText(pos=(486, 9), size=(60, 40), font=1, flags=RT_HALIGN_RIGHT, text=likes))
        return res

    def GetPicturePath(self):
        try:
            returnValue = str(self['menu'].l.getCurrentSelection()[0][0])
            path = metrixTools.downloadFile(self.screenshotpath + returnValue)
            return path
        except:
            pass

    def updateMeta(self):
        self['designname'].setText(_(str(self['menu'].l.getCurrentSelection()[0][1])))
        self['author'].setText(_('by ' + str(self['menu'].l.getCurrentSelection()[0][2])))
        self['votes'].setText(_(str(self['menu'].l.getCurrentSelection()[0][3])))
        self['date'].setText(_(str(self['menu'].l.getCurrentSelection()[0][4])))

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
        self.UpdatePicture()

    def keyDown(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveDown)
        self.updateMeta()
        self.ShowPicture()

    def keyUp(self):
        self['menu'].instance.moveSelection(self['menu'].instance.moveUp)
        self.updateMeta()
        self.ShowPicture()

    def save(self):
        config.plugins.MyMetrix.Color.save()
        configfile.save()
        self.close()

    def exit(self):
        self.close()

    def likeString(self, likes):
        if str(likes) == '1':
            return '1Vote'
        else:
            return str(likes) + 'Votes'

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
                        self.showInfo('Design successfully applied!')
                    except:
                        self.showInfo('Design corrupt!')

        except:
            self.showInfo('Design corrupt!')

    def likeDesign(self):
        try:
            designname = self['menu'].l.getCurrentSelection()[0][0]
            query = '?name=' + urllib.quote(designname)
            query = query + '&userid=' + urllib.quote(str(get_mac()))
            print 'query: ' + query
            file = urllib2.urlopen(self.likeurl + query)
            data = file.read()
            file.close()
            dom = parseString(data)
            for query in dom.getElementsByTagName('query'):
                status = str(query.getAttributeNode('status').nodeValue)
                if status == 'success':
                    self.showInfo('Liked!')
                    self['menu'].l.getCurrentSelection()[0][3] = str(int(self['menu'].l.getCurrentSelection()[0][3]) + 1)
                    self.updateMeta()
                else:
                    self.showInfo('Already liked!')

        except:
            self.showInfo('Already liked!')

    def toRGB(self, text):
        rgb = []
        textar = str(text.replace('[', '').replace(']', '')).split(',')
        rgb.append(int(textar[0]))
        rgb.append(int(textar[1]))
        rgb.append(int(textar[2]))
        return rgb

    def showInfo(self, text = 'Information'):
        self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)


class StoreList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        self.l.setFont(0, gFont('SetrixHD', 26))
        self.l.setFont(1, gFont('Regular', 22))
