import time
import datetime
import struct
from bluepy import btle

def settime(ctrl_mac):
    print("Connecting to controller {}".format(ctrl_mac))

    p = btle.Peripheral(ctrl_mac, 'random')
    service = p.getServiceByUUID('5d67af3f-b46e-4836-abfa-f7bffab6bceb')
    read_char = service.getCharacteristics('00002000-0000-1000-8000-00805f9b34fb')
    write_char = service.getCharacteristics('00002001-0000-1000-8000-00805f9b34fb')

    read_char = read_char[0]
    write_char = write_char[0]
    now = time.time()
    now_str = datetime.datetime.fromtimestamp(now).strftime('%c')
    write_char.write(struct.pack('>i', int(now)), withResponse=True);
    print("Set controller time to {}".format(now_str))

    print("Sleep 30 seconds for controller")
    time.sleep(30)
    print("Reading Controller")

    ctrl_time = struct.unpack('>i', read_char.read())[0]
    now = time.time()
    now_str = datetime.datetime.fromtimestamp(now).strftime('%c')
    ctrl_time_str = datetime.datetime.fromtimestamp(ctrl_time).strftime('%c')

    print("Controller now reports time as {} ({})".format(ctrl_time_str,
                                                          now_str))

if __name__ == "__main__":
    settime('C1:49:4B:B4:61:17')
