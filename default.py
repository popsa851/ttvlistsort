
import xbmc
import xbmcgui
import xbmcaddon
import codecs,sys,subprocess
import threading
from threading import Thread



ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')
ADDON_NAME = ADDON.getAddonInfo('name')

reload(sys)
sys.setdefaultencoding('utf-8')

class Channel:

    def __init__(self, index=None, Name=None, status=0, enable=0):
        self._index = index
        self._Name = Name

        # status : 0 - default; 1 - delete; 2 - new; 3 - update
        self._status = status
        self._enable = enable



    def loadChannels(self):
        channels_list  = []
        with codecs.open('/storage/.config/acelist/fav_full.txt', 'r', encoding='utf8') as fav:
            fav_list = fav.read().splitlines()
            i = 1
        for item in fav_list:
            channels_list.append(Channel(i,item.encode('utf-8'),1,1))
            i+=1;
        return  channels_list




class GUI(Channel,xbmcgui.WindowXMLDialog):



    def onInit(self):

        pDialog = xbmcgui.DialogProgress()
        pDialog.create(ADDON_NAME, self.getLang(32056))
        xbmc.sleep(500)
        self.defineControls()
        pDialog.update(25)
        self.thread = threading.Thread(self.showDialog())
        self.thread.start()
        xbmc.sleep(500)
        pDialog.update(100)




    def getLang(self, code):
        return ADDON.getLocalizedString(code)

    def defineControls(self):
        try:
            # control ids
            self._control_heading_label_id = 1
            self._control_achannels_update_button_id = 20
            self._control_achannels_sortby_button_id = 21
            self._control_achannels_list_id = 22
            self._control_schannels_clear_button_id = 24
            self._control_schannels_correction_button_id = 25
            self._control_schannels_list_id = 26
            self._control_save_button_id = 28
            self._control_cancel_button_id = 29
            # controls
            self._heading_label = self.getControl(self._control_heading_label_id)
            self._achannels_update_button = self.getControl(self._control_achannels_update_button_id)
            self._achannels_sortby_button = self.getControl(self._control_achannels_sortby_button_id)
            self._achannels_list = self.getControl(self._control_achannels_list_id)
            self._schannels_clear_button = self.getControl(self._control_schannels_clear_button_id)
            self._schannels_correction_button = self.getControl(self._control_schannels_correction_button_id)
            self._schannels_list = self.getControl(self._control_schannels_list_id)
            self._save_button = self.getControl(self._control_save_button_id)
            self._cancel_button = self.getControl(self._control_cancel_button_id)
        except : pass


    def showDialog(self):
        try:

            self._heading_label.setLabel(self.getLang(32040))
            self._achannels_update_button.setLabel(self.getLang(32041))
            self._achannels_sortby_button.setLabel(self.getLang(32043))
            self._schannels_clear_button.setLabel(self.getLang(32046))
            self._schannels_correction_button.setLabel(self.getLang(32048))
            self._save_button.setLabel(self.getLang(32049))
            self._cancel_button.setLabel(self.getLang(32050))
            #init
            self.updateChannelsList()
            self.setFocus(self._achannels_list)
        except :pass

    def onClick(self, controlId):
        try:
            if controlId == self._control_achannels_list_id:
                self.fullList_Click()
                self.countUpadte()
            elif controlId == self._control_schannels_list_id:
                self.favList_Click()
                self.countUpadte()
            if controlId == self._control_save_button_id:
                self.saveList()
            #cancel dialog
            if controlId == self._control_cancel_button_id:
                self.closeDialog()

        except : pass

    def updateChannelsList(self):
        a = 0
        for chn in Channel.loadChannels(self):

            Item = xbmcgui.ListItem(chn._Name)
            self._achannels_list.addItem(Item)
            a += 1

        self.countUpadte()

    def fullList_Click(self):
        try:
            selItem = self._achannels_list.getSelectedItem()
            selPos = self._achannels_list.getSelectedPosition()
            self._schannels_list.addItem(selItem)
            self._achannels_list.removeItem(selPos)
            self._achannels_list.selectItem(selPos)
        except : pass

    def favList_Click(self):
        try:
            selItem = self._schannels_list.getSelectedItem()
            selPos = self._schannels_list.getSelectedPosition()
            self._achannels_list.addItem(selItem)
            self._schannels_list.removeItem(selPos)
            self._schannels_list.selectItem(selPos)


        except : pass

    def countUpadte(self):
        self._achannels_sortby_button.setLabel(str(self._achannels_list.size()))
        self._schannels_correction_button.setLabel(str(self._schannels_list.size()))

    def saveList(self):
        listSize = self._schannels_list.size()
        with codecs.open('/storage/.config/acelist/fav.txt', 'w', encoding='utf8') as favfile:
            for i in range(listSize):
                item = self._schannels_list.getListItem(i)
                xbmc.log(item.getLabel())
                favfile.write(item.getLabel()+'\n')
        self.Execute('systemctl start acelist')
        self.showExitDialog()
        self.closeDialog()

    def Execute(self, command_line, get_result=0):
        try:

            if get_result == 0:
                process = subprocess.Popen(command_line, shell=True, close_fds=True)
                process.wait()
            else:
                result = ''
                process = subprocess.Popen(command_line, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                process.wait()
                for line in process.stdout.readlines():
                    result = result + line
                return result

        except : pass


    def closeDialog(self):
        try:
            self.close()
            xbmc.log("Application Exit")
        except : pass

    def showExitDialog(self):
        dialog = xbmcgui.Dialog()
        ok = dialog.ok(ADDON_NAME, self.getLang(32057))

if (__name__ == '__main__'):
    # [kodi 18] media windows use the built-in container by default, so do not set the fifth argument (it defaults to False) as we are not going to use it
    ui = GUI('script-testwindow.xml', CWD, 'default', '1080p')
    ui.doModal()
    del ui
