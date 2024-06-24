#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import argparse

import generic_templates as gen_templates


# add_generic_cli_templates_arguments: for generic tests, create a subparser for a given target
def add_generic_cli_templates_arguments(subparser,
                                        generate_template_run,
                                        tools_list=None,
                                        target_basename=None,
                                        path_to_header_file=None,
                                        path_to_target_test_file=None,
                                        target_secret_inputs=None,
                                        additional_includes=None,
                                        target_dependent_src_files=None,
                                        target_dependent_header_files=None,
                                        target_include_directory=None,
                                        target_cflags=None,
                                        target_libraries=None,
                                        target_build_directory=None,
                                        runtime_output_directory=None,
                                        template_only=None,
                                        compile_and_run_only=None,
                                        run_only=None,
                                        redirect_test_output_to_file=None,
                                        security_level=None,
                                        number_of_measurements='1e4',
                                        timeout='86400'):

    if target_secret_inputs is None:
        target_secret_inputs = []
    if target_cflags is None:
        target_cflags = []
    if target_dependent_src_files is None:
        target_dependent_src_files = []
    if target_dependent_header_files is None:
        target_dependent_header_files = []
    if additional_includes is None:
        additional_includes = []
    if target_include_directory is None:
        target_include_directory = []

    generic_parser = subparser.add_parser(f'{generate_template_run}',
                                          help=f'{generate_template_run}:...',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Default tools list
    default_tools_list = ["binsec", "ctgrind", "dudect", "flowtracker", "ctverif"]
    arguments = f"'--tools', '-tools', dest='tools', nargs='+', default={default_tools_list}, help = '{tools_list}'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--target_header', '-type',dest='header',type=str,default=f'{path_to_header_file}', \
    help=' {path_to_header_file}'"
    add_args_commdand = f"generic_parser.add_argument(f{arguments})"
    exec(add_args_commdand)
    arguments = f"'--target_basename', '-target',dest='target',type=str,default=f'{target_basename}', \
    help ='target basename'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--test_harness', '-test_harness',dest='test_harness', type=str, \
    default=f'{path_to_target_test_file}',"
                 f"help = 'path to the test harness file'")
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--secret_inputs', nargs='+', default={target_secret_inputs}"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--additional_includes', nargs='+', default={additional_includes}"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--required_sources_files', nargs='+', default={target_dependent_src_files}, \
    help = 'required source files'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--required_include_files', nargs='+', default={target_dependent_header_files}, \
    help = 'required header files'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--include_directories', nargs='+', default={target_include_directory}, help = 'include directories'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--cflags', nargs='+', default={target_cflags}, help = 'target cflags for compilation'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--libraries', nargs='+', default={target_libraries}, help = 'target link libraries'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--build', '-build', dest='build',default=f'{target_build_directory}'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--runtime_output_directory', '-runtime_output_directory', dest='runtime', \
    default=f'{runtime_output_directory}'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--template_only','-template_only',dest='template_only', default=f'{template_only}',help = 'no'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--compile_run','-compile_run',dest='compile_run', default=f'{compile_and_run_only}', help='no'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--run_only','-run_only',dest='run_only', default=f'{run_only}', help='no'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--redirect_output','-redirect_output',dest='redirect_output', \
    default=f'{redirect_test_output_to_file}', help='no'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--security_level','-security_level', dest='security_level', default={security_level},\
    help = 'Instance security level'")
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--number_measurements','-number_measurements', dest='number_measurements',\
     default={number_of_measurements}, help = 'Number of measurements (Dudect)'")
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--timeout','-timeout', dest='timeout',\
     default={timeout}, help = 'timeout (Dudect)'")
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)


# =============================== CLI: use argparse module ===========================
# ====================================================================================


# run_cli_candidate: Run candidate with CLI
def run_cli_candidate(args_parse):
    """ Function: run_cli_candidate"""
    candidate = args.binsec_test
    list_of_tools = args_parse.tools
    build_directory = args_parse.build
    security_level = args_parse.security_level
    number_measurements = args_parse.number_measurements
    timeout = args_parse.timeout
    if candidate == 'generic_tests':
        print("::::::: Running generic tests")
        target_header_file = args_parse.header
        target_basename = args_parse.target
        target_test_harness = args_parse.test_harness
        target_secret_inputs = args_parse.secret_inputs
        target_additional_includes = args_parse.additional_includes
        target_required_src_files = args_parse.required_sources_files
        target_required_include_files = args_parse.required_include_files
        target_include_directories = args_parse.include_directories
        target_cflags = args_parse.cflags
        target_libraries = args_parse.libraries
        target_runtime_output_directory = args_parse.runtime
        target_template_only = args_parse.template_only
        target_compile_run = args_parse.compile_run
        target_run_only = args_parse.run_only
        target_redirect_output = args_parse.redirect_output
        generic_arguments = f'''{list_of_tools}, f'{target_header_file}', f'{target_basename}',
                         f'{target_test_harness}', {target_secret_inputs},
                         {target_required_src_files}, f'{target_required_include_files}', {target_include_directories},
                         f'{target_cflags}', f'{target_libraries}', {build_directory},
                         f'{target_runtime_output_directory}', {target_template_only},
                         f'{target_compile_run}', f'{target_redirect_output}',
                        f'{security_level}',
                        f'{number_measurements}', f'{timeout}' '''
        template_arguments = f'''{list_of_tools}, f'{target_basename}', f'{target_header_file}', {target_secret_inputs}, f'{target_test_harness}',
        {target_additional_includes}
        '''
        # execution_arguments = f'''{executable_file}, {config_file}, {output_file}, {sse_depth}, {stats_file}, {timeout},
        # {additional_options}
        # '''


        #tool = list_of_tools[0]
        # tool_obj = gen_templates.Tools(tool)
        # tool_obj.tool_template(target_basename,target_header_file,target_secret_inputs,target_test_harness,None)
        # tool_obj.tool_execution(executable_file,config_file,output_file,sse_depth, stats_file,timeout,additional_options)
        # target_create_template = f'tool_obj.tool_template({template_arguments})'
        # target_execution = f'tool_obj.tool_execution({execution_arguments})'
        target_template_only = target_template_only.strip()
        target_template_only = target_template_only.lower()
        target_run_only = target_run_only.strip()



        # generic_template(tools_list: list, target_basename: str, target_header_file,
        # secret_arguments, path_to_test_harness, includes)
        target_create_template = f'gen_templates.generic_template({template_arguments})'
        if target_template_only == 'yes' or 'y' in target_template_only:
            exec(target_create_template)
        elif target_run_only.lower() == 'yes' or 'y' in target_run_only.lower():
            pass
            # exec(target_execution)
        elif target_compile_run:
            exec(target_create_template)
            # exec(target_execution)






# Create a parser
parser = argparse.ArgumentParser(prog="NIST-Signature",
                                 description="Constant time check with Binsec, Ctgrind, Dudect and Flowtracker",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)


subparser = parser.add_subparsers(help="", dest='binsec_test')

# parser.add_argument('-a', '--all',
#                     action=RunAllCandidates,
#                     help='Run a given tool on all instances of all candidates',
#                     )

# Add a subparser for manual tests for any target implementation, not necessarily one of the signatures
#generic_subparser = parser.add_subparsers(help="", dest='generic_test')


# add_generic_cli_templates_arguments(subparser, 'generic_tests', 'template', '')
add_generic_cli_templates_arguments(subparser, 'generic_tests')


# set all the command-line arguments into the object args
args = parser.parse_args()


def main():
    """ Function: main"""
    run_cli_candidate(args)


if __name__ == "__main__":
    main()
