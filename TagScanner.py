from DataHandler import write_data
from Setup import setup
import cProfile


def main():
    setup()
    write_data()


if __name__ == "__main__":
    # main()
    cProfile.run("main()", sort="time")
