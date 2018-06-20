import yaml
import struct
import datetime
import time
import paho.mqtt.client as mqtt


def on_message(client_in, userdata, msg):
    _data = userdata['devices'][msg.topic]

    if 'last update' in _data:
        diff = time.time() - _data['last update']
        if diff < _data['update period']:
            #print("Skipping {} due to update frequency {}".format(
            #    msg.topic, diff))
            return

    _data['last update'] = time.time()
    _offset = _data.get('time offset', 0)
    _val = struct.unpack('>q', msg.payload)
    _meas = _val[0] & 0xFFFFFFFF
    _timestamp = _val[0] >> 32

    if 'factor' in _data:
        _meas = float(_meas) / _data['factor']

    print('Topic {} has value {} at timestamp {}'.format(msg.topic, _meas, hex(_timestamp)))

    if 'client_out' in userdata:
        client_out = userdata['client_out']
        client_out.publish(_data['topic'], str(_meas))
        print('Published to {} from topic {} value {}'.format(_data['topic'],
                                                              msg.topic,
                                                              str(_meas)))

def on_connect(client_in, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for topic, data in userdata['devices'].items():
        client_in.subscribe(topic, qos=1)
        print("Subscribing to topic {}".format(topic))


def main(config):

    client_in = mqtt.Client(userdata=config)
    client_in.on_message = on_message
    client_in.on_connect = on_connect
    client_in.connect(config['mqtt']['host'], config['mqtt']['port'], 60)

    client_out = mqtt.Client()
    client_out.username_pw_set(config['adafruit']['username'],
                               config['adafruit']['key'])
    client_out.connect(config['adafruit']['host'], config['adafruit']['port'],
                       60)

    config['client_in'] = client_in
    config['client_out'] = client_out


    client_in.loop_forever()
