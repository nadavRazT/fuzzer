import argparse
import sys
import signal
import subprocess
import ptrace.debugger as debugger
import ptrace
from mutation_engine import mutate
import threading
import time
import visual_data as vd


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
    # pid = debugger.child.createChild(cmd, no_stdout=False, env=None)
    p = subprocess.Popen(cmd, stderr=False, stdout=subprocess.DEVNULL)
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


def fuzz():
    global cases, start
    dbg = ptrace.debugger.PtraceDebugger()

    while True:
        cases += 1
        data = create_mutation()
        execute_fuzz(dbg, data, cases)

        if cases % 10 == 0:
            vd.print_data(cases, start)
            # vd.print_data_pycharm(cases, start)


def fuzz_thread():
    global start, cases
    for i in range(4):
        threading.Thread(target=fuzz).start()


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
