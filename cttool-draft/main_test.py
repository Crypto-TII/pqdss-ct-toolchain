#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import argparse

import cli as cli
import pqc_signature as signature
import benchmarks as bench
import generics_tests as gen_tests


# path to user entry-point
path_to_user_entry_point = 'cttool-draft/candidates.json'
ret = signature.from_json_to_python_dict(path_to_user_entry_point)
candidates_dict, chosen_tools, libraries, benchmark_libraries = ret


# GENERICS TESTS: path to user entry-point
path_to_user_entry_point_generic_tests = 'cttool-draft/generics_tests.json'
ret_gen_tests = gen_tests.parse_json_to_dict_generic_tests(path_to_user_entry_point_generic_tests)
targets, generic_tests_chosen_tools = ret_gen_tests

# print("---targets: ", targets)
# print("---generic_tests_chosen_tools: ", generic_tests_chosen_tools)


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
        additional_options['RUN_CT_TESTS'] = "ON"
        additional_options['RUN_BENCHMARKS'] = "OFF"
        signature.run_tests(user_entry_point, tools, candidate, instances, all_candidates_dict, direct_link_to_library,
                            number_measurements, compilation, run, algorithms, depth, timeout, implementation_type,
                            security_level, additional_cmake_definitions, *add_args, **additional_options)
    elif test_mode == 'benchmark':
        print(":::::::Running Benchmarks")
        number_of_iterations = args_parse.iterations
        min_msg_length = args_parse.min_msg_len
        max_msg_length = args_parse.max_msg_len
        custom_benchmark = args_parse.custom_benchmark
        candidate_benchmark = args_parse.candidate_benchmark
        if custom_benchmark.strip() == 'yes':
            custom_benchmark = True
        if candidate_benchmark is None or candidate_benchmark.strip() == 'no':
            candidate_benchmark = False
        elif candidate_benchmark.strip() == 'yes':
            candidate_benchmark = True
        additional_options['RUN_BENCHMARKS'] = "ON"
        additional_options['RUN_CT_TESTS'] = "OFF"
        bench.run_benchmarks(candidate, instances, candidates_dict, direct_link_or_compile_target,
                             implementation_type, security_level, number_of_iterations,
                             min_msg_length, max_msg_length, cpu_cores_isolated, compilation, run, custom_benchmark,
                             candidate_benchmark, *add_args, **additional_options)

    elif test_mode == 'generic-tests':
        targets_basename = args_parse.target
        tools = args_parse.tools
        print("_______user_entry_point: ", user_entry_point)
        print("targets_basename: ", targets_basename)
        print("tools: ", tools)
        gen_tests.generic_tests_templates(user_entry_point, targets_basename, tools)


# Define a new class action for the flag -a (--all).
class RunAllCandidates(argparse.Action):
    def __init__(self, option_strings,  dest, **kwargs):
        return super().__init__(option_strings , dest, nargs='+', default=argparse.SUPPRESS, **kwargs)

    def __call__(self, parser, namespace, values, option_string, **kwargs):
        tools_list = [val for val in values if '=' not in val]
        list_of_options = [opt for opt in values if opt not in tools_list]
        bench.benchmarks_single_run_nist_candidates(candidates_dict, tools_list)
        parser.exit()


# Create a parser
parser = argparse.ArgumentParser(prog="tii-constant-time-toolchain",
                                 description="Constant time check with Binsec, Ctgrind (TIMECOP), Dudect",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)


subparser = parser.add_subparsers(help="", dest='tii_ct_toolchain')

cli.add_cli_arguments(subparser, 'ct-tests', path_to_user_entry_point, '')
cli.add_cli_arguments(subparser, 'benchmark', path_to_user_entry_point, '')
cli.add_cli_arguments(subparser, 'generic-tests', path_to_user_entry_point, '')


parser.add_argument('-a', '--all',
                    action=RunAllCandidates,
                    help='Run a given tool on all instances of all candidates',
                    )

# set all the command-line arguments into the object args
args = parser.parse_args()


def main():
    """ Function: main"""
    run_cli_candidate(args)


if __name__ == "__main__":
    main()
