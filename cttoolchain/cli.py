#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import argparse
import subprocess
import sys
from typing import Optional, Union, List


# add_cli_arguments: create a parser for a given candidate
def add_cli_arguments(subparser,
                      test_mode,
                      path_to_user_entry_point: str,
                      candidate,
                      candidate_default_instances=None,
                      optimized_imp_folder: str = 'opt',
                      additional_required_includes=None,
                      additional_cmake_definitions=None,
                      link_to_library: bool = True,
                      number_of_measurements='1e4',
                      timeout='900',
                      implementation_type='opt'):
    # Default algorithms pattern to test
    default_algorithms = ["keypair", "sign"]
    if candidate_default_instances is None:
        candidate_default_instances = []
    candidate_parser = subparser.add_parser(f'{test_mode}',
                                            help=f'{test_mode}:...',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cpu_cores_isolated = ["1", "2", "3"]
    security_level = None
    benchmark = None
    # Default tools list
    default_tools_list = ["binsec", "timecop", "dudect"]
    arguments = f"'--entry_point', '-entry-point',dest='entry_point',type=str,default=f'{path_to_user_entry_point}', \
        help='user provided entry file'"
    add_args_commdand = f"candidate_parser.add_argument(f{arguments})"
    exec(add_args_commdand)
    arguments = f"'--candidate', '-candidate',dest='candidate',type=str,default=f'{candidate}',help ='{candidate}'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--optimization_folder', '-opt_folder',dest='ref_opt', type=str, default=f'{optimized_imp_folder}',"
                 f"help = '{optimized_imp_folder}'")
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--path_to_target_binary', '-target_binary',dest='target_binary', type=str, default='Yes',"
                 f"help = 'Path to the target function binary (library, object file)'")
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--direct_link_to_library', '-link_to_library',dest='link_to_library', type=str,"
                 f"default=f'{link_to_library}', help = 'Direct link to library or compile target'")
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--instances', nargs='+', default={candidate_default_instances}"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--path_to_api', '-api',dest='api',type=str, help = 'api'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--path_to_rng', '-rng', dest='rng',type=str"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--compile', '-compile', dest='compile',default='Yes'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--run', '-run', dest='run',default='Yes'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--build_with_makefile', '-with_makefile', dest='with_makefile',default=True"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--build', '-build', dest='build',default='build'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--algorithms', nargs='+', default={default_algorithms},help = 'algorithms (keypair, sign, verifi)'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--additional_required_includes', '-add_includes', dest='required_incs', nargs='+',"
                 f"default={additional_required_includes},help = 'additional required includes'")
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--cmake_additional_definitions','-cmake_definition', nargs='+', dest='cmake_definition', \
    default={additional_cmake_definitions},help = 'List of CMake additional definitions if any'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--security_level','-security_level', dest='security_level', default={security_level},\
    help = 'Instance security level'")
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--ref_opt_add_implementation','-ref_opt_add', dest='ref_opt_add_implementation',\
     default=f'{implementation_type}', help = 'Opt., Add. or Ref. implementation'")
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--additional_options', '-add_options', dest='add_options', nargs='*', default='',"
                 f" help = 'Additional options'")
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)

    arguments = (f"'--cpu_cores_isolated', '-cpu_cores', dest='cpu_cores', nargs='+',"
                 f"default={cpu_cores_isolated}, help = 'cpu cores isolated'")
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)

    if test_mode == 'pqdss-ct-tests':
        arguments = f"'--tools', '-tools', dest='tools', nargs='+', default={default_tools_list}, help = 'tools'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--number_measurements','-number_measurements', dest='number_measurements',\
         default={number_of_measurements}, help = 'Number of measurements (Dudect)'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--timeout','-timeout', dest='timeout',\
         default={timeout}, help = 'timeout (Dudect)'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--depth', '-depth', dest='depth',default='1000000',help = 'depth'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
    if test_mode == 'pqdss-benchmarks':
        default_algorithms.append('verify')
        arguments = (f"'--benchmark_keyword', '-bench_keywords', dest='bench_keywords', nargs='+',"
                     f"default='', help = 'Benchmarks average, mean, quartile'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--iterations', '-iterations', dest='iterations', default='1000', help = 'number of iterations'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--min_msg_size', '-min_msg_len', dest='min_msg_len', default='1', help = 'minimum message size'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--max_msg_size', '-max_msg_len', dest='max_msg_len', default='3300',"
                     f"help = 'maximum message size'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--custom_benchmark', '-custom_benchmark', dest='custom_benchmark',  default='yes', "
                     f"help= 'Custom benchmark'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--candidate_benchmark', '-candidate_benchmark', dest='candidate_benchmark', "
                     f"help = 'Candidates benchmark'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
    if test_mode == 'generic-ct-tests':
        arguments = f"'--tools', '-tools', dest='tools', nargs='+', default={default_tools_list}, help = 'tools'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--target_basename', '-target',dest='target', nargs='+', help ='target basename'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--test_harness', '-test_harness',dest='test_harness', type=str, \
        help = 'path to the test harness file'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--runtime_output_directory', '-runtime_output_directory', dest='runtime', \
        default='build'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--template_only','-template_only',dest='template_only',help = 'no', default='no'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--compile_run','-compile_run',dest='compile_run', help='no', default='no'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--redirect_output','-redirect_output',dest='redirect_output', default='yes', help='no'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--number_measurements','-number_measurements', dest='number_measurements',\
         default={number_of_measurements}, help = 'Number of measurements (Dudect)'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--timeout','-timeout', dest='timeout',\
         default={timeout}, help = 'timeout (Dudect)'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--depth', '-depth', dest='depth',default='1000000',help = 'depth'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = f"'--run_test_only','-run_test_only',dest='run_test_only', default='no', help='no'"
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
        arguments = (f"'--compilation_flags', '-compilation_flags', dest='compilation_flags', nargs='+',"
                     f" help = 'compilation flags'")
        add_args_commdand = f"candidate_parser.add_argument({arguments})"
        exec(add_args_commdand)
