#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import sys
import json
import subprocess
import shutil
from subprocess import Popen

from typing import Optional, Union, List

import tools
import generics as gen


def set_benchmark_template(template: str, algorithm: Union[str, list], number_of_executions: Union[str, int] = '1e3'):
    pass


def generate_template(number_of_executions: Union[str, int] = '1e3'):
    pass


def bench_candidate(path_to_benchmark_binary: str, cpu_core_isolated: Union[str, list] = '1',
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


def generate_template_candidate(abs_path_to_api_or_sign, abs_path_to_rng, path_to_benchmark_folder,
                                add_includes, number_of_executions='1e3'):

    list_of_path_to_folders = [path_to_benchmark_folder]
    gen.generic_create_tests_folders(list_of_path_to_folders)
    api_or_sign = os.path.basename(abs_path_to_api_or_sign)
    api_or_sign = f'"{api_or_sign}"'
    rng = os.path.basename(abs_path_to_rng)
    rng = f'"{rng}"'

    test_keypair = f'{path_to_benchmark_folder}/bench.c'
    ret_kp = gen.keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type_kp, f_basename_kp, args_types_kp, args_names_kp = ret_kp
    ret_sign = gen.sign_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type_s, f_basename_s, args_types_s, args_names_s = ret_sign
    # ret_verif = gen.verif_find_args_types_and_names(abs_path_to_api_or_sign)


def generate_benchmarks(candidate, abs_path_to_api_or_sign, abs_path_to_rng,
                        instance_folder, add_includes, number_of_executions='1e3'):
    path_candidate = f'{abs_path_to_api_or_sign.split(candidate)[0]}/{candidate}'
    path_to_benchmark_folder = path_candidate
    if not instance_folder == "":
        path_to_benchmark_folder += f'/{instance_folder}'
    path_to_benchmark_folder += f'/benchmarks'
    generate_template_candidate(abs_path_to_api_or_sign, abs_path_to_rng, path_to_benchmark_folder,
                                add_includes, number_of_executions)


def generic_benchmarks_nist_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng, instances_list,
                                      add_includes, number_of_executions: Union[str, int] = '1e3'):
    list_of_instances = []
    if not instances_list:
        list_of_instances = [""]
    else:
        for instance_folder in instances_list:
            list_of_instances.append(instance_folder)
    for instance in list_of_instances:
        generate_benchmarks(candidate, abs_path_to_api_or_sign, abs_path_to_rng,
                            instance, add_includes, number_of_executions)


def generic_benchmarks_init_compile(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                    default_instance: str, instances, additional_includes,
                                    path_to_candidate_makefile_cmake, direct_link_or_compile_target: bool = True,
                                    libraries_names: Union[str, list] = 'lcttest',
                                    path_to_include_directories: Union[str, list] = '', build_with_make: bool = True,
                                    additional_cmake_definitions=None, number_of_executions='1e4',
                                    compiler: str = 'gcc', binary_patterns: Optional[Union[str, list]] = None,
                                    benchmark_templates: Optional[Union[str, list]] = None, *args, **kwargs):

    if benchmark_templates is not None:
        generic_benchmarks_nist_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng,
                                          instances, additional_includes, number_of_executions)

    cflags = [] # to be fixed
    path_candidate = abs_path_to_api_or_sign.split(candidate)[0]
    if path_candidate.endswith('/'):
        path_candidate += candidate
    else:
        path_candidate += f'/{candidate}'
    path_to_test_library_directory = f'{path_to_candidate_makefile_cmake}/build'
    if not direct_link_or_compile_target:
        if not instances:
            gen.compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
                                         additional_cmake_definitions, *args, **kwargs)
        else:
            for instance in instances:
                path_to_candidate_makefile_cmake_split = path_to_candidate_makefile_cmake.split(default_instance)
                path_to_candidate_makefile_cmake_split.insert(1, instance)
                path_to_candidate_makefile_cmake = "".join(path_to_candidate_makefile_cmake_split)
                gen.compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
                                             additional_cmake_definitions, *args, **kwargs)
    if benchmark_templates is not None:
        gen.generic_target_compilation(path_candidate, path_to_test_library_directory, libraries_names,
                                       path_to_include_directories, cflags, default_instance, instances,
                                       compiler, binary_patterns)

def run_benchmarks(user_entry_point: str, candidate: str, instances, candidates_dict,
                   direct_link_or_compile_target: bool = False, number_of_executions='1e3',
                   binary_patterns: Optional[Union[str, list]] = None, implementation_type='opt',
                   security_level=None, benchmark_templates: Optional[Union[list, str]] = None,
                   benchmarks_keywords: Optional[list] = None, *args, **kwargs):
    candidates_dict = gen.parse_candidates_json_file(candidates_dict, candidate)
    abs_path_to_api_or_sign = candidates_dict['path_to_api']
    abs_path_to_rng = candidates_dict['path_to_rng']
    optimized_imp_folder = candidates_dict['optimized_implementation']
    additional_imp_folder = candidates_dict['additional_implementation']
    additional_includes = ''
    path_to_candidate_makefile_cmake = candidates_dict['path_to_makefile_folder']
    libraries_names = candidates_dict['link_libraries']
    path_to_include_directories = "/".join(abs_path_to_api_or_sign.split('/')[:-1])
    build_with_make = candidates_dict['build_with_makefile']
    compiler = candidates_dict['compiler']
    default_instance = candidates_dict['default_instance']
    benchmark_keywords = candidates_dict['benchmark_keywords']
    additional_cmake_definitions = '' # to be fixed

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
    generic_benchmarks_init_compile(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                                    default_instance, instances, additional_includes, path_to_candidate_makefile_cmake,
                                    direct_link_or_compile_target, libraries_names, path_to_include_directories,
                                    build_with_make, additional_cmake_definitions, number_of_executions, compiler,
                                    binary_patterns, benchmark_templates, *args, **kwargs)
