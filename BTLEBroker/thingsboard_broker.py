import yaml
import struct
import datetime
import time
import json
import urllib.request
import paho.mqtt.client as mqtt


def on_message(client_in, userdata, msg):
    _data = userdata['devices out'][msg.topic]

    if 'update period' in _data:
        if 'last update' in _data:
            diff = time.time() - _data['last update']
            if diff < _data['update period']:
                return

    _data['last update'] = time.time()
    _offset = _data.get('time offset', 0)
    _timestamp = struct.unpack('>l', msg.payload[0:4])[0]
    _meas = struct.unpack('>l', msg.payload[4:])[0]

    if 'factor' in _data:
        _meas = float(_meas) / _data['factor']
    if 'enum' in _data:
        _meas = _data['enum'][_meas]

    print('Topic {} has value {} at timestamp {}'.format(msg.topic, _meas,
                                                         hex(_timestamp)))

    url = userdata['thingsboard']['url'] + "/api/v1/"
    url += userdata['thingsboard']['token'][_data['device']]
    url += "/telemetry"
    req = urllib.request.Request(url)
    req.add_header('Content-Type','application/json')

    data = dict()
    data['ts'] = _timestamp * 1000
    data['values'] = dict()
    data['values'][_data['topic']] = _meas
    jsondata = json.dumps(data)

    response = urllib.request.urlopen(req,jsondata.encode('utf-8'))


def on_connect(client_in, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for topic, data in userdata['devices out'].items():
        client_in.subscribe(topic, qos=1)
        print("Subscribing to topic {}".format(topic))


def main(config):

    client_in = mqtt.Client(userdata=config)
    client_in.on_message = on_message
    client_in.on_connect = on_connect
    client_in.connect(config['mqtt']['host'], config['mqtt']['port'], 60)

    config['client_in'] = client_in

    client_in.loop_forever()
