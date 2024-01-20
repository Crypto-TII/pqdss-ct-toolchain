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
# [TODO:Rename functions if needed/if not working with new script keep old script ...]
# [TODO: rng_outside_instance_folder]
def compile_run_qr_uov(tools_list, signature_type, candidate, optimized_imp_folder,
                       instance_folders_list, rel_path_to_api, rel_path_to_sign,
                       rel_path_to_rng, to_compile, to_run, depth, build_folder,
                       binary_patterns, rng_outside_instance_folder="no", with_core_dump="yes"):
    """ Function: compile_run_qr_uov"""

    build_candidate.compile_run_qr_uov(tools_list, signature_type, candidate, optimized_imp_folder,
                                       instance_folders_list, rel_path_to_api, rel_path_to_sign,
                                       rel_path_to_rng, to_compile, to_run, depth, build_folder,
                                       binary_patterns, rng_outside_instance_folder)


# compile_run_candidate: generic function to run a given candidate with given tools
def compile_run_candidate(tools_list, signature_type, candidate, optimized_imp_folder,
                          instance_folders_list, rel_path_to_api, rel_path_to_sign,
                          rel_path_to_rng, to_compile, to_run, depth, build_folder,
                          binary_patterns, rng_outside_instance_folder="no", with_core_dump="yes"):
    """ Function: compile_run_candidate"""
    candidates_to_build_with_makefile = ["mirith", "mira", "mqom", "perk", "ryde", "pqsigrm", "wave",
                                         "snova", "tuov", "uov", "vox", "aimer", "ascon_sign", "faest",
                                         "sphincs_alpha", "preon", "squirrels"]
    candidate_to_build_with_cmake = ["cross", "less", "mayo", "sqisign"]
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
                                              rng_outside_instance_folder, with_core_dump)
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
                                              rng_outside_instance_folder, with_core_dump)
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
                                              rng_outside_instance_folder, with_core_dump)
    if candidate == "qr_uov":
        compile_run_qr_uov(tools_list, signature_type, candidate, optimized_imp_folder,
                           instance_folders_list, rel_path_to_api, rel_path_to_sign,
                           rel_path_to_rng, to_compile, to_run, depth, build_folder,
                           binary_patterns, rng_outside_instance_folder, with_core_dump)


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
    arguments = f'''{list_of_tools}, f'{type_based_signature}', f'{target_candidate}',
                     f'{optimization_folder}', {list_of_instance_folders},
                     {relative_path_to_api}, f'{relative_path_to_sign}', {relative_path_to_rng},
                     f'{compile_candidate}', f'{run_candidate}', {binsec_depth_flag},
                     f'{build_directory}', {executable_patterns},
                     f'{is_rng_in_different_folder}', f'{with_core_dump}' '''
    target = f'compile_run_candidate({arguments})'
    exec(target)


# Create a parser
parser = argparse.ArgumentParser(prog="NIST-Signature",
                                 description="Constant time check with Binsec, Ctgrind, Dudect and Flowtracker",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
subparser = parser.add_subparsers(help="", dest='binsec_test')


# ============ Common default arguments ==============================================

# Default tools list
default_tools_list = ["binsec", "ctgrind", "dudect", "flowtracker"]
# Default algorithms pattern to test
default_binary_patterns = ["keypair", "sign"]

# [TODO]
# Improve the message for help
default_help_message = 'compile and run test'


# =============================================================================================
# ============  Create a parser for every function in the sub-parser name  ====================
# =============================================================================================
# Create a parser for every function in the sub-parser and add arguments in its namespace
# [TODO:]
# Take into account the case where api.h and sign.h are both needed in
# the function add_cli_arguments(...)
# ===================================== MPC-IN-THE-HEAD ========================================
# ===================================== cross ==================================================

generic.add_cli_arguments(subparser, 'mpc-in-the-head', 'cross',
                          'Optimized_Implementation',
                          '"../../../Reference_Implementation/include/api.h"', '""',
                          '"../../../Additional_Implementations/KAT_Generation/include/KAT_NIST_rng.h"')

# ============================== mira ==========================================================
# In case of second run, for example when ctgrind folder is already created by the first run
mira_opt_folder = "mpc-in-the-head/mira/Optimized_Implementation"
mira_default_list_of_folders = os.listdir(mira_opt_folder)
mira_default_list_of_folders.remove('README.md')
mira_default_list_of_folders = generic.get_default_list_of_folders(mira_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'mpc-in-the-head', 'mira',
                          'Optimized_Implementation',
                          '"../../../src/api.h"', '""',
                          '"../../../lib/randombytes/randombytes.h"')


# ============================ Mirith ===========================================================
mirith_opt_folder = "mpc-in-the-head/mirith/Optimized_Implementation"
mirith_default_list_of_folders = os.listdir(mirith_opt_folder)
mirith_default_list_of_folders = generic.get_default_list_of_folders(mirith_default_list_of_folders,
                                                                     default_tools_list)

generic.add_cli_arguments(subparser, 'mpc-in-the-head', 'mirith',
                          'Optimized_Implementation',
                          '"../../../api.h"', '"../../../sign.h"',
                          '"../../../nist/rng.h"')


# ================================ perk =========================================================
perk_opt_folder = "mpc-in-the-head/perk/Optimized_Implementation"
perk_default_list_of_folders = os.listdir(perk_opt_folder)
perk_default_list_of_folders.remove('README')
perk_default_list_of_folders = generic.get_default_list_of_folders(perk_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'mpc-in-the-head', 'perk',
                          'Optimized_Implementation',
                          '"../../../src/api.h"', '""',
                          '"../../../lib/randombytes/rng.h"')


# ================================ SDITH ==========================================================
sdith_opt_folder = "mpc-in-the-head/sdith/Optimized_Implementation"
sdith_default_list_of_folders = os.listdir(sdith_opt_folder)
sdith_default_list_of_folders = generic.get_default_list_of_folders(sdith_default_list_of_folders,
                                                                    default_tools_list)

generic.add_cli_arguments(subparser, 'mpc-in-the-head', 'sdith',
                          'Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../rng.h"')


# ================================ mqom ===========================================================
mqom_opt_folder = "mpc-in-the-head/mqom/Optimized_Implementation"
mqom_default_list_of_folders = os.listdir(mqom_opt_folder)
mqom_default_list_of_folders = generic.get_default_list_of_folders(mqom_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'mpc-in-the-head', 'mqom',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../generator/rng.h"')


# ============================== ryde =============================================================
ryde_opt_folder = "mpc-in-the-head/ryde/Optimized_Implementation"
ryde_default_list_of_folders = os.listdir(ryde_opt_folder)
ryde_default_list_of_folders.remove('README')
ryde_default_list_of_folders = generic.get_default_list_of_folders(ryde_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'mpc-in-the-head', 'ryde',
                          'Optimized_Implementation',
                          '"../../../src/api.h"', '""',
                          '"../../../lib/randombytes/randombytes.h"')


# ====================================== CODE ======================================================
# ====================================== pqsigrm ===================================================
pqsigrm_default_list_of_folders = []

generic.add_cli_arguments(subparser, 'code', 'pqsigrm',
                          'Optimized_Implementation',
                          '"../../pqsigrm613/src/api.h"', '""',
                          '"../../pqsigrm613/src/rng.h"')


# =============================== fuleeca ========================================================
fuleeca_opt_folder = "code/fuleeca/Reference_Implementation"
fuleeca_default_list_of_folders = os.listdir(fuleeca_opt_folder)
default_list = generic.get_default_list_of_folders(fuleeca_default_list_of_folders,
                                                   default_tools_list)
fuleeca_default_list_of_folders = default_list

generic.add_cli_arguments(subparser, 'code', 'fuleeca',
                          'Optimized_Implementation',
                          '"../../../Reference_Implementation/api.h"', '""',
                          '"../../../Reference_Implementation/rng.h"')


# ==================================== less ======================================================
less_default_list_of_folders = []
generic.add_cli_arguments(subparser, 'code', 'less',
                          'Optimized_Implementation',
                          '"../../include/api.h"', '""',
                          '"../../include/rng.h"')

# ==================================== meds ======================================================
meds_opt_folder = "code/meds/Optimized_Implementation"
meds_default_list_of_folders = os.listdir(meds_opt_folder)
meds_default_list_of_folders = generic.get_default_list_of_folders(meds_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'code', 'meds',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')


# =================================== wave =======================================================
wave_opt_folder = "code/wave/Optimized_Implementation"
wave_default_list_of_folders = os.listdir(wave_opt_folder)
wave_default_list_of_folders.remove('README.md')
wave_default_list_of_folders.remove('AUTHORS.md')
wave_default_list_of_folders.remove('LICENSE')
wave_default_list_of_folders = generic.get_default_list_of_folders(wave_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'code', 'wave',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../NIST-kat/rng.h"')


# ====================================== LATTICE =================================================
# ====================================== squirrels ===============================================
# [TODO:Path to /KAT/generator/katrng.h]
squirrels_opt_folder = "lattice/squirrels/Optimized_Implementation"
squirrels_default_list_of_folders = os.listdir(squirrels_opt_folder)
default_list = generic.get_default_list_of_folders(squirrels_default_list_of_folders,
                                                   default_tools_list)
squirrels_default_list_of_folders = default_list

squirrels_signature_type = 'lattice'
generic.add_cli_arguments(subparser, 'lattice', 'squirrels',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../NIST-kat/rng.h"')


# ======================================= haetae ================================================
haetae_default_list_of_folders = []
generic.add_cli_arguments(subparser, 'lattice', 'haetae',
                          'Optimized_Implementation',
                          '""', '"../../include/sign.h"',
                          '"../../include/randombytes.h"')


# ========================================= eaglesign ===========================================
opt_folder = 'Specifications_and_Supporting_Documentation/Optimized_Implementation'
eaglesign_opt_folder = f'lattice/eaglesign/{opt_folder}'
eaglesign_default_list_of_folders = os.listdir(eaglesign_opt_folder)
default_list = generic.get_default_list_of_folders(eaglesign_default_list_of_folders,
                                                   default_tools_list)
eaglesign_default_list_of_folders = default_list

generic.add_cli_arguments(subparser, 'lattice', 'eaglesign',
                          opt_folder,
                          '""', '"../../../sign.h"',
                          '"../../../rng.h"')


# ========================================== ehtv3v4 ==========================================
ehtv3v4_opt_folder = "lattice/ehtv3v4/Optimized_Implementation/crypto_sign"
ehtv3v4_default_list_of_folders = os.listdir(ehtv3v4_opt_folder)
default_list = generic.get_default_list_of_folders(ehtv3v4_default_list_of_folders,
                                                   default_tools_list)
ehtv3v4_default_list_of_folders = default_list

generic.add_cli_arguments(subparser, 'lattice', 'ehtv3v4',
                          'Optimized_Implementation/crypto_sign',
                          '"../../../../api.h"', '""',
                          '"../../../../rng.h"')


# ========================================== HAWK ==============================================
hawk_opt_folder = "lattice/hawk/Optimized_Implementation/avx2"
hawk_default_list_of_folders = os.listdir(hawk_opt_folder)
hawk_default_list_of_folders = generic.get_default_list_of_folders(hawk_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'lattice', 'hawk',
                          'Optimized_Implementation/avx2',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')

# =========================================== hufu ==============================================
hufu_opt_folder = "lattice/hufu/HuFu/Optimized_Implementation/crypto_sign"
hufu_default_list_of_folders = os.listdir(hufu_opt_folder)
hufu_default_list_of_folders = generic.get_default_list_of_folders(hufu_default_list_of_folders,
                                                                   default_tools_list)

generic.add_cli_arguments(subparser, 'lattice', 'hufu',
                          'Optimized_Implementation/crypto_sign',
                          '"../../../../api.h"', '""',
                          '"../../../../rng.h"')


# ============================================ raccoon ===========================================
raccoon_opt_folder = "lattice/raccoon/Optimized_Implementation"
raccoon_default_list_of_folders = os.listdir(raccoon_opt_folder)
default_list = generic.get_default_list_of_folders(raccoon_default_list_of_folders,
                                                   default_tools_list)
raccoon_default_list_of_folders = default_list
generic.add_cli_arguments(subparser, 'lattice', 'raccoon',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')

generic.add_cli_arguments(subparser, 'code', 'wave',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../NIST-kat/rng.h"')


# ============================================= MULTIVARIATE ===================================
# ============================================= snova ==========================================
snova_opt_folder = "multivariate/snova/Optimized_Implementation"
snova_default_list_of_folders = os.listdir(snova_opt_folder)
snova_default_list_of_folders = generic.get_default_list_of_folders(snova_default_list_of_folders,
                                                                    default_tools_list)

generic.add_cli_arguments(subparser, 'multivariate', 'snova',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')

# ================================================ biscuit ====================================
biscuit_opt_folder = "multivariate/biscuit/Optimized_Implementation"
biscuit_default_list_of_folders = os.listdir(biscuit_opt_folder)
default_list = generic.get_default_list_of_folders(biscuit_default_list_of_folders,
                                                   default_tools_list)
biscuit_default_list_of_folders = default_list
generic.add_cli_arguments(subparser, 'multivariate', 'biscuit',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')


# ================================================ dme_sign ====================================
# [TODO:]
# each subfolder of DME-SIGN_nist-pqc-2023 has Reference_Implementation
# and Optimized_Implementaton folder
dme_sign_opt_folder = "multivariate/dme_sign/DME-SIGN_nist-pqc-2023/\
                    dme-3rnds-8vars-32bits-sign/Optimized_Implementation"
# dme_sign_default_list_of_folders = os.listdir(dme_sign_opt_folder)
dme_sign_default_list_of_folders = []
opt_fold = 'DME-SIGN_nist-pqc-2023/dme-3rnds-8vars-32bits-sign/Optimized_Implementation'
generic.add_cli_arguments(subparser, 'multivariate', 'dme_sign',
                          opt_fold,
                          '"../../../api.h"')


# ================================================= hppc ========================================
hppc_opt_folder = "multivariate/hppc/Optimized_Implementation"
hppc_default_list_of_folders = os.listdir(hppc_opt_folder)
hppc_default_list_of_folders = generic.get_default_list_of_folders(hppc_default_list_of_folders,
                                                                   default_tools_list)
generic.add_cli_arguments(subparser, 'multivariate', 'hppc',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')


# =============================================== mayo ===========================================
mayo_default_list_of_folders = []
generic.add_cli_arguments(subparser, 'multivariate', 'mayo',
                          'Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../../include/rng.h"',
                          'yes')


# ================================================ prov ===========================================
prov_opt_folder = "multivariate/prov/Optimized_Implementation"
prov_default_list_of_folders = os.listdir(prov_opt_folder)
prov_default_list_of_folders = generic.get_default_list_of_folders(prov_default_list_of_folders,
                                                                   default_tools_list)
generic.add_cli_arguments(subparser, 'multivariate', 'prov',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')


# ================================================= qr_uov =========================================
qruov_default_list_of_folders = ["qruov1q7L10v740m100", "qruov1q31L3v165m60",
                                 "qruov1q31L10v600m70", "qruov1q127L3v156m54",
                                 "qruov3q7L10v1100m140", "qruov3q31L3v246m87",
                                 "qruov3q31L10v890m100", "qruov3q127L3v228m78",
                                 "qruov5q7L10v1490m190", "qruov5q31L3v324m114",
                                 "qruov5q31L10v1120m120", "qruov5q127L3v306m105"]
generic.add_cli_arguments(subparser, 'multivariate', 'qr_uov',
                          'QR_UOV/Optimized_Implementation',
                          '"../../../portable64/api.h"', '""',
                          '"../../../portable64/rng.h"')


# ================================================= tuov ========================================
tuov_opt_folder = "multivariate/tuov/TUOV/Optimized_Implementation"
tuov_default_list_of_folders = os.listdir(tuov_opt_folder)
tuov_default_list_of_folders = generic.get_default_list_of_folders(tuov_default_list_of_folders,
                                                                   default_tools_list)
tuov_default_list_of_folders.remove('tests')
tuov_default_list_of_folders.remove('nistkat')
generic.add_cli_arguments(subparser, 'multivariate', 'tuov',
                          'TUOV/Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../nistkat/rng.h"',
                          'yes')


# ================================================== uov ========================================
uov_opt_folder = "multivariate/uov/UOV/Optimized_Implementation"
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

generic.add_cli_arguments(subparser, 'multivariate', 'uov',
                          'UOV/Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../nistkat/rng.h"',
                          'yes')


# ==================================================== vox =======================================
generic.add_cli_arguments(subparser, 'multivariate', 'vox',
                          'Reference_Implementation/vox_sign',
                          '"../../../../api.h"', '""',
                          '"../../../../rng/rng.h"')


# ==================================================== SYMMETRIC ==================================
# ==================================================== aimer ======================================
aimer_opt_folder = "symmetric/aimer/AIMer_submission/Optimized_Implementation"
aimer_default_list_of_folders = os.listdir(aimer_opt_folder)
aimer_default_list_of_folders = generic.get_default_list_of_folders(aimer_default_list_of_folders,
                                                                    default_tools_list)

generic.add_cli_arguments(subparser, 'symmetric', 'aimer',
                          'AIMer_submission/Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')

# ===================================================== ascon_sign =================================
ascon_opt_folder = "symmetric/ascon_sign/Optimized_Implementation"
ascon_default_robust_and_simple_folders = os.listdir(ascon_opt_folder)
ascon_default_robust_and_simple_folders.remove('Readme')
default_list = generic.get_default_list_of_folders(ascon_default_robust_and_simple_folders,
                                                   default_tools_list)
ascon_default_robust_and_simple_folders = default_list

ascon_robust = ascon_default_robust_and_simple_folders[0]
ascon_simple = ascon_default_robust_and_simple_folders[1]
ascon_default_list_of_folders = []
abs_path_to_ascon_robust = ascon_opt_folder+"/"+ascon_robust
abs_path_to_ascon_simple = ascon_opt_folder+"/"+ascon_simple
robust_ext = [ascon_robust+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_robust)]
ascon_default_list_of_folders.extend(robust_ext)
simple_ext = [ascon_simple+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_simple)]
ascon_default_list_of_folders.extend(simple_ext)

generic.add_cli_arguments(subparser, 'symmetric', 'ascon_sign',
                          'Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../rng.h"')


# ============================================== faest ===========================================
faest_opt_folder = "symmetric/faest/Reference_Implementation"
faest_default_list_of_folders = os.listdir(faest_opt_folder)
faest_default_list_of_folders = generic.get_default_list_of_folders(faest_default_list_of_folders,
                                                                    default_tools_list)

generic.add_cli_arguments(subparser, 'symmetric', 'faest',
                          'Reference_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../NIST-KATs/rng.h"')



# =============================================== Sphincs_alpha ==================================
sphincs_opt_folder = "symmetric/sphincs_alpha/Optimized_Implementation"
sphincs_default_list_of_folders = os.listdir(sphincs_opt_folder)
default_list = generic.get_default_list_of_folders(sphincs_default_list_of_folders,
                                                   default_tools_list)
sphincs_default_list_of_folders = default_list

generic.add_cli_arguments(subparser, 'symmetric', 'sphincs_alpha',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')


# =============================================== OTHER =========================================
# =============================================== preon =========================================
preon_opt_folder = "other/preon/Optimized_Implementation"
preon_default_128_192_256_folders = os.listdir(preon_opt_folder)
default_list = generic.get_default_list_of_folders(preon_default_128_192_256_folders,
                                                   default_tools_list)
preon_default_128_192_256_folders = default_list

preon_128 = preon_default_128_192_256_folders[0]
preon_192 = preon_default_128_192_256_folders[1]
preon_256 = preon_default_128_192_256_folders[2]
preon_default_list_of_folders = []
abs_path_to_preon_128 = preon_opt_folder+"/"+preon_128
abs_path_to_ascon_192 = preon_opt_folder+"/"+preon_192
abs_path_to_ascon_256 = preon_opt_folder+"/"+preon_256
preon_ext = [preon_128+"/"+subfold for subfold in os.listdir(abs_path_to_preon_128)]
preon_default_list_of_folders.extend(preon_ext)
p129_ext = [preon_192+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_192)]
preon_default_list_of_folders.extend(p129_ext)
p256_ext = [preon_256+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_256)]
preon_default_list_of_folders.extend(p256_ext)

generic.add_cli_arguments(subparser, 'other', 'preon',
                          'Optimized_Implementation',
                          '"../../../../api.h"', '""',
                          '"../../../../rng.h"')


# =================================================== alteq ===================================
# [TODO:figure out and modify path to api]
alteq_opt_folder = "other/alteq/Optimized_Implementation"
alteq_default_list_of_folders = []

generic.add_cli_arguments(subparser, 'other', 'alteq',
                          'Optimized_Implementation',
                          '"../../../api/api.h"', '""',
                          '"../../../include/rng.h"')


# ==================================================== emle2_0 ==============================
emle2_0_opt_folder = "other/emle2_0/Additional_Implementations/aesni/crypto_sign"
emle2_0_default_list_of_folders = os.listdir(emle2_0_opt_folder)
default_list = generic.get_default_list_of_folders(emle2_0_default_list_of_folders,
                                                   default_tools_list)
emle2_0_default_list_of_folders = default_list

generic.add_cli_arguments(subparser, 'other', 'emle2_0',
                          'Additional_Implementations/aesni/crypto_sign',
                          '"../../../../../api.h"', '""',
                          '"../../../../../rng.h"')


# ==================================================== kaz_sign ==============================
kaz_sign_opt_folder = "other/kaz_sign/Optimized_Implementation"
kaz_sign_default_list_of_folders = os.listdir(kaz_sign_opt_folder)
default_list = generic.get_default_list_of_folders(kaz_sign_default_list_of_folders,
                                                   default_tools_list)
kaz_sign_default_list_of_folders = default_list

generic.add_cli_arguments(subparser, 'other', 'kaz_sign',
                          'Optimized_Implementation',
                          '"../../../api.h"', '""',
                          '"../../../rng.h"')


# ======================================================= xifrat ============================
xifrat_opt_folder = "other/xifrat/Optimized_Implementation"
xifrat_default_list_of_folders = []

generic.add_cli_arguments(subparser, 'other', 'xifrat',
                          'Optimized_Implementation',
                          '"../../../Reference_Implementation/api.h"', '""',
                          '"../../../Reference_Implementation/rng.h"')


# ======================================================= ISOGENY ============================
# ======================================================= sqisign ============================
# [TODO: to test and to round up]
sqisign_opt_folder = "isogeny/sqisign/Additional_Implementations/broadwell"
sqisign_default_list_of_folders = []

generic.add_cli_arguments(subparser, 'isogeny', 'sqisign',
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
