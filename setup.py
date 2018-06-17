#!/usr/bin/env python

from distutils.core import setup

setup(name='BTLE Broker',
      version='0.1.0',
      description='Broker for MQTT and BTLE',
      author='Stuart B. Wilkins',
      author_email='stuwilkins@mac.com',
      packages=['BTLEBroker'],
      scripts=['scripts/mqtt_broker',
               'scripts/keen_broker',
               'scripts/set_bt_time',
               'scripts/pool_controller',
               'scripts/wunderground'],
      data_files=[('/etc/systemd/system', ['config/pool_controller.service',
                                           'config/weather_station.service',
                                           'config/keen.service',
                                           'config/wunderground.service']),
                  ('/etc/BTLEBroker',     ['config/keen_setup.yaml',
                                           'config/bluetooth_setup.yaml',
                                           'config/auth.yaml',
                                           'config/wunderground.yaml'])]
      )
