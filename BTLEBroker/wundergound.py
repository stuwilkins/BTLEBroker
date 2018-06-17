import yaml
import struct
import datetime
import time
import paho.mqtt.client as mqtt
from urllib.request import urlopen
from urllib.parse import urlencode

#WU_URL = "http://weatherstation.wunderground.com/"
#WU_URL += "weatherstation/updateweatherstation.php"

WU_URL = "https://rtupdate.wunderground.com/"
WU_URL += "weatherstation/updateweatherstation.php"

config = {'myhome/weather/temperature':       {'update period': 0,
                                               'factor': 555.5555,
                                               'offset': 32,
                                               'wu_field': 'tempf'},
          'myhome/weather/humidity':          {'update period': 0,
                                               'factor': 1000,
                                               'wu_field': 'humidity'},
          'myhome/weather/pressure':          {'update period': 0,
                                               'factor': 33863.88667,
                                               'wu_field': 'baromin'},
          'myhome/weather/wind_direction':    {'update period': 0,
                                               'factor': 1000,
                                               'wu_field': 'winddir'},
          'myhome/weather/wind_speed':        {'update period': 0,
                                               'factor': 1000,
                                               'wu_field': 'windspeedmph'},
          'myhome/weather/rain_hour_curr':    {'update period': 0,
                                               'factor': 25400,
                                               'wu_field': 'rainin'},
          'myhome/weather/rain_day_curr':     {'update period': 0,
                                               'factor': 25400,
                                               'wu_field': 'dailyrainin'},
          'myhome/weather/wind_direction_2m': {'update period': 0,
                                               'factor': 25400,
                                               'wu_field': 'winddir_avg2m'},
          'myhome/weather/wind_speed_2m':     {'update period': 0,
                                               'factor': 1000,
                                               'wu_field': 'windspdmph_avg2m'},
          'myhome/weather/dew_point':         {'update period': 0,
                                               'factor': 555.5555,
                                               'offset': 32,
                                               'wu_field': 'dewptf'},
          'myhome/weather/wind_speed_gust_10m':{'update period': 0,
                                               'factor': 1000,
                                               'wu_field': 'windgustmph'},
          'myhome/weather/wind_direction_gust_10m': {'update period': 0,
                                                    'factor': 1000,
                                                    'wu_field': 'windgustdir'}}



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
    for _name, _data in data.items():
        print(_name)
        diff = datetime.datetime.now().timestamp() - _data['timestamp']
        if(diff < delay):
            wu_data[_data['wu_field']] = '{0:.2f}'.format((_data['value']))


    wu_header = {"action": "updateraw",
                 "dateutc": "now",
                 "realtime": "1",
                 "rtfreq": "2.5"}

    wu_data = {**wu_data, **wu_header}

    print(wu_data)

    if(update):
        upload_url = WU_URL + "?" + urlencode(wu_data)
        print(upload_url)
        response = urlopen(upload_url)
        html = response.read()
        print("Server response:", html)
        response.close()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for topic, data in userdata.items():
        client.subscribe(topic, qos=1)
        print("Subscribing to topic {}".format(topic))


client = mqtt.Client(userdata=config)
client.on_message = on_message
client.on_connect = on_connect
client.connect("192.168.1.2", 1883, 60)

client.loop_start()
while(1):
    time.sleep(2.5)
    print("Tick Tock ... ")
    update_wunderground(config, True, 120)
