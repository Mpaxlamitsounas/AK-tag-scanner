import requests
import json


class DataHandler:
    def __init__(self):

        r = requests.get(
            "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/refs/heads/main/en_US/gamedata/excel/gacha_table.json",
            headers={
                "If-None-Match": 'W/"933b81facafacd8eaddd474cedd9df33e62d79acf0a906b55612949267ee18a1"'
            },
        )
