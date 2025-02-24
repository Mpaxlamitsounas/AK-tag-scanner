import os
import pickle

from Config import config, read_config, write_config
from DataHandler import read_data, check_update, update_data


def setup():
    initial_setup()
    read_config()
    read_data()

    update_needed, gacha_table_response = check_update()
    if update_needed:
        update_data(gacha_table_response)


def initial_setup():
    if not os.path.exists("./config.json"):
        write_config()

    if not os.path.exists(config.data_dir_path):
        os.mkdir(config.data_dir_path)

    cached_ETag_file_path = os.path.join(config.data_dir_path, "cached_ETag.txt")
    if not os.path.exists(cached_ETag_file_path):
        with open(cached_ETag_file_path, "w") as file:
            pass

    recruitable_file_path = os.path.join(config.data_dir_path, "recruitable.pickle")
    if not os.path.exists(recruitable_file_path):
        # noinspection PyTypeChecker
        pickle.dump(frozenset([]), open(recruitable_file_path, "wb"))

    tags_file_path = os.path.join(config.data_dir_path, "tags.pickle")
    if not os.path.exists(tags_file_path):
        # noinspection PyTypeChecker
        pickle.dump(frozenset([]), open(tags_file_path, "wb"))
