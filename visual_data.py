import time
import sys


def print_data(cases, start):
    elapsed = time.time() - start
    min_elapsed = int(elapsed // 60)
    sec_elapsed = int(elapsed) % 60
    rate = cases / elapsed

    print(f"time elapsed : [{min_elapsed} mins :{sec_elapsed} secs]")
    print(f"number of fuzzes: {cases:10}")
    print(f"fuzz rate: {rate:10.2f} fuzzes per second")
    sys.stdout.write("\033[F" * 3)


def print_data_pycharm(cases, start):
    elapsed = time.time() - start
    min_elapsed = int(elapsed // 60)
    sec_elapsed = int(elapsed) % 60
    rate = cases / elapsed

    sys.stdout.write(f"\r fuzzes: [{cases}] | time: [{min_elapsed} mins :{sec_elapsed} secs] | rate: {rate:10.2f} FPS")

