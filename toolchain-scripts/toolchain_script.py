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
                                         "sphincs_alpha", "preon", "squirrels", "hawk", "meds", "haeatae",
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
    print("========= Target candidate: ", candidate)
    list_of_tools = args_parse.tools
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
    build_directory = args_parse.build
    executable_patterns = args_parse.algorithms_patterns
    is_rng_in_different_folder = args_parse.rng_outside
    with_core_dump = args_parse.core_dump
    cmake_additional_definitions = args_parse.cmake_definition
    security_level = args_parse.security_level
    number_measurements = args_parse.number_measurements
    timeout = args_parse.timeout
    implementation_type = args_parse.ref_opt_add_implementation
    candidate_implementation_folder = f'{candidate}_implementations_folders'
    impl_folder = f"folder = {candidate_implementation_folder}['{implementation_type}']"
    loc = {}
    exec(impl_folder, globals_vars, loc)
    folder = loc['folder']
    optimization_folder = folder
    arguments = f'''{list_of_tools}, f'{type_based_signature}', f'{target_candidate}',
                     f'{optimization_folder}', {list_of_instance_folders},
                     {relative_path_to_api}, f'{relative_path_to_sign}', {relative_path_to_rng},
                     f'{compile_candidate}', f'{run_candidate}', {binsec_depth_flag},
                     f'{build_directory}', {executable_patterns},
                     f'{is_rng_in_different_folder}', f'{with_core_dump}',
                    {cmake_additional_definitions}, f'{security_level}',
                    f'{number_measurements}', f'{timeout}', f'{implementation_type}' '''
    target = f'compile_run_candidate({arguments})'
    exec(target)


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


# ============ Common default arguments ==============================================
# List of integrated candidates so far
list_of_integrated_candidates = ["mirith", "mira", "mqom", "perk", "ryde", "pqsigrm", "wave", "prov",
                                 "snova", "tuov", "vox", "aimer", "ascon_sign", "faest",
                                 "sphincs_alpha", "preon", "meds", "haeatae",
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


# Improve the message for help
default_help_message = 'compile and run test'


# =============================================================================================
# ============  Create a parser for every function in the sub-parser name  ====================
# =============================================================================================
# Create a parser for every function in the sub-parser and add arguments in its namespace

# Take into account the case where api.h and sign.h are both needed in
# the function add_cli_arguments(...)


# ===================================== MPC-IN-THE-HEAD ========================================
# ===================================== cross ==================================================
cross_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Reference_Implementation',
                                 'add': ''}
globals_vars['cross_implementations_folders'] = cross_implementations_folders
cross_default_list_of_folders = []
generic.add_cli_arguments(subparser, 'candidates/mpc-in-the-head', 'cross',
                          'Optimized_Implementation',
                          '"../../include/api.h"', '""',
                          '"../../../Additional_Implementations/KAT_Generation/include/KAT_NIST_rng.h"',
                          'no', cross_default_list_of_folders, 'yes',
                          None, None, '1e4',
                          '100', 'opt')

# ============================== mira ==========================================================
mira_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['mira_implementations_folders'] = mira_implementations_folders

mira_opt_folder = "candidates/mpc-in-the-head/mira/Optimized_Implementation"
mira_default_list_of_folders = os.listdir(mira_opt_folder)
mira_default_list_of_folders.remove('README.md')
mira_default_list_of_folders = generic.get_default_list_of_folders(mira_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/mpc-in-the-head', 'mira',
                          'Optimized_Implementation',
                          '"../../../src/api.h"', '""',
                          '"../../../lib/randombytes/randombytes.h"','no',
                          mira_default_list_of_folders,'yes')


# ============================ Mirith ===========================================================
mirith_implementation = "candidates/mpc-in-the-head/mirith"
mirith_implementations_folders = {'ref': 'Reference_Implementation',
                                  'opt': 'Optimized_Implementation',
                                  'add': ''}
globals_vars['mirith_implementations_folders'] = mirith_implementations_folders

mirith_opt_folder = "candidates/mpc-in-the-head/mirith/Optimized_Implementation"
mirith_default_list_of_folders = os.listdir(mirith_opt_folder)
mirith_default_list_of_folders = generic.get_default_list_of_folders(mirith_default_list_of_folders,
                                                                     default_tools_list)

# neon-based implementation is not taken into account yet
mirith_default_list_of_folders = [instance for instance in mirith_default_list_of_folders if 'neon' not in instance]


generic.add_cli_arguments(subparser, 'candidates/mpc-in-the-head', 'mirith',
                          'Optimized_Implementation',
                          '"../../../api.h"', '"../../../sign.h"',
                          '"../../../nist/rng.h"',
                          'no', mirith_default_list_of_folders,'yes',None,None,'1e4', '100', 'opt')


# ================================ perk =========================================================
perk_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['perk_implementations_folders'] = perk_implementations_folders

perk_opt_folder = "candidates/mpc-in-the-head/perk/Optimized_Implementation"
perk_default_list_of_folders = os.listdir(perk_opt_folder)
perk_default_list_of_folders.remove('README')
perk_default_list_of_folders = generic.get_default_list_of_folders(perk_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/mpc-in-the-head', 'perk',
                          'Optimized_Implementation',
                          '"../../../src/api.h"', '""',
                          '"../../../lib/randombytes/rng.h"',
                          'no', perk_default_list_of_folders)


# ================================ mqom ===========================================================
mqom_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['mqom_implementations_folders'] = mqom_implementations_folders

mqom_opt_folder = "candidates/mpc-in-the-head/mqom/Optimized_Implementation"
mqom_default_list_of_folders = os.listdir(mqom_opt_folder)
mqom_default_list_of_folders = generic.get_default_list_of_folders(mqom_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/mpc-in-the-head', 'mqom',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../generator/rng.h"',
                          'no', mqom_default_list_of_folders)


# ============================== ryde =============================================================
ryde_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['ryde_implementations_folders'] = ryde_implementations_folders
ryde_default_list_of_folders = ['ryde128f', 'ryde128s', 'ryde192f', 'ryde192s', 'ryde256f', 'ryde256s']

generic.add_cli_arguments(subparser, 'candidates/mpc-in-the-head', 'ryde',
                          'Optimized_Implementation',
                          '"../../../src/api.h"', '""',
                          '"../../../lib/randombytes/randombytes.h"',
                          'no', ryde_default_list_of_folders)


# ====================================== CODE ======================================================
# ====================================== pqsigrm ===================================================
pqsigrm_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': 'Optimized_Implementation',
                                   'add': ''}
globals_vars['pqsigrm_implementations_folders'] = pqsigrm_implementations_folders
pqsigrm_default_list_of_folders = []
generic.add_cli_arguments(subparser, 'candidates/code', 'pqsigrm',
                          'Optimized_Implementation',
                          '"../../pqsigrm613/src/api.h"', '""',
                          '"../../pqsigrm613/src/rng.h"',
                          'no', pqsigrm_default_list_of_folders)


# =============================== fuleeca ========================================================
fuleeca_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': 'Reference_Implementation',
                                   'add': ''}
globals_vars['fuleeca_implementations_folders'] = fuleeca_implementations_folders
fuleeca_opt_folder = "candidates/code/fuleeca/Reference_Implementation"
fuleeca_default_list_of_folders = os.listdir(fuleeca_opt_folder)
default_list = generic.get_default_list_of_folders(fuleeca_default_list_of_folders,
                                                   default_tools_list)
fuleeca_default_list_of_folders = default_list

generic.add_cli_arguments(subparser, 'candidates/code', 'fuleeca',
                          'Optimized_Implementation',
                          '"../../../Reference_Implementation/api.h"', '""',
                          '"../../../Reference_Implementation/rng.h"',
                          'no', fuleeca_default_list_of_folders)


# ==================================== less ======================================================
less_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': 'Additional_Implementations/AVX2'}
globals_vars['less_implementations_folders'] = less_implementations_folders

less_default_list_of_folders = []
avx2_build = ["-DAVX2_OPTIMIZED=ON"]
generic.add_cli_arguments(subparser, 'candidates/code', 'less',
                          'Optimized_Implementation',
                          '"../../include/api.h"', '""',
                          '"../../include/rng.h"','no',
                          less_default_list_of_folders, 'yes')

# ==================================== meds ======================================================
meds_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['meds_implementations_folders'] = meds_implementations_folders
meds_opt_folder = "candidates/code/meds/Optimized_Implementation"
meds_default_list_of_folders = os.listdir(meds_opt_folder)
meds_default_list_of_folders = generic.get_default_list_of_folders(meds_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/code', 'meds',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"', 'no', meds_default_list_of_folders)


# =================================== wave =======================================================
wave_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['wave_implementations_folders'] = wave_implementations_folders

wave_default_list_of_folders = ['Wave1249', 'Wave1644', 'Wave822']

generic.add_cli_arguments(subparser, 'candidates/code', 'wave',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../NIST-kat/rng.h"', 'no', wave_default_list_of_folders)


# ====================================== LATTICE =================================================
# ====================================== squirrels ===============================================
# [TODO:Path to /KAT/generator/katrng.h]
squirrels_implementations_folders = {'ref': 'Reference_Implementation',
                                     'opt': 'Optimized_Implementation',
                                     'add': ''}
globals_vars['squirrels_implementations_folders'] = squirrels_implementations_folders
squirrels_opt_folder = "candidates/lattice/squirrels/Optimized_Implementation"
squirrels_default_list_of_folders = os.listdir(squirrels_opt_folder)
default_list = generic.get_default_list_of_folders(squirrels_default_list_of_folders,
                                                   default_tools_list)
squirrels_default_list_of_folders = default_list

squirrels_signature_type = 'candidates/lattice'
generic.add_cli_arguments(subparser, 'candidates/lattice', 'squirrels',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../NIST-kat/rng.h"',
                          'no', squirrels_default_list_of_folders)


# ======================================= haetae ================================================
haetae_implementations_folders = {'ref': 'Reference_Implementation',
                                  'opt': 'Optimized_Implementation',
                                  'add': ''}
globals_vars['haetae_implementations_folders'] = haetae_implementations_folders
haetae_default_list_of_folders = []
generic.add_cli_arguments(subparser, 'candidates/lattice', 'haetae',
                          'Optimized_Implementation',
                          '""', '"../../include/sign.h"',
                          '"../../include/randombytes.h"',
                          'no', haetae_default_list_of_folders)


# ========================================== HAWK ==============================================
hawk_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['hawk_implementations_folders'] = hawk_implementations_folders
hawk_opt_folder = "candidates/lattice/hawk/Optimized_Implementation/avx2"
hawk_default_list_of_folders = os.listdir(hawk_opt_folder)
hawk_default_list_of_folders = generic.get_default_list_of_folders(hawk_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/lattice', 'hawk',
                          'Optimized_Implementation/avx2',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"',
                          'no', haetae_default_list_of_folders)


# =========================================== hufu ==============================================
hufu_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['hufu_implementations_folders'] = hufu_implementations_folders
hufu_implementations_folders = {'ref': 'HuFu/Reference_Implementation',
                                'opt': 'HuFu/Optimized_Implementation',
                                'add': 'HuFu/Additional_Implementation/avx2'}
globals_vars['hufu_implementations_folders'] = hufu_implementations_folders


hufu_opt_folder = "candidates/lattice/hufu/HuFu/Optimized_Implementation/crypto_sign"
hufu_default_list_of_folders = os.listdir(hufu_opt_folder)
hufu_default_list_of_folders = generic.get_default_list_of_folders(hufu_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/lattice', 'hufu',
                          'HuFu/Optimized_Implementation/crypto_sign',
                          '"../../../../api.h"', '""',
                          '"../../../../rng.h"',
                          'no', hufu_default_list_of_folders)


# ============================================ raccoon ===========================================
raccoon_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': 'Optimized_Implementation',
                                   'add': ''}
globals_vars['raccoon_implementations_folders'] = raccoon_implementations_folders
raccoon_opt_folder = "candidates/lattice/raccoon/Optimized_Implementation"
raccoon_default_list_of_folders = os.listdir(raccoon_opt_folder)
default_list = generic.get_default_list_of_folders(raccoon_default_list_of_folders,
                                                   default_tools_list)
raccoon_default_list_of_folders = default_list
generic.add_cli_arguments(subparser, 'candidates/lattice', 'raccoon',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"',
                          'no', raccoon_default_list_of_folders)


# ============================================= MULTIVARIATE ===================================
# ============================================= snova ==========================================
snova_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Optimized_Implementation',
                                 'add': ''}
globals_vars['snova_implementations_folders'] = snova_implementations_folders
snova_opt_folder = "candidates/multivariate/snova/Optimized_Implementation"
snova_default_list_of_folders = os.listdir(snova_opt_folder)
snova_default_list_of_folders = generic.get_default_list_of_folders(snova_default_list_of_folders,
                                                                    default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/multivariate', 'snova',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"',
                          'no', snova_default_list_of_folders)


# =============================================== mayo ===========================================
mayo_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': 'Additional_Implementations/AVX2'}
globals_vars['mayo_implementations_folders'] = mayo_implementations_folders

mayo_default_list_of_folders = ["src/mayo_1", "src/mayo_2", "src/mayo_3", "src/mayo_5"]
mayo_avx2_build = ["-DMAYO_BUILD_TYPE=avx2"]
generic.add_cli_arguments(subparser, 'candidates/multivariate', 'mayo',
                          'Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../../include/rng.h"',
                          'yes', mayo_default_list_of_folders, 'yes', mayo_avx2_build)


# ================================================ prov ===========================================
prov_implementations_folders = {'ref': 'Reference_Implementation',
                                'opt': 'Optimized_Implementation',
                                'add': ''}
globals_vars['prov_implementations_folders'] = prov_implementations_folders
prov_opt_folder = "candidates/multivariate/prov/Optimized_Implementation"
prov_default_list_of_folders = os.listdir(prov_opt_folder)
prov_default_list_of_folders = generic.get_default_list_of_folders(prov_default_list_of_folders,
                                                                   default_tools_list)
generic.add_cli_arguments(subparser, 'candidates/multivariate', 'prov',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"',
                          'no', prov_default_list_of_folders)


# ================================================= qr_uov =========================================
# qr_uov_implementations_folders = {'ref': 'QR_UOV/Reference_Implementation',
#                                   'opt': 'QR_UOV/Optimized_Implementation',
#                                   'add': 'QR_UOV/Alternative_Implementation'}
# globals_vars['qr_uov_implementations_folders'] = qr_uov_implementations_folders
# qruov_default_list_of_folders = ["qruov1q7L10v740m100", "qruov1q31L3v165m60",
#                                  "qruov1q31L10v600m70", "qruov1q127L3v156m54",
#                                  "qruov3q7L10v1100m140", "qruov3q31L3v246m87",
#                                  "qruov3q31L10v890m100", "qruov3q127L3v228m78",
#                                  "qruov5q7L10v1490m190", "qruov5q31L3v324m114",
#                                  "qruov5q31L10v1120m120", "qruov5q127L3v306m105"]
# generic.add_cli_arguments(subparser, 'candidates/multivariate', 'qr_uov',
#                           'QR_UOV/Optimized_Implementation',
#                           '"../../../portable64/api.h"', '""',
#                           '"../../../portable64/rng.h"',
#                           'no', qruov_default_list_of_folders)

qr_uov_implementations_folders = {'ref': 'QR_UOV/Reference_Implementation',
                                  'opt': 'QR_UOV/Optimized_Implementation',
                                  'add': 'QR_UOV/Alternative_Implementation'}
globals_vars['qr_uov_implementations_folders'] = qr_uov_implementations_folders
qruov_default_list_of_folders = ["qruov1q7L10v740m100", "qruov1q31L3v165m60",
                                 "qruov1q31L10v600m70", "qruov1q127L3v156m54",
                                 "qruov3q7L10v1100m140", "qruov3q31L3v246m87",
                                 "qruov3q31L10v890m100", "qruov3q127L3v228m78",
                                 "qruov5q7L10v1490m190", "qruov5q31L3v324m114",
                                 "qruov5q31L10v1120m120", "qruov5q127L3v306m105"]
generic.add_cli_arguments(subparser, 'candidates/multivariate', 'qr_uov',
                          'QR_UOV/Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"',
                          'no', qruov_default_list_of_folders)





# ================================================= tuov ========================================
tuov_implementations_folders = {'ref': 'TUOV/Reference_Implementation',
                                'opt': 'TUOV/Optimized_Implementation',
                                'add': ''}
globals_vars['tuov_implementations_folders'] = tuov_implementations_folders
tuov_opt_folder = "candidates/multivariate/tuov/TUOV/Optimized_Implementation"
tuov_default_list_of_folders = os.listdir(tuov_opt_folder)
tuov_default_list_of_folders = generic.get_default_list_of_folders(tuov_default_list_of_folders,
                                                                   default_tools_list)
tuov_default_list_of_folders.remove('tests')
tuov_default_list_of_folders.remove('nistkat')
generic.add_cli_arguments(subparser, 'candidates/multivariate', 'tuov',
                          'TUOV/Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../nistkat/rng.h"',
                          'yes', tuov_default_list_of_folders)


# ================================================== uov ========================================
uov_implementations_folders = {'ref': 'UOV/Reference_Implementation',
                               'opt': 'UOV/Optimized_Implementation',
                               'add': ''}
globals_vars['uov_implementations_folders'] = uov_implementations_folders
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

generic.add_cli_arguments(subparser, 'candidates/multivariate', 'uov',
                          'UOV/Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../nistkat/rng.h"',
                          'yes', uov_default_list_of_folders)


# ==================================================== vox =======================================
vox_implementations_folders = {'ref': 'Reference_Implementation',
                               'opt': 'Reference_Implementation',
                               'add': 'Additional_Implementations/avx2'}
# Take into account the folder 'flint' in Additional implementations
globals_vars['vox_implementations_folders'] = vox_implementations_folders
vox_default_list_of_folders = ["vox_sign"]
generic.add_cli_arguments(subparser, 'candidates/multivariate', 'vox',
                          'Reference_Implementation/vox_sign',
                          '"../../../api.h"', '""',
                          '"../../../rng/rng.h"', 'no', vox_default_list_of_folders,
                          "yes", None, "256")

# ==================================================== SYMMETRIC ==================================
# ==================================================== aimer ======================================
aimer_implementations_folders = {'ref': 'AIMer_submission/Reference_Implementation',
                                 'opt': 'AIMer_submission/Optimized_Implementation',
                                 'add': ''}
globals_vars['aimer_implementations_folders'] = aimer_implementations_folders
aimer_opt_folder = "candidates/symmetric/aimer/AIMer_submission/Optimized_Implementation"
aimer_default_list_of_folders = os.listdir(aimer_opt_folder)
aimer_default_list_of_folders = generic.get_default_list_of_folders(aimer_default_list_of_folders,
                                                                    default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/symmetric', 'aimer',
                          'AIMer_submission/Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"',
                          'no', aimer_default_list_of_folders)

# ===================================================== ascon_sign =================================
ascon_sign_implementations_folders = {'ref': 'Reference_Implementation',
                                      'opt': 'Optimized_Implementation',
                                      'add': ''}
globals_vars['ascon_sign_implementations_folders'] = ascon_sign_implementations_folders
ascon_default_list_of_folders = ['Ascon_Sign_Robust/Ascon-Sign-128f', 'Ascon_Sign_Robust/Ascon-Sign-128s',
                                 'Ascon_Sign_Robust/Ascon-Sign-192f', 'Ascon_Sign_Robust/Ascon-Sign-192s',
                                 'Ascon_Sign_Simple/Ascon-Sign-128f', 'Ascon_Sign_Simple/Ascon-Sign-128s',
                                 'Ascon_Sign_Simple/Ascon-Sign-192f', 'Ascon_Sign_Simple/Ascon-Sign-192s']

generic.add_cli_arguments(subparser, 'candidates/symmetric', 'ascon_sign',
                          'Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../rng.h"',
                          'no', ascon_default_list_of_folders)


# ============================================== faest ===========================================
faest_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Reference_Implementation',
                                 'add': 'Additional_Implementations/avx2'}
globals_vars['faest_implementations_folders'] = faest_implementations_folders
faest_opt_folder = "candidates/symmetric/faest/Reference_Implementation"
faest_default_list_of_folders = os.listdir(faest_opt_folder)
faest_default_list_of_folders = generic.get_default_list_of_folders(faest_default_list_of_folders,
                                                                    default_tools_list)

generic.add_cli_arguments(subparser, 'candidates/symmetric', 'faest',
                          'Reference_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../NIST-KATs/rng.h"',
                          'no', faest_default_list_of_folders)


# =============================================== Sphincs_alpha ==================================
sphincs_alpha_implementations_folders = {'ref': 'Reference_Implementation',
                                         'opt': 'Optimized_Implementation',
                                         'add': 'Additional_Implementation/avx2'}
globals_vars['sphincs_alpha_implementations_folders'] = sphincs_alpha_implementations_folders
sphincs_opt_folder = "candidates/symmetric/sphincs_alpha/Optimized_Implementation"
sphincs_default_list_of_folders = os.listdir(sphincs_opt_folder)
default_list = generic.get_default_list_of_folders(sphincs_default_list_of_folders,
                                                   default_tools_list)
sphincs_default_list_of_folders = default_list

generic.add_cli_arguments(subparser, 'candidates/symmetric', 'sphincs_alpha',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"',
                          'no', sphincs_default_list_of_folders)


# =============================================== OTHER =========================================
# =============================================== preon =========================================
preon_implementations_folders = {'ref': 'Reference_Implementation',
                                 'opt': 'Optimized_Implementation',
                                 'add': ''}
globals_vars['preon_implementations_folders'] = preon_implementations_folders

preon_default_list_of_folders = ['Preon128/Preon128A', 'Preon128/Preon128B', 'Preon128/Preon128C',
                                 'Preon192/Preon192A', 'Preon192/Preon192B', 'Preon192/Preon192C',
                                 'Preon256/Preon256A', 'Preon256/Preon256B', 'Preon256/Preon256C']

generic.add_cli_arguments(subparser, 'candidates/other', 'preon',
                          'Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../rng.h"',
                          'no', preon_default_list_of_folders)


# ======================================================= ISOGENY ============================
# ======================================================= sqisign ============================
# [TODO]
sqisign_implementations_folders = {'ref': 'Reference_Implementation',
                                   'opt': '',
                                   'add': 'Additional_Implementations/broadwell'}
globals_vars['sqisign_implementations_folders'] = sqisign_implementations_folders
sqisign_opt_folder = "candidates/isogeny/sqisign/Additional_Implementations/broadwell"
sqisign_default_list_of_folders = []

generic.add_cli_arguments(subparser, 'candidates/isogeny', 'sqisign',
                          'Additional_Implementations/broadwell',
                          '"../../../src/nistapi/lvl1/api.h"', '""',
                          '"../../../include/rng.h"')

# ============================================================================================
# =========================================================  D  ==============================
# ============================================================================================

# set all the command-line arguments into the object args
args = parser.parse_args()


def main():
    """ Function: main"""
    run_cli_candidate(args)


if __name__ == "__main__":
    main()
