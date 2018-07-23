#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
        requirements = f.read().splitlines()

service_files = [ 'config/wunderground.service']

config_files = ['config/wunderground.yaml']

setup(name='BTLE Broker',
      version='0.1.0',
      description='Broker for MQTT and BTLE',
      author='Stuart B. Wilkins',
      author_email='stuwilkins@mac.com',
      packages=['BTLEBroker'],
      entry_points = {
          'console_scripts': [
              'neurio_broker=BTLEBroker.cmdline:neurio_broker_main',
              'wunderground=BTLEBroker.cmdline:wunderground_main']
      },
      data_files=[('/etc/systemd/system', service_files),
                  ('/etc/BTLEBroker', config_files)],
      install_requires=requirements
      )
