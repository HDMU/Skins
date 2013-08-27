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
    skin = '\n<screen name="MyMetrix-Store-Browse" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">\n<eLabel position="0,0" size="1280,720" backgroundColor="#b0ffffff" zPosition="-50" />\n<eLabel position="40,40" size="620,640" backgroundColor="#40111111" zPosition="-1" />\n<eLabel position="660,60" size="575,600" backgroundColor="#40222222" zPosition="-1" />\n<eLabel position="644,40" size="5,60" backgroundColor="#000000ff" />\n<widget position="500,61" size="136,40" name="sort" foregroundColor="#00bbbbbb" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" />\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="695,619" size="174,33" text="%s" transparent="1" />\n <widget name="menu" position="55,122" scrollbarMode="showNever" size="605,555" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <widget position="55,55" size="453,50" name="title" noWrap="1" foregroundColor="#00ffffff" font="SetrixHD; 33" valign="center" transparent="1" backgroundColor="#40000000" />\n  <widget position="679,585" size="533,32" name="isInstalled" foregroundColor="#00ffffff" font="Regular; 20" valign="center" halign="left" transparent="1" backgroundColor="#40000000" />\n  <eLabel position="681,620" size="5,40" backgroundColor="#0000ff00" />\n<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/star.png" position="1192,619" size="32,34" zPosition="1" alphatest="blend" />\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="899,618" size="170,33" text="%s" transparent="1" />\n<widget name="helperimage" position="669,150" size="550,310" zPosition="1" alphatest="blend" />\n<widget position="674,62" size="546,50" name="itemname" foregroundColor="#00ffffff" font="SetrixHD; 35" valign="center" transparent="1" backgroundColor="#40000000" noWrap="1" />\n <widget position="1073,617" size="113,40" name="votes" foregroundColor="#00ffffff" font="Regular; 25" valign="center" halign="right" transparent="1" backgroundColor="#40000000" noWrap="1" />\n<eLabel position="885,620" zPosition="1" size="5,40" backgroundColor="#00ffff00" />\n<widget position="674,462" size="545,121" name="description" foregroundColor="#00ffffff" font="Regular; 17" valign="center" halign="left" transparent="1" backgroundColor="#40000000" />\n<widget position="674,112" size="341,35" name="author" foregroundColor="#00bbbbbb" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n<widget position="1019,113" size="200,35" name="date" foregroundColor="#00999999" font="Regular; 25" valign="center" backgroundColor="#40000000" transparent="1" halign="right" zPosition="1" />\n<eLabel position="0,10" size="40,700" backgroundColor="#30000000" zPosition="-1" />\n </screen>\n' % (_('Install '), _('Vote'))

    def __init__(self, session, screenname = '%', suite_id = '%', title = 'SkinParts'):
        self['title'] = Label(_('OpenStore // ' + screenname))
        if screenname == '%':
            self['title'] = Label(_('OpenStore // ' + title))
        self.orderby = 'date desc'
        self.screenname = screenname
        self.suite_id = suite_id
        self.url = 'http://connect.mymetrix.de/store/api/?q=get.xml.skinparts'
        self.screenshotpath = 'http://connect.mymetrix.de/store/api/?q=get.pngresized&width=550'
        self.screenshotpath_v2 = 'http://connect.mymetrix.de/store/api/?q=v2.get.png&width=550&type=6'
        Screen.__init__(self, session)
        self.session = session
        self['itemname'] = Label()
        self['author'] = Label()
        self['votes'] = Label()
        self['date'] = Label()
        self['sort'] = Label(_('New'))
        self['description'] = Label()
        self['isInstalled'] = Label()
        self.currentauthor = ''
        self.currentid = '0'
        self.image_id = ''
        self.image_token = ''
        self.currenttype = 'widget'
        self.currentgroup = 'SkinParts'
        self.picPath = ''
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['helperimage'] = Pixmap()
        self.getCatalog = True
        self.getEntry = True
        self.initPicture = True
        self.action_downloadSkinPart = False
        self['menu'] = SkinPartsList([])
        self.menulist = []
        self.menulist.append(self.SkinPartsListEntry('-', _('loading, please wait...'), '', '0', '0', '0', '0', '0', '0', '0', '', ''))
        self['menu'].setList(self.menulist)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'up': self.keyUp,
         'ok': self.selectItem,
         'green': self.installSkinPart,
         'blue': self.changeSort,
         'down': self.keyDown,
         'right': self.pageDown,
         'left': self.pageUp,
         'yellow': self.openRating,
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
                self.getSkinParts()
            if self.initPicture == True:
                self.initPicture = False
                self.UpdatePicture()
                self.updateMeta()
            if self.getEntry == True:
                self.getEntry = False
                self.updateMeta()
                self.ShowPicture()
            if self.action_downloadSkinPart == True:
                self.action_downloadSkinPart = False
                self.downloadSkinPart()
            time.sleep(1)

    def getSkinParts(self, isactive = ''):
        try:
            params = {'screenname': self.screenname,
             'suite_id': self.suite_id,
             'v2': 'true',
             'orderby': self.orderby}
            data = metrixCore.getWeb('http://connect.mymetrix.de/store/api/?q=get.xml.skinparts', True, params)
            if not data:
                print '[MyMetrix] Error getting SkinParts'
            dom = parseString(data)
            self.menulist = []
            for design in dom.getElementsByTagName('entry'):
                item_id = str(design.getAttributeNode('id').nodeValue)
                name = str(design.getAttributeNode('name').nodeValue)
                author = str(design.getAttributeNode('author').nodeValue)
                version = str(design.getAttributeNode('version').nodeValue)
                rating = str(design.getAttributeNode('rating').nodeValue)
                date = str(design.getAttributeNode('date').nodeValue)
                item_type = str(design.getAttributeNode('type').nodeValue)
                screenname = str(design.getAttributeNode('screenname').nodeValue)
                image_id = str(design.getAttributeNode('image_id').nodeValue)
                image_token = str(design.getAttributeNode('image_token').nodeValue)
                total_votes = str(design.getAttributeNode('total_votes').nodeValue)
                description = str(design.getAttributeNode('description').nodeValue)
                self.menulist.append(self.SkinPartsListEntry(item_id, name, author, rating, date, version, total_votes, item_type, image_id, image_token, description, screenname, isactive))

            self['menu'].setList(self.menulist)
            self.updateMeta()
            self.ShowPicture()
        except:
            pass

    def SkinPartsListEntry(self, item_id, name, author, rating, date, version, total_votes, item_type, image_id, image_token, description, screenname, isactive = ''):
        res = [[item_id,
          name,
          author,
          rating,
          date,
          version,
          total_votes,
          item_type,
          image_id,
          image_token,
          description,
          screenname,
          isactive]]
        path = metrixDefaults.pathRoot() + 'skinparts/' + item_type + 's/active/' + item_type + '_' + str(item_id) + '/'
        if os.path.exists(path):
            pngtype = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/' + item_type + '-on.png'
        else:
            pngtype = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/' + item_type + '.png'
        png = '/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/vote' + rating + '.png'
        res.append(MultiContentEntryPixmapAlphaTest(pos=(412, 9), size=(170, 32), png=loadPNG(png)))
        res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 7), size=(32, 32), png=loadPNG(pngtype)))
        res.append(MultiContentEntryText(pos=(40, 4), size=(367, 45), font=0, text=name))
        return res

    def installSkinPart(self):
        self.action_downloadSkinPart = True

    def downloadSkinPart(self):
        self['isInstalled'].setText('Installing...')
        try:
            id = self.currentid
            type = self.currenttype
            author = self.currentauthor
            type = str(self['menu'].l.getCurrentSelection()[0][7])
            image_id = str(self['menu'].l.getCurrentSelection()[0][8])
            image_token = str(self['menu'].l.getCurrentSelection()[0][9])
            if type == 'bundle':
                metrix_SkinPartTools.installBundle(id, type, author)
            else:
                metrix_SkinPartTools.installSkinPart(id, type, author, image_id, image_token)
            getCatalog = True
            getEntry = True
            self['isInstalled'].setText('Installation successful!')
        except Exception as e:
            print '[MyMetrix] ' + str(e)
            traceback.print_exc()
            self['isInstalled'].setText('Error during installation!')

    def GetPicturePath(self):
        try:
            self.image_id = str(self['menu'].l.getCurrentSelection()[0][8])
            self.item_id = str(self['menu'].l.getCurrentSelection()[0][0])
            self.image_token = str(self['menu'].l.getCurrentSelection()[0][9])
            path = ''
            if self.image_id == '':
                path = metrixTools.downloadFile(self.screenshotpath_v2 + '&id=' + self.item_id, path + 'preview.png')
            else:
                path = metrixTools.downloadFile(self.screenshotpath + '&image_id=' + self.image_id + '&token=' + self.image_token, path + 'preview.png')
            return path
        except:
            pass

    def updateMeta(self):
        try:
            self['itemname'].setText(_(str(self['menu'].l.getCurrentSelection()[0][1])))
            self['author'].setText(_('loading...'))
            self['votes'].setText(str(self['menu'].l.getCurrentSelection()[0][6]))
            self['date'].setText(str(self['menu'].l.getCurrentSelection()[0][5]))
            self['description'].setText(str(self['menu'].l.getCurrentSelection()[0][10]))
            self.currentid = str(self['menu'].l.getCurrentSelection()[0][0])
            self.currenttype = str(self['menu'].l.getCurrentSelection()[0][7])
            self.currentauthor = str(self['menu'].l.getCurrentSelection()[0][2])
            id = self.currentid
            type = self.currenttype
            path = metrixDefaults.pathRoot() + 'skinparts/' + type + 's/active/' + type + '_' + str(id) + '/'
            if os.path.exists(path):
                self['isInstalled'].setText('Already installed!')
            else:
                self['isInstalled'].setText('')
        except Exception as e:
            print '[MyMetrix] ' + str(e)
            traceback.print_exc()

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
        self['author'].setText(_('by ' + str(self['menu'].l.getCurrentSelection()[0][2])))

    def DecodePicture(self, PicInfo = ''):
        ptr = self.PicLoad.getData()
        self['helperimage'].instance.setPixmap(ptr)

    def UpdateComponents(self):
        self.UpdatePicture()
        self.updateMeta()

    def selectItem(self):
        self.getEntry = True

    def pageUp(self):
        self['menu'].instance.moveSelection(self['menu'].instance.pageUp)

    def pageDown(self):
        self['menu'].instance.moveSelection(self['menu'].instance.pageDown)

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

    def openRating(self):
        self.session.open(metrix_Store_SubmitRating.OpenScreen, self.currentid, self.currentgroup)
        self.getCatalog = True
        self.getEntry = True

    def showInfo(self, text = 'Information'):
        self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)

    def changeSort(self):
        if self.orderby == 'date desc':
            self.orderby = 'rating.total_value desc'
            self['sort'].setText('Charts')
        elif self.orderby == 'rating.total_value desc':
            self.orderby = 'rating.total_votes desc'
            self['sort'].setText('Popular')
        elif self.orderby == 'rating.total_votes desc':
            self.orderby = 'date desc'
            self['sort'].setText('New')
        self.getCatalog = True
        self.getEntry = True


class SkinPartsList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        self.l.setFont(0, gFont('SetrixHD', 24))
        self.l.setFont(1, gFont('Regular', 22))
