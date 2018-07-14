#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
        requirements = f.read().splitlines()

service_files = ['config/keen.service',
                 'config/thingsboard.service',
                 'config/thingsboard_pool.service',
                 'config/wunderground.service']

config_files = ['config/keen_setup.yaml',
                'config/bluetooth_setup.yaml',
                'config/auth.yaml',
                'config/neurio.yaml',
                'config/thingsboard_setup.yaml',
                'config/wunderground.yaml']

setup(name='BTLE Broker',
      version='0.1.0',
      description='Broker for MQTT and BTLE',
      author='Stuart B. Wilkins',
      author_email='stuwilkins@mac.com',
      packages=['BTLEBroker'],
      entry_points = {
          'console_scripts': [
              'adafruit_broker=BTLEBroker.cmdline:adafruit_broker_main',
              'neurio_broker=BTLEBroker.cmdline:neurio_broker_main',
              'thingsboard_broker=BTLEBroker.cmdline:thingsboard_broker_main',
              'thingsboard_broker_out=BTLEBroker.cmdline:thingsboard_broker_out_main',
              'keen_broker=BTLEBroker.cmdline:keen_broker_main',
              'mqtt_broker=BTLEBroker.cmdline:mqtt_broker_main',
              'wunderground=BTLEBroker.cmdline:wunderground_main',
              'set_bt_time=BTLEBroker.cmdline:set_bt_time_main']
      },
      data_files=[('/etc/systemd/system', service_files),
                  ('/etc/BTLEBroker', config_files)],
      install_requires=requirements
      )
