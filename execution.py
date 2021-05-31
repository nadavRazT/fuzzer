import argparse
import sys
import signal
import subprocess
import ptrace.debugger as debugger
import ptrace
import threading
import time
import visual_data as vd
from Mutator import Mutator

NUM_OF_RUNS = 1

# total number of cases
cases = 0
crashes = 0

# start time
start = time.time()

# parser configuration
config = {
    "file": "data/mutated.jpg",
    "source": "data/test.jpg",
    "target": ""
}


def execute_fuzz(dbg, data, i):
    global crashes
    cmd = [config["target"], config["file"]]
    # pid = debugger.child.createChild(cmd, no_stdout=False, env=None)
    p = subprocess.Popen(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    pid = p.pid
    try:
        process = dbg.addProcess(pid, is_attached=False)
        process.cont()
        sig = dbg.waitProcessEvent()
        # sig = dbg.waitSignals()
        dbg.deleteProcess(process, pid)
    except:
        return
    if sig.signum == signal.SIGSEGV:
        crashes += 1
        with open("crashes/crash.{}.jpg".format(crashes), "wb+") as fh:
            fh.writelines(data)
    process.detach()


def fuzz():
    global cases, start, crashes
    dbg = ptrace.debugger.PtraceDebugger()
    mutator = Mutator(config)
    while True:
        cases += 1
        data = mutator.mutate()
        execute_fuzz(dbg, data, cases)

        if cases % 10 == 0:
            vd.print_data(cases, start, crashes)
            # vd.print_data_pycharm(cases, start, crashes)


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
    # fuzz_thread()
    fuzz()


if __name__ == "__main__":
    main()
