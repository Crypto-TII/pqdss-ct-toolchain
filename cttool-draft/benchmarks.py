#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import sys
import re
import json
import subprocess
import shutil
import textwrap
from subprocess import Popen

from typing import Optional, Union, List

import tools
import generics as gen
import errors as error


def benchmark_template(candidate: str, instance: str, security_level: str, path_to_benchmark_file: str,
                       api_or_sign: str, rng: str, add_includes: str, function_return_type: str, args_types: list,
                       args_names: list, number_of_iterations: Union[str, int] = '1e3',
                       min_msg_len: Union[str, int] = '0', max_msg_len: Union[str, int] = '3300'):
    api_h = os.path.basename(api_or_sign)
    rng_h = os.path.basename(rng)
    args_types[2] = re.sub("const ", "", args_types[2])
    args_types[4] = re.sub("const ", "", args_types[4])

    sorting_functions_block = f'''
    void swap(ticks* a, ticks* b)
    {{
        ticks t = *a;
        *a = *b;
        *b = t;
    }}
    
    /* Performs one step of pivot sorting with the last
        element taken as pivot. */
    int partition (ticks arr[], int low, int high)
    {{
        ticks pivot = arr[high];
        int i = (low - 1);
    
        int j;
        for(j = low; j <= high- 1; j++)
        {{
        if(arr[j] < pivot)
        {{
        i++;
        swap(&arr[i], &arr[j]);
        }}
        }}
        swap(&arr[i + 1], &arr[high]);
        return (i + 1);
    }}
    
    void quicksort(ticks arr[], int low, int high)
    {{
        if (low < high)
        {{
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
        }}
    }}
    '''

    includes_block = f'''
    #include<time.h>
    #include <math.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <stdbool.h>
    
    #include "cycle.h"
    
    #include "{api_h}"
    
    //#include "{rng_h}"
    #include "toolchain_randombytes.h"
    '''
    bench_content_block = f'''
    
    {sorting_functions_block}
    
    int main(void)
    {{
   
    \t//int i = 0;
    \t//int iterations = TOTAL_ITERATIONS;
    \t//int min_msg_len = MINIMUM_MSG_LENGTH;
    \t//int max_msg_len = MAXIMUM_MSG_LENGTH;
    \t{args_types[3]} i = 0;
    \t{args_types[3]} iterations = TOTAL_ITERATIONS;
    \t{args_types[3]} min_msg_len = MINIMUM_MSG_LENGTH;
    \t{args_types[3]} max_msg_len = MAXIMUM_MSG_LENGTH;
    \t{args_types[3]} mlen;
    \t{args_types[1]} smlen;
    \t//bool pass;
    \t{function_return_type} pass;

    \t// For storing clock cycle counts
    \tticks cc_mean = 0, cc_stdev = 0,
    \tcc0, cc1,
    \t*cc_sample =(ticks *)malloc(iterations * sizeof(ticks));

    \t// For storing keypair
    \t{args_types[4]} *pk = ({args_types[4]} *)malloc(CRYPTO_PUBLICKEYBYTES * iterations * sizeof({args_types[4]}));
    \t{args_types[4]} *sk = ({args_types[4]} *)malloc(CRYPTO_SECRETKEYBYTES * iterations * sizeof({args_types[4]}));

    \t// For storing plaintext messages
    \t{args_types[2]} *m = ({args_types[2]} *)malloc(max_msg_len * iterations * sizeof({args_types[2]}));
    \t//mlen = getrandom(m, max_msg_len * iterations, 0);
    \tct_randombytes(m, max_msg_len * iterations);
    \t//if((int)mlen < max_msg_len * iterations){{
    \tif(mlen < max_msg_len * iterations){{
    \t\tprintf("Error in generating random messages\\n");
    \t\treturn -1;
    \t}}

    \t// For storing signed messages
    \t{args_types[0]} *sm = ({args_types[0]} *)malloc((CRYPTO_BYTES + max_msg_len) * iterations * sizeof({args_types[0]}));

    \tprintf("Candidate: {candidate}\\n");
    \tprintf("Security Level: {security_level}\\n");
    \tprintf("Instance: {instance}\\n");

    \t// ================== KEYGEN ===================
    \tcc_mean = 0; cc_stdev = 0;
    \t//Gather statistics
    \tfor (i = 0; i < iterations; i++)
    \t{{
   
    \t\tcc0 = getticks();
    \t\tpass = crypto_sign_keypair(&pk[i*CRYPTO_PUBLICKEYBYTES], &sk[i*CRYPTO_SECRETKEYBYTES]);
    \t\tcc1 = getticks();
    \t\tcc_sample[i] = cc1 - cc0;
    \t\tcc_mean += cc_sample[i];

    \t\tif(pass){{
    \t\t\tprintf("Error in Keygen\\n");
    \t\t\treturn -1;
    \t\t}}
    \t}};
    \tprintf("Algorithm: Keygen:\\n");
    \tcc_mean /= iterations;
    \tquicksort(cc_sample, 0, iterations - 1);

    \t// Compute the standard deviation
    \tfor (i = 0; i < iterations; ++i){{
    \t\tcc_stdev += (cc_sample[i] - cc_mean)*(cc_sample[i] - cc_mean);
    \t}}
    \tcc_stdev = sqrt(cc_stdev / iterations);

    \tprintf("Average running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_mean) / 1000000.0);
    \tprintf("Standard deviation (million cycles): \\t %7.03lf\\n", (1.0 * cc_stdev) / 1000000.0);
    \tprintf("Minimum running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[0]) / 1000000.0);
    \tprintf("First quartile (million cycles): \\t \\t %7.03lf\\n", (1.0 * cc_sample[iterations/4]) / 1000000.0);
    \tprintf("Median (million cycles):    \\t \\t %7.03lf\\n", (1.0 * cc_sample[iterations/2]) / 1000000.0);
    \tprintf("Third quartile (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[(3*iterations)/4]) / 1000000.0);
    \tprintf("Maximum running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[iterations-1]) / 1000000.0);
    \tprintf("\\n");

    \t// ================== SIGNING ===================
    \tcc_mean = 0; cc_stdev = 0;
    \t// Gather statistics
    \tfor (i = 0; i < iterations; i++)
    \t{{
    \t\tmlen = min_msg_len + i*(max_msg_len - min_msg_len)/(iterations);
    \t\tsmlen = mlen + CRYPTO_BYTES;
    \t\tcc0 = getticks();
    \t\tpass = crypto_sign(&sm[(CRYPTO_BYTES + max_msg_len)*i], &smlen, &m[max_msg_len*i], mlen, &sk[i*CRYPTO_SECRETKEYBYTES]);
    \t\tcc1 = getticks();
    \t\tcc_sample[i] = cc1 - cc0;
    \t\tcc_mean += cc_sample[i];

    \t\tif(pass)
    \t\t{{
    \t\t\tprintf("Error in signing\\n");
    \t\t\treturn -1;
    \t\t}}
    \t}};
    \tprintf("Candidate: {candidate}\\n");
    \tprintf("Security Level: {security_level}\\n");
    \tprintf("Instance: {instance}\\n");
    \tprintf("Algorithm: Sign:\\n");
    \tcc_mean /= iterations;
    \tquicksort(cc_sample, 0, iterations - 1);

    \t// Compute the standard deviation
    
    \tfor (i = 0; i < iterations; ++i){{
    \t\tcc_stdev += (cc_sample[i] - cc_mean)*(cc_sample[i] - cc_mean);
    }}
    \tcc_stdev = sqrt(cc_stdev / iterations);
    
    \tprintf("Average running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_mean) / 1000000.0);
    \tprintf("Standard deviation (million cycles): \\t %7.03lf\\n", (1.0 * cc_stdev) / 1000000.0);
    \tprintf("Minimum running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[0]) / 1000000.0);
    \tprintf("First quartile (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[iterations/4]) / 1000000.0);
    \tprintf("Median (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[iterations/2]) / 1000000.0);
    \tprintf("Third quartile (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[(3*iterations)/4]) / 1000000.0);
    \tprintf("Maximum running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[iterations-1]) / 1000000.0);
    \tprintf("\\n");

    \t// ================== VERIFICATION ===================
    \tcc_mean = 0; cc_stdev = 0;
    \t// Gather statistics
    \tfor (i = 0; i < iterations; i++)
    \t{{
    \t\tmlen = min_msg_len + i*(max_msg_len - min_msg_len)/(iterations);
    \t\tsmlen = mlen + CRYPTO_BYTES;
    \t\tcc0 = getticks();
    \t\tpass = crypto_sign_open(&m[max_msg_len*i], &mlen, &sm[(CRYPTO_BYTES + max_msg_len)*i], smlen, &pk[i*CRYPTO_PUBLICKEYBYTES]);
    \t\tcc1 = getticks();
    \t\tcc_sample[i] = cc1 - cc0;
    \t\tcc_mean += cc_sample[i];
    
    \t\tif(pass){{
    \t\t\tprintf("Verification failed\\n");
    \t\t\treturn -1;
    \t\t}}
    \t}};
        
    \tprintf("Candidate: {candidate}\\n");
    \tprintf("Security Level: {security_level}\\n");
    \tprintf("Instance: {instance}\\n");
    \tprintf("Algorithm: Verify:\\n");
    \tcc_mean /= iterations;
    \tquicksort(cc_sample, 0, iterations - 1);

    \t// Compute the standard deviation
    \tfor (i = 0; i < iterations; ++i){{
    \t\tcc_stdev += (cc_sample[i] - cc_mean)*(cc_sample[i] - cc_mean);
    }}
    \tcc_stdev = sqrt(cc_stdev / iterations);

    \tprintf("Average running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_mean) / 1000000.0);
    \tprintf("Standard deviation (million cycles): \\t %7.03lf\\n", (1.0 * cc_stdev) / 1000000.0);
    \tprintf("Minimum running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[0]) / 1000000.0);
    \tprintf("First quartile (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[iterations/4]) / 1000000.0);
    \tprintf("Median (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[iterations/2]) / 1000000.0);
    \tprintf("Third quartile (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[(3*iterations)/4]) / 1000000.0);
    \tprintf("Maximum running time (million cycles): \\t %7.03lf\\n", (1.0 * cc_sample[iterations-1]) / 1000000.0);
    \tprintf("\\n");

    \t// -----------------------------------------------------
    \tfree(cc_sample);
    \tfree(m);
    \tfree(sm);
    \tfree(pk);
    \tfree(sk);
    \treturn 0;
    }}
    '''
    add_includes_block = f''''''
    if not add_includes == []:
        for include in add_includes:
            add_includes_block += f'#include {include}\n'
    benchmark_content = f'''
    {includes_block}
    #define MINIMUM_MSG_LENGTH {min_msg_len}
    #define MAXIMUM_MSG_LENGTH {max_msg_len}
    #define TOTAL_ITERATIONS   {number_of_iterations}
    {add_includes_block}
    {bench_content_block}
    '''
    with open(path_to_benchmark_file, "w") as bench_file:
        bench_file.write(textwrap.dedent(benchmark_content))


def generic_target_compilation_24(path_candidate: str, path_to_test_library_directory: str,
                               libraries_names: [Union[str, list]], path_to_include_directories: Union[str, list],
                               cflags: list, default_instance: str, instances: Optional[Union[str, list]] = None,
                               compiler: str = 'gcc'):
    benchmark_file_basename = 'bench.c'  # it has to be handled by a generic Object or global
    benchmarks_folder_basename = 'benchmarks'  # it has to be handled by a generic Object or global
    path_to_benchmark_folder = f'{path_candidate}/{benchmarks_folder_basename}'  # to be fixed

    candidate = path_candidate.split('/')[-1]
    instances_list = []
    if instances:
        instances_list = []
        if isinstance(instances, str):
            instances_list = instances.split()
        elif isinstance(instances, list):
            instances_list = instances.copy()
    else:
        instances_list = ["."]
    for instance in instances_list:
        if instance == ".":
            path_to_instance = f'{path_to_benchmark_folder}'
        else:
            path_to_instance = f'{path_to_benchmark_folder}/{instance}'
            path_to_include_directories_split = path_to_include_directories.split(default_instance)
            path_to_include_directories_split.insert(1, instance)
            path_to_include_directories = "".join(path_to_include_directories_split)
            if default_instance in path_to_test_library_directory:
                path_to_test_library_directory_split = path_to_test_library_directory.split(default_instance)
                path_to_test_library_directory_split.insert(1, instance)
                path_to_test_library_directory = "".join(path_to_test_library_directory_split)

        path_to_benchmark_file = f'{path_to_instance}/{benchmark_file_basename}'
        path_to_bench_binary = path_to_benchmark_file.split('.c')[0]
        gen.generic_compilation(path_to_benchmark_file, path_to_bench_binary, path_to_test_library_directory,
                                libraries_names, path_to_include_directories, cflags, compiler)


def generic_target_compilation(path_candidate: str, path_to_test_library_directory: str,
                               libraries_names: [Union[str, list]], path_to_include_directories: Union[str, list],
                               cflags: list, default_instance: str, instances: Optional[Union[str, list]] = None,
                               compiler: str = 'gcc'):
    path_to_include_directories_initial = path_to_include_directories
    path_to_test_library_directory_initial = path_to_test_library_directory
    benchmark_file_basename = 'bench.c'  # it has to be handled by a generic Object or global
    benchmarks_folder_basename = 'benchmarks'  # it has to be handled by a generic Object or global
    path_to_benchmark_folder = f'{path_candidate}/{benchmarks_folder_basename}'  # to be fixed

    candidate = path_candidate.split('/')[-1]
    instances_list = []
    if instances:
        instances_list = []
        if isinstance(instances, str):
            instances_list = instances.split()
        elif isinstance(instances, list):
            instances_list = instances.copy()
    else:
        instances_list = ["."]
    for instance in instances_list:
        if instance == ".":
            path_to_instance = f'{path_to_benchmark_folder}'
        else:
            path_to_instance = f'{path_to_benchmark_folder}/{instance}'
            path_to_include_directories_split = path_to_include_directories.split(default_instance)
            path_to_include_directories_split.insert(1, instance)
            path_to_include_directories = "".join(path_to_include_directories_split)
            if default_instance in path_to_test_library_directory:
                path_to_test_library_directory_split = path_to_test_library_directory.split(default_instance)
                path_to_test_library_directory_split.insert(1, instance)
                path_to_test_library_directory = "".join(path_to_test_library_directory_split)

        path_to_benchmark_file = f'{path_to_instance}/{benchmark_file_basename}'
        path_to_bench_binary = path_to_benchmark_file.split('.c')[0]
        gen.generic_compilation(path_to_benchmark_file, path_to_bench_binary, path_to_test_library_directory,
                                libraries_names, path_to_include_directories, cflags, compiler)
        path_to_include_directories = path_to_include_directories_initial
        path_to_test_library_directory = path_to_test_library_directory_initial


def run_bench_candidate(path_to_benchmark_binary: str, cpu_core_isolated: Union[str, list] = '1',
                        path_to_output_file: Optional[str] = None):
    if isinstance(cpu_core_isolated, list):
        cpu_core_list = cpu_core_isolated.copy()
    else:
        cpu_core_list = cpu_core_isolated.split('')

    chosen_cpu_core = cpu_core_list[0]
    cmd_str = f'taskset --cpu-list {chosen_cpu_core} ./{path_to_benchmark_binary}'
    cmd_args_lst = cmd_str.split()
    if path_to_output_file.strip() == '' or path_to_output_file is None:
        subprocess.call(cmd_args_lst, stdin=sys.stdin)
    else:
        with open(path_to_output_file, "w") as file:
            execution = Popen(cmd_args_lst, universal_newlines=True, stdout=file, stderr=file)
            execution.communicate()


def candidate_instances_benchmarks(path_to_candidate_global_bench: str, path_to_instance_bench_output_file: str):
    with open(path_to_candidate_global_bench, "a+") as global_bench:
        with open(path_to_instance_bench_output_file, "r") as instance_bench:
            global_bench.write(instance_bench.read())


def candidates_benchmarks(path_to_all_candidates: str, path_to_candidate_global_bench: str):
    with open(path_to_all_candidates, "a+") as global_bench:
        with open(path_to_candidate_global_bench, "r") as instance_bench:
            global_bench.write(instance_bench.read())


def generic_run_bench_candidate(path_to_candidate, instances, default_instance: str,
                                cpu_core_isolated: Union[str, list] = '1',
                                path_to_candidate_bench: Optional[str] = None, custom_benchmark: bool = True,
                                candidate_benchmark: bool = True):
    list_of_instances = []
    path_to_benchmark_binary = path_to_candidate_bench
    list_path_to_bench_binaries = []
    path_to_benchmark_folder = ''
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
        if path_to_candidate.endswith('/'):
            path_to_benchmark_folder = f'{path_to_candidate}/benchmarks'
        else:
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
    path_to_candidate_global_bench = f'{path_to_benchmark_folder}/{candidate}_bench.txt'
    for executable in list_path_to_bench_binaries:
        path_to_output_file = f'{executable}_output.txt'
        run_bench_candidate(executable, cpu_core_isolated, path_to_output_file)
        candidate_instances_benchmarks(path_to_candidate_global_bench, path_to_output_file)


def generate_template_candidate(candidate: str, instance: str, security_level: str, abs_path_to_api_or_sign,
                                abs_path_to_rng, path_to_benchmark_folder, add_includes, number_of_iterations='1e3',
                                min_msg_len: Union[str, int] = '0', max_msg_len: Union[str, int] = '3300'):
    list_of_path_to_folders = [path_to_benchmark_folder]
    gen.generic_create_tests_folders(list_of_path_to_folders)
    api_or_sign = os.path.basename(abs_path_to_api_or_sign)
    rng = os.path.basename(abs_path_to_rng)
    path_to_benchmark_file = f'{path_to_benchmark_folder}/bench.c'
    ret_sign = gen.sign_find_args_types_and_names(abs_path_to_api_or_sign)
    sign_return_type, sign_basename, sign_args_types, sign_args_names = ret_sign
    benchmark_template(candidate, instance, security_level, path_to_benchmark_file, api_or_sign, rng, add_includes,
                       sign_return_type, sign_args_types, sign_args_names, number_of_iterations, min_msg_len,
                       max_msg_len)


def generate_benchmarks(candidate, abs_path_to_api_or_sign, abs_path_to_rng, instance, add_includes,
                        number_of_iterations='1e3', min_msg_len: Union[str, int] = '0',
                        max_msg_len: Union[str, int] = '3300', security_level: str = '128'):
    path_candidate = f'{abs_path_to_api_or_sign.split(candidate)[0]}/{candidate}'
    path_to_benchmark_folder = f'{path_candidate}/benchmarks'
    if not instance == "":
        path_to_benchmark_folder += f'/{instance}'
    generate_template_candidate(candidate, instance, security_level, abs_path_to_api_or_sign, abs_path_to_rng,
                                path_to_benchmark_folder, add_includes, number_of_iterations, min_msg_len, max_msg_len)


def generic_benchmarks_nist_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng, instances_list,
                                      add_includes, number_of_iterations='1e3', min_msg_len: Union[str, int] = '0',
                                      max_msg_len: Union[str, int] = '3300', security_level: Union[str, list] = '128'):
    list_of_instances = []
    if not instances_list:
        list_of_instances = [""]
    else:
        for instance_folder in instances_list:
            list_of_instances.append(instance_folder)
    if instances_list:
        for instance, sec_level in zip(list_of_instances, security_level):
            generate_benchmarks(candidate, abs_path_to_api_or_sign, abs_path_to_rng, instance,
                                add_includes, number_of_iterations, min_msg_len, max_msg_len, sec_level)
    else:
        generate_benchmarks(candidate, abs_path_to_api_or_sign, abs_path_to_rng, "",
                            add_includes, number_of_iterations, min_msg_len, max_msg_len, security_level)


def generic_benchmarks_init_compile(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                    default_instance: str, instances, additional_includes,
                                    path_to_candidate_makefile_cmake, direct_link_or_compile_target: bool = True,
                                    libraries_names: Union[str, list] = 'lbench',
                                    path_to_include_directories: Union[str, list] = '', build_with_make: bool = True,
                                    additional_cmake_definitions=None, compiler: str = 'gcc',
                                    custom_benchmark: Optional[bool] = True, number_of_iterations='1e3',
                                    min_msg_len: Union[str, int] = '0', max_msg_len: Union[str, int] = '3300',
                                    security_level: Union[str, list] = '128', *args, **kwargs):
    path_to_candidate_makefile_cmake_initial = path_to_candidate_makefile_cmake
    print(":::::generic_benchmarks_init_compile")
    if custom_benchmark:
        print("------GENERATE: custom_benchmark")
        generic_benchmarks_nist_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng, instances,
                                          additional_includes, number_of_iterations, min_msg_len,
                                          max_msg_len, security_level)
    cflags = []  # to be fixed
    path_candidate = abs_path_to_api_or_sign.split(candidate)[0]
    if path_candidate.endswith('/'):
        path_candidate += candidate
    else:
        path_candidate += f'/{candidate}'
    path_to_test_library_directory = f'{path_to_candidate_makefile_cmake}/build'
    if direct_link_or_compile_target:
        if not instances:
            gen.compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
                                         additional_cmake_definitions, *args, **kwargs)
        else:
            if build_with_make:
                for instance in instances:
                    path_to_candidate_makefile_cmake_split = path_to_candidate_makefile_cmake.split(default_instance)
                    path_to_candidate_makefile_cmake_split.insert(1, instance)
                    path_to_candidate_makefile_cmake = "".join(path_to_candidate_makefile_cmake_split)
                    gen.compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
                                                 additional_cmake_definitions, *args, **kwargs)
                    path_to_candidate_makefile_cmake = path_to_candidate_makefile_cmake_initial
            else:
                gen.compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
                                             additional_cmake_definitions, *args, **kwargs)

    if custom_benchmark:
        if build_with_make:
            generic_target_compilation(path_candidate, path_to_test_library_directory, libraries_names,
                                       path_to_include_directories, cflags, default_instance, instances, compiler)


def generic_compile_run_bench_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                        default_instance: str, instances, additional_includes,
                                        path_to_candidate_makefile_cmake, path_to_candidate_bench: Optional[str] = None,
                                        direct_link_or_compile_target: bool = True,
                                        libraries_names: Union[str, list] = 'lbench',
                                        path_to_include_directories: Union[str, list] = '',
                                        build_with_make: bool = True,
                                        additional_cmake_definitions=None, compiler: str = 'gcc',
                                        number_of_iterations='1e3',
                                        min_msg_len: Union[str, int] = '0', max_msg_len: Union[str, int] = '3300',
                                        cpu_core_isolated: Union[str, list] = '1', compilation: str = 'yes',
                                        execution: str = 'yes', custom_benchmark: bool = True,
                                        candidate_benchmark: bool = True, security_level: Union[str, list] = '128',
                                        *args, **kwargs):
    path_to_candidate = abs_path_to_api_or_sign.split(candidate)[0]
    if path_to_candidate.endswith('/'):
        path_to_candidate += candidate
    else:
        path_to_candidate += f'/{candidate}'
    if 'yes' in compilation.lower() and 'yes' in execution.lower():
        generic_benchmarks_init_compile(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                        default_instance, instances, additional_includes, path_to_candidate_makefile_cmake,
                                        direct_link_or_compile_target, libraries_names, path_to_include_directories,
                                        build_with_make, additional_cmake_definitions, compiler,
                                        custom_benchmark, number_of_iterations, min_msg_len, max_msg_len, security_level,
                                        *args, **kwargs)
        generic_run_bench_candidate(path_to_candidate, instances, default_instance,
                                    cpu_core_isolated, path_to_candidate_bench, custom_benchmark, candidate_benchmark)
    elif 'yes' in compilation.lower() and 'no' in execution.lower():
        generic_benchmarks_init_compile(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                        default_instance, instances, additional_includes, path_to_candidate_makefile_cmake,
                                        direct_link_or_compile_target, libraries_names, path_to_include_directories,
                                        build_with_make, additional_cmake_definitions, compiler,
                                        custom_benchmark, number_of_iterations, min_msg_len, max_msg_len, security_level,
                                        *args, **kwargs)
    if 'no' in compilation.lower() and 'yes' in execution.lower():
        generic_run_bench_candidate(path_to_candidate, instances, default_instance,
                                    cpu_core_isolated, path_to_candidate_bench, custom_benchmark, candidate_benchmark)


def get_instance_security_level_14_dec(instances: Union[str, list], security_level_dict: dict):
    security_level_list = []
    for instance in instances:
        for sec_level in security_level_dict.keys():
            if any(sec_lev_inst in instance for sec_lev_inst in security_level_dict[sec_level]):
                security_level_list.append(sec_level)
                break
    return security_level_list


def get_instance_security_level(instances: Union[str, list], security_level_dict: dict):
    security_level_list = []
    if instances:
        for instance in instances:
            for sec_level in security_level_dict.keys():
                if any(sec_lev_inst in instance for sec_lev_inst in security_level_dict[sec_level]):
                    security_level_list.append(sec_level)
                    break
    return security_level_list


def run_benchmarks_23(user_entry_point: str, candidate: str, instances, candidates_dict,
                   direct_link_or_compile_target: bool = False, implementation_type='opt',
                   security_level=None, benchmarks_keywords: Optional[list] = None, number_of_iterations='1e3',
                   min_msg_len: Union[str, int] = '0', max_msg_len: Union[str, int] = '3300',
                   cpu_core_isolated: Union[str, list] = '1', compilation: str = 'yes',
                   execution: str = 'yes', custom_benchmark: bool = True,
                   candidate_benchmark: bool = True, *args, **kwargs):
    candidates_dict = gen.parse_candidates_json_file(candidates_dict, candidate)
    abs_path_to_api_or_sign = candidates_dict['path_to_api']
    abs_path_to_rng = candidates_dict['path_to_rng']
    optimized_imp_folder = candidates_dict['optimized_implementation']
    additional_imp_folder = candidates_dict['additional_implementation']
    additional_includes = ''
    path_to_candidate_makefile_cmake = candidates_dict['path_to_makefile_folder']
    libraries_names_all = candidates_dict['link_libraries']
    libraries_names = libraries_names_all["ct_tests"]
    bench_additional_library = libraries_names_all["bench"]
    if isinstance(bench_additional_library, str):
        libraries_names.extend(bench_additional_library.split())
    elif isinstance(bench_additional_library, list):
        libraries_names.extend(bench_additional_library)
    path_to_include_directories = "/".join(abs_path_to_api_or_sign.split('/')[:-1])
    build_with_make = candidates_dict['build_with_makefile']
    compiler = candidates_dict['compiler']
    default_instance = candidates_dict['default_instance']
    benchmark_keywords = candidates_dict['benchmark_keywords']
    path_to_bench_binary = candidates_dict['path_to_bench_binary']
    additional_cmake_definitions = ''  # to be fixed
    security_levels = candidates_dict['security_level']
    security_level_list = get_instance_security_level(instances, security_levels)
    if implementation_type == 'add':
        abs_path_to_api_or_sign_split = abs_path_to_api_or_sign.split(optimized_imp_folder)
        abs_path_to_api_or_sign_split.insert(1, additional_imp_folder)
        abs_path_to_api_or_sign = "".join(abs_path_to_api_or_sign_split)
        abs_path_to_rng_split = abs_path_to_rng.split(optimized_imp_folder)
        abs_path_to_rng_split.insert(1, additional_imp_folder)
        abs_path_to_rng = "".join(abs_path_to_rng_split)
        path_to_include_directories_split = path_to_include_directories.split(optimized_imp_folder)
        path_to_include_directories_split.insert(1, additional_imp_folder)
        path_to_include_directories = "".join(path_to_include_directories_split)

        path_to_candidate_makefile_cmake_split = path_to_candidate_makefile_cmake.split(optimized_imp_folder)
        path_to_candidate_makefile_cmake_split.insert(1, additional_imp_folder)
        path_to_candidate_makefile_cmake = "".join(path_to_candidate_makefile_cmake_split)
        optimized_imp_folder = additional_imp_folder
    generic_compile_run_bench_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                        default_instance, instances, additional_includes,
                                        path_to_candidate_makefile_cmake, path_to_bench_binary,
                                        direct_link_or_compile_target, libraries_names, path_to_include_directories,
                                        build_with_make, additional_cmake_definitions, compiler, number_of_iterations,
                                        min_msg_len, max_msg_len, cpu_core_isolated, compilation, execution,
                                        custom_benchmark, candidate_benchmark, security_level_list, *args, **kwargs)


def run_benchmarks_14_dec(candidate: str, instances, candidates_dict,
                   direct_link_or_compile_target: bool = False, implementation_type='opt',
                   security_level=None, number_of_iterations='1e3',
                   min_msg_len: Union[str, int] = '0', max_msg_len: Union[str, int] = '3300',
                   cpu_core_isolated: Union[str, list] = '1', compilation: str = 'yes',
                   execution: str = 'yes', custom_benchmark: bool = True,
                   candidate_benchmark: bool = True, *args, **kwargs):
    candidate_dict = gen.parse_candidates_json_file(candidates_dict, candidate)
    abs_path_to_api_or_sign = candidate_dict['path_to_api']
    abs_path_to_rng = candidate_dict['path_to_rng']
    optimized_imp_folder = candidate_dict['optimized_implementation']
    additional_imp_folder = candidate_dict['additional_implementation']
    additional_includes = ''
    path_to_candidate_makefile_cmake = candidate_dict['path_to_makefile_folder']
    libraries_names_all = candidate_dict['link_libraries']
    libraries_names = libraries_names_all["ct_tests"]
    bench_additional_library = libraries_names_all["bench"]
    if not instances or instances is None:
        instances = candidate_dict['instances']
    if isinstance(bench_additional_library, str):
        libraries_names.extend(bench_additional_library.split())
    elif isinstance(bench_additional_library, list):
        libraries_names.extend(bench_additional_library)
    path_to_include_directories = os.path.dirname(abs_path_to_api_or_sign)
    build_with_make = candidate_dict['build_with_makefile']
    compiler = candidate_dict['compiler']
    default_instance = candidate_dict['default_instance']
    path_to_bench_binary = candidate_dict['path_to_bench_binary']
    additional_cmake_definitions = ''  # to be fixed
    security_levels = candidate_dict['security_level']
    security_level_list = get_instance_security_level(instances, security_levels)
    print(":::::::::::::run_benchmarks: ")
    if implementation_type == 'add':
        abs_path_to_api_or_sign_split = abs_path_to_api_or_sign.split(optimized_imp_folder)
        abs_path_to_api_or_sign_split.insert(1, additional_imp_folder)
        abs_path_to_api_or_sign = "".join(abs_path_to_api_or_sign_split)
        abs_path_to_rng_split = abs_path_to_rng.split(optimized_imp_folder)
        abs_path_to_rng_split.insert(1, additional_imp_folder)
        abs_path_to_rng = "".join(abs_path_to_rng_split)
        path_to_include_directories_split = path_to_include_directories.split(optimized_imp_folder)
        path_to_include_directories_split.insert(1, additional_imp_folder)
        path_to_include_directories = "".join(path_to_include_directories_split)

        path_to_candidate_makefile_cmake_split = path_to_candidate_makefile_cmake.split(optimized_imp_folder)
        path_to_candidate_makefile_cmake_split.insert(1, additional_imp_folder)
        path_to_candidate_makefile_cmake = "".join(path_to_candidate_makefile_cmake_split)
        optimized_imp_folder = additional_imp_folder
    generic_compile_run_bench_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                        default_instance, instances, additional_includes,
                                        path_to_candidate_makefile_cmake, path_to_bench_binary,
                                        direct_link_or_compile_target, libraries_names, path_to_include_directories,
                                        build_with_make, additional_cmake_definitions, compiler, number_of_iterations,
                                        min_msg_len, max_msg_len, cpu_core_isolated, compilation, execution,
                                        custom_benchmark, candidate_benchmark, security_level_list, *args, **kwargs)


def run_benchmarks(candidate: str, instances, candidates_dict,
                   direct_link_or_compile_target: bool = False, implementation_type='opt',
                   security_level=None, number_of_iterations='1e3',
                   min_msg_len: Union[str, int] = '0', max_msg_len: Union[str, int] = '3300',
                   cpu_core_isolated: Union[str, list] = '1', compilation: str = 'yes',
                   execution: str = 'yes', custom_benchmark: bool = True,
                   candidate_benchmark: bool = True, *args, **kwargs):
    candidate_dict = gen.parse_candidates_json_file(candidates_dict, candidate)
    abs_path_to_api_or_sign = candidate_dict['path_to_api']
    abs_path_to_rng = candidate_dict['path_to_rng']
    optimized_imp_folder = candidate_dict['optimized_implementation']
    additional_imp_folder = candidate_dict['additional_implementation']
    additional_includes = ''
    path_to_candidate_makefile_cmake = candidate_dict['path_to_makefile_folder']
    libraries_names_all = candidate_dict['link_libraries']
    libraries_names = libraries_names_all["ct_tests"]
    bench_additional_library = libraries_names_all["bench"]
    if not instances or instances is None:
        instances = candidate_dict['instances']
    if isinstance(bench_additional_library, str):
        libraries_names.extend(bench_additional_library.split())
    elif isinstance(bench_additional_library, list):
        libraries_names.extend(bench_additional_library)
    path_to_include_directories = os.path.dirname(abs_path_to_api_or_sign)
    build_with_make = candidate_dict['build_with_makefile']
    compiler = candidate_dict['compiler']
    default_instance = candidate_dict['default_instance']
    path_to_bench_binary = candidate_dict['path_to_bench_binary']
    additional_cmake_definitions = ''  # to be fixed
    if build_with_make:
        additional_cmake_definitions = kwargs
        # additional_cmake_definitions['RUN_BENCHMARKS'] = "ON"
        print(".........additional_cmake_definitions: ", additional_cmake_definitions)
    security_levels = candidate_dict['security_level']
    security_level_list = get_instance_security_level(instances, security_levels)
    print(":::::::::::::run_benchmarks: ")
    if implementation_type == 'add':
        abs_path_to_api_or_sign_split = abs_path_to_api_or_sign.split(optimized_imp_folder)
        abs_path_to_api_or_sign_split.insert(1, additional_imp_folder)
        abs_path_to_api_or_sign = "".join(abs_path_to_api_or_sign_split)
        abs_path_to_rng_split = abs_path_to_rng.split(optimized_imp_folder)
        abs_path_to_rng_split.insert(1, additional_imp_folder)
        abs_path_to_rng = "".join(abs_path_to_rng_split)
        path_to_include_directories_split = path_to_include_directories.split(optimized_imp_folder)
        path_to_include_directories_split.insert(1, additional_imp_folder)
        path_to_include_directories = "".join(path_to_include_directories_split)

        path_to_candidate_makefile_cmake_split = path_to_candidate_makefile_cmake.split(optimized_imp_folder)
        path_to_candidate_makefile_cmake_split.insert(1, additional_imp_folder)
        path_to_candidate_makefile_cmake = "".join(path_to_candidate_makefile_cmake_split)
        optimized_imp_folder = additional_imp_folder
    generic_compile_run_bench_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                        default_instance, instances, additional_includes,
                                        path_to_candidate_makefile_cmake, path_to_bench_binary,
                                        direct_link_or_compile_target, libraries_names, path_to_include_directories,
                                        build_with_make, additional_cmake_definitions, compiler, number_of_iterations,
                                        min_msg_len, max_msg_len, cpu_core_isolated, compilation, execution,
                                        custom_benchmark, candidate_benchmark, security_level_list, *args, **kwargs)


def get_candidates_instances(candidate: str, path_to_instances_folder: str):
    instances = os.listdir(path_to_instances_folder)
    instances = [instance for instance in instances if os.path.isdir(f'{path_to_instances_folder}/{instance}')]
    instances = list(filter(lambda instance: any(candidate_pattern in instance for candidate_pattern
                                                 in [candidate.upper(), candidate.lower()]), instances))
    return instances


def run_benchmarks_all_candidates(candidates_dict: dict, implementation_type='opt', number_of_iterations='1e3',
                                  min_msg_len: Union[str, int] = '0', max_msg_len: Union[str, int] = '3300',
                                  cpu_core_isolated: Union[str, list] = '1', *args, **kwargs):
    list_of_candidates = list(candidates_dict.keys())
    print("------:::::::::::list_of_candidates: ", list_of_candidates)
    list_of_candidates = ["perk", "ryde"]
    print("------:::::::::::list_of_candidates::::::::: ", list_of_candidates)
    for candidate in list_of_candidates:
        instances = None
        security_level = None
        run_benchmarks(candidate, instances, candidates_dict, True, implementation_type,
                       security_level, number_of_iterations, min_msg_len, max_msg_len, cpu_core_isolated, 'yes',
                       'yes', True, False, *args, **kwargs)


def benchmarks_single_run_nist_candidates(candidates_dict: dict, list_of_options: list):
    ref_opt_add_impl_folder = "opt"
    min_msg_size = "1"
    max_msg_size = "3300"
    number_of_iterations = "1e3"
    cpu_cores_isolated = ["1"]
    for element in list_of_options:
        if '--optimization_folder' in element:
            ref_opt_add_impl_folder = element.split('=')[-1]
        if 'max_msg_size' in element:
            max_msg_size = element.split('=')[-1]
        if 'min_msg_size' in element:
            min_msg_size = element.split('=')[-1]
        if 'iterations' in element:
            number_of_iterations = element.split('=')[-1]
        if 'cpu_cores_isolated' in element:
            cpu_cores_isolated = element.split('=')[-1]
    run_benchmarks_all_candidates(candidates_dict, ref_opt_add_impl_folder, number_of_iterations, min_msg_size,
                                  max_msg_size, cpu_cores_isolated)

