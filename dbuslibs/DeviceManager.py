# -*- Mode: Python; coding: utf-8 -*-

import dbus
from dbus.mainloop.qt import DBusQtMainLoop

DBusQtMainLoop(set_as_default=True)

HAL_DEVICE_REMOVE = 0
HAL_DEVICE_ADD = 1

class _HALDevice(object):
    def __init__(self, bus, udi):
        self.udi = udi
        self._device = dbus.Interface(
            bus.get_object('org.freedesktop.Hal', udi),
            'org.freedesktop.Hal.Device')
        self.path = self.get('linux.sysfs_path')

    def get(self, property):
        return self._device.GetProperty(property)

    def __str__(self):
        ret =  'HAL Device\n'
        ret += 'udi: %s\n' % self.udi
        ret += 'sys path: %s\n' % self.path
        return ret

class _HALKillSwitchDevice(_HALDevice):
    def __init__(self, bus, udi):
        _HALDevice.__init__(self, bus, udi)
        self._killswitch = dbus.Interface(
            bus.get_object('org.freedesktop.Hal', udi),
            'org.freedesktop.Hal.Device.KillSwitch')
        self.type_name = self.get('killswitch.type')
        self.state = int(open(self.path + '/state').read().strip())

    def __str__(self):
        state ={0: 'off', 1: 'on', 2: 'hard blocked'}
        ret = 'HAL KillSwitch Device\n'
        ret += 'type: %s\n' % self.type_name
        ret += 'power: %s\n' % (self.GetPower() and 'on' or 'off')
        ret += 'state: %s\n' % state.get(self.state,'unknown (%s)' % self.state)
        ret += 'udi: %s\n' % self.udi
        ret += 'sys path: %s\n' % self.path
        return ret

    def GetPower(self):
        return self._killswitch.GetPower()

    def SetPower(self, state):
        if self.state<2:
            r = self._killswitch.SetPower(state)
            self.state = int(open(self.path + '/state').read().strip())
            return r
        else:
            return False

class DeviceManager(object):
    def __init__(self, state_updater = None):
        self.parent_state_updater = state_updater
        self._bus = dbus.SystemBus()
        hal_obj = self._bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
        self._hal = dbus.Interface(hal_obj,"org.freedesktop.Hal.Manager")
        self._bus.add_signal_receiver(self.gdl_changed,
                                      "DeviceAdded",
                                      "org.freedesktop.Hal.Manager",
                                      "org.freedesktop.Hal",
                                      "/org/freedesktop/Hal/Manager",
                                      member_keyword='member')
        self._bus.add_signal_receiver(self.gdl_changed,
                                      "DeviceRemoved",
                                      "org.freedesktop.Hal.Manager",
                                      "org.freedesktop.Hal",
                                      "/org/freedesktop/Hal/Manager",
                                      member_keyword='member')

    def find_device(self, capability):
        for udi in self._hal.FindDeviceByCapability(capability):
            yield udi

    def get_killswitch_devices(self):
        devices = []
        for udi in self.find_device(capability='killswitch'):
            devices.append(_HALKillSwitchDevice(self._bus, udi))
        return devices

    def gdl_changed(self, *args, **kwargs):
        member = kwargs.get('member',None)
        mm = {'DeviceAdded': HAL_DEVICE_ADD,
              'DeviceRemoved': HAL_DEVICE_REMOVE}
        [device_udi] = args
        if self.parent_state_updater:
            self.parent_state_updater(device_udi, mm[member])
        else:
            print "\n%s, udi=%s"%(member, device_udi)

if __name__ == '__main__':
    dm = DeviceManager()
    devices = dm.get_killswitch_devices()
    for dev in devices:
        print dev