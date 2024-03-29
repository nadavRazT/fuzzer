import time
import sys
import os


def print_data(cases, start, crashes):
    elapsed = time.time() - start
    min_elapsed = int(elapsed // 60)
    sec_elapsed = int(elapsed) % 60
    rate = cases / elapsed
    print(f"time elapsed : [{min_elapsed} mins :{sec_elapsed} secs]")
    print(f"number of fuzzes: {cases:10}")
    print(f"fuzz rate: {rate:10.2f} fuzzes per second")
    print(f"number of crashes: {crashes}")
    sys.stdout.write("\033[F" * 4)
    if(cases % 1000 == 0):
        os.system('clear')


def print_data_pycharm(cases, start, crashes):
    elapsed = time.time() - start
    min_elapsed = int(elapsed // 60)
    sec_elapsed = int(elapsed) % 60
    rate = cases / elapsed

    sys.stdout.write(
        f"\r fuzzes: [{cases}] | time: [{min_elapsed} mins :{sec_elapsed} secs] | rate: {rate:10.2f} FPS | crashes found: {crashes}")
    if(cases % 1000 == 0):
        os.system('clear')