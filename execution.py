import argparse
import sys
import signal
import subprocess
import ptrace.debugger as debugger
import ptrace
from mutation_engine import mutate
import time
import threading

# total number of runs
NUM_OF_RUNS = 10000

# total number of cases
cases = 0

# start time
start = time.time()

# parser configuration
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
    # pid = debugger.child.createChild(cmd, no_stdout=True, env=None)
    p = subprocess.Popen(cmd, stdout=False, shell=True)
    pid = p.pid
    try:
        process = dbg.addProcess(pid, is_attached=False)
        process.cont()
        sig = process.waitSignals()
        dbg.deleteProcess(process, pid)
    except:
        return
    if sig.signum == signal.SIGSEGV:
        process.detach()
        with open("crashes/crash.{}.jpg".format(i), "wb+") as fh:
            fh.write(data)


def fuzz_loop():
    global cases, start
    dbg = ptrace.debugger.PtraceDebugger()

    while True:
        cases += 1
        data = create_mutation()
        execute_fuzz(dbg, data, cases)
        elapsed = time.time() - start

        rate = cases / elapsed
        if cases % 10 == 0:
            min_elapsed = int(elapsed // 60)
            sec_elapsed = int(elapsed) % 60
            sys.stdout.write('\r' + f"[{min_elapsed} mins :{sec_elapsed} secs] case [{cases:10}] | {rate:10.2f} cps |"
                                    f" {threading.activeCount()} threads")


def fuzz():
    global start, cases
    fuzz_loop()
    # for i in range(4):
    #     threading.Thread(target=fuzz_loop).start()


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
