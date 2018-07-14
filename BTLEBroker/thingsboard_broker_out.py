import json
import struct
import urllib.request
import paho.mqtt.client as mqtt
import os
from urllib.error import (HTTPError, URLError)


def request_response(config, token):

    url = config['thingsboard']['url']
    url += '/api/v1/'
    url += token
    url += '/rpc'

    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    else:
        _data = response.read().decode()
        data = json.loads(_data)
        return data

    return None


def parse_response(config, name, data):

    _config = config['devices in'][name]
    mqtt_client = config['mqtt_client']

    if data is None:
        return None

    if 'method' not in data:
        return None

    if data['method'] not in _config['commands']:
        return None

    _d = _config['commands'][data['method']]
    if _d['type'] == 'numeric':
        val = data['params']
        if 'factor' in _d:
            val = val * _d['factor']
        _b = struct.pack(_d['struct'], int(val))
    else:
        return None

    print("Publishing {} to topic {}".format(str(_b), _d['topic']))
    mqtt_client.publish(_d['topic'], _b, qos=2)


def on_connect(client_in, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def setup_mqtt(config, name):
    _config = config['mqtt']
    name = 'thingsboard_out_{}'.format(os.getpid())
    mqtt_client = mqtt.Client(name, userdata=config)
    #mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(_config['host'], _config['port'], 60)
    mqtt_client.loop_start()
    return mqtt_client


def main(config, name):
    device = config['devices in'][name]['device']
    token = config['thingsboard']['token'][device]

    mqtt_client = setup_mqtt(config, None)
    config['mqtt_client'] = mqtt_client

    while(1):
        data = request_response(config, token)
        parse_response(config, name, data)
