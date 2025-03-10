import orjson
from orjson.orjson import OPT_INDENT_2

from Classes import Config

config = Config()


def write_default_config():
    with open("./config.json", "wb") as file:
        file.write(orjson.dumps(vars(config), option=OPT_INDENT_2))


def read_config():
    global config
    try:
        with open("./config.json", "rb") as file:
            config = Config(**orjson.loads(file.read()))
    except FileNotFoundError:
        config = Config()
        write_default_config()
