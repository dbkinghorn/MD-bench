#!/usr/bin/env python3
"""
NAMD GPU Benchmarking
"""

import statistics as st
import time
import argparse
from pathlib import Path
import json
import subprocess
import os
import platform
from meta_data import meta_data

# import sysinfo for the OS in use
OS_IN_USE = platform.system()

if OS_IN_USE == "Linux":
    import linux_sysinfo as sysinfo
elif OS_IN_USE == "Windows":
    import windows_sysinfo as sysinfo
else:
    print("Unsupported OS, no sysinfo file available, exiting ...")
    exit()

# ******************************************************************************
# Global Variables
# ******************************************************************************
NAMD_PATH = Path("namd/NAMD_2.14_Linux-x86_64-multicore-CUDA/namd2")
BENCHMARK_JOBS = ["f1atpase", "apoa1", "stmv"]

# ******************************************************************************
# Utility Functions
# ******************************************************************************


def nv_gpuinfo():
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,index", "--format=csv,noheader"],
        capture_output=True,
        text=True,
    )
    return result.stdout.replace("\n", "").split(",")


def print_result(result):
    print(f".\n. Result Summary ({result['name']})\n.")
    for k, v in result.items():
        num_str = f"{v:.4f}" if isinstance(v, float) else f"{v}"
        print(f"{k:18} = {num_str}")


def run_cmd_rtn_out(cmd, sys_env=None):
    """Run cmd in a with output polling to show progress and return stdout and return code"""

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=sys_env
    )
    cmd_out = ""
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            cmd_out += output
            print(output.strip())

    rtn_code = process.poll()
    return cmd_out, rtn_code


# ******************************************************************************
# namd_gpu
# ******************************************************************************
def namd_gpu(job, repeats=3, cores=None, gpus=0, silent=False):
    """Run NAMD on a GPU"""

    job_path = Path(f"namd/{job}/{job}.namd")
    if not job_path.exists():
        raise Exception(f"Benchmark {job} path does not exist")

    if cores is None:  # set to all threads
        cores = os.cpu_count()

    commandline = f"{NAMD_PATH} +p{cores} +setcpuaffinity +idlepoll +isomalloc_sync +devices {gpus} {job_path}".split()

    timings = []
    day_per_ns = []
    memory = []

    for i in range(repeats):
        start_time = time.perf_counter()
        cmd_out, rtn_code = run_cmd_rtn_out(commandline)
        timings.append(time.perf_counter() - start_time)
        day_per_ns.extend(
            [
                float(line.split()[7])  # magic num 7 for days/ns
                for line in cmd_out.split("\n")
                if line.startswith("Info: Benchmark")
            ]
        )
        memory.extend(
            [
                float(line.split()[9])  # magic num 9 for memory
                for line in cmd_out.split("\n")
                if line.startswith("Info: Benchmark")
            ]
        )

    result = {
        "name": job_path.parts[1],  # magic number 1 is the job name
        "num_processes": cores,
        "nv_gpus_available": nv_gpuinfo(),
        "gpu_index_used": gpus,
        "commandline": " ".join(commandline),
        "min_time": round(min(timings), 4),
        "max_time": round(max(timings), 4),
        "median_time": round(st.median(timings), 4),
        "standard_deviation": round(st.stdev(timings), 4) if len(timings) > 1 else 0,
        "memory_usage": round(st.median(memory), 4),
        "performance": round(st.median(day_per_ns), 5),
        "performance_unit": "days/ns",
    }
    print_result(result) if not silent else None
    return result


def run_jobs(jobs, **kwargs):
    results = []
    for job in jobs:
        if job in BENCHMARK_JOBS:
            results.append(namd_gpu(job, **kwargs))
        else:
            print(f"\nError: Unknown benchmark {job}")
    return results


def init_output_dict(output_fh):
    output_dict = {}
    output_dict["meta"] = meta_data
    output_dict["specs"] = sysinfo.specs_dict()
    output_dict["results"] = []
    with open(output_fh, "w") as f:
        json.dump(output_dict, f, indent=4)
    return output_dict


def write_results(results, output_file):
    if not output_file.exists() or Path(output_file).stat().st_size == 0:
        with open(output_file, "w") as f:
            json.dump({"results": []}, f)

    try:
        with open(output_file, "r") as f:
            jason_results = json.load(f)

        jason_results["results"].extend(results)

        with open(output_file, "w") as f:
            json.dump(jason_results, f, indent=4)
    except Exception as e:
        print(f"\nError: {e} writing results to {output_file}")


# ******************************************************************************
# Main Command Line Interface
# ******************************************************************************
def main():
    def get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("-r", "--repeats", type=int, default=3)
        parser.add_argument("--silent", action="store_true", help="Don't print results")
        parser.add_argument(
            "-o",
            "--output",
            type=Path,
            default="results.json",
            help="Output file (JSON)",
        )
        parser.add_argument(
            "-c", "--cores", type=int, default=None, help="Number of cores to use"
        )
        parser.add_argument(
            "-g",
            "--gpus",
            type=int,
            default=0,
            help="List of NVIDIA GPU indexes example 0,1,2,3",
        )
        parser.add_argument(
            "jobs",
            nargs="*",
            default=BENCHMARK_JOBS,
            help="Jobs to run --list for list of jobs",
        )
        parser.add_argument(
            "-l", "--list", action="store_true", help="List available jobs"
        )
        parser.add_argument("--scaling", nargs="*", help="list of #cores to use")
        return parser.parse_args()

    args = get_args()

    repeats = args.repeats
    silent = args.silent
    cores = args.cores
    gpus = args.gpus
    jobs = args.jobs
    list_jobs = args.list
    scaling = args.scaling
    output_file = args.output

    if list_jobs:
        print(f"\nAvailable Jobs: {BENCHMARK_JOBS} Default is all of them")
        return

    # Initialize the output file dictionary (json)
    output_dict = init_output_dict(output_file)

    if scaling:
        print(f"\nRunning {jobs} with scaling {scaling} cores")
        num_cores = [int(c) for c in scaling]
        for c in num_cores:
            results = run_jobs(jobs, repeats=repeats, cores=c, gpus=gpus, silent=silent)
            write_results(results, output_file)
    else:
        results = run_jobs(jobs, repeats=repeats, cores=cores, gpus=gpus, silent=silent)
        write_results(results, output_file)


if __name__ == "__main__":
    main()

