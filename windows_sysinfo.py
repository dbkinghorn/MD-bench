import platform
import subprocess
from collections import Counter

specs = {}


def get_os_type():
    """Linux, Windows, or Darwin"""
    return platform.system()


os_cmd = "wmic os get caption,buildnumber /format:csv".split()
cpu_cmd = "wmic cpu get name /format:csv".split()
mb1_cmd = "wmic baseboard get product,manufacturer /format:csv".split()
mb2_cmd = "wmic bios get SMBIOSBIOSVersion /format:csv".split()
ram_cmd = "wmic memorychip get Capacity,Speed /format:csv".split()
gpu_cmd = "wmic path win32_VideoController get name,driverversion /format:csv".split()
system_cmd = "wmic computersystem get manufacturer,model /format:csv".split()


def mk_info_dict(info_cmd):
    try:
        pout = subprocess.run(info_cmd, text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        print("Error ocurred: " + err.stderr)
    if pout.stderr:
        return None

    info_str = pout.stdout.strip()
    lines = [
        line.split(",") for line in info_str.split("\n\n") if line
    ]  # ugly compound split

    cntr = Counter([(*ln,) for ln in lines])
    lines = [list(k + (v,)) for k, v in cntr.items()]
    lines[0][-1] = "Item_Count"

    if len(lines) == 2:
        info_dict = dict(zip(lines[0], lines[1]))  # Headers and data
    else:
        # cntr=Counter([(*ln,) for ln in lines[1:]])
        info_dict = {k: v for k, *v in zip(*lines)}

    # print(info_dict)
    return info_dict


def get_win_os(os_cmd):
    if os_dict := mk_info_dict(os_cmd):
        return f"{os_dict['Caption']} ({os_dict['BuildNumber']})"
    else:
        return "N/A"


def get_win_cpu(cpu_cmd):
    if cpu_dict := mk_info_dict(cpu_cmd):
        return f"{cpu_dict['Name']}"
    else:
        return "N/A"


def get_win_mb(mb1_cmd, mb2_cmd):  # Motherboard
    if mb_dict := mk_info_dict(mb1_cmd) | mk_info_dict(mb2_cmd):
        return f"{mb_dict['Manufacturer']} {mb_dict['Product']} ({mb_dict['SMBIOSBIOSVersion']})"
    else:
        return "N/A"


def get_win_ram(ram_cmd):
    if ram_dict := mk_info_dict(ram_cmd):
        stick_size = int(ram_dict["Capacity"]) // 1024 ** 3
        num_sticks = int(ram_dict["Item_Count"])
        total_mem = stick_size * num_sticks
        return f"{total_mem}GB ({num_sticks}x{stick_size}GB) {ram_dict['Speed']}MHz"
    else:
        return "N/A"


def get_win_gpu(gpu_cmd):
    if gpu_dict := mk_info_dict(gpu_cmd):
        return f"{gpu_dict['Name']} ({gpu_dict['DriverVersion']})"
    else:
        return "N/A"


def get_win_system(system_cmd):
    if system_dict := mk_info_dict(system_cmd):
        return f"{system_dict['Manufacturer']} ({system_dict['Model']})"
    else:
        return "N/A"


def specs_dict():
    specs["os"] = get_win_os(os_cmd)
    specs["cpu"] = get_win_cpu(cpu_cmd)
    specs["mb"] = get_win_mb(mb1_cmd, mb2_cmd)
    specs["ram"] = get_win_ram(ram_cmd)
    specs["gpu"] = get_win_gpu(gpu_cmd)
    specs["system"] = get_win_system(system_cmd)
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
