import os

from Config import config, read_config
from DataHandler import (
    check_update,
    compute_base_tag_results,
    read_data,
    update_data,
    write_updated_data,
)


def initial_setup():
    if not os.path.exists(config.data_dir_path):
        os.mkdir(config.data_dir_path)


def setup():
    initial_setup()
    read_config()
    read_data()

    update_needed, gacha_table_response = check_update()
    if update_needed:
        update_data(gacha_table_response)
        compute_base_tag_results()
        write_updated_data()
