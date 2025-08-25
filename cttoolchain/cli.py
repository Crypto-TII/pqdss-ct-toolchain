#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
from typing import Optional, Union


# add_cli_arguments: create a parser for a given candidate
def add_cli_arguments(subparser,
                      test_mode: str,
                      path_to_user_entry_point: str,
                      candidate: Union[str, list],
                      candidate_default_instances: Optional[str] = None,
                      optimized_imp_folder: str = 'opt',
                      additional_required_includes: Optional[Union[str, list]] = None,
                      additional_cmake_definitions: Optional[Union[str, list, dict]] = None,
                      link_to_library: bool = True,
                      number_of_measurements: str = '1e4',
                      timeout: str = '900',
                      implementation_type: str = 'opt'):
    # Default algorithms pattern to test
    default_algorithms = ["sign"]
    if candidate_default_instances is None:
        candidate_default_instances = []
    candidate_parser = subparser.add_parser(f'{test_mode}',
                                            help=f'{test_mode}:...',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cpu_cores_isolated = ["1", "2", "3"]
    security_level = None
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
