from Config import config


def log(message: str, message_log_level: int):
    if config.log_level >= message_log_level:
        print(message)
