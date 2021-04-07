import argparse
import sys
import signal
import subprocess
import ptrace.debugger as debugger
import ptrace
from mutation_engine import mutate
import time

NUM_OF_RUNS = 10

config = {
    "file": "data/mutated.jpg",
    "source": "data/test.jpg",
    "target": ""
}

def create_mutation():
    with open(config["source"], "rb") as f:
        data = f.readlines()

    data = mutate(data)
    with open(config["file"], "wb") as f:
        f.writelines(data)
    return data


def execute_fuzz(dbg, data, i):
    cmd = [config["target"], config["file"]]
    pid = debugger.child.createChild(cmd, no_stdout=True, env=None)
    process = dbg.addProcess(pid, True)
    process.cont()
    try:
        sig = process.waitSignals()
    except:
        return

    if sig.signum == signal.SIGSEGV:
        process.detach()
        with open("crashes/crash.{}.jpg".format(i), "wb+") as fh:
            fh.write(data)


def fuzz():
    dbg = ptrace.debugger.PtraceDebugger()

    i = 0
    while NUM_OF_RUNS > i:
        i += 1
        # data = create_mutation()
        # execute_fuzz(dbg, data, i)
        print(i, end="\r")
        time.sleep(1)

def update_config(args):
    config["target"] = args.target


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", help="target program",
                        required=True)
    args = parser.parse_args()
    update_config(args)
    fuzz()


if __name__ == "__main__":
    main()
