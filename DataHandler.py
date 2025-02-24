import logging
import os
import pickle
import re

import orjson
import requests

from Config import config
from Operator import Operator

cached_ETag: str
recruitable: frozenset[Operator]
tags: frozenset[str]

name_fixes: dict[str, str] = {"Justice Knight": "'Justice Knight'"}


def read_data():
    global cached_ETag, recruitable, tags

    with open(os.path.join(config.data_dir_path, "cached_ETag.txt")) as file:
        cached_ETag = file.read()

    recruitable_file_path = os.path.join(config.data_dir_path, "recruitable.pickle")
    recruitable = pickle.load(open(recruitable_file_path, "rb"))

    tags_file_path = os.path.join(config.data_dir_path, "tags.pickle")
    tags = pickle.load(open(tags_file_path, "rb"))


def write_data():
    cached_ETag_file_path = os.path.join(config.data_dir_path, "cached_ETag.txt")
    with open(cached_ETag_file_path, "w") as file:
        file.write(cached_ETag)

    recruitable_file_path = os.path.join(config.data_dir_path, "recruitable.pickle")
    if not os.path.exists(recruitable_file_path):
        # noinspection PyTypeChecker
        pickle.dump(recruitable, open(recruitable_file_path, "wb"))

    tags_file_path = os.path.join(config.data_dir_path, "tags.pickle")
    if not os.path.exists(tags_file_path):
        # noinspection PyTypeChecker
        pickle.dump(tags, open(tags_file_path, "wb"))


def check_update() -> tuple[bool, requests.Response | None]:
    # gacha_table_response = requests.get(
    #     "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/refs/heads/main/en_US/gamedata/excel/gacha_table.json",
    #     headers={"If-None-Match": cached_ETag},
    # )
    gacha_table_response = pickle.load(open("response0.resp", "rb"))

    if cached_ETag != gacha_table_response.headers["ETag"]:
        return True, gacha_table_response
    else:
        return False, None


def update_data(gacha_table_response: requests.Response):
    global cached_ETag, recruitable, tags

    # TODO actually cache
    # cached_ETag = gacha_table_response.headers["ETag"]

    recruitable_names = parse_recruitable_names(
        orjson.loads(gacha_table_response.text)["recruitDetail"]
    )
    # operator_details_response = requests.get(
    #     "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/refs/heads/main/en_US/gamedata/excel/character_table.json",
    # )
    operator_details_response = pickle.load(open("response.resp", "rb"))

    recruitable = get_operator_details(
        recruitable_names, orjson.loads(operator_details_response.text)
    )

    tags = parse_tags(orjson.loads(gacha_table_response.text)["gachaTags"])


def parse_recruitable_names(recruit_detail_str: str) -> tuple[str, ...]:
    recruit_detail_str = recruit_detail_str[recruit_detail_str.index("★") :]
    recruit_detail_str = re.sub(
        "<[^>]+>|★+|--------------------", "", recruit_detail_str
    )
    recruit_detail_str = re.sub("\n", " / ", recruit_detail_str)
    recruitable_names = re.findall("[^/ ][^/]+[^ /]", recruit_detail_str)

    return tuple(fix_operator_names(recruitable_names))


# YoStar, I SWEAR to fucking GOD
def fix_operator_names(recruitable_names: list[str]):
    for index, name in enumerate(recruitable_names):
        try:
            recruitable_names[index] = name_fixes[name]
        except KeyError:
            continue

    return recruitable_names


def get_operator_details(
    recruitable_names: tuple[str, ...], operator_details: dict[str, dict]
) -> frozenset[Operator]:
    recruitable_set = set()
    for name in recruitable_names:
        for code_name, details in operator_details.items():
            if details["name"] == name:
                rarity = int(details["rarity"][-1:])
                if rarity == 5:
                    details["tagList"].append("Senior Operator")
                elif rarity == 6:
                    details["tagList"].append("Top Operator")

                recruitable_set.add(
                    Operator(
                        name,
                        frozenset(details["tagList"]),
                        rarity,
                        code_name,
                    )
                )
                break

    if len(recruitable_names) != len(recruitable_set):
        logging.warning(
            f"{len(recruitable_names) - len(recruitable_set)} operators could not be parsed successfully"
        )
        logging.warning(
            "You can fix this by manually adding a name correction near the top of the DataHandler.py file"
        )
        logging.warning(
            "The incorrect name goes on the left, do not forget a comma at the end of every line"
        )
        logging.warning("Incorrect operator names:")
        for operator in set(recruitable_names).difference(
            set([operator.name for operator in recruitable_set])
        ):
            logging.warning(operator)

    return frozenset(recruitable_set)


def parse_tags(tags_str: list[dict[str, str]]) -> frozenset[str]:
    return frozenset([tag_entry["tagName"] for tag_entry in tags_str])
