#!/usr/bin/env python

import subprocess
import re
from pathlib import Path

specs = {}

os_cmd = "lsb_release -d".split()
cpu_cmd = "lscpu".split()
ram_cmd = "cat /proc/meminfo".split()
gpu_cmd = "lspci".split()


def run_cmd(info_cmd):
    try:
        pout = subprocess.run(info_cmd, text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        print("Error ocurred: " + err.stderr)
    if pout.stderr:
        return None
    else:
        return pout


def get_lin_os(os_cmd):
    if pout := run_cmd(os_cmd):
        return pout.stdout.strip().split("\t")[1]
    else:
        return "N/A"


def get_lin_cpu(cpu_cmd):
    if pout := run_cmd(cpu_cmd):
        return (
            [ln for ln in pout.stdout.split("\n") if re.search(r"Model name", ln)][0]
            .split(":")[1]
            .strip()
        )
    else:
        return "N/A"


def get_lin_gpu(gpu_cmd):
    if pout := run_cmd(gpu_cmd):
        return (
            [
                ln
                for ln in pout.stdout.split("\n")
                if re.search(r"VGA compatible controller", ln)
            ][0]
            .split(":")[2]
            .strip()
        )
    else:
        return "N/A"


def get_lin_mb():
    mb_vendor = Path("/sys/devices/virtual/dmi/id/board_vendor").read_text().strip()
    mb_name = Path("/sys/devices/virtual/dmi/id/board_name").read_text().strip()
    mb_version = Path("/sys/devices/virtual/dmi/id/board_version").read_text().strip()
    return f"{mb_vendor} {mb_name} ({mb_version})"


def get_lin_system():
    mb_vendor = Path("/sys/devices/virtual/dmi/id/board_vendor").read_text().strip()
    mb_version = Path("/sys/devices/virtual/dmi/id/board_version").read_text().strip()
    return f"{mb_vendor} {mb_version}"


def get_lin_ram(ram_cmd):
    if pout := run_cmd(ram_cmd):
        mem_nonreserved = (
            [ln for ln in pout.stdout.split("\n") if re.search(r"MemTotal", ln)][0]
            .split(":")[1]
            .strip()
            .split()[0]
        )
        mem_nonreserved = f"{int(mem_nonreserved)//(1024**2)} GB (Non-Reserved)"
        return mem_nonreserved
    else:
        return "N/A"


def specs_dict():
    specs["os"] = get_lin_os(os_cmd)
    specs["cpu"] = get_lin_cpu(cpu_cmd)
    specs["mb"] = get_lin_mb()
    specs["ram"] = get_lin_ram(ram_cmd)
    specs["gpu"] = get_lin_gpu(gpu_cmd)
    specs["system"] = get_lin_system()
    specs["engine"] = "N/A"  # get_win_engine(engine_cmd)
    return specs


def print_specs(specs):
    print(f'{"*"*60}')
    print(f"{'**** System Specs ****':^60s}")
    print(f'{"*"*60}')
    for k, v in specs.items():
        print(f"{k:8} : {v}")
    print(f'{"*"*60}')


if __name__ == "__main__":
    spec_info = specs_dict()
    print_specs(spec_info)
