#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import argparse

import cli as cli
import pqc_signature as signature
import benchmarks as bench


# path to user entry-point
path_to_user_entry_point = 'cttool-draft/candidates.json'
ret = signature.from_json_to_python_dict(path_to_user_entry_point)
candidates_dict, chosen_tools, libraries, benchmark_libraries = ret


# run_cli_candidate: Run candidate with CLI
def run_cli_candidate(args_parse):
    """ Function: run_cli_candidate"""
    test_mode = args.tii_ct_toolchain
    candidate = args_parse.candidate
    instances = args_parse.instances
    user_entry_point = args_parse.entry_point
    compilation = args_parse.compile
    run = args_parse.run
    direct_link_or_compile_target = args_parse.link_to_library
    direct_link_to_library = False
    algorithms = args_parse.algorithms
    implementation_type = args_parse.ref_opt_add_implementation
    additional_cmake_definitions = args_parse.cmake_definition
    cpu_cores_isolated = args_parse.cpu_cores
    add_options = args_parse.add_options
    all_candidates_dict = candidates_dict
    if 'yes' in direct_link_or_compile_target:
        direct_link_to_library = True
    # add_options = args_parse.add_options
    add_args = list(filter(lambda element: '=' not in element, add_options))
    add_kwargs_list = list(filter(lambda element: '=' in element, add_options))
    additional_options = {}
    if add_kwargs_list:
        additional_options = dict([n for n in pair.split('=')] for pair in add_kwargs_list)
    security_level = args_parse.security_level
    if test_mode == 'ct-tests':
        print(":::::::Running constant time tests")
        tools = args_parse.tools
        number_measurements = args_parse.number_measurements
        depth = args_parse.depth
        timeout = args_parse.timeout
        signature.run_tests(user_entry_point, tools, candidate, instances, all_candidates_dict, direct_link_to_library,
                            number_measurements, compilation, run, algorithms, depth, timeout, implementation_type,
                            security_level, additional_cmake_definitions, *add_args, **additional_options)
    elif test_mode == 'benchmark':
        print(":::::::Running Benchmarks")
        benchmark_templates = args_parse.bench_template
        benchmarks_keywords = args_parse.bench_keywords
        number_of_iterations = args_parse.iterations
        min_msg_length = args_parse.min_msg_len
        max_msg_length = args_parse.max_msg_len
        custom_benchmark = args_parse.custom_benchmark
        candidate_benchmark = args_parse.candidate_benchmark
        bench.run_benchmarks(user_entry_point, candidate, instances, candidates_dict, direct_link_or_compile_target,
                             algorithms, implementation_type, security_level, benchmark_templates, benchmarks_keywords,
                             number_of_iterations, min_msg_length, max_msg_length, cpu_cores_isolated, compilation, run,
                             custom_benchmark, candidate_benchmark, *add_args, **additional_options)


# Create a parser
parser = argparse.ArgumentParser(prog="tii-constant-time-toolchain",
                                 description="Constant time check with Binsec, Ctgrind (TIMECOP), Dudect",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)


subparser = parser.add_subparsers(help="", dest='tii_ct_toolchain')


# cli.cli_generate_template(subparser, '', list(cttool.supported_tools.keys()), [],
#                           None, None, 'ct-tests')
#


cli.add_cli_arguments(subparser, 'ct-tests', path_to_user_entry_point, '')
cli.add_cli_arguments(subparser, 'benchmark', path_to_user_entry_point, '')

# set all the command-line arguments into the object args
args = parser.parse_args()


def main():
    """ Function: main"""
    run_cli_candidate(args)


if __name__ == "__main__":
    main()
