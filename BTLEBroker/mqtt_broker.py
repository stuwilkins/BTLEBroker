import time
import struct
from bluepy import btle
import paho.mqtt.client as mqtt
from optparse import OptionParser
import os


class BTLEDelegate(btle.DefaultDelegate):
    def __init__(self, cfg, mqtt_client=None, debug=False):
        btle.DefaultDelegate.__init__(self)
        self._cfg = cfg
        self._mqtt_client = mqtt_client
        self._debug = debug

    def handleNotification(self, cHandle, data):
        cfg = self._cfg[cHandle]
        topic = cfg['mqtt_topic']

        self._mqtt_client.publish(cfg['mqtt_topic'],
                                    data, retain=True)
        print('Published {} to topic {}'.format(str(data),
                                                topic))


def enable_notify(periferal, service_uuid, char_uuid):
    setup_data = b"\x01\x00"
    svc = periferal.getServiceByUUID(service_uuid)
    ch = svc.getCharacteristics(char_uuid)[0]
    notify_handle = ch.getHandle() + 1
    periferal.writeCharacteristic(notify_handle, setup_data,
                                  withResponse=True)
    return ch


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe('myhome/pool/pump_speed_sp')


def setup_mqtt(config):
    mqtt_client = mqtt.Client('mqtt_publisher_{}'.format(os.getpid()))
    mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(config['host'],
                        config['port'])
    return mqtt_client


def _connect(cfg, mqtt_client):
    address = cfg['address']
    services = cfg['services']

    try:
        print('Attempting to connect to host {}'.format(address))
        p = btle.Peripheral(address, "random")
    except btle.BTLEException:
        print("Failed to connect to host {}".format(address))
        return None

    print("Connected to {}".format(address))

    chars_dict = dict()
    for svname, service in services.items():
        for chname, ch in service['characteristics'].items():
            chdev = enable_notify(p, service['UUID'], ch['UUID'])
            print('Notification enabled on {} '
                  'for service {}'.format(ch['UUID'], service['UUID']))
            chars_dict[chdev.getHandle()] = ch
            print('Characteristic {} on service {} is registered as name \''
                  '{}\''.format(ch['UUID'], service['UUID'], ch['mqtt_topic']))

    p.setDelegate(BTLEDelegate(chars_dict, mqtt_client, True))

    return p


def connect(config, mqtt_client, name=None):
    clients = list()
    if name in config['clients']:
        client = _connect(config['clients'][name], mqtt_client)
    else:
        raise RuntimeError('Unable to find name {} in config file'.format(
                            name))

    return client


def poll(client, mqtt_client):
    try:
        client.waitForNotifications(1)
    except btle.BTLEException:
        return False

    mqtt_client.loop(timeout=0.1)

    return True


def main(config, name):
    mqtt_client = setup_mqtt(config['mqtt'])
    while True:
        client = connect(config, mqtt_client, name)
        if client is None:
            print("Failed to connect, retrying")
            time.sleep(5)
            continue

        while True:
            if poll(client, mqtt_client) is False:
                break
