import yaml
import struct
import keen
import datetime
import time
import paho.mqtt.client as mqtt


def on_message(client, userdata, msg):
    _data = userdata[msg.topic]

    if 'last update' in _data:
        diff = time.time() - _data['last update']
        if diff < _data['update period']:
            #print("Skipping {} due to update frequency {}".format(
            #    msg.topic, diff))
            return

    _data['last update'] = time.time()
    _offset = _data.get('time offset', 0)
    _timestamp = struct.unpack('>I', msg.payload[0:4])[0]
    _meas = struct.unpack('>i', msg.payload[4:8])[0]

    if 'factor' in _data:
        _meas = float(_meas) / _data['factor']

    print('Topic {} has value {} at timestamp {}'.format(msg.topic, _meas, hex(_timestamp)))

    event = dict()
    event['keen'] = {'timestamp': datetime.datetime.utcfromtimestamp(_timestamp + _offset).isoformat()}
    event[_data['ev_name']] = _meas
    print(event)
    keen.add_event(_data['ev_collection'], event)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for topic, data in userdata.items():
        client.subscribe(topic, qos=1)
        print("Subscribing to topic {}".format(topic))


def main(config):
    keen.project_id = config['keen.io']['project_id']
    keen.write_key = config['keen.io']['write_key']
    keen.read_key = config['keen.io']['read_key']

    client = mqtt.Client(userdata=config['devices'])
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(config['mqtt']['host'], config['mqtt']['port'], 60)

    client.loop_forever()
