from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from xml.dom.minidom import parseString
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
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import ePicLoad, eListboxPythonMultiContent, gFont, addFont, loadPic, loadPNG
from Components.Pixmap import Pixmap
from Components.Label import Label
import urllib
import gettext
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixColors
import metrixDefaults
import shutil
import os
import time
import threading
import traceback
import metrix_SkinPartTools
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
    skin = '\n<screen name="MyMetrix-MySkinParts" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#b0ffffff">\n<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />\n<eLabel position="660,70" size="575,580" backgroundColor="#40222222" zPosition="-1" />\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="695,609" size="160,33" text="%s" transparent="1" />\n <widget name="mainmenu" position="55,122" scrollbarMode="showOnDemand" size="590,541" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <widget position="55,55" size="589,50" foregroundColor="#00ffffff" name="title" font="SetrixHD; 40" valign="center" transparent="1" backgroundColor="#40000000" />\n  \n  <eLabel position="681,610" size="5,40" backgroundColor="#00ff0000" />\n<widget position="679,496" size="532,112" name="description" foregroundColor="#00ffffff" font="Regular; 17" valign="center" halign="left" transparent="1" backgroundColor="#40000000" />\n\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="884,608" size="162,33" text="%s" transparent="1" />\n<widget name="helperimage" position="671,181" size="550,310" zPosition="1" alphatest="blend" />\n<widget position="674,82" size="546,50" name="itemname" foregroundColor="#00ffffff" font="SetrixHD; 35" valign="center" transparent="1" backgroundColor="#40000000" noWrap="1" />\n <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="1074,608" size="162,33" text="%s" transparent="1" />\n<eLabel position="870,610" zPosition="1" size="5,40" backgroundColor="#0000ff00" />\n<widget position="675,132" size="341,50" name="author" foregroundColor="#00bbbbbb" font="Regular; 28" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n\n<eLabel position="1060,610" zPosition="1" size="5,40" backgroundColor="#000000ff" />\n\n<widget position="1019,135" size="200,40" name="date" foregroundColor="#00999999" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" zPosition="1" />\n\n\n </screen>\n' % (_('Disable'), _('Enable'), _('Delete'))

    def __init__(self, session, args = None, picPath = None):
        self['title'] = Label(_('MyMetrix // My SkinParts'))
        self.skin_lines = []
        Screen.__init__(self, session)
        self.session = session
        self.picPath = picPath
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['helperimage'] = Pixmap()
        self['itemname'] = Label()
        self['author'] = Label()
        self['date'] = Label()
        self['description'] = Label()
        self.getCatalog = True
        self.getEntry = True
        self.initPicture = True
        self['mainmenu'] = StoreList([])
        self.mainmenu = []
        self.mainmenu.append(self.StoreMenuEntry('No SkinParts installed!'))
        self['mainmenu'].setList(self.mainmenu)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'right': self.pageDown,
         'left': self.pageUp,
         'down': self.keyDown,
         'up': self.keyUp,
         'ok': self.keyRight,
         'red': self.disableSkinPart,
         'green': self.enableSkinPart,
         'blue': self.deleteSkinPart,
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
                self.getSkinParts(metrixDefaults.pathRoot() + 'skinparts/widgets/active/', '-on')
                self.getSkinParts(metrixDefaults.pathRoot() + 'skinparts/screens/active/', '-on')
                self.getSkinParts(metrixDefaults.pathRoot() + 'skinparts/widgets/inactive/')
                self.getSkinParts(metrixDefaults.pathRoot() + 'skinparts/screens/inactive/')
            if self.initPicture == True:
                self.initPicture = False
                self.UpdatePicture()
                self.updateMeta()
            if self.getEntry == True:
                self.getEntry = False
                self.updateMeta()
                self.ShowPicture()
            time.sleep(1)

    def getSkinParts(self, path, isactive = ''):
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
                    type = str(design.getAttributeNode('type').nodeValue)
                    version = str(design.getAttributeNode('version').nodeValue)
                    self.mainmenu.append(self.StoreMenuEntry(name, path + dir, type, author, version, description, isactive, id))

                self['mainmenu'].setList(self.mainmenu)
            except:
                pass

    def StoreMenuEntry(self, name, value = '', type = 'screen', author = '', version = '', description = '', isactive = '', id = ''):
        res = [[value,
          name,
          type,
          author,
          version,
          description,
          isactive,
          id]]
        pngtype = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/' + type + isactive + '.png'
        res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 7), size=(32, 32), png=loadPNG(pngtype)))
        res.append(MultiContentEntryText(pos=(40, 4), size=(405, 45), font=0, text=name))
        return res

    def updateMeta(self):
        try:
            self['itemname'].setText(str(self['mainmenu'].l.getCurrentSelection()[0][1]))
            self['author'].setText(_('by ' + str(self['mainmenu'].l.getCurrentSelection()[0][3])))
            self['date'].setText(str(self['mainmenu'].l.getCurrentSelection()[0][4]))
            self['description'].setText(str(self['mainmenu'].l.getCurrentSelection()[0][5]))
        except:
            pass

    def disableSkinPart(self):
        try:
            file = self['mainmenu'].l.getCurrentSelection()[0][0]
            metrix_SkinPartTools.disableSkinPart(file)
        except Exception as e:
            print '[MyMetrix] ' + str(e)
            traceback.print_exc()

        self.getCatalog = True

    def deleteSkinPart(self):
        try:
            file = self['mainmenu'].l.getCurrentSelection()[0][0]
            print file
            shutil.rmtree(file)
        except Exception as e:
            print '[MyMetrix] ' + str(e)
            traceback.print_exc()

        self.getCatalog = True

    def enableSkinPart(self):
        try:
            file = self['mainmenu'].l.getCurrentSelection()[0][0]
            metrix_SkinPartTools.enableSkinPart(file)
        except Exception as e:
            print '[MyMetrix] ' + str(e)
            traceback.print_exc()

        self.getCatalog = True

    def GetPicturePath(self):
        config.plugins.MyMetrix.Color.save()
        try:
            path = self['mainmenu'].l.getCurrentSelection()[0][0] + '/preview.png'
            return path
        except:
            return '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/nopreview.png'

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
        self.exit()

    def keyRight(self):
        self.getEntry = True

    def pageUp(self):
        self['mainmenu'].instance.moveSelection(self['mainmenu'].instance.pageUp)

    def pageDown(self):
        self['mainmenu'].instance.moveSelection(self['mainmenu'].instance.pageDown)

    def keyDown(self):
        self['mainmenu'].instance.moveSelection(self['mainmenu'].instance.moveDown)
        self.getEntry = True

    def keyUp(self):
        self['mainmenu'].instance.moveSelection(self['mainmenu'].instance.moveUp)
        self.getEntry = True

    def showInfo(self):
        self.session.open(MessageBox, _('Information'), MessageBox.TYPE_INFO)

    def save(self):
        self.close()

    def exit(self):
        self.close()


class StoreList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        self.l.setFont(0, gFont('SetrixHD', 26))
        self.l.setFont(1, gFont('Regular', 22))
