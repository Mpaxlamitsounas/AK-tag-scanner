import atexit

from DataHandler import write_computed_combinations
from RecruitmentHandler import compute_results, rank_results
from Setup import setup


def __exit():
    write_computed_combinations()


def main():
    atexit.register(__exit)
    setup()

    # TODO: test more
    results = compute_results(frozenset(["Ranged", "Melee"]))
    best, ranked_results = rank_results(results)
    print(len(ranked_results), best)
    for result in ranked_results:
        print(result.tags, result.get_sorted_operators())


if __name__ == "__main__":
    main()

    # cProfile.run("main()", sort="time")
    # arg1, arg2 = recruitable_operator_names, orjson.loads(operator_details_response.text)
    # time = timeit.timeit(
    #     "get_operator_details(arg1, arg2)",
    #     "from DataHandler import get_operator_details",
    #     number=1000,
    #     globals=locals(),
    # )
