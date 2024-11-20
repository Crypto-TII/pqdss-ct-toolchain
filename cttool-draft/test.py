#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from subprocess import Popen
import sys

import os

# def test_sed(path_to_file: str, expression):
#     file_directory = "/".join(path_to_file.split('/')[:-1])
#     print("---file_directory: ", file_directory)
#     os.chdir(file_directory)
#     makefile = f'Makefile'
#     # sed -i 's/^projdir .*$/projdir PacMan/' .ignore
#     cmd = [f"sed -i 's/^TOOLS_FLAGS := .*$/TOOLS_FLAGS := {expression}/g' {makefile}"]
#     subprocess.call(cmd, stdin=sys.stdin, shell=True)
#
#
# path_to_file = 'candidates/mpc-in-the-head/perk/Optimized_Implementation/perk-128-fast-3/Makefile'
# exp = '-g -Wall'
# test_sed(path_to_file, exp)

# path_to_benchmark_folder = 'candidates/mpc-in-the-head/mqom/Optimized_Implementation/mqom_cat1_gf31_fast'
#
# list_file = os.listdir(path_to_benchmark_folder)
# print("===list_file")
# print(list_file)
# list_file = [file for file in list_file if os.path.isfile(f'{path_to_benchmark_folder}/{file}')]
# print("===list_file")
# print(list_file)


# sys.stdout.write("Hello")
# print("PRINT", file=sys.stderr)


#print("1\t2\t3".expandtabs(4))

cond1 = 'no'






def generic_run_bench_candidate(path_to_candidate, instances, default_instance: str,
                                cpu_core_isolated: Union[str, list] = '1',
                                path_to_candidate_bench: Optional[str] = None, custom_benchmark: bool = True,
                                candidate_benchmark: bool = True):
    list_of_instances = []
    path_to_benchmark_binary = path_to_candidate_bench
    list_path_to_bench_binaries = []
    candidate = os.path.basename(path_to_candidate)
    if custom_benchmark is None or custom_benchmark == 'no':
        custom_benchmark = False
    elif custom_benchmark == 'yes':
        custom_benchmark = True
    if candidate_benchmark == 'yes':
        candidate_benchmark = True
    elif candidate_benchmark == 'no':
        candidate_benchmark = False

    if candidate_benchmark and path_to_candidate_bench is None:
        raise error.CTToolchainError("Candidate {} doesn't have a benchmark".format(candidate))
    if candidate_benchmark and custom_benchmark:
        print("------------ Benchmark: Processing both candidate and custom benchmark")
    if candidate_benchmark and not custom_benchmark:
        print("------------ Benchmark: Processing only candidate benchmark")
    if custom_benchmark and not candidate_benchmark:
        print("------------ Benchmark: Processing only custom benchmark")
    if candidate_benchmark and path_to_candidate_bench:
        bench_basename = os.path.basename(path_to_candidate_bench)
        path_to_benchmark_folder = path_to_candidate_bench.split(bench_basename)[0]
        if not instances:
            benchmark_folder_folder_content = os.listdir(path_to_benchmark_folder)
            list_path_to_bench_binaries = [file for file in benchmark_folder_folder_content if '.' not in file]
            list_path_to_bench_binaries = [file for file in list_path_to_bench_binaries
                                           if os.path.isfile(f'{path_to_benchmark_folder}/{file}')]
            list_path_to_bench_binaries = [f'{path_to_benchmark_folder}/{file}' for file in list_path_to_bench_binaries
                                           if 'KAT' not in file]
        else:
            for instance in instances:
                path_to_instance = f'{path_to_benchmark_folder}/{instance}'
                list_of_instances.append(path_to_instance)
                path_to_benchmark_binary_split = path_to_benchmark_binary.split(default_instance)
                path_to_benchmark_binary_split.insert(1, instance)
                path_to_benchmark_binary = "".join(path_to_benchmark_binary_split)
                list_path_to_bench_binaries.append(path_to_benchmark_binary)
    if custom_benchmark:
        print("-----------YEAH MAN--------")
        path_to_benchmark_folder = f'{path_to_candidate}/benchmarks'
        if not instances:
            path_to_instance = path_to_benchmark_folder
            list_of_instances.append(path_to_instance)
            bin_files = os.listdir(path_to_instance)
            bin_files = [f'{path_to_instance}/{exe}' for exe in bin_files if '.' not in exe]
            list_path_to_bench_binaries.extend(bin_files)
        else:
            for instance in instances:
                path_to_instance = f'{path_to_benchmark_folder}/{instance}'
                bin_files = os.listdir(path_to_instance)
                bin_files = [f'{path_to_instance}/{exe}' for exe in bin_files if '.' not in exe]
                list_path_to_bench_binaries.extend(bin_files)
    print("================list_path_to_bench_binaries")
    print(list_path_to_bench_binaries)
    for executable in list_path_to_bench_binaries:
        path_to_output_file = f'{executable}_output.txt'
        run_bench_candidate(executable, cpu_core_isolated, path_to_output_file)