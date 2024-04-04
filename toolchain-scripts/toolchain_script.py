#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import argparse
import subprocess
import sys


import candidates_build as build_candidate
import generic_functions as generic


# Special cases: the following candidates need special steps for compilation

# =================================== QR-UOV ======================================
def compile_run_qr_uov(tools_list, signature_type, candidate, optimized_imp_folder,
                       instance_folders_list, rel_path_to_api, rel_path_to_sign,
                       rel_path_to_rng, to_compile, to_run, depth, build_folder,
                       binary_patterns, rng_outside_instance_folder="no", with_core_dump="yes",
                       number_of_measurements='1e4', timeout='86400', implementation_type='opt'):
    """ Function: compile_run_qr_uov"""

    build_candidate.compile_run_qr_uov(tools_list, signature_type, candidate, optimized_imp_folder,
                                       instance_folders_list, rel_path_to_api, rel_path_to_sign,
                                       rel_path_to_rng, to_compile, to_run, depth, build_folder,
                                       binary_patterns, rng_outside_instance_folder, with_core_dump,
                                       number_of_measurements, timeout, implementation_type)


def compile_run_candidate(tools_list, signature_type, candidate, optimized_imp_folder,
                          instance_folders_list, rel_path_to_api_or_sign, sources, headers, target_functions,
                          add_required_includes, rel_path_to_rng, to_compile, to_run, depth, build_folder,
                          binary_patterns, rng_outside_instance_folder="no", with_core_dump="yes",
                          additional_cmake_definitions=None, security_level=None,
                          number_of_measurements='1e4', timeout='86400', implementation_type='opt'):
    """ Function: compile_run_candidate"""
    candidates_to_build_with_makefile = ["mirith", "mira", "mqom", "perk", "ryde", "pqsigrm", "wave", "prov",
                                         "snova", "tuov", "uov", "vox", "aimer", "ascon_sign", "faest",
                                         "sphincs_alpha", "preon", "squirrels", "hawk", "meds",
                                         "hufu", "meds", "fuleeca", "eaglesign", "ehtv3v4", "sdith", "biscuit",
                                         "dme_sign", "hppc", "wise", "alteq", "emle", "kaz_sign", "xifrat"]
    candidate_to_build_with_cmake = ["cross", "less", "mayo", "sqisign", "haetae"]
    if candidate in candidates_to_build_with_makefile:
        add_includes = []
        with_cmake = 'no'
        if candidate == "tuov" or candidate == "uov":
            rng_outside_instance_folder = 'yes'
        if candidate == "eaglesign":
            for inst in instance_folders_list:
                incs = f'"../../../{inst}/params.h"'
                add_includes.append(incs)
        if candidate == 'alteq':
            path_to_impl_folder = f'candidates/other/alteq/{optimized_imp_folder}'
            cmd_str = f'cp {path_to_impl_folder}/api/api.h.1.fe {path_to_impl_folder}/api.h'
            cmd = cmd_str.split()
            subprocess.call(cmd, stdin=sys.stdin)
        if candidate == 'xifrat':
            print('-------')
        if candidate == 'ehtv3v4':
            if tools_list[0].strip() == 'ctverif':
                incs = f'"api.h"'
                add_includes.append(incs)
        if candidate == 'sdith':
            if tools_list[0].strip() == 'ctverif':
                incs = f'"api.h"'
                add_includes.append(incs)
        generic.generic_compile_run_candidate(tools_list, signature_type, candidate,
                                              optimized_imp_folder, instance_folders_list,
                                              rel_path_to_api_or_sign, rel_path_to_rng, sources, headers,
                                              target_functions, add_required_includes,
                                              with_cmake, add_includes, to_compile, to_run,
                                              depth, build_folder, binary_patterns,
                                              rng_outside_instance_folder, with_core_dump,
                                              additional_cmake_definitions, security_level,
                                              number_of_measurements, timeout, implementation_type)
    if candidate in candidate_to_build_with_cmake:
        add_includes = []
        with_cmake = 'yes'
        if tools_list[0].strip() == 'flowtracker':
            with_cmake = 'no'
        if candidate == 'mayo':
            rng_outside_instance_folder = 'yes'
        generic.generic_compile_run_candidate(tools_list, signature_type, candidate,
                                              optimized_imp_folder, instance_folders_list,
                                              rel_path_to_api_or_sign, rel_path_to_rng, sources, headers,
                                              target_functions, add_required_includes,
                                              with_cmake, add_includes, to_compile, to_run,
                                              depth, build_folder, binary_patterns,
                                              rng_outside_instance_folder, with_core_dump,
                                              additional_cmake_definitions, security_level,
                                              number_of_measurements, timeout, implementation_type)
    # Special cases
    if candidate == "raccoon":
        add_includes = []
        with_cmake = 'sh'
        if tools_list[0].strip() == 'flowtracker':
            with_cmake = 'no'
        generic.generic_compile_run_candidate(tools_list, signature_type, candidate,
                                              optimized_imp_folder, instance_folders_list,
                                              rel_path_to_api_or_sign, rel_path_to_rng, sources, headers,
                                              target_functions, add_required_includes,
                                              with_cmake, add_includes, to_compile, to_run,
                                              depth, build_folder, binary_patterns,
                                              rng_outside_instance_folder, with_core_dump,
                                              additional_cmake_definitions, security_level,
                                              number_of_measurements, timeout, implementation_type)
    # if candidate == "qr_uov":
    #     compile_run_qr_uov(tools_list, signature_type, candidate, optimized_imp_folder,
    #                        instance_folders_list, rel_path_to_api_or_sign, rel_path_to_sign,
    #                        rel_path_to_rng, to_compile, to_run, depth, build_folder,
    #                        binary_patterns, rng_outside_instance_folder, with_core_dump,
    #                        number_of_measurements, timeout, implementation_type)


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
        test_harness = args_parse.test_harness
        target_secret_inputs = args_parse.secret_inputs
        target_required_src_files = args_parse.required_sources_files
        target_required_include_files = args_parse.required_include_files
        target_include_directories = args_parse.include_directories
        target_cflags = args_parse.cflags
        target_libraries = args_parse.libraries
        target_runtime_output_directory = args_parse.runtime
        target_template_only = args_parse.template_only
        target_compile_run = args_parse.compile_run
        target_redirect_output = args_parse.redirect_output
        generic_arguments = f'''{list_of_tools}, f'{target_header_file}', f'{target_basename}',
                         f'{test_harness}', {target_secret_inputs},
                         {target_required_src_files}, f'{target_required_include_files}', {target_include_directories},
                         f'{target_cflags}', f'{target_libraries}', {build_directory},
                         f'{target_runtime_output_directory}', {target_template_only},
                         f'{target_compile_run}', f'{target_redirect_output}',
                        f'{security_level}',
                        f'{number_measurements}', f'{timeout}' '''
    else:
        print(":::::::Running NIST-pqc signatures candidates tests")
        print("======= Target candidate: ", candidate)
        type_based_signature = args_parse.type
        target_candidate = args_parse.candidate
        optimization_folder = args_parse.ref_opt
        list_of_instance_folders = args_parse.instance_folders_list
        relative_path_to_api_or_sign = args_parse.api
        relative_path_to_rng = args_parse.rng
        sources_files = args_parse.src
        headers = args_parse.headers
        target_functions = args_parse.target_functions
        relative_path_to_add_req_incs = args_parse.required_incs
        compile_candidate = args_parse.compile
        run_candidate = args_parse.run
        binsec_depth_flag = args_parse.depth
        executable_patterns = args_parse.algorithms_patterns
        is_rng_in_different_folder = args_parse.rng_outside
        with_core_dump = args_parse.core_dump
        cmake_additional_definitions = args_parse.cmake_definition
        implementation_type = args_parse.ref_opt_add_implementation
        # Get candidate implementation folder
        candidate_implementation_folder = f'{candidate}_implementations_folders'
        impl_folder = f"candidate_chosen_implementation_folder = {candidate_implementation_folder}['{implementation_type}']"
        loc = {}
        exec(impl_folder, globals_vars, loc)
        candidate_chosen_implementation_folder = loc['candidate_chosen_implementation_folder']
        optimization_folder = candidate_chosen_implementation_folder
        # Set candidate default list of folders according to the chosen implementation
        candidate_chosen_implementation_folder = f"{optimization_folder}"
        candidate_list_of_instances = list_of_instance_folders
        if len(list_of_instance_folders) >= 2:
            path_to_candidate_opt_folder = f'{type_based_signature}/{candidate}/{candidate_chosen_implementation_folder}'
            candidate_list_of_instances = os.listdir(path_to_candidate_opt_folder)
            candidate_list_of_instances = [inst for inst in candidate_list_of_instances if '.' not in inst]
            exclude_files = ['README', 'Readme', 'LICENSE', 'Makefile']
            candidate_list_of_instances = [inst for inst in candidate_list_of_instances if inst not in exclude_files]
        list_of_instance_folders = candidate_list_of_instances
        arguments = f'''{list_of_tools}, f'{type_based_signature}', f'{target_candidate}',
                         f'{optimization_folder}', {list_of_instance_folders},
                         f'{relative_path_to_api_or_sign}', {sources_files}, {headers}, {target_functions},
                         {relative_path_to_add_req_incs}, f'{relative_path_to_rng}',
                         f'{compile_candidate}', f'{run_candidate}', {binsec_depth_flag},
                         f'{build_directory}', {executable_patterns},
                         f'{is_rng_in_different_folder}', f'{with_core_dump}',
                        {cmake_additional_definitions}, f'{security_level}',
                        f'{number_measurements}', f'{timeout}', f'{implementation_type}' '''
        target = f'compile_run_candidate({arguments})'
        if optimization_folder:
            exec(target)
        else:
            print("---'{}' has no Additional Implementation or it is not taken into account yet.".format(candidate.upper()))


# Add_cli_arguments_for_all_candidates: Create a parser for all candidates in the sub-parser and
# add arguments in its namespace
def add_cli_arguments_for_all_candidates(sub_parser):
    """ Function: add_cli_arguments_for_all_candidates"""
    default_implementation = 'opt'
    for signature_type, list_of_candidates in signature_type_based_candidates_dict.items():
        signature_type = f'candidates/{signature_type}'
        for candidate in list_of_candidates:
            implementation_folder = f'{candidate}_implementations_folders'
            impl_folder = f"candidate_chosen_impl_folder = {implementation_folder}['{default_implementation}']"
            loc = {}
            exec(impl_folder, globals_vars, loc)
            candidate_chosen_implementation_folder = loc['candidate_chosen_impl_folder']
            optimization_folder = candidate_chosen_implementation_folder
            # api, sign, rng, is_rng_in_cwd = candidates_api_sign_rng_path[candidate]
            candidate_data = candidates_api_sign_rng_path[candidate][0]
            api_or_sign = candidate_data['api']
            rng = candidate_data['rng']
            sources = candidate_data['src']
            headers = candidate_data['headers']
            is_rng_in_cwd = 'no'
            if len(sources) == 1:
                sources.extend(sources)
                headers.extend(headers)
            target_functions = candidate_data['targets']
            add_required_incs = None
            if 'add_incs' in candidate_data.keys():
                add_required_incs = candidate_data['add_incs']
            cand_default_list_of_instances = f'{candidate}_default_list_of_folders'
            if 'rng_same_fold' in candidate_data.keys():
                is_rng_in_cwd = candidate_data['rng_same_fold']
            cand_default_list_of_instances = f'{candidate}_default_list_of_folders'
            list_of_instances = default_list_of_instances[cand_default_list_of_instances]
            generic.add_cli_arguments(sub_parser, signature_type, candidate, optimization_folder,
                                      api_or_sign, rng, is_rng_in_cwd, sources, headers,
                                      target_functions, add_required_incs, list_of_instances, 'yes',
                                      None, '256', '1e4',
                                      '86400', 'opt')


# set_global_dictionaries: Set the (key, value) of the dictionaries: globals_vars and default_list_of_instances
def set_global_dictionaries(list_of_candidates):
    for candidate in list_of_candidates:
        cand_impl_folder = f'{candidate}_implementations_folders'
        cand_default_list_of_fold = f'{candidate}_default_list_of_folders'
        glob_var_exec = f"globals_vars['{cand_impl_folder}'] = {cand_impl_folder}"
        exec(glob_var_exec)
        default_list_exec = f"default_list_of_instances['{cand_default_list_of_fold}'] = {cand_default_list_of_fold}"
        exec(default_list_exec)


# Define a new class action for the flag -a (--all).
class RunAllCandidates(argparse.Action):
    def __init__(self, option_strings,  dest, **kwargs):
        return super().__init__(option_strings , dest, nargs='+', default=argparse.SUPPRESS, **kwargs)

    def __call__(self, parser, namespace, values, option_string, **kwargs):
        tools_list = [val for val in values if '=' not in val]
        list_of_options = [opt for opt in values if opt not in tools_list]
        generic.run_given_tool_on_all_candidates(tools_list, list_of_integrated_candidates, list_of_options)
        parser.exit()


# Create a parser
parser = argparse.ArgumentParser(prog="NIST-Signature",
                                 description="Constant time check with Binsec, Ctgrind, Dudect and Flowtracker",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)


subparser = parser.add_subparsers(help="", dest='binsec_test')

parser.add_argument('-a', '--all',
                    action=RunAllCandidates,
                    help='Run a given tool on all instances of all candidates',
                    )

# Add a subparser for manual tests for any target implementation, not necessarily one of the signatures
#generic_subparser = parser.add_subparsers(help="", dest='generic_test')
generic.add_generic_cli_templates_arguments(subparser, 'generic_tests', 'template', '')

# ============ Common default arguments ==============================================
# List of integrated candidates so far
# list_of_integrated_candidates = ["mira", "mqom", "perk", "ryde", "pqsigrm", "wave", "prov",
#                                  "snova", "tuov", "uov", "vox", "aimer", "ascon_sign", "faest",
#                                  "sphincs_alpha", "preon", "meds", "haetae", "fuleeca",
#                                  "hufu", "meds", "cross", "less", "mayo", "raccoon", 'squirrels', "qr_uov", "mirith",
#                                  "eaglesign", "ehtv3v4", "sdith", "biscuit", "dme_sign", "hppc", "wise",
#                                  "alteq", "emle", "kaz_sign", "xifrat"]

list_of_integrated_candidates = ["fuleeca", "less", "meds", "wave", "haetae", "hufu", "raccoon", "eaglesign",
                                 "ehtv3v4", "mira", "mirith", "mqom", "perk", "ryde", "sdith", "hppc", "wise",
                                 "snova", "aimer", "ascon_sign", "faest", "sphincs_alpha", "preon", "alteq",
                                 "emle", "kaz_sign", "pqsigrm", "squirrels", "hawk", "cross", "biscuit", "dme_sign",
                                 "mayo", "prov", "tuov", "uov", "vox"]


# Default tools list
default_tools_list = ["binsec", "ctgrind", "dudect", "flowtracker", "ctverif"]
# Default algorithms pattern to test
default_binary_patterns = ["keypair", "sign"]

# Global variables for consisting in a dictionary of whose (key, values) are the pairs
# (CANDIDATE_implementation_folders, CANDIDATE_implementation_folders) such that CANDIDATE_implementation_folders is
# also a dictionary whose keys are the keywords for Reference, Optimized and Additional implementation and the values
# are the corresponding folders.
globals_vars = {}
default_list_of_instances = {}


# Improve the message for help
default_help_message = 'compile and run test'

# Dictionary whose keys are the signature categories and the values are the list of candidates based on that category
# signature_type_based_candidates_dict = {'code': ['fuleeca', 'less', 'meds', 'pqsigrm', 'wave'],
#                                         'lattice': ['haetae', 'hufu', 'raccoon', 'squirrels', 'eaglesign', 'ehtv3v4'],
#                                         'mpc-in-the-head': ['cross', 'mira', 'mirith', 'mqom', 'perk', 'ryde', 'sdith'],
#                                         'multivariate': ['mayo', 'prov', 'qr_uov', 'snova', 'tuov', 'uov',
#                                                          'vox', 'biscuit', "dme_sign", "hppc", "wise"],
#                                         'symmetric': ['aimer', 'ascon_sign', 'faest', 'sphincs_alpha'],
#                                         'other': ['preon', 'alteq', 'emle', 'kaz_sign', 'xifrat']}

signature_type_based_candidates_dict = {'code': ['fuleeca', 'less', 'meds', 'wave', 'pqsigrm'],
                                        'lattice': ['haetae', 'hufu', 'raccoon', 'eaglesign', 'ehtv3v4', 'squirrels',
                                                    'hawk'],
                                        'mpc-in-the-head': ['mira', 'mirith', 'mqom', 'perk', 'ryde', 'sdith', 'cross'],
                                        'multivariate': ['hppc', 'wise', 'snova', 'biscuit', 'dme_sign',  'mayo',
                                                         'prov', 'tuov', 'uov', 'vox'],
                                        'symmetric': ['aimer', 'ascon_sign', 'faest', 'sphincs_alpha'],
                                        'other': ['preon', 'alteq', 'emle', 'kaz_sign']}


# candidates_api_sign_rng_path: dictionary whose keys and values are such that:
#   key:  candidate;
#   values: list consisting of the api, sign, rng relative path (as explained in the README.md), respond to the
#   'is the rng in the same folder as a given instance of the candidate'
depth_2 = '../../'
candidates_api_sign_rng_path = {'fuleeca': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h', 'rng_same_fold': 'no',
                                             'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../sign.h'],
                                             'targets': ['crypto_sign_keypair', 'crypto_sign'], 'add_incs': None}],
                                'less': [{'api': f'{depth_2}include/api.h', 'rng': f'{depth_2}include/rng.h',
                                          'rng_same_fold': 'no', 'src': [f'{depth_2}lib/LESS.c'],
                                          'headers': [f'{depth_2}include/LESS.h'],
                                          'targets': ['LESS_keygen', 'LESS_sign']}],
                                'meds': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                          'src': [f'{depth_2}../meds.c'], 'headers': [f'{depth_2}../api.h'],
                                          'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'pqsigrm': [{'api': f'{depth_2}pqsigrm613/src/api.h', 'rng': f'{depth_2}pqsigrm613/src/rng.h',
                                             'src': [f'{depth_2}../keypair.c', f'{depth_2}../sign.c'],
                                             'headers': [f'{depth_2}../api.h', f'{depth_2}../api.h'],
                                             'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'wave': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../NIST-kat/rng.h',
                                          'src': [f'{depth_2}../keygen.c', f'{depth_2}../api.c'],
                                          'headers': [f'{depth_2}../keygen.h', f'{depth_2}../api.h'],
                                          'targets': ['keygen', 'crypto_sign']}],
                                'haetae': [{'api': f'{depth_2}include/sign.h', 'rng': f'{depth_2}include/randombytes.h',
                                            'src': [f'{depth_2}src/sign.c'], 'headers': [f'{depth_2}include/sign.h'],
                                            'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'hufu': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                          'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../api.h'],
                                          'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'hawk': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                          'src': [f'{depth_2}../api.c'], 'headers': [f'{depth_2}../api.h'],
                                          'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'raccoon': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                             'src': [f'{depth_2}../racc_core.c'], 'headers': [f'{depth_2}../racc_core.h'],
                                             'targets': ['racc_core_keygen', 'racc_core_sign']}],
                                'eaglesign': [{'api': f'{depth_2}../sign.h', 'rng': f'{depth_2}../rng.h',
                                               'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../sign.h'],
                                               'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'ehtv3v4': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                             'src': [f'{depth_2}../eht_keygen.c', f'{depth_2}../eht_siggen.c'],
                                             'headers': [f'{depth_2}../eht_keygen.h', f'{depth_2}../eht_siggen.h'],
                                             'targets': ['key_gen', 'sig_gen']}],
                                'squirrels': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../../KAT/generator/katrng.h', 'rng_same_fold': 'yes',
                                               'src': [f'{depth_2}../nist.c'], 'headers': [f'{depth_2}../api.h'],
                                               'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'cross': [{'api': f'{depth_2}include/api.h', 'rng': '', 'src': [f'{depth_2}lib/CROSS.c'],
                                           'headers': [f'{depth_2}include/CROSS.h'],
                                           'targets': ['CROSS_keygen', 'CROSS_sign']}],
                                'mira': [{'api': f'{depth_2}../src/api.h', 'rng': f'{depth_2}../lib/randombytes/randombytes.h',
                                          'src': [f'{depth_2}../src/keygen.c', f'{depth_2}../src/sign.c'],
                                          'headers': [f'{depth_2}../src/keygen.h', f'{depth_2}../src/sign.h'],
                                          'targets': ['sign_mira_128_keygen', 'sign_mira_128_sign']}],
                                'mirith': [{'api': f'{depth_2}../sign.h', 'rng': f'{depth_2}../nist/rng.h',
                                            'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../sign.h'],
                                            'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'mqom': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../generator/rng.h',
                                          'src': [f'{depth_2}../keygen.c', f'{depth_2}../sign.c'],
                                          'headers': [f'{depth_2}../api.h', f'{depth_2}../api.h'],
                                          'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'perk': [{'api': f'{depth_2}../src/api.h', 'rng': f'{depth_2}../lib/randombytes/rng.h',
                                          'src': [f'{depth_2}../src/sign.c'], 'headers': [f'{depth_2}../src/api.h'],
                                          'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'ryde': [{'api': f'{depth_2}../src/api.h', 'rng': f'{depth_2}../lib/randombytes/randombytes.h',
                                          'src': [f'{depth_2}../src/keypair.c', f'{depth_2}../src/sign.c'],
                                          'headers': [f'{depth_2}../src/keypair.h', f'{depth_2}../src/api.h'],
                                          'targets': ['ryde_128f_keygen', 'crypto_sign']}],
                                'sdith': [{'api': f'{depth_2}../../api.h', 'rng': f'{depth_2}../../generator/rng.h',
                                           'src': [f'{depth_2}../../sdith.c', f'{depth_2}../../sign.c'],
                                           'headers': [f'{depth_2}../../sdith.h', f'{depth_2}../../api.h'],
                                           'targets': ['keygen', 'crypto_sign']}],
                                'biscuit': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                             'src': [f'{depth_2}../api.c'], 'headers': [f'{depth_2}../api.h'],
                                             'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'dme_sign': [{'api': f'{depth_2}../../api.h', 'rng': f'{depth_2}../../rng.h',
                                              'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../api.h'],
                                              'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'hppc': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                          'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../api.h'],
                                          'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'wise': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                          'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../api.h'],
                                          'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'mayo': [{'api': f'{depth_2}../../api.h', 'rng': f'{depth_2}../../../include/rng.h', 'rng_same_fold': 'yes',
                                          'src': [f'{depth_2}../../mayo.c'], 'headers': [f'{depth_2}../../../include/mayo.h'],
                                          'targets': ['mayo_keypair', 'mayo_sign']}],
                                'prov': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                          'src': [f'{depth_2}../prov.c'], 'headers': [f'{depth_2}../prov.h'],
                                          'targets': ['prov_keygen', 'prov_sign']}],
                                'qr_uov': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h'}],
                                'snova': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                           'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../api.h'],
                                           'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'tuov': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../nistkat/rng.h', 'rng_same_fold': 'yes',
                                          'src': [f'{depth_2}../tuov_keypair.c', f'{depth_2}../tuov.c'],
                                          'headers': [f'{depth_2}../tuov.h', f'{depth_2}../tuov.h'],
                                          'targets': ['generate_keypair', 'tuov_sign']}],
                                'uov': [{'api': f'{depth_2}../../api.h', 'rng': f'{depth_2}../../nistkat/rng.h', 'rng_same_fold': 'yes',
                                         'src': [f'{depth_2}../../ov_keypair.c', f'{depth_2}../../ov.c'],
                                         'headers': [f'{depth_2}../../ov.h', f'{depth_2}../../ov.h'],
                                         'targets': ['generate_keypair_pkc_skc', 'ov_expand_and_sign']}],
                                'vox': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng/rng.h',
                                         'src': [f'{depth_2}../api.c', f'{depth_2}../vox_sign_core.c'],
                                         'headers': [f'{depth_2}../api.h', f'{depth_2}../vox_sign_core.h'],
                                         'targets': ['crypto_sign_keypair', 'VOX_sign_core']}],
                                'aimer': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                           'src': [f'{depth_2}../api.c'], 'headers': [f'{depth_2}../api.h'],
                                           'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'ascon_sign': [{'api': f'{depth_2}../../api.h', 'rng': f'{depth_2}../../rng.h',
                                                'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../api.h'],
                                                'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'faest': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../NIST-KATs/rng.h',
                                           'src': [f'{depth_2}../crypto_sign.c'], 'headers': [f'{depth_2}../api.h'],
                                           'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'sphincs_alpha': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                                   'src': [f'{depth_2}../sign.c'], 'headers': [f'{depth_2}../api.h'],
                                                   'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'preon': [{'api': f'{depth_2}../../api.h', 'rng': f'{depth_2}../../rng.h',
                                           'src': [f'{depth_2}../api.c'], 'headers': [f'{depth_2}../api.h'],
                                           'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'alteq': [{'api': f'{depth_2}api.h', 'rng': f'{depth_2}aes/aes256.h',
                                           'src': [f'{depth_2}sign.c'], 'headers': [f'{depth_2}/api/api.h.1.fe'],
                                           'targets': ['crypto_sign_keypair', 'crypto_sign']}],
                                'emle': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                          'src': [f'{depth_2}../impl.c'], 'headers': [f'{depth_2}../impl.h'],
                                          'targets': ['keygen', 'sign']}],
                                'kaz_sign': [{'api': f'{depth_2}../api.h', 'rng': f'{depth_2}../rng.h',
                                              'src': [f'{depth_2}../kaz_api.c'], 'headers': [f'{depth_2}../kaz_api.h'],
                                              'targets': ['KAZ_DS_KeyGen', 'KAZ_DS_SIGNATURE']}],
                                'xifrat': [{'api': f'{depth_2}Reference_Implementation/api.h', 'rng': f'{depth_2}Reference_Implementation/rng.h'}]}


# =============================================================================================
# ============  Create a parser for every function in the sub-parser name  ====================
# =============================================================================================
# Create a parser for every function in the sub-parser and add arguments in its namespace

# Take into account the case where api.h and sign.h are both needed in
# the function add_cli_arguments(...)

# =================== CANDIDATES IMPLEMENTATION FOLDERS =======================================

# ===================================== MPC-IN-THE-HEAD ========================================
# ===================================== cross ==================================================
cross_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Reference_Implementation',
                                 'add': ''}
cross_default_list_of_folders = []
# ============================== mira ==========================================================
mira_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
mira_opt_folder = "candidates/mpc-in-the-head/mira/Optimized_Implementation"
mira_default_list_of_folders = os.listdir(mira_opt_folder)
mira_default_list_of_folders.remove('README.md')
mira_default_list_of_folders = generic.get_default_list_of_folders(mira_default_list_of_folders,
                                                                   default_tools_list)
# ============================ Mirith ===========================================================
mirith_implementations_folders = {'ref': 'Reference_Implementation',
                                  'opt': 'Optimized_Implementation',
                                  'add': ''}
mirith_opt_folder = "candidates/mpc-in-the-head/mirith/Optimized_Implementation"
mirith_default_list_of_folders = os.listdir(mirith_opt_folder)
mirith_default_list_of_folders = generic.get_default_list_of_folders(mirith_default_list_of_folders,
                                                                     default_tools_list)
# neon-based implementation is not taken into account yet
mirith_default_list_of_folders = [instance for instance in mirith_default_list_of_folders if 'neon' not in instance]



# ================================ perk =========================================================
perk_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
perk_opt_folder = "candidates/mpc-in-the-head/perk/Optimized_Implementation"
perk_default_list_of_folders = os.listdir(perk_opt_folder)
perk_default_list_of_folders.remove('README')
perk_default_list_of_folders = generic.get_default_list_of_folders(perk_default_list_of_folders,
                                                                   default_tools_list)
# ================================ mqom ===========================================================
mqom_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
mqom_opt_folder = "candidates/mpc-in-the-head/mqom/Optimized_Implementation"
mqom_default_list_of_folders = os.listdir(mqom_opt_folder)
mqom_default_list_of_folders = generic.get_default_list_of_folders(mqom_default_list_of_folders,
                                                                   default_tools_list)
# ============================== ryde =============================================================
ryde_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
ryde_default_list_of_folders = ['ryde128f', 'ryde128s', 'ryde192f', 'ryde192s', 'ryde256f', 'ryde256s']
# ============================== sdith =============================================================
sdith_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Optimized_Implementation',
                                 'add': ''}
sdith_opt_folder_hypercube = "candidates/mpc-in-the-head/sdith/Optimized_Implementation/Hypercube_Variant"
sdith_opt_folder_threshold = "candidates/mpc-in-the-head/sdith/Optimized_Implementation/Threshold_Variant"
hypercube_instances = os.listdir(sdith_opt_folder_hypercube)
hypercube_instances = [f'Hypercube_Variant/{instance}' for instance in hypercube_instances]
threshold_instances = os.listdir(sdith_opt_folder_threshold)
threshold_instances = [f'Threshold_Variant/{instance}' for instance in threshold_instances]

sdith_default_list_of_folders = hypercube_instances.copy()
sdith_default_list_of_folders.extend(threshold_instances)
# ====================================== CODE ======================================================
# ====================================== pqsigrm ===================================================
pqsigrm_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': 'Optimized_Implementation',
                                   'add': ''}
pqsigrm_default_list_of_folders = []
# =============================== fuleeca ========================================================
fuleeca_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': 'Reference_Implementation',
                                   'add': ''}
fuleeca_opt_folder = "candidates/code/fuleeca/Reference_Implementation"
fuleeca_default_list_of_folders = os.listdir(fuleeca_opt_folder)
fuleeca_default_list_of_folders = generic.get_default_list_of_folders(fuleeca_default_list_of_folders,
                                                                      default_tools_list)
# ==================================== less ======================================================
less_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': 'Additional_Implementations/AVX2'}
less_default_list_of_folders = []
# ==================================== meds ======================================================
meds_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
meds_opt_folder = "candidates/code/meds/Optimized_Implementation"
meds_default_list_of_folders = os.listdir(meds_opt_folder)
meds_default_list_of_folders = generic.get_default_list_of_folders(meds_default_list_of_folders,
                                                                   default_tools_list)
# =================================== wave =======================================================
wave_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
wave_default_list_of_folders = ['Wave1249', 'Wave1644', 'Wave822']
# ====================================== LATTICE =================================================
# ====================================== eagle_sign ===============================================
eaglesign_implementations_folders = {'ref': 'Specifications_and_Supporting_Documentation/Reference_Implementation',
                                     'opt': 'Specifications_and_Supporting_Documentation/Optimized_Implementation',
                                     'add': ''}
eaglesign_default_list_of_folders = ['EagleSign3', 'EagleSign5']
# eaglesign_opt_folder = f'candidates/lattice/eaglesign/'
# eaglesign_opt_folder += f'Specifications_and_Supporting_Documentation/Optimized_Implementation'
# eaglesign_default_list_of_folders = os.listdir(eaglesign_opt_folder)
# eaglesign_default_list_of_folders = generic.get_default_list_of_folders(eaglesign_default_list_of_folders,
#                                                                         default_tools_list)
# ====================================== ehtv3v4 ===============================================
ehtv3v4_implementations_folders = {'ref': 'Reference_Implementation/crypto_sign',
                                   'opt': 'Optimized_Implementation/crypto_sign',
                                   'add': ''}
ehtv3v4_default_list_of_folders = ['ehtv3l1', 'ehtv3l3', 'ehtv3l5', 'ehtv4l1', 'ehtv4l5']
# ====================================== squirrels ===============================================
# [TODO:Path to /KAT/generator/katrng.h]
squirrels_implementations_folders = {'ref': 'Reference_Implementation',
                                     'opt': 'Optimized_Implementation',
                                     'add': ''}
globals_vars['squirrels_implementations_folders'] = squirrels_implementations_folders
squirrels_opt_folder = "candidates/lattice/squirrels/Optimized_Implementation"
squirrels_default_list_of_folders = os.listdir(squirrels_opt_folder)
squirrels_default_list_of_folders = generic.get_default_list_of_folders(squirrels_default_list_of_folders,
                                                                        default_tools_list)
# ======================================= haetae ================================================
haetae_implementations_folders = {'ref': 'Reference_Implementation',
                                  'opt': 'Optimized_Implementation',
                                  'add': ''}
haetae_default_list_of_folders = []
# ========================================== HAWK ==============================================
hawk_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation/avx2',
                                'add': ''}
hawk_opt_folder = "candidates/lattice/hawk/Optimized_Implementation/avx2"
hawk_default_list_of_folders = os.listdir(hawk_opt_folder)
hawk_default_list_of_folders = generic.get_default_list_of_folders(hawk_default_list_of_folders,
                                                                   default_tools_list)
# =========================================== hufu ==============================================
hufu_implementations_folders = {'ref': 'HuFu/Reference_Implementation/crypto_sign',
                                'opt': 'HuFu/Optimized_Implementation/crypto_sign',
                                'add': 'HuFu/Additional_Implementation/avx2/crypto_sign'}
hufu_opt_folder = "candidates/lattice/hufu/HuFu/Optimized_Implementation/crypto_sign"
hufu_default_list_of_folders = os.listdir(hufu_opt_folder)
hufu_default_list_of_folders = generic.get_default_list_of_folders(hufu_default_list_of_folders,
                                                                   default_tools_list)
# ============================================ raccoon ===========================================
raccoon_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': 'Optimized_Implementation',
                                   'add': ''}
raccoon_opt_folder = "candidates/lattice/raccoon/Optimized_Implementation"
raccoon_default_list_of_folders = os.listdir(raccoon_opt_folder)
raccoon_default_list_of_folders = generic.get_default_list_of_folders(raccoon_default_list_of_folders,
                                                                      default_tools_list)
# ============================================= MULTIVARIATE ===================================
# ============================================= snova ==========================================
snova_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Optimized_Implementation',
                                 'add': ''}
snova_opt_folder = "candidates/multivariate/snova/Optimized_Implementation"
snova_default_list_of_folders = os.listdir(snova_opt_folder)
snova_default_list_of_folders = generic.get_default_list_of_folders(snova_default_list_of_folders,
                                                                    default_tools_list)
# =============================================== mayo ===========================================
mayo_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': 'Additional_Implementations/AVX2'}
mayo_default_list_of_folders = ["src/mayo_1", "src/mayo_2", "src/mayo_3", "src/mayo_5"]
# =============================================== biscuit ===========================================
biscuit_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': 'Optimized_Implementation',
                                   'add': 'Additional_Implementations/ss2'}
biscuit_default_list_of_folders = ["biscuit128f", "biscuit128s", "biscuit192f", "biscuit192s",
                                   "biscuit256f", "biscuit256s"]
# =============================================== dme_sign ===========================================
dme_sign_implementations_folders = {'ref': 'DME-SIGN_nist-pqc-2023',
                                    'opt': 'DME-SIGN_nist-pqc-2023',
                                    'add': ''}
dme_fold = 'DME-SIGN_nist-pqc-2023'
opt_impl = 'Optimized_Implementation'
dme_sign_default_list_of_folders = [f"{dme_fold}/dme-3rnds-8vars-32bits-sign/{opt_impl}",
                                    f"{dme_fold}/dme-3rnds-8vars-48bits-sign/{opt_impl}",
                                    f"{dme_fold}/dme-3rnds-8vars-64bits-sign/{opt_impl}"]
# =============================================== hppc ===========================================
hppc_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
hppc_default_list_of_folders = ["HPPC128", "HPPC192", "HPPC256"]
# =============================================== wise ===========================================
wise_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
wise_default_list_of_folders = ["3WISE-128", "3WISE-192", "3WISE-256"]
# ================================================ prov ===========================================
prov_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
prov_opt_folder = "candidates/multivariate/prov/Optimized_Implementation"
prov_default_list_of_folders = os.listdir(prov_opt_folder)
prov_default_list_of_folders = generic.get_default_list_of_folders(prov_default_list_of_folders,
                                                                   default_tools_list)
# ================================================= qr_uov =========================================
qr_uov_implementations_folders = {'ref': 'QR_UOV/Reference_Implementation',
                                  'opt': 'QR_UOV/Optimized_Implementation',
                                  'add': 'QR_UOV/Alternative_Implementation'}
qr_uov_default_list_of_folders = ["qruov1q7L10v740m100", "qruov1q31L3v165m60",
                                  "qruov1q31L10v600m70", "qruov1q127L3v156m54",
                                  "qruov3q7L10v1100m140", "qruov3q31L3v246m87",
                                  "qruov3q31L10v890m100", "qruov3q127L3v228m78",
                                  "qruov5q7L10v1490m190", "qruov5q31L3v324m114",
                                  "qruov5q31L10v1120m120", "qruov5q127L3v306m105"]
# ================================================= tuov ========================================
tuov_implementations_folders = {'ref': 'TUOV/Reference_Implementation',
                                'opt': 'TUOV/Optimized_Implementation',
                                'add': ''}
tuov_opt_folder = "candidates/multivariate/tuov/TUOV/Optimized_Implementation"
tuov_default_list_of_folders = os.listdir(tuov_opt_folder)
tuov_default_list_of_folders = generic.get_default_list_of_folders(tuov_default_list_of_folders,
                                                                   default_tools_list)
tuov_default_list_of_folders.remove('tests')
tuov_default_list_of_folders.remove('nistkat')
# ================================================== uov ========================================
uov_implementations_folders = {'ref': 'UOV/Reference_Implementation',
                               'opt': 'UOV/Optimized_Implementation',
                               'add': ''}
uov_opt_folder = "candidates/multivariate/uov/UOV/Optimized_Implementation"
uov_amd64_avx2_neon_folders = os.listdir(uov_opt_folder)
uov_amd64_avx2_neon_folders = generic.get_default_list_of_folders(uov_amd64_avx2_neon_folders,
                                                                  default_tools_list)

uov_amd64 = uov_amd64_avx2_neon_folders[0]
uov_avx2 = uov_amd64_avx2_neon_folders[1]
uov_neon = uov_amd64_avx2_neon_folders[2]
uov_default_list_of_folders = []
abs_path_to_uov_amd64 = uov_opt_folder+"/"+uov_amd64
abs_path_to_uov_avx2 = uov_opt_folder+"/"+uov_avx2
abs_path_to_uov_neon = uov_opt_folder+"/"+uov_neon
amd64_ext = [uov_amd64+"/"+fold for fold in os.listdir(abs_path_to_uov_amd64)]
uov_default_list_of_folders.extend(amd64_ext)
uov_default_list_of_folders.remove(uov_amd64+"/nistkat")
avx2_ext = [uov_avx2+"/"+fold for fold in os.listdir(abs_path_to_uov_avx2)]
uov_default_list_of_folders.extend(avx2_ext)
if uov_avx2+"/nistkat" in uov_default_list_of_folders:
    uov_default_list_of_folders.remove(uov_avx2+"/nistkat")
neon_ext = [uov_neon+"/"+fold for fold in os.listdir(abs_path_to_uov_neon)]
uov_default_list_of_folders.extend(neon_ext)
if uov_neon+"/nistkat" in uov_default_list_of_folders:
    uov_default_list_of_folders.remove(uov_neon+"/nistkat")
# ==================================================== vox =======================================
vox_implementations_folders = {'ref': 'Reference_Implementation',
                               'opt': 'Reference_Implementation',
                               'add': 'Additional_Implementations/avx2'}
# Take into account the folder 'flint' in Additional implementations
vox_default_list_of_folders = ["vox_sign"]
# ==================================================== SYMMETRIC ==================================
# ==================================================== aimer ======================================
aimer_implementations_folders = {'ref': 'AIMer_submission/Reference_Implementation',
                                 'opt': 'AIMer_submission/Optimized_Implementation',
                                 'add': ''}
aimer_opt_folder = "candidates/symmetric/aimer/AIMer_submission/Optimized_Implementation"
aimer_default_list_of_folders = os.listdir(aimer_opt_folder)
aimer_default_list_of_folders = generic.get_default_list_of_folders(aimer_default_list_of_folders,
                                                                    default_tools_list)
# ===================================================== ascon_sign =================================
ascon_sign_implementations_folders = {'ref': 'Reference_Implementation',
                                      'opt': 'Optimized_Implementation',
                                      'add': ''}
ascon_sign_default_list_of_folders = ['Ascon_Sign_Robust/Ascon-Sign-128f', 'Ascon_Sign_Robust/Ascon-Sign-128s',
                                      'Ascon_Sign_Robust/Ascon-Sign-192f', 'Ascon_Sign_Robust/Ascon-Sign-192s',
                                      'Ascon_Sign_Simple/Ascon-Sign-128f', 'Ascon_Sign_Simple/Ascon-Sign-128s',
                                      'Ascon_Sign_Simple/Ascon-Sign-192f', 'Ascon_Sign_Simple/Ascon-Sign-192s']
# ============================================== faest ===========================================
faest_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Reference_Implementation',
                                 'add': 'Additional_Implementations/avx2'}
faest_opt_folder = "candidates/symmetric/faest/Reference_Implementation"
faest_default_list_of_folders = os.listdir(faest_opt_folder)
faest_default_list_of_folders = generic.get_default_list_of_folders(faest_default_list_of_folders,
                                                                    default_tools_list)
# =============================================== Sphincs_alpha ==================================
sphincs_alpha_implementations_folders = {'ref': 'Reference_Implementation',
                                         'opt': 'Optimized_Implementation',
                                         'add': 'Additional_Implementation/avx2'}
sphincs_opt_folder = "candidates/symmetric/sphincs_alpha/Optimized_Implementation"
sphincs_default_list_of_folders = os.listdir(sphincs_opt_folder)
sphincs_alpha_default_list_of_folders = generic.get_default_list_of_folders(sphincs_default_list_of_folders,
                                                                            default_tools_list)
# =============================================== OTHER =========================================
# =============================================== preon =========================================
preon_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Optimized_Implementation',
                                 'add': ''}
preon_default_list_of_folders = ['Preon128/Preon128A', 'Preon128/Preon128B', 'Preon128/Preon128C',
                                 'Preon192/Preon192A', 'Preon192/Preon192B', 'Preon192/Preon192C',
                                 'Preon256/Preon256A', 'Preon256/Preon256B', 'Preon256/Preon256C']
# =============================================== alteq ===========================================
alteq_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Optimized_Implementation',
                                 'add': ''}
alteq_default_list_of_folders = []
# =============================================== emle ===========================================
emle_implementations_folders = {'ref': 'Reference_Implementation/crypto_sign',
                                'opt': 'Reference_Implementation/crypto_sign',
                                'add': 'Additional_Implementations/aesni/crypto_sign'}
emle_default_list_of_folders = ["eMLE-Sig-I", "eMLE-Sig-III", "eMLE-Sig-V"]
# =============================================== kaz_sign ===========================================
kaz_sign_implementations_folders = {'ref': 'Reference_Implementation',
                                    'opt': 'Optimized_Implementation',
                                    'add': ''}
kaz_sign_default_list_of_folders = ["Kaz458", "Kaz738", "Kaz970"]
# =============================================== xifrat ===========================================
xifrat_implementations_folders = {'ref': 'Reference_Implementation',
                                  'opt': 'Optimized_Implementation',
                                  'add': 'ReduceSec_Implementation'}
xifrat_default_list_of_folders = []
# ======================================================= ISOGENY ============================
# ======================================================= sqisign ============================
# [TODO]
sqisign_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': '',
                                   'add': 'Additional_Implementations/broadwell'}
sqisign_opt_folder = "candidates/isogeny/sqisign/Additional_Implementations/broadwell"
sqisign_default_list_of_folders = []
# ============================================================================================
# =========================================================  D  ==============================
# ============================================================================================

# Set dictionaries (key, value)
set_global_dictionaries(list_of_integrated_candidates)
# Add subparser for all candidates and add arguments to their namespace
add_cli_arguments_for_all_candidates(subparser)


# set all the command-line arguments into the object args
args = parser.parse_args()


def main():
    """ Function: main"""
    run_cli_candidate(args)


if __name__ == "__main__":
    main()
