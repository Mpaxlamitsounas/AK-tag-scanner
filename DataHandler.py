import logging
import os
import pickle
import re
from collections import defaultdict
from collections.abc import Collection, Mapping, MutableSequence

import orjson
import requests

from Classes import Operator
from Config import config

operator_name_fixes: dict[str, str] = {"Justice Knight": "'Justice Knight'"}

cached_ETag: str
recruitable_operators: frozenset[Operator]
recruitment_tags: frozenset[str]
cased_recruitment_tag_lookup: dict[str, str]
tag_results: dict[str, frozenset[Operator]]


def read_data():
    global cached_ETag, recruitable_operators, recruitment_tags, cased_recruitment_tag_lookup, tag_results

    files = [
        "cached_ETag.pickle",
        "recruitable_operators.pickle",
        "recruitment_tags.pickle",
        "cased_recruitment_tags.pickle",
        "tag_results.pickle",
    ]
    variables = ["", frozenset(), frozenset(), {}, {}]
    for index, file in enumerate(files):
        try:
            variables[index] = pickle.load(
                open(os.path.join(config.data_dir_path, file), "rb")
            )
        except FileNotFoundError:
            pass

    cached_ETag = variables[0]
    recruitable_operators = variables[1]
    recruitment_tags = variables[2]
    cased_recruitment_tag_lookup = variables[3]
    tag_results = variables[4]


def write_updated_data():
    files = [
        "cached_ETag.pickle",
        "recruitable_operators.pickle",
        "recruitment_tags.pickle",
        "cased_recruitment_tags.pickle",
        "tag_results.pickle",
    ]
    variables = [
        cached_ETag,
        recruitable_operators,
        recruitment_tags,
        cased_recruitment_tag_lookup,
        tag_results,
    ]
    for file, data in zip(files, variables):
        # noinspection PyTypeChecker
        pickle.dump(data, open(os.path.join(config.data_dir_path, file), "wb"))


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
            extra_tags.append("robot")
        case 2:
            extra_tags.append("starter")
        case 5:
            extra_tags.append("senior operator")
        case 6:
            extra_tags.append("top operator")
        case _:
            pass

    match position:
        case "MELEE":
            extra_tags.append("melee")
        case "RANGED":
            extra_tags.append("ranged")

    match profession:
        case "PIONEER":
            extra_tags.append("vanguard")
        case "WARRIOR":
            extra_tags.append("guard")
        case "TANK":
            extra_tags.append("defender")
        case "SNIPER":
            extra_tags.append("sniper")
        case "CASTER":
            extra_tags.append("caster")
        case "MEDIC":
            extra_tags.append("medic")
        case "SUPPORT":
            extra_tags.append("supporter")
        case "SPECIAL":
            extra_tags.append("specialist")

    return extra_tags


def parse_recruitable_operators(
    recruitable_operator_names: Collection[str],
    operator_details: Mapping[str, dict],
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
                        code_name,
                        details["name"],
                        frozenset(
                            [tag.lower() for tag in details["tagList"]]
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
def fix_operator_names(operator_names: MutableSequence[str]):
    for index, name in enumerate(operator_names):
        try:
            operator_names[index] = operator_name_fixes[name]
        except KeyError:
            continue

    return operator_names


def update_data(
    gacha_table_response: requests.Response,
):
    global cached_ETag, recruitable_operators, recruitment_tags, cased_recruitment_tag_lookup

    # TODO actually cache
    # cached_ETag = gacha_table_response.headers["ETag"]

    recruitable_operator_names = parse_recruitable_operator_names(
        orjson.loads(gacha_table_response.text)["recruitDetail"]
    )

    # operator_details_response = requests.get(
    #     "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/refs/heads/main/en_US/gamedata/excel/character_table.json",
    # )
    operator_details_response = pickle.load(open("response.resp", "rb"))

    recruitable_operator_names = fix_operator_names(recruitable_operator_names)
    recruitable_operators = parse_recruitable_operators(
        recruitable_operator_names, orjson.loads(operator_details_response.text)
    )

    special_tags = {
        "Robot",
        "Starter",
        "Senior Operator",
        "Top Operator",
        "Melee",
        "Ranged",
        "Vanguard",
        "Guard",
        "Defender",
        "Sniper",
        "Caster",
        "Medic",
        "Supporter",
        "Specialist",
    }
    cased_recruitment_tag_lookup = {
        tag.lower(): tag
        for tag in parse_tags(orjson.loads(gacha_table_response.text)["gachaTags"])
        | special_tags
    }
    recruitment_tags = frozenset(cased_recruitment_tag_lookup.keys())


def compute_base_tag_results():
    global tag_results
    tag_results_temp: dict[str, set] = defaultdict(set)

    for operator in recruitable_operators:
        for tag in operator.tags:
            tag_results_temp[tag].add(operator)

    for tag, result in tag_results_temp.items():
        tag_results[tag] = frozenset(result)


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
