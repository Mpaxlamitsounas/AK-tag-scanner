import logging
import os
import pickle
import re

import orjson
import requests

from Classes import Operator, RecruitResult
from Config import config

operator_name_fixes: dict[str, str] = {"Justice Knight": "'Justice Knight'"}

cached_ETag: str
recruitable_operators: frozenset[Operator]
recruitment_tags: frozenset[str]
computed_results: dict[frozenset[str], RecruitResult]


def read_data():
    global cached_ETag, recruitable_operators, recruitment_tags, computed_results

    try:
        with open(os.path.join(config.data_dir_path, "cached_ETag.txt")) as file:
            cached_ETag = file.read()
    except FileNotFoundError:
        cached_ETag = ""

    try:
        recruitable_file_path = os.path.join(
            config.data_dir_path, "recruitable_operators.pickle"
        )
        recruitable_operators = pickle.load(open(recruitable_file_path, "rb"))
    except FileNotFoundError:
        recruitable_operators = frozenset()

    try:
        tags_file_path = os.path.join(config.data_dir_path, "recruitment_tags.pickle")
        recruitment_tags = pickle.load(open(tags_file_path, "rb"))
    except FileNotFoundError:
        recruitment_tags = frozenset()

    try:
        computed_combinations_file_path = os.path.join(
            config.data_dir_path, "computed_tag_combinations.pickle"
        )
        computed_results = pickle.load(open(computed_combinations_file_path, "rb"))
    except FileNotFoundError:
        computed_results = {}


def write_updated_data():
    # noinspection PyPep8Naming
    cached_ETag_file_path = os.path.join(config.data_dir_path, "cached_ETag.txt")
    with open(cached_ETag_file_path, "w") as file:
        file.write(cached_ETag)

    recruitable_file_path = os.path.join(
        config.data_dir_path, "recruitable_operators.pickle"
    )
    # noinspection PyTypeChecker
    pickle.dump(recruitable_operators, open(recruitable_file_path, "wb"))

    tags_file_path = os.path.join(config.data_dir_path, "recruitment_tags.pickle")
    # noinspection PyTypeChecker
    pickle.dump(recruitment_tags, open(tags_file_path, "wb"))


def write_computed_combinations():
    computed_tag_combinations_file_path = os.path.join(
        config.data_dir_path, "computed_tag_combinations.pickle"
    )
    # noinspection PyTypeChecker
    pickle.dump(computed_results, open(computed_tag_combinations_file_path, "wb"))


# Pray YoStar doesn't change formatting
def parse_recruitable_operator_names(recruit_detail_str: str) -> list[str]:
    recruit_detail_str = recruit_detail_str[recruit_detail_str.index("★") :]
    recruit_detail_str = re.sub(
        "<[^>]+>|★+|--------------------", "", recruit_detail_str
    )
    recruit_detail_str = re.sub("\n", " / ", recruit_detail_str)
    recruitable_names = re.findall("[^/ ][^/]+[^ /]", recruit_detail_str)

    return recruitable_names


def parse_tags(tags_str: list[dict[str, str]]) -> frozenset[str]:
    return frozenset([tag_entry["tagName"] for tag_entry in tags_str])


def get_special_tags(rarity: int, position: str, profession: str) -> list[str]:
    extra_tags: list[str] = []
    match rarity:
        case 1:
            extra_tags.append("Robot")
        case 2:
            extra_tags.append("Starter")
        case 5:
            extra_tags.append("Senior Operator")
        case 6:
            extra_tags.append("Top Operator")
        case _:
            pass

    match position:
        case "MELEE":
            extra_tags.append("Melee")
        case "RANGED":
            extra_tags.append("Ranged")

    match profession:
        case "PIONEER":
            extra_tags.append("Vanguard")
        case "WARRIOR":
            extra_tags.append("Guard")
        case "TANK":
            extra_tags.append("Defender")
        case "SNIPER":
            extra_tags.append("Sniper")
        case "CASTER":
            extra_tags.append("Caster")
        case "MEDIC":
            extra_tags.append("Medic")
        case "SUPPORT":
            extra_tags.append("Supporter")
        case "SPECIAL":
            extra_tags.append("Specialist")

    return extra_tags


def parse_recruitable_operators(
    recruitable_operator_names: list[str], operator_details: dict[str, dict]
) -> frozenset[Operator]:
    operators: set[Operator] = set()
    for code_name, details in operator_details.items():
        if len(operators) == len(recruitable_operator_names):
            break

        if details["name"] in recruitable_operator_names:
            try:
                rarity = int(details["rarity"][-1:])
                operators.add(
                    Operator(
                        details["name"],
                        frozenset(
                            details["tagList"]
                            + get_special_tags(
                                rarity, details["position"], details["profession"]
                            )
                        ),
                        rarity,
                    )
                )
            except TypeError:
                continue

    if len(recruitable_operator_names) != len(operators):
        logging.warning(
            f"{len(recruitable_operator_names) - len(operators)} operators could not be parsed successfully"
            + "You can fix this by manually adding a name correction near the top of the DataHandler.py file"
            + "The incorrect name goes on the left, do not forget a comma at the end of every line"
            + "Incorrect operator names:"
        )
        for operator in set(recruitable_operator_names).difference(
            set([operator.name for operator in operators])
        ):
            logging.warning(operator)

    return frozenset(operators)


# YoStar, I SWEAR to fucking GOD
def fix_operator_names(operator_names: list[str]):
    for index, name in enumerate(operator_names):
        try:
            operator_names[index] = operator_name_fixes[name]
        except KeyError:
            continue

    return operator_names


def update_data(
    gacha_table_response: requests.Response,
) -> tuple[frozenset[Operator], frozenset[str]]:
    global cached_ETag, recruitable_operators, recruitment_tags

    # TODO actually cache
    # cached_ETag = gacha_table_response.headers["ETag"]

    recruitable_operator_names = parse_recruitable_operator_names(
        orjson.loads(gacha_table_response.text)["recruitDetail"]
    )
    recruitable_operator_names = fix_operator_names(recruitable_operator_names)

    # operator_details_response = requests.get(
    #     "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/refs/heads/main/en_US/gamedata/excel/character_table.json",
    # )
    operator_details_response = pickle.load(open("response.resp", "rb"))

    old_recruitable_operators = recruitable_operators.copy()
    recruitable_operators = parse_recruitable_operators(
        recruitable_operator_names, orjson.loads(operator_details_response.text)
    )

    old_recruitment_tags = recruitment_tags.copy()
    recruitment_tags = parse_tags(orjson.loads(gacha_table_response.text)["gachaTags"])

    return old_recruitable_operators, old_recruitment_tags


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
