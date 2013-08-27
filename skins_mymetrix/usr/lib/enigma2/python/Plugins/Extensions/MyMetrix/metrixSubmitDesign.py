import base64
from encode import multipart_encode
from streaminghttp import register_openers
import cookielib
import MultipartPostHandler
from Plugins.Plugin import PluginDescriptor
from uuid import getnode as get_id
from Screens.Screen import Screen
import os
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
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import urllib, urllib2
from xml.dom.minidom import parseString
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import metrixColors
import metrixDefaults
import metrixPreview2
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


class MyMetrixSubmitDesignWindow(ConfigListScreen, Screen):
    skin = '\n<screen name="MyMetrix-Colors" position="350,245" size="631,235" flags="wfNoBorder" backgroundColor="#40000000">\n  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="39,196" size="250,33" text="Cancel" transparent="1" />\n <widget name="config" position="21,77" itemHeight="30" scrollbarMode="showOnDemand" size="590,107" transparent="1" foregroundColor="#00ffffff" backgroundColor="#40000000" />\n  <eLabel position="20,15" size="348,50" text="MyMetrix" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />\n  <eLabel position="223,15" size="349,50" text="Publish in OpenStore" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />\n  <eLabel position="20,195" size="5,40" backgroundColor="#00ff0000" />\n   \n <eLabel position="324,195" size="5,40" backgroundColor="#0000ff00" />\n  <widget name="button_green" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="339,196" size="250,33" transparent="1" />\n\n   \n  </screen>\n'

    def __init__(self, session, args = None, picPath = None):
        self.url = 'http://connect.mymetrix.de/designs/designs.php'
        self.submiturl = 'http://connect.mymetrix.de/designs/submitdesign.php'
        self.submitimageurl = 'http://connect.mymetrix.de/designs/submitdesignimage.php'
        self.skin_lines = []
        self.grabbed = False
        self['button_green'] = Label(_('Add screenshot'))
        Screen.__init__(self, session)
        self.session = session
        list = []
        list.append(getConfigListEntry(_('Design name'), config.plugins.MyMetrix.Store.Designname))
        list.append(getConfigListEntry(_('Author: ' + config.plugins.MyMetrix.Store.Author.value)))
        ConfigListScreen.__init__(self, list)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions'], {'green': self.grabScreen,
         'red': self.exit,
         'cancel': self.exit}, -1)

    def grabScreen(self):
        if self.grabbed == False:
            config.plugins.MyMetrix.Store.Designname.save()
            config.plugins.MyMetrix.Store.Author.save()
            self.session.open(metrixPreview2.MyMetrixPreview2Window)
            self['button_green'].setText('Submit')
            self.grabbed = True
        else:
            self.submitDesign()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.ShowPicture()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.ShowPicture()

    def exit(self):
        self.close()

    def submitDesign(self):
        if 1 == 1:
            config.plugins.MyMetrix.Store.Designname.save()
            config.plugins.MyMetrix.Store.Author.save()
            params = {'file': open('/tmp/metrixPreview.png', 'rb').read(),
             'product': 'MyMetrix',
             'title': config.plugins.MyMetrix.Store.Designname.value,
             'name': config.plugins.MyMetrix.Store.Designname.value.replace(' ', '-').replace('&', '-').replace('!', '-').replace('$', '-').replace('/', '-').replace('=', '-').replace('?', '-').replace('"', '-').replace('\\', '-').replace('+', '-').replace('.', '-').replace(';', '-').replace('@', '-').lower(),
             'backgroundtrans': config.plugins.MyMetrix.Color.BackgroundTransparency.value,
             'selectiontrans': config.plugins.MyMetrix.Color.SelectionTransparency.value,
             'backgroundtexttrans': config.plugins.MyMetrix.Color.BackgroundTextTransparency.value,
             'selection': config.plugins.MyMetrix.Color.Selection.value,
             'progressbars': config.plugins.MyMetrix.Color.ProgressBar.value,
             'background': config.plugins.MyMetrix.Color.Background.value,
             'background2': config.plugins.MyMetrix.Color.Background2.value,
             'foreground': config.plugins.MyMetrix.Color.Foreground.value,
             'backgroundtext': config.plugins.MyMetrix.Color.BackgroundText.value,
             'accent1': config.plugins.MyMetrix.Color.Accent1.value,
             'accent2': config.plugins.MyMetrix.Color.Accent2.value,
             'selection_custom': str(config.plugins.MyMetrix.Color.Selection_Custom.value),
             'background_custom': str(config.plugins.MyMetrix.Color.Background_Custom.value),
             'background2_custom': str(config.plugins.MyMetrix.Color.Background2_Custom.value),
             'foreground_custom': str(config.plugins.MyMetrix.Color.Foreground_Custom.value),
             'backgroundtext_custom': str(config.plugins.MyMetrix.Color.BackgroundText_Custom.value),
             'accent1_custom': str(config.plugins.MyMetrix.Color.Accent1_Custom.value),
             'accent2_custom': str(config.plugins.MyMetrix.Color.Accent2_Custom.value)}
            try:
                data = metrixCore.getWeb(self.submiturl, True, params)
                dom = parseString(data)
                for design in dom.getElementsByTagName('query'):
                    status = str(design.getAttributeNode('status').nodeValue)
                    if status == 'success':
                        self.showInfo('Design successfully submitted!')
                        self.close()
                    else:
                        self.showInfo('Design name already given!')

            except:
                self.showInfo('Error publishing Design!')

    def showInfo(self, text = 'Information'):
        self.session.open(MessageBox, _(text), MessageBox.TYPE_INFO)
