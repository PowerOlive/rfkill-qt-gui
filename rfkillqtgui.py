#! /usr/bin/python
# -*- Mode: Python; coding: utf-8 -*-

from dbuslibs.RfkillDevices import RfkillDevices
import subprocess, sys
from PyQt4 import QtGui, QtCore


ICON_DIR = 'icons'

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, noScript = False, workAll = False, parent = None):
        self.noScript = noScript
        self.workAll = workAll
        #Icon cash
        self.trayIconPixmaps = {'on_on_on':    QtGui.QPixmap(ICON_DIR+'/icon-bt-on-wifi-on-wimax-on.png'),
                                'on_on_off':   QtGui.QPixmap(ICON_DIR+'/icon-bt-on-wifi-on-wimax-off.png'),
                                'on_off_on':   QtGui.QPixmap(ICON_DIR+'/icon-bt-on-wifi-off-wimax-on.png'),
                                'on_off_off':  QtGui.QPixmap(ICON_DIR+'/icon-bt-on-wifi-off-wimax-off.png'),
                                'off_on_on':   QtGui.QPixmap(ICON_DIR+'/icon-bt-off-wifi-on-wimax-on.png'),
                                'off_on_off':  QtGui.QPixmap(ICON_DIR+'/icon-bt-off-wifi-on-wimax-off.png'),
                                'off_off_on':  QtGui.QPixmap(ICON_DIR+'/icon-bt-off-wifi-off-wimax-on.png'),
                                'off_off_off': QtGui.QPixmap(ICON_DIR+'/icon-bt-off-wifi-off-wimax-off.png')}
        self.menuIconPixmaps = {'bt-on':     QtGui.QPixmap(ICON_DIR+'/icon-bt-on.png'),
                                'bt-off':    QtGui.QPixmap(ICON_DIR+'/icon-bt-off.png'),
                                'wifi-on':   QtGui.QPixmap(ICON_DIR+'/icon-wifi-on.png'),
                                'wifi-off':  QtGui.QPixmap(ICON_DIR+'/icon-wifi-off.png'),
                                'wimax-on':  QtGui.QPixmap(ICON_DIR+'/icon-wimax-on.png'),
                                'wimax-off': QtGui.QPixmap(ICON_DIR+'/icon-wimax-off.png')}
        QtGui.QSystemTrayIcon.__init__(self, QtGui.QIcon(self.trayIconPixmaps['on_on_on']), parent)

        #Menu Actions
        self.btAction =    QtGui.QAction(QtGui.QIcon(self.menuIconPixmaps['bt-on']),    '&Bluetooth', self)
        QtCore.QObject.connect(self.btAction, QtCore.SIGNAL('triggered()'), self.switchBluetooth)
        self.btAction.setCheckable(True)
        self.wifiAction =  QtGui.QAction(QtGui.QIcon(self.menuIconPixmaps['wifi-on']),  '&Wi-Fi', self)
        QtCore.QObject.connect(self.wifiAction, QtCore.SIGNAL('triggered()'), self.switchWifi)
        self.wifiAction.setCheckable(True)
        self.wimaxAction = QtGui.QAction(QtGui.QIcon(self.menuIconPixmaps['wimax-on']), 'Wi&Max', self)
        QtCore.QObject.connect(self.wimaxAction, QtCore.SIGNAL('triggered()'), self.switchWimax)
        self.wimaxAction.setCheckable(True)

        self.quitAction = QtGui.QAction('&Quit', self)
        QtCore.QObject.connect(self.quitAction, QtCore.SIGNAL('triggered()'), QtGui.qApp, QtCore.SLOT('quit()'))

        #Tray Menu
        self.menu = QtGui.QMenu(parent)
        self.menu.addAction(self.btAction)
        self.menu.addAction(self.wifiAction)
        self.menu.addAction(self.wimaxAction)
        self.menu.addSeparator()
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)
        QtCore.QObject.connect(self, QtCore.SIGNAL('activated(QSystemTrayIcon::ActivationReason)'), self.menuClick)
        self.click_pos = QtCore.QPoint(640,480)
        self.installEventFilter(self)

        #rfkill
        self.rfkill = RfkillDevices(self.updateState)
        self.updateState()

        #update timer
        self.timer = QtCore.QTimer(parent)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.updateState);
        self.timer.start(5000)

    def updateState(self):
        of = ['off', 'on']
        states = self.rfkill.GetStates()
        self.btAction.setIcon(QtGui.QIcon(self.menuIconPixmaps['bt-' + of[states[0]]]))
        self.btAction.setChecked(states[0])
        self.wifiAction.setIcon(QtGui.QIcon(self.menuIconPixmaps['wifi-' + of[states[1]]]))
        self.wifiAction.setChecked(states[1])
        self.wimaxAction.setIcon(QtGui.QIcon(self.menuIconPixmaps['wimax-' + of[states[2]]]))
        self.wimaxAction.setChecked(states[2])
        ss = [of[x] for x in states]
        self.setIcon(QtGui.QIcon(self.trayIconPixmaps['_'.join(ss)]))
        self.setToolTip("Bluetooth: %s Wi-Fi: %s WiMAX: %s" % tuple(ss))

    def switchBluetooth(self):
        self.rfkill.SetBluetoothState(not self.rfkill.GetBluetoothState())
        self.updateState()

    def switchWifi(self):
        if not self.workAll and not self.rfkill.GetWifiState():
            if self.rfkill.GetWimaxState():
                self.switchWimax()
                self.updateState()
        self.rfkill.SetWifiState(not self.rfkill.GetWifiState())
        self.updateState()

    def switchWimax(self):
        if not self.workAll and not self.rfkill.GetWimaxState:
            if self.rfkill.GetWifiState():
                self.rfkill.SetWifiState(False)
                self.updateState()
        self.rfkill.SetWimaxState(not self.rfkill.GetWimaxState())
        if self.rfkill.GetWimaxState():
            self.execScript('scripts/wimax-connect.sh')
        else:
            self.execScript('scripts/wimax-disconnect.sh')
        self.updateState()

    def execScript(self, script):
        if self.noScript: return 0
        print 'Run:', script
        r = subprocess.call(["/usr/bin/kdesu", "-c", script])
        print 'Rerturn:', r

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ToolTip:
            self.click_pos = event.globalPos()
        return QtGui.QSystemTrayIcon.eventFilter(self, obj, event)

    def menuClick(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.menu.popup(self.click_pos)

def usage():
    print "rfcillqtgui.py [--no-script] [--all]\n\t-s, --no-script\t\t- to disable the WiMAX scripts\n\t-a, --all\t\t- allow to work simultaneously Wi-Fi and WiMAX"


def main():
    #Parse options
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hsa", ["help", "no-script", "all"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    noScript = False
    workAll = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(2)
        if o in ("-s", "--no-script"):
            noScript = True
        if o in ("-a", "--all"):
            workAll = True
    #Main icon
    app = QtGui.QApplication(sys.argv)
    style = app.style()
    icon = QtGui.QIcon(style.standardPixmap(QtGui.QStyle.SP_FileIcon))
    trayIcon = SystemTrayIcon(icon, noScript, workAll)

    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
