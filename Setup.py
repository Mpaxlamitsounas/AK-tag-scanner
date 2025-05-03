import os

from Classes import Config
from DataHandler import DataHandler


def initial_setup(data_dir_path: str):
    if not os.path.exists(data_dir_path):
        os.mkdir(data_dir_path)


def setup():
    config = Config()
    initial_setup(config.data_dir_path)
    config.read_config()
    data_handler = DataHandler()
    data_handler.read_data(config.data_dir_path)

    update_needed, gacha_table_response = data_handler.check_update()
    if update_needed:
        data_handler.update_data(gacha_table_response)
        data_handler.compute_base_tag_results()
        data_handler.write_updated_data(config.data_dir_path)

    return config, data_handler
