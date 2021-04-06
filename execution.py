import argparse
import sys
import signal
import subprocess
import ptrace.debugger as debugger
import ptrace

NUM_OF_RUNS = 10

config = {
    "file": "data/test.jpg",
    "target": ""
}


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
        data = mutate()
        execute_fuzz(dbg, data,i)


def update_config(args):
    config["target"] = args.target


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", help="target program",
                        required=True)
    args = parser.parse_args()
    update_config(args)
    fuzz()


def mutate():
    return None

if __name__ == "__main__":
    main()
