#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse

import cli as cli
import pqdss_ct_tests as signature

# path to user entry-point
path_to_user_entry_point = 'user_entry_point/candidates.json'
ret = signature.from_json_to_python_dict(path_to_user_entry_point)
candidates_dict, chosen_tools, libraries = ret


# run_cli_candidate: Run candidate with CLI
def run_cli_candidate(args_parse):
    """ Function: run_cli_candidate"""
    # test_mode = args.ct_toolchain
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
    security_level = None
    if add_kwargs_list:
        additional_options = dict([n for n in pair.split('=')] for pair in add_kwargs_list)
    tools = args_parse.tools
    number_measurements = args_parse.number_measurements
    depth = args_parse.depth
    timeout = args_parse.timeout
    additional_options['RUN_CT_TESTS'] = "ON"
    additional_options['RUN_BENCHMARKS'] = "OFF"
    signature.run_tests(user_entry_point, tools, candidate, instances, all_candidates_dict, direct_link_to_library,
                        number_measurements, compilation, run, algorithms, depth, timeout, implementation_type,
                        security_level, additional_cmake_definitions, *add_args, **additional_options)


# Define a new class action for the flag -a (--all).
class RunAllCandidates(argparse.Action):
    def __init__(self, option_strings,  dest, **kwargs):
        super().__init__(option_strings, dest, default=argparse.SUPPRESS, **kwargs)

    def __call__(self, custom_parser, namespace, values, option_string=None):
        add_kwargs_list = list(filter(lambda element: '=' in element, values))
        additional_options = {}
        if add_kwargs_list:
            additional_options = dict([n for n in pair.split('=', 1)] for pair in add_kwargs_list)
        signature.run_ct_tests_all_candidates(path_to_user_entry_point, **additional_options)
        custom_parser.exit()


# Create a parser
parser = argparse.ArgumentParser(prog="constant-time-toolchain",
                                 description="Constant time check with Binsec, Timecop, Dudect",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)


subparser = parser.add_subparsers(help="", dest='ct_toolchain')

cli.add_cli_arguments(subparser, 'pqdss-ct-tests', path_to_user_entry_point, '')


parser.add_argument('-a', '--all',
                    nargs='+',
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
