import logging
from collections.abc import Collection, Iterable
from copy import copy
from itertools import combinations

from Classes import Config, Data, Operator, RecruitResult


def compute_result_rarities(
    operators: Iterable[Operator],
) -> tuple[int, dict[int, int]]:
    rarity = 0
    rarities = dict.fromkeys(range(1, 6 + 1), 0)

    for operator in operators:
        rarities[operator.rarity] += 1

        if rarity == 0:
            rarity = operator.rarity

        if operator.rarity == 3:
            rarity = 3
            continue

        if rarity != operator.rarity:
            if operator.rarity in (1, 2):
                continue

            if rarity < 3:
                rarity = operator.rarity

            rarity = min(rarity, operator.rarity)

    return rarity, rarities


def count_duplicates(results: Iterable[RecruitResult]) -> int:
    duplicate_count = 0
    results_copy = list(copy(results))
    for cur_result in copy(results):
        results_copy.remove(cur_result)
        if any([cur_result.operators == result.operators for result in results_copy]):
            duplicate_count += 1

    return duplicate_count


def compute_result(data: Data, tags: Iterable[str]) -> RecruitResult | None:
    possible_operators = data.recruitable_operators.copy()
    for tag in tags:
        if tag not in data.recruitment_tags:
            logging.warning(f'Unrecognised tag: "{tag}", expect incomplete results.')
            return None

        possible_operators &= data.tag_results[tag]

        # early exit
        if len(possible_operators) == 0:
            return None

    if "top operator" not in tags:
        possible_operators = [
            operator for operator in possible_operators if operator.rarity != 6
        ]

    if len(possible_operators) == 0:
        return None

    return RecruitResult(
        frozenset(tags),
        possible_operators,
        *compute_result_rarities(possible_operators),
    )


def compute_results(data: Data, tags: Iterable[str]) -> list[RecruitResult]:
    tag_combinations: list[frozenset[str]] = [frozenset()]
    for combination_length in range(1, 6 + 1):
        tag_combinations.extend(
            [
                frozenset(combination)
                for combination in combinations(tags, combination_length)
            ]
        )

    results = [
        compute_result(data, tag_combination) for tag_combination in tag_combinations
    ]
    return [result for result in results if result is not None]


def rank_results(
    data: Data, results: Collection[RecruitResult], config: Config = Config()
) -> tuple[list[RecruitResult], RecruitResult | None]:
    if len(results) == 0:
        return [], None

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

    special_results.sort(key=lambda x: (x.rarity, -len(x.operators)), reverse=True)
    regular_results.sort(key=lambda x: (x.rarity, -len(x.operators)), reverse=True)

    special_count = len(special_results) - count_duplicates(special_results)

    if special_count != 0:
        return (
            special_results + regular_results,
            (special_results[0] if special_count == 1 else None),
        )

    max_rarity = regular_results[0].rarity

    if max_rarity == 3:
        return regular_results, compute_result(data, frozenset())

    if max_rarity == 4:
        rarity_results = [result for result in results if result.rarity == 4]
        if len(rarity_results) == 1:
            return regular_results, rarity_results[0]

        if config.automatically_select_4stars:
            return (
                regular_results,
                max(rarity_results, key=lambda x: x.operator_rarities[5]),
            )
        else:
            return regular_results, None


def print_results(
    data: Data, results: Collection[RecruitResult], best: RecruitResult | None
):
    if best is None:
        print("Could not pick a best result.")
    else:
        print("Best result:")
        print(f"{best.rarity}★ combination, Tags: [", end="")
        print(
            *[data.cased_recruitment_tag_lookup[tag] for tag in best.tags],
            sep=", ",
            end="], Operators:\n\t[",
        )
        print(
            *[f"{op.name}: {str(op.rarity)}★" for op in best.get_sorted_operators()],
            sep=", ",
            end="]\n",
        )

    print()
    print("Results:")
    for result in results:
        print(f"{result.rarity}★ combination, Tags: [", end="")
        print(
            *[data.cased_recruitment_tag_lookup[tag] for tag in result.tags],
            sep=", ",
            end="], Operators:\n\t[",
        )
        print(
            *[f"{op.name}: {str(op.rarity)}★" for op in result.get_sorted_operators()],
            sep=", ",
            end="]\n",
        )

    print()
