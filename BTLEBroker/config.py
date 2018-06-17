import yaml


def read_config(cfg_files):
    config = dict();
    for f in cfg_files:
        with open(f, 'r') as yamlfile:
            config= {**config, **yaml.load(yamlfile)}

    return config

