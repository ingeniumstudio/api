#!/usr/bin/env python

import subprocess


def do_reboot():
    args_ss = ["sudo", "ss", "-lptn", "sport = :8000"]
    args_kill = ["sudo", "kill", "-9"]

    ss_process = subprocess.run(args_ss, capture_output=True, text=True)

    pid_list = [pid.split('=')[1] for pid in ss_process.stdout.split(',')
                if pid.startswith("pid=")]

    for pid in sorted(pid_list):  # lesser pid first in list
        subprocess.run(args_kill + [pid])

    return ", ".join(pid_list)

if __name__ == "__main__":
    do_reboot()
