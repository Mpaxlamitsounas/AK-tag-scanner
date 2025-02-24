from dataclasses import dataclass

import orjson


@dataclass
class Config:  # filled with default values
    data_dir_path: str = "data/"
    log_level: int = 1


config = Config()


def read_config():
    with open("./config.json", "rb") as file:
        global config
        config = Config(**orjson.loads(file.read()))


def write_config():
    with open("./config.json", "wb") as file:
        file.write(orjson.dumps(vars(config)))
