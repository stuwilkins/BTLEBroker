from optparse import OptionParser
from BTLEBroker import config
from BTLEBroker import adafruit_broker

parser = OptionParser()
parser.add_option("-c", "--config", dest="config_file",
                help="yaml config file for setup", metavar="FILE")
parser.add_option("-a", "--auth", dest="auth_file",
                help="yaml config file for auth", metavar="FILE")


def keen_broker_main():
    from BTLEBroker import keen_broker
    (options, args) = parser.parse_args()
    cfg = config.read_config((options.config_file, options.auth_file))
    keen_broker.main(cfg)


def mqtt_broker_main():
    from BTLEBroker import mqtt_broker
    parser.add_option("-n", "--name", dest="name",
                    help="Name of device in yaml file", metavar="FILE")
    (options, args) = parser.parse_args()
    cfg = config.read_config((options.config_file, options.auth_file))
    mqtt_broker.main(cfg, options.name)


def wunderground_main():
    from BTLEBroker import wunderground
    (options, args) = parser.parse_args()
    cfg = config.read_config((options.config_file, options.auth_file))
    wunderground.main(cfg)


def adafruit_broker_main():
    from BTLEBroker import adafruit_broker
    (options, args) = parser.parse_args()
    cfg = config.read_config((options.config_file, options.auth_file))
    adafruit_broker.main(cfg)
