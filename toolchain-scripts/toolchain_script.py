#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import argparse


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


# compile_run_candidate: generic function to run a given candidate with given tools
def compile_run_candidate(tools_list, signature_type, candidate, optimized_imp_folder,
                          instance_folders_list, rel_path_to_api, rel_path_to_sign,
                          rel_path_to_rng, to_compile, to_run, depth, build_folder,
                          binary_patterns, rng_outside_instance_folder="no", with_core_dump="yes",
                          additional_cmake_definitions=None, security_level=None,
                          number_of_measurements='1e4', timeout='86400', implementation_type='opt'):
    """ Function: compile_run_candidate"""
    candidates_to_build_with_makefile = ["mirith", "mira", "mqom", "perk", "ryde", "pqsigrm", "wave", "prov",
                                         "snova", "tuov", "uov", "vox", "aimer", "ascon_sign", "faest",
                                         "sphincs_alpha", "preon", "squirrels", "hawk", "meds", "haetae",
                                         "hufu", "meds"]
    candidate_to_build_with_cmake = ["cross", "less", "mayo", "sqisign", "haetae"]
    if candidate in candidates_to_build_with_makefile:
        add_includes = []
        with_cmake = 'no'
        if candidate == "tuov" or candidate == "uov":
            rng_outside_instance_folder = 'yes'
        generic.generic_compile_run_candidate(tools_list, signature_type, candidate,
                                              optimized_imp_folder, instance_folders_list,
                                              rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
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
                                              rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
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
                                              rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                                              with_cmake, add_includes, to_compile, to_run,
                                              depth, build_folder, binary_patterns,
                                              rng_outside_instance_folder, with_core_dump,
                                              additional_cmake_definitions, security_level,
                                              number_of_measurements, timeout, implementation_type)
    if candidate == "qr_uov":
        compile_run_qr_uov(tools_list, signature_type, candidate, optimized_imp_folder,
                           instance_folders_list, rel_path_to_api, rel_path_to_sign,
                           rel_path_to_rng, to_compile, to_run, depth, build_folder,
                           binary_patterns, rng_outside_instance_folder, with_core_dump,
                           number_of_measurements, timeout, implementation_type)


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
        relative_path_to_api = args_parse.api
        relative_path_to_sign = args_parse.sign
        relative_path_to_rng = args_parse.rng
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
                         {relative_path_to_api}, f'{relative_path_to_sign}', {relative_path_to_rng},
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
            api, sign, rng, is_rng_in_cwd = candidates_api_sign_rng_path[candidate]
            cand_default_list_of_instances = f'{candidate}_default_list_of_folders'
            list_of_instances = default_list_of_instances[cand_default_list_of_instances]
            generic.add_cli_arguments(sub_parser, signature_type, candidate, optimization_folder,
                                      api, sign, rng, is_rng_in_cwd, list_of_instances, 'yes',
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
list_of_integrated_candidates = ["mirith", "mira", "mqom", "perk", "ryde", "pqsigrm", "wave", "prov",
                                 "snova", "tuov", "vox", "aimer", "ascon_sign", "faest",
                                 "sphincs_alpha", "preon", "meds", "haetae", "fuleeca",
                                 "hufu", "meds", "cross", "less", "mayo", "raccoon", "qr_uov"]

# hawk - squirrels - uov - sqisign -

# Default tools list
default_tools_list = ["binsec", "ctgrind", "dudect", "flowtracker"]
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
signature_type_based_candidates_dict = {'code': ['fuleeca', 'less', 'meds', 'pqsigrm', 'wave'],
                                        'lattice': ['haetae', 'hufu', 'raccoon'],
                                        'mpc-in-the-head': ['cross', 'mira', 'mirith', 'mqom', 'perk', 'ryde'],
                                        'multivariate': ['mayo', 'prov', 'qr_uov', 'snova', 'tuov', 'vox'],
                                        'symmetric': ['aimer', 'ascon_sign', 'faest', 'sphincs_alpha'],
                                        'other': ['preon']}

# candidates_api_sign_rng_path: dictionary whose keys and values are such that:
#   key:  candidate;
#   values: list consisting of the api, sign, rng relative path (as explained in the README.md), respond to the
#   'is the rng in the same folder as a given instance of the candidate'

candidates_api_sign_rng_path = {'fuleeca': ['"../../../Reference_Implementation/api.h"', '""', '"../../../Reference_Implementation/rng.h"', 'no'],
                                'less': ['"../../include/api.h"', '""', '"../../include/rng.h"', 'no'],
                                'meds': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'pqsigrm': ['"../../pqsigrm613/src/api.h"', '""', '"../../pqsigrm613/src/rng.h"', 'no'],
                                'wave': ['"../../../api.h"', '""', '"../../../NIST-kat/rng.h"', 'no'],
                                'haetae': ['""', '"../../include/sign.h"', '"../../include/randombytes.h"', 'no'],
                                'hufu': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'hawk': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'raccoon': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'squirrels': ['"../../../api.h"', '""', '"../../../NIST-kat/rng.h"', 'no'],
                                'cross': ['"../../include/api.h"', '""', '""', 'no'],
                                'mira': ['"../../../src/api.h"', '""', '"../../../lib/randombytes/randombytes.h"','no'],
                                'mirith': ['"../../../api.h"', '"../../../sign.h"', '"../../../nist/rng.h"', 'no'],
                                'mqom': ['"../../../api.h"', '""', '"../../../generator/rng.h"', 'no'],
                                'perk': ['"../../../src/api.h"', '""', '"../../../lib/randombytes/rng.h"', 'no'],
                                'ryde': ['"../../../src/api.h"', '""', '"../../../lib/randombytes/randombytes.h"', 'no'],
                                'mayo': ['"../../../../api.h"', '""', '"../../../../../include/rng.h"', 'yes'],
                                'prov': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'qr_uov': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'snova': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'tuov': ['"../../../api.h"', '""', '"../../../nistkat/rng.h"', 'yes'],
                                'vox': ['"../../../api.h"', '""', '"../../../rng/rng.h"', 'no'],
                                'aimer': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'ascon_sign': ['"../../../../api.h"', '""', '"../../../../rng.h"', 'no'],
                                'faest': ['"../../../api.h"', '""', '"../../../NIST-KATs/rng.h"', 'no'],
                                'sphincs_alpha': ['"../../../api.h"', '""', '"../../../rng.h"', 'no'],
                                'preon': ['"../../../../api.h"', '""', '"../../../../rng.h"', 'no']}


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
                                'opt': 'Optimized_Implementation',
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
