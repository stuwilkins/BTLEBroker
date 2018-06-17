import time
import datetime
import struct
from bluepy import btle

def set_pump(ctrl_mac, val):
    print("Connecting to controller {}".format(ctrl_mac))

    p = btle.Peripheral(ctrl_mac, 'random')
    service = p.getServiceByUUID('036451ed-6956-41ae-9840-5aca6c150ec7')
    read_char = service.getCharacteristics('00001010-0000-1000-8000-00805f9b34fb')
    write_char = service.getCharacteristics('00001011-0000-1000-8000-00805f9b34fb')

    read_char = read_char[0]
    write_char = write_char[0]

    write_char.write(struct.pack('B', val), withResponse=True);

    print("Sleep 30 seconds for controller")
    time.sleep(30)
    print("Reading Controller")

    pump_speed = struct.unpack('>q', read_char.read())[0]
    pump_speed = pump_speed & 0xFFFF

    print("Pump is running at {} rpm".format(pump_speed))

if __name__ == "__main__":
    set_pump('C1:49:4B:B4:61:17', 4)
