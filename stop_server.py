#!/usr/bin/env python3

import subprocess

from functions import get_pids_in_port
from functions import ntfy_client

SIGNAL = "SIGTERM"

def do_reboot():
    args_kill = ["sudo", "kill", f"-{SIGNAL}"]
    #  args_kill = ["sudo", "kill", "-9"]

    pid_list = get_pids_in_port(port=8000)

    subprocess.run(args_kill + pid_list)

    return pid_list

if __name__ == "__main__":
    pid_list = do_reboot()
    pids = ", ".join(pid_list)
    message = f"pids: {pids}"
    print(message)
    ntfy_client(message=message, title="server stopped", priority="low")
