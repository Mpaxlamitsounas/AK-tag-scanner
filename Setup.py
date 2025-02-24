import os
from Config import config, read_config, write_config


def setup():
    initial_setup()
    read_config()


def initial_setup():
    if not os.path.exists("./config.json"):
        write_config()

    if not os.path.exists(config.data_dir_path):
        os.mkdir(config.data_dir_path)
