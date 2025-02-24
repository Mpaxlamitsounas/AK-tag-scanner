import orjson
from types import SimpleNamespace

config = SimpleNamespace(data_dir_path="data/", log_level=1, ETag="")


def read_config():
    with open("./config.json", "rb") as file:
        global config
        config = SimpleNamespace(**orjson.loads(file.read()))


def write_config():
    with open("./config.json", "wb") as file:
        file.write(orjson.dumps(vars(config)))
