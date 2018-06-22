import yaml
import struct
import datetime
import time
import paho.mqtt.client as mqtt
import pprint
from urllib.request import urlopen
from urllib.parse import urlencode


def on_message(client, userdata, msg):
    _data = userdata[msg.topic]

    if 'last update' in _data:
        diff = time.time() - _data['last update']
        if diff < _data['update period']:
            return

    _data['last update'] = time.time()
    _offset = _data.get('time offset', 0)
    _val = struct.unpack('>q', msg.payload)
    _meas = _val[0] & 0xFFFFFFFF
    _timestamp = _val[0] >> 32

    if 'factor' in _data:
        _meas = float(_meas) / _data['factor']

    if 'offset' in _data:
        _meas = float(_meas) + _data['offset']

    _data['value'] = _meas
    _data['timestamp'] = _timestamp

    print('Topic {} has value {} at timestamp {}'.format(msg.topic,
                                                         _meas,
                                                         hex(_timestamp)))


def update_wunderground(data, update, delay):
    wu_data = dict()
    for _name, _data in data['config'].items():
        diff = datetime.datetime.now().timestamp() - _data['timestamp']
        if((diff < delay) or (diff < (delay + 4*60*60))):
            wu_data[_data['wu_field']] = '{0:.2f}'.format((_data['value']))

    wu_header = {"action": "updateraw",
                 "dateutc": "now"}

    wu_data = {**wu_data, **wu_header, **data['wunderground']}

    if(update):
        pprint.pprint(wu_data)
        upload_url = data['url'] + "?" + urlencode(wu_data)
        response = urlopen(upload_url)
        html = response.read()
        response.close()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for topic, data in userdata.items():
        client.subscribe(topic, qos=1)
        print("Subscribing to topic {}".format(topic))

def main(config):

    client = mqtt.Client(userdata=config['config'])
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(config['mqtt']['host'], config['mqtt']['port'], 60)

    client.loop_start()
    while(1):
        time.sleep(2.5)
        update_wunderground(config, True, 240)
