import os

from RecruitmentHandler import compute_results, print_results, rank_results
from Setup import setup


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    setup()

    while True:
        tags = input(
            'Enter tags separated with a comma, enter "exit" to quit:\n? '
        ).split(",")
        tags = [tag.lower().strip() for tag in tags if tag != ""]
        clear()
        if len(tags) > 0 and (tags[0] == "exit" or tags[0] == "quit"):
            break

        results = compute_results(tags)
        ranked_results, best_result = rank_results(results)
        print_results(ranked_results, best_result)

    # TODO: test more
    # TODO: check for edge cases


if __name__ == "__main__":
    main()
