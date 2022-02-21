
"""
This module provides access to RUDAT attenuator.
Set attenuation by Rudat().set(value)
"""

class Rudat():

    def __init__(self):
        """
        Query USB bus for various RUDAT USB devices
        Return: Success(Tuple of Devices), Fail(Exception)
        """
        devices = []
        self._device = None
        # find all rudat USB devices
        # first generation usb devices
        found = usb.core.find(find_all=True, idVendor=0x20ce, idProduct=0x0023)

        # identify rudat usb devices
        for self._device in found:
            try:
                if (os.name == "posix") and (self._device.is_kernel_driver_active(0)):
                    self._device.detach_kernel_driver(0)
            except Exception as e:
                print(e)
                pass

        if self._device is None:
            raise Exception("Device not found")

        self._raw = bytearray(256)
        self._ep_in = self._device[0][(0, 0)][0]  # fixed HID read endpoint
        self._ep_out = self._device[0][(0, 0)][1]  # fixed HID write endpoint

    def model_name(self):
        data = [0] * 64
        data[0] = 40
        self._raw = []
        # print data
        self._device.write(self._ep_out, data)
        r = self._device.read(self._ep_in, 64)
        for i in range(1, 64):
            if r[i] == 0:
                break;
            self._raw.append(r[i])
        self._model = ''.join(chr(x) for x in self._raw)
        print("Model name: {self._model}")
        return self._model

    def serial_no(self):
        data = [0] * 64
        data[0] = 41
        self._raw = []
        # print data
        self._device.write(self._ep_out, data)
        r = self._device.read(self._ep_in, 64)
        for i in range(1, 64):
            if r[i] == 0:
                break;
            self._raw.append(r[i])
        self._serial_no = ''.join(chr(x) for x in self._raw)
        print(f"serial no: {self._serial_no}")
        return self._serial_no

    def _set(self, wt1, wt2):
        data = [0] * 64
        data[0] = 19
        data[1] = wt1
        data[2] = wt2
        self._device.write(self._ep_out, data)
        r = self._device.read(self._ep_in, 64)

    def read(self):
        data = [0] * 64
        data[0] = 18
        # print data
        self._device.write(self._ep_out, data)
        r = self._device.read(self._ep_in, 64)
        print(f"attenuation is  {float(r[1]) + (r[2] / float(4))} dB")

    def set(self, value):
        print(f"setting attenuation to {value} dB")
        if value > 95 or value < 0:
            raise Exception(f"attenuation value should be with in 0-95dB")
        wt1 = value * 100
        wt2 = (float(value) - int(value)) / .25
        self._set(int(value), int(wt2))

