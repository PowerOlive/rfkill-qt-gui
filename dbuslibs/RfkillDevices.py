# -*- Mode: Python; coding: utf-8 -*-

import time

class RfkillDevices(object):
    def __init__(self, state_updater = None):
        from DeviceManager import DeviceManager
        self.parent_state_updater = state_updater
        self._dm = DeviceManager(self.state_updater)
        self._update_device_list()
        self.sate2str = {0: 'off', 1: 'on', 2: 'off'}

    def _update_device_list(self):
        self._devices = self._dm.get_killswitch_devices()
        self.bt = []
        self.wifi = []
        self.wimax = []
        self.unknown = []
        for dev in self._devices:
            if dev.type_name == 'bluetooth':
                dev.frendly_name = 'Bluetooth'
                self.bt.append(dev)
            elif dev.type_name == 'wlan':
                dev.frendly_name = 'Wi-Fi\t'
                self.wifi.append(dev)
            elif dev.type_name == 'wwan':
                dev.frendly_name = 'WiMAX\t'
                self.wimax.append(dev)
            else:
                dev.frendly_name = 'Unknown device:'
                self.unknown.append(dev)

    def __str__(self):
        def p(devcls):
            ss = {0: 'Power Off', 1: 'Power On', 2: 'Hard blocked'}
            ret = ''
            for d in devcls:
                ret += '\t%s\t%s\n' % (d.frendly_name, ss[d.state])
                if len(devcls)>1:
                    ret += '\tPath: %s\n' % d.path
            return ret
        ret = 'rfkill devices:\n'
        if self.bt:
            ret += p(self.bt)
        else:
            ret += 'Bluetooth not present or hard blocked\n'
        if self.wifi:
            ret += p(self.wifi)
        else:
            ret += 'Wi-Fi not present or hard blocked\n'
        if self.wimax:
            ret += p(self.wimax)
        else:
            ret += 'WiMAX not present or hard blocked\n'
        if self.unknown:
            ret += p(self.unknown)
        else:
            ret += 'All devices found'
        return ret

    def state_updater(self, dev, state):
        from DeviceManager import HAL_DEVICE_ADD, HAL_DEVICE_REMOVE
        ss = {HAL_DEVICE_ADD: 'Add', HAL_DEVICE_REMOVE: 'Del'}
        self._update_device_list()
        if self.parent_state_updater:
            self.parent_state_updater()
        else:
            print ss[state], dev

    def SetClassState(self, devcls, state):
        r = False
        for d in devcls:
            r = d.SetPower(state) or r
            time.sleep(1)
        return r

    def GetBluetoothState(self, devid=0):
        if self.bt and devid<len(self.bt):
            return self.bt[devid].GetPower()
        else:
            return 0

    def GetWifiState(self, devid=0):
        if self.wifi and devid<len(self.wifi):
            return self.wifi[devid].GetPower()
        else:
            return 0

    def GetWimaxState(self, devid=0):
        if self.wimax and devid<len(self.wimax):
            return self.wimax[devid].GetPower()
        else:
            return 0

    def GetStates(self):
        return [self.GetBluetoothState(), self.GetWifiState(), self.GetWimaxState()]

    def SetBluetoothState(self, state, devid=0):
        if self.bt and devid<len(self.bt):
            self.bt[devid].SetPower(state)
            time.sleep(1)

    def SetWifiState(self, state, devid=0):
        if self.wifi and devid<len(self.wifi):
            self.wifi[devid].SetPower(state)
            time.sleep(1)

    def SetWimaxState(self, state, devid=0):
        if self.wimax and devid<len(self.wimax):
            self.wimax[devid].SetPower(state)
            time.sleep(1)

if __name__ == '__main__':
    rfkill = RfkillDevices()
    print rfkill
    rfkill.SetBluetoothState(0)
    rfkill.SetWifiState(1)
    rfkill.SetWimaxState(0)
    print rfkill