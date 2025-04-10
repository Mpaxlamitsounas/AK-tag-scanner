import os
from collections.abc import Collection

from RecruitmentHandler import compute_results, print_results, rank_results
from Setup import setup


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def process_recruitment(tags: Collection[str]):
    tags = [tag.lower().strip() for tag in tags if tag != ""]
    clear()

    results = compute_results(tags)
    ranked_results, best_result = rank_results(results)
    print_results(ranked_results, best_result)


def main():
    setup()

    while True:
        tags = input(
            'Enter tags separated with a comma, enter "exit" to quit:\n? '
        ).split(",")

        if any([tag.lower() == "exit" or tag.lower() == "quit" for tag in tags]):
            break

        process_recruitment(tags)

    # TODO: test more
    # TODO: check for edge cases


if __name__ == "__main__":
    main()
