import sys
import pdb
import os
import subprocess
import ptrace.debugger

def execute_fuzz():
    args = [sys.executable, '-c', 'import time; time.sleep(60)']
    child_popen = subprocess.Popen(args)
    pid = child_popen.pid
    debugger = ptrace.debugger.PtraceDebugger()
    process = debugger.addProcess(pid, False)
    # process is a PtraceProcess instance
    print("IP before: %#x" % process.getInstrPointer())


if __name__ == "__main__":
    execute_fuzz()
