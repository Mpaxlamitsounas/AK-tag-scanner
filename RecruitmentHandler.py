import logging
import random
from collections import defaultdict
from itertools import combinations

# noinspection PyPep8Naming
import DataHandler as data
from Classes import Operator, RecruitResult
from Config import config

# TODO: test
def invalidate_updated_combinations(
    old_recruitable_operators: frozenset[Operator], old_recruitment_tags: frozenset[str]
):
    updated_tags: set[str] = set()
    for tag in data.recruitment_tags.symmetric_difference(old_recruitment_tags):
        updated_tags.add(tag)

    for operator in data.recruitable_operators.symmetric_difference(
        old_recruitable_operators
    ):
        updated_tags.update(operator.tags)

    for tag_combination in list(data.computed_results.keys()):
        if not tag_combination.isdisjoint(updated_tags):
            del data.computed_results[tag_combination]


def compute_result_rarity(operators: frozenset[Operator]) -> int:
    rarity = 0

    for operator in operators:
        if rarity == 0:
            rarity = operator.rarity

        if rarity != operator.rarity:
            return 0

    return rarity


def compute_base_tag_results():
    results: defaultdict[str, set[Operator]] = defaultdict(set)
    for operator in data.recruitable_operators:
        for tag in operator.tags:
            results[tag].add(operator)

    for tag, operators in results.items():
        tag = frozenset((tag,))
        data.computed_results[tag] = RecruitResult(
            tag, frozenset(operators), compute_result_rarity(frozenset(operators))
        )


def rank_results(
    results: list[RecruitResult],
) -> tuple[RecruitResult | None, list[RecruitResult]]:
    if len(results) == 0:
        return None, []

    special_results: list[RecruitResult] = []
    regular_results: list[RecruitResult] = []
    for result in results:
        if (
            any([result.rarity == 5, result.rarity == 6])
            or config.allow_robots
            and result.rarity == 1
        ):
            special_results.append(result)
        else:
            regular_results.append(result)

    if len(special_results) > 0:
        special_results.sort(key=lambda x: (x.rarity, -len(x.operators)))
    if len(regular_results) > 0:
        regular_results.sort(key=lambda x: (x.rarity, -len(x.operators)))

    if len(special_results) != 0:
        return (
            special_results[0] if len(special_results) == 1 else None
        ), special_results + regular_results

    max_rarity = regular_results[0].rarity

    matching_rarity = (0, 3)
    if max_rarity == 4:
        matching_rarity = (4,)
        if not config.randomly_select_4stars:
            return None, regular_results

    return (
        random.choice(
            [result for result in regular_results if result.rarity in matching_rarity]
        ),
        regular_results,
    )


def compute_result(tags: frozenset[str]) -> RecruitResult | None:
    possible_operators = data.recruitable_operators.copy()
    for tag in tags:
        if tag not in data.recruitment_tags:
            logging.warning(f'Unrecognised tag: ""{tag}"", expect incomplete results.')
            return None

        possible_operators = possible_operators.intersection(
            data.computed_results[frozenset((tag,))].operators
        )

        if len(possible_operators) == 0:
            return None

    if "Top Operator" not in tags:
        possible_operators = frozenset(
            [operator for operator in possible_operators if operator.rarity != 6]
        )

    return RecruitResult(
        tags, possible_operators, compute_result_rarity(possible_operators)
    )


def compute_results(tags: frozenset[str]) -> list[RecruitResult]:
    tag_combination_results: list[RecruitResult] = []

    tag_combinations: list[frozenset[str]] = []
    for combination_length in range(1, 6 + 1):
        tag_combinations.extend(
            [
                frozenset(combination)
                for combination in combinations(tags, combination_length)
            ]
        )

    for tag_combination in tag_combinations:
        if tag_combination not in data.computed_results:
            recruitment_result = compute_result(tag_combination)
            if recruitment_result is not None:
                data.computed_results[tag_combination] = recruitment_result
            else:
                continue

        tag_combination_results.append(data.computed_results[tag_combination])

    return tag_combination_results
