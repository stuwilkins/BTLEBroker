import neurio
import pprint


def setup_neurio(config):

    tp = neurio.TokenProvider(key=config['neurio']['client id'],
                              secret=config['neurio']['client secret'])
    nc = neurio.Client(token_provider=tp)
    user_info = nc.get_user_information()

    pp = pprint.PrettyPrinter(indent=4)
    ip_address = user_info['locations'][0]['sensors'][0]['ipAddress']

    sample = nc.get_samples_live_last(sensor_id='0x0000C47F51019C5A')
    pp.pprint(sample)

    sample = nc.get_local_current_sample(ip_address)

    pp.pprint(sample)


def main(config):
    setup_neurio(config)
