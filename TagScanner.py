import os
from collections.abc import Collection

from Classes import Config, Data
from RecruitmentHandler import compute_results, print_results, rank_results
from Setup import setup


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def process_recruitment(config: Config, data: Data, tags: Collection[str]):
    tags = [tag.lower().strip() for tag in tags if tag != ""]
    clear()

    results = compute_results(data, tags)
    ranked_results, best_result = rank_results(data, results, config)
    print_results(data, ranked_results, best_result)


def main():
    config, data_handler = setup()

    while True:
        tags = input(
            'Enter tags separated with a comma, enter "exit" or "quit" to quit:\n? '
        ).split(",")

        if any([tag.lower() == "exit" or tag.lower() == "quit" for tag in tags]):
            break

        process_recruitment(config, data_handler.data, tags)

    # TODO: test more
    # TODO: check for edge cases


if __name__ == "__main__":
    main()
