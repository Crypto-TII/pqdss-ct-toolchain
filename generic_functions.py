#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import glob
import re
import subprocess
import sys
import textwrap
import argparse

import candidates_build as build_cand
import tools as tool


# ============================ MIRITH ==========================================
def makefile_mirith(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_mirith(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ MIRA ==========================================
def makefile_mira(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_mira(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ PERK ==========================================
def makefile_perk(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_perk(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ MQOM ==========================================
def makefile_mqom(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_mqom(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ RYDE ==========================================
def makefile_ryde(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_ryde(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ SDITH ==========================================
def makefile_sdith(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_sdith(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ CROSS ==========================================
def cmake_cross(path_to_cmake_lists, tool_type, candidate):
    build_cand.cmake_cross(path_to_cmake_lists, tool_type, candidate)


# ==============================  CODE ===========================================
# ================================================================================

# ===============================  PQSIGRM =======================================
def makefile_pqsigrm(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_pqsigrm(path_to_makefile_folder, subfolder, tool_type, candidate)


# ========================= LESS ==============================================
def cmake_less(path_to_cmakelist, subfolder, tool_type, candidate):
    build_cand.cmake_less(path_to_cmakelist, subfolder, tool_type, candidate)


# =========================== FULEECA =============================================
# [TODO]
def makefile_fuleeca(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_fuleeca(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ MEDS ==========================================
# [TODO]
def makefile_meds(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_meds(path_to_makefile_folder, subfolder, tool_type, candidate)


# ================================= WAVE =====================================
def makefile_wave(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_wave(path_to_makefile_folder, subfolder, tool_type, candidate)


# ================================== LATTICE ===================================
# ==============================================================================
# =================================== SQUIRRELS =================================
# [TODO]

def makefile_squirrels(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_squirrels(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ HAETAE ===========================================

def cmake_haetae(path_to_cmakelist, subfolder, tool_type, candidate):
    build_cand.cmake_haetae(path_to_cmakelist, subfolder, tool_type, candidate)


# ============================ EAGLESIGN ===================================
# [TODO]
def makefile_eaglesign(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_eaglesign(path_to_makefile_folder, subfolder, tool_type, candidate)


# =============================== ehtv3v4 =======================================
# [TODO]
def makefile_ehtv3v4(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_ehtv3v4(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ HAWK =============================================
# [TODO]
def makefile_hawk(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_hawk(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================ HUFU ==================================================
# [TODO]
def makefile_hufu(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_hufu(path_to_makefile_folder, subfolder, tool_type, candidate)


# =============================== RACCOON ===============================================
# [TODO:Shell script compilation]


# ===================================  MULTIVARIATE =============================
# ===============================================================================

# =================================== QR-UOV ======================================
# [TODO:Rename functions if needed/if not working with new script keep old script ...]


# ================================= snova ===============================================
# [TODO:error after running binsec. Make sure binary is static]
def makefile_snova(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_snova(path_to_makefile_folder, subfolder, tool_type, candidate)


# ================================  BISCUIT =========================================
# [TODO]
def makefile_biscuit(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_biscuit(path_to_makefile_folder, subfolder, tool_type, candidate)


# =================================  dme_sign =======================================
# [TODO]
def makefile_dme_sign(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_dme_sign(path_to_makefile_folder, subfolder, tool_type, candidate)


# ==================================  hppc ===========================================
# [TODO]
def makefile_hppc(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_hppc(path_to_makefile_folder, subfolder, tool_type, candidate)


# ====================================  MAYO =======================================
# [TODO]
def cmake_mayo(path_to_cmakelist, subfolder, tool_type, candidate):
    build_cand.cmake_mayo(path_to_cmakelist, subfolder, tool_type, candidate)


# ==================================  PROV ===============================================
# [TODO]
def makefile_prov(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_prov(path_to_makefile_folder, subfolder, tool_type, candidate)


# =================================== TUOV =============================================
# [TODO]
def makefile_tuov(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_tuov(path_to_makefile_folder, subfolder, tool_type, candidate)


# ==================================  UOV ==============================================
# [TODO]

def makefile_uov(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_uov(path_to_makefile_folder, subfolder, tool_type, candidate)


# ===================================== VOX ================================================
# [TODO]
def makefile_vox(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_vox(path_to_makefile_folder, subfolder, tool_type, candidate)


# ================================  SYMMETRIC =====================================
# =================================================================================

# ================================= AIMER =========================================
def makefile_aimer(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_aimer(path_to_makefile_folder, subfolder, tool_type, candidate)


# ================================= ascon_sign ====================================

def makefile_ascon_sign(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_ascon_sign(path_to_makefile_folder, subfolder, tool_type, candidate)


# =================================== faest ========================================

def makefile_faest(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_faest(path_to_makefile_folder, subfolder, tool_type, candidate)


# ================================== Sphincs-alpha ============================
def makefile_sphincs_alpha(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_sphincs_alpha(path_to_makefile_folder, subfolder, tool_type, candidate)


# =================================  OTHER =========================================
# ==================================================================================
# ================================= PREON ==========================================


def makefile_preon(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_preon(path_to_makefile_folder, subfolder, tool_type, candidate)


# ================================ ALTEQ ====================================
# [TODO]
def makefile_alteq(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_alteq(path_to_makefile_folder, subfolder, tool_type, candidate)


# ================================== EMLE2_0 ======================================
# [TODO]
def makefile_emle2_0(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_emle2_0(path_to_makefile_folder, subfolder, tool_type, candidate)


# =================================== kaz_sign ====================================
# [TODO]
def makefile_kaz_sign(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_kaz_sign(path_to_makefile_folder, subfolder, tool_type, candidate)


# ============================= xifrat ==========================================
# [TODO]
def makefile_xifrat(path_to_makefile_folder, subfolder, tool_type, candidate):
    build_cand.makefile_xifrat(path_to_makefile_folder, subfolder, tool_type, candidate)


# =================================  ISOGENY ===============================
# ==========================================================================
# ========================================== sqisign =======================
# [TODO]
def cmake_sqisign(path_to_cmakelist, subfolder, tool_type, candidate):
    build_cand.cmake_sqisign(path_to_cmakelist, subfolder, tool_type, candidate)


def find_starting_pattern(folder, pattern):
    test_folder = glob.glob(folder + '/' + pattern + '*')
    return test_folder[0]


def find_ending_pattern(folder, pattern):
    test_folder = glob.glob(folder + '/*' + pattern)
    return test_folder[0]


def get_default_list_of_folders(candidate_default_list_of_folders, tools_list):
    for tool_name in tools_list:
        if tool_name in candidate_default_list_of_folders:
            candidate_default_list_of_folders.remove(tool_name)
    return candidate_default_list_of_folders


class GenericPatterns(object):
    def __init__(self, tool_type, test_harness_keypair="test_harness_crypto_sign_keypair",
                 test_harness_sign="test_harness_crypto_sign",
                 ctgrind_taint="taint",dudect_dude="dude" ):
        self.tool_type = tool_type
        self.binsec_test_harness_keypair = test_harness_keypair
        self.binsec_test_harness_sign = test_harness_sign
        self.binsec_configuration_file_keypair = "cfg_keypair"
        self.binsec_configuration_file_sign = "cfg_sign"
        self.ctgrind_taint = ctgrind_taint
        self.dudect_dude = dudect_dude


# A candidate is a string. It refers to as the declaration of a function.
# An object of type Candidate has many attributes like the base name of a given candidate,
# its list of arguments in the (type name) format, the list of its names of arguments, etc.
# Such type of object also incorporate many methods used to set some attributes. For example,
# the arguments names are given by the method get_candidate_arguments_names().


# Call it Target instead of Candidate
class Candidate(object):
    def __init__(self, candidate):
        self.candidate = candidate
        self.candidate_arguments_with_types = {}
        self.candidate_return_type = ""
        self.candidate_types = ""
        self.candidate_args_names = ""
        self.candidate_args_declaration = ""
        self.candidate_basename = ""
        self.candidate_test_harness_name = ""
        self.candidate_source_file_name = ""
        self.candidate_executable = ""  # One call it "base_name-candidate_bin"
        self.candidate_configuration_file = ""
        self.candidate_stats_file = ""
        self.candidate_assumption = ""
        self.parent_header_file = ""
        self.parent_source_file = ""
        self.candidate_secret_data = []
        self.candidate_public_data = []
        self.cmd_binsec_compilation_candidate = []
        self.cmd_binsec_run_candidate = []

        self.candidate_has_arguments_status = True
        self.candidate_split = re.split(r"[()]\s*", candidate)
        self.candidate_args = self.candidate_split[1]
        self.get_candidate_has_arguments_status()

    def get_candidate_has_arguments_status(self):
        if self.candidate_args == '' or self.candidate_args == ' ':
            self.candidate_has_arguments_status = False
        else:
            self.candidate_has_arguments_status = True
            token = tokenize_candidate(self.candidate)
            self.candidate_return_type = token[0]
            self.candidate_basename = token[1]
            self.candidate_types = token[2]
            self.candidate_args_names = token[3]
            self.candidate_args_declaration = token[4]
        return self.candidate_has_arguments_status

    def get_candidate_basename(self):
        return self.candidate_basename

    def get_candidate_source_file_basename(self):
        return self.candidate_basename + ".c"

    def get_candidate_test_harness_basename(self):
        return "test_harness_" + self.candidate_basename + ".c"

    def get_candidate_memory_init_basename(self):
        return "memory_edit_" + self.candidate_basename + ".txt"

    def get_candidate_configuration_basename(self):
        return self.candidate_basename + ".cfg"

    def get_candidate_stats_file_basename(self):
        return self.candidate_basename + ".toml"

    def get_candidate_executable_basename(self):
        return self.candidate_basename + "_bin"

    def get_arg_names(self):
        return self.candidate_args_names

    def get_candidate_arguments_names(self):
        return self.candidate_args_names

    def get_candidate_secret_data(self):
        for el in self.candidate_secret_data:
            if el not in self.candidate_args_names:
                error_message = 'is not an argument of the function'
                print("{0} {1}  {2}".format(el, error_message, self.candidate_basename))
                self.candidate_secret_data = []
                return self.candidate_secret_data
        return self.candidate_secret_data

    def get_candidate_public_data(self):
        for el in self.candidate_public_data:
            if el not in self.candidate_args_names:
                error_message = 'is not an argument of the function'
                print("{0} {1} {2}".format(el, error_message, self.candidate_basename))
                self.candidate_secret_data = []
                return self.candidate_secret_data
        return self.candidate_public_data

    def candidate_arguments_initialization(self, file):
        pass

    def candidate_arguments_declaration(self):
        return self.candidate_args_declaration

    def binsec_compile_candidate(self, folder):
        cand_src_file = glob.glob(folder + '/binsec_' + '*' + '*.c')[0]
        candidate_src_file = os.path.basename(cand_src_file)
        candidate_executable_file = "candidate_exec"
        t_harness = find_starting_pattern(folder, "test_h")
        candidate_exec = candidate_executable_file
        if self.cmd_binsec_compilation_candidate:
            subprocess.call(self.cmd_binsec_compilation_candidate)
        else:
            cmd_str = f'gcc -g -m32 -static {t_harness} {folder}/{candidate_src_file} -o {folder}/{candidate_exec}'
            cmd = cmd_str.split()
            subprocess.call(cmd)

    def binsec_run_candidate(self, folder):
        candidate_executable_file = find_ending_pattern(folder, "_exec")
        config_file = glob.glob(folder + '/*.cfg')[0]
        stats_file = glob.glob(folder + '/*.toml')[0]
        st_file = open(stats_file, 'w')
        st_file.close()
        if self.cmd_binsec_run_candidate:
            subprocess.call(self.cmd_binsec_run_candidate, stdin=sys.stdin)
        else:
            cmd_str = f'''binsec -checkc -checkct-script
                    {config_file} -checkct-stats-file {stats_file}
                    {candidate_executable_file}'''
            cmd = cmd_str.split()
            subprocess.call(cmd, stdin=sys.stdin)


# Take into account the case in which one have a pointer input
# that points to just one value (not really as an array)

def tokenize_argument(argument: str):
    type_arg = ""
    name_arg = ""
    argument_declaration = ""
    default_length = "1000"
    is_pointer = False
    is_array = False
    is_array_with_special_length = False
    if "*" in argument and "[" not in argument:
        is_pointer = True
    elif "[" in argument and "*" not in argument:
        is_array = True
    elif "*" in argument and "[" in argument:
        is_array_with_special_length = True

    argument = argument.strip()
    argument_split = re.split(r"\s", argument)
    argument_split_without_space = [el for el in argument_split if el != '']
    no_space = argument_split_without_space
    if is_pointer:
        no_space = [re.sub(r"\*", "", strg) for strg in no_space]
        no_space = [el for el in no_space if el != '']
        if len(no_space) > 2:
            type_arg = " ".join(no_space[0:-1])
        else:
            type_arg = no_space[0]
        name_arg = no_space[-1]
        argument_declaration = type_arg + " " + name_arg + "[" + default_length + "];"
    elif is_array:
        initial_length_array = re.search(r"\[(.+?)]", argument)
        if initial_length_array:
            if not initial_length_array.group(1) == "" and not initial_length_array.group(1) == " ":
                default_length = initial_length_array.group(1)
                no_space = [re.sub(r"\[", "", strg) for strg in no_space]
                no_space = [re.sub(r"]", "", strg) for strg in no_space]
                no_space = [el for el in no_space if el != '']
                if no_space[-1] == default_length:
                    name_arg = no_space[-2]
                    if len(no_space) > 3:
                        type_arg = " ".join(no_space[0:-2])
                    else:
                        type_arg = no_space[0]
                    argument_declaration = type_arg + " " + name_arg + "[" + default_length + "];"
                else:
                    n_arg = re.split(default_length, no_space[-1])
                    name_arg = n_arg[0]
                    if len(no_space) > 2:
                        type_arg = " ".join(no_space[0:-1])
                    else:
                        type_arg = no_space[0]
                    argument_declaration = type_arg + " " + name_arg + "[" + default_length + "];"
        else:
            no_space = [re.sub(r"\[", "", strg) for strg in no_space]
            no_space = [re.sub("]", "", strg) for strg in no_space]
            no_space = [el for el in no_space if el != '']
            if len(no_space) > 2:
                type_arg = " ".join(no_space[0:-1])
            else:
                type_arg = no_space[0]
            name_arg = no_space[-1]
            argument_declaration = type_arg + " " + name_arg + "[" + default_length + "];"
    elif is_array_with_special_length:
        initial_length_array = re.search(r"\[(.+?)]", argument)
        default_length = initial_length_array.group(1)
        # initial_length_array = initial_length_array.group(0)
        no_space = re.split(r"\[", argument)
        no_space = no_space[0:-1]
        argument_split = re.split(r"\s", no_space[0])
        no_space = [el for el in argument_split if el != '']
        name_arg = no_space[-1]
        if len(no_space) > 2:
            type_arg = " ".join(no_space[0:-1])
        else:
            type_arg = no_space[0]
        argument_declaration = type_arg + " " + name_arg + "[" + default_length + "];"
    else:
        if len(no_space) > 2:
            type_arg = " ".join(no_space[0:-1])
        else:
            type_arg = no_space[0]
        name_arg = no_space[-1]
        argument_declaration = type_arg + " " + name_arg + ";"

    return type_arg, name_arg, argument_declaration


def tokenize_candidate(candidate: str):
    candidate_split = re.split(r"[()]\s*", candidate)
    ret_type_basename = candidate_split[0].split(" ")
    candidate_return_type = ret_type_basename[0]
    candidate_base_name = ret_type_basename[1]
    candidate_args = candidate_split[1]
    if candidate_args == '' or candidate_args == ' ':
        print("The function {} has no arguments", candidate_base_name)
    else:
        candidate_input_names = []
        candidate_input_initialization = []
        candidate_all_types_of_input = []
        for input_arg in re.split(r",", candidate_args):
            type_arg, name_arg, input_declaration = tokenize_argument(input_arg)
            candidate_all_types_of_input.append(type_arg)
            candidate_input_names.append(name_arg)
            candidate_input_initialization.append(input_declaration)
        output = (candidate_return_type, candidate_base_name,
                  candidate_all_types_of_input, candidate_input_names,
                  candidate_input_initialization)
        return output


# List of src subfolders and generate those subfolders into binsec folder


def group_multiple_lines(file_content_list,
                         starting_pattern,
                         ending_pattern,
                         exclude_pattern,
                         starting_index,
                         ending_index):
    matching_string_list = []
    break_index = -1
    found_start_index = 0
    found_end_index = 0
    i = starting_index
    line = file_content_list[i]
    line.strip()
    while (i <= ending_index) and (break_index < 0):
        if exclude_pattern in line:
            i += 1
        line = file_content_list[i]
        line.strip()
        if starting_pattern in line:
            found_start_index = i
            if "int" not in line:
                matching_string_list.append("int")
            matching_string_list.append(line)
            if ending_pattern in line:
                found_end_index = i
                break
            break_index = i
            for j in range(found_start_index + 1, ending_index):
                line = file_content_list[j]
                line.strip()
                matching_string_list.append(line)
                if ending_pattern in line:
                    found_end_index = j
                    break_index = j
                    break
        i += 1

    matching_string_list_strip = [word.strip() for word in matching_string_list]
    matching_string = " ".join(matching_string_list_strip)
    return matching_string, found_start_index, found_end_index


def group_multiple_lines_new_to_check(file_content_list,
                                      starting_pattern,
                                      ending_pattern,
                                      exclude_pattern,
                                      starting_index,
                                      ending_index):
    matching_string_list = []
    break_index = -1
    found_start_index = 0
    found_end_index = 0
    i = starting_index
    line = file_content_list[i]
    line.strip()
    exclude_pattern = exclude_pattern.strip()
    exclude_pattern_list = exclude_pattern.split()
    while (i <= ending_index) and (break_index < 0):
        for word in exclude_pattern_list:
            if word in line:
                i += 1
                line = file_content_list[i]
            if starting_pattern in line and word in line:
                i += 1
                line = file_content_list[i]
        line = file_content_list[i]
        line.strip()
        if starting_pattern in line:
            found_start_index = i
            if "int" not in line:
                matching_string_list.append("int")
            matching_string_list.append(line)
            if ending_pattern in line:
                found_end_index = i
                break
            break_index = i
            for j in range(found_start_index + 1, ending_index):
                line = file_content_list[j]
                line.strip()
                matching_string_list.append(line)
                if ending_pattern in line:
                    found_end_index = j
                    break_index = j
                    break
        i += 1

    matching_string_list_strip = [word.strip() for word in matching_string_list]
    matching_string = " ".join(matching_string_list_strip)
    return matching_string, found_start_index, found_end_index


def find_sign_and_keypair_definition_from_api_or_sign(api_sign_header_file):
    file = open(api_sign_header_file, 'r')
    file_content = file.read()
    file_content_line_by_line = file_content.split('\n')
    exclude_pattern = "open _seed_"
    ending_pattern = ");"
    included_pattern_keypair = "sign_keypair("
    starting_index = 0
    ending_index = len(file_content_line_by_line)
    keypair_def, start, end = group_multiple_lines(file_content_line_by_line,
                                                   included_pattern_keypair,
                                                   ending_pattern, exclude_pattern,
                                                   starting_index, ending_index)
    included_pattern_sign = "_sign("
    starting_index = end + 1
    sign_def, start, end = group_multiple_lines(file_content_line_by_line,
                                                included_pattern_sign,
                                                ending_pattern, exclude_pattern,
                                                starting_index, ending_index)
    file.close()
    keypair_sign_def = [keypair_def, sign_def]
    return keypair_sign_def


def sign_find_args_types_and_names(abs_path_to_api_or_sign):
    keypair_sign_def = find_sign_and_keypair_definition_from_api_or_sign(abs_path_to_api_or_sign)
    sign_candidate = keypair_sign_def[1]
    cand_obj = Candidate(sign_candidate)
    args_names = cand_obj.candidate_args_names
    args_types = cand_obj.candidate_types
    cand_basename = cand_obj.get_candidate_basename()
    cand_return_type = cand_obj.candidate_return_type
    return cand_return_type, cand_basename, args_types, args_names


def keypair_find_args_types_and_names(abs_path_to_api_or_sign):
    keypair_sign_def = find_sign_and_keypair_definition_from_api_or_sign(abs_path_to_api_or_sign)
    keypair_candidate = keypair_sign_def[0]
    cand_obj = Candidate(keypair_candidate)
    args_names = cand_obj.candidate_args_names
    args_types = cand_obj.candidate_types
    cand_basename = cand_obj.get_candidate_basename()
    cand_return_type = cand_obj.candidate_return_type
    return cand_return_type, cand_basename, args_types, args_names


# ======================TEST HARNESS =================================
# ====================================================================
def test_harness_content_keypair(test_harness_file,
                                 api, sign, add_includes,
                                 function_return_type,
                                 function_name):
    test_harness_file_content_block1 = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h>
    '''
    test_harness_file_content_block2 = f'''
    uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;
    uint8_t sk[CRYPTO_SECRETKEYBYTES] ;
    
    int main(){{
    \t{function_return_type} result =  {function_name}(pk, sk);
    \texit(result);
    }} 
    '''
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block1))
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == '""':
            t_harness_file.write(f'#include {sign}\n')
        if not api == '""':
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block2))


def sign_test_harness_content(test_harness_file, api,
                              sign, add_includes,
                              function_return_type,
                              function_name, args_types,
                              args_names):
    if 'const' in args_types[2]:
        args_types[2] = re.sub("const ", "", args_types[2])
        args_types[4] = re.sub("const ", "", args_types[4])
    test_harness_file_content_block1 = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h> 
    '''
    arguments = f'{args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]}'
    test_harness_file_content_block2 = f'''
    #define msg_length  256
    {args_types[0]} {args_names[0]}[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len
    {args_types[1]} {args_names[1]} ;
    {args_types[3]} {args_names[3]} = msg_length ;
    {args_types[2]} {args_names[2]}[msg_length] ;
    {args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES] ;
    
    int main(){{
    \t{function_return_type} result =  {function_name}({arguments});
    \texit(result);
    }}
    '''
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block1))
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == '""':
            t_harness_file.write(f'#include {sign}\n')
        if not api == '""':
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block2))


def ctgrind_keypair_taint_content(taint_file, api,
                                  sign, add_includes,
                                  function_return_type,
                                  function_name,
                                  args_types,
                                  args_names):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    #include <ctgrind.h>
    #include <openssl/rand.h>
    
    '''
    taint_file_content_block_main = f'''
    #define CTGRIND_SAMPLE_SIZE 100
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} *{args_names[1]};
    
    int main() {{
    \t{args_names[0]} = calloc(CRYPTO_PUBLICKEYBYTES, sizeof({args_types[0]})); 
    \t{args_names[1]} = calloc(CRYPTO_SECRETKEYBYTES, sizeof({args_types[1]}));

    \t{function_return_type} result = 2 ;
    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\tct_poison({args_names[1]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[1]}));
    \t\tresult = {function_name}({args_names[0]},{args_names[1]}); 
    \t\tct_unpoison({args_names[1]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[1]})); 
    \t}}

    \tfree({args_names[0]});
    \tfree({args_names[1]});
    \treturn result; 
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        if not sign == '""':
            t_file.write(f'#include {sign}\n')
        if not api == '""':
            t_file.write(f'#include {api}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


def ctgrind_sign_taint_content(taint_file, api, sign,
                               rng, add_includes,
                               function_return_type,
                               function_name, args_types,
                               args_names):
    args_types[2] = re.sub("const ", "", args_types[2])
    args_types[4] = re.sub("const ", "", args_types[4])
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    #include <ctgrind.h>
    '''
    taint_file_content_block_main = f'''
    #define CTGRIND_SAMPLE_SIZE 100
    #define max_message_length 3300
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} {args_names[1]};
    {args_types[2]} *{args_names[2]};
    {args_types[3]} {args_names[3]};
    {args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES];
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \trandombytes({args_names[2]}, {args_names[3]});
    \trandombytes({args_names[4]}, CRYPTO_SECRETKEYBYTES);
    }} 
    
    int main() {{
    
    \t{args_names[2]} = ({args_types[2]} *)calloc({args_names[3]}, sizeof({args_types[2]}));
    \t{args_names[0]} = ({args_types[0]} *)calloc({args_names[3]}+CRYPTO_BYTES, sizeof({args_types[0]})); 
    
    
    \t{function_return_type} result = 2 ; 
    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\t{args_names[3]} = 33*(i+1);
    \t\tgenerate_test_vectors(); 
    \t\tct_poison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tresult = {function_name}({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]}); 
    \t\tct_unpoison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t}}

    \tfree({args_names[0]}); 
    \tfree({args_names[2]});
    \treturn result;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        if not sign == '""':
            t_file.write(f'#include {sign}\n')
        if not api == '""':
            t_file.write(f'#include {api}\n')
        t_file.write(f'#include {rng}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


def dudect_keypair_dude_content(taint_file, api,
                                sign, add_includes,
                                function_return_type,
                                function_name,
                                args_types,
                                args_names):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #define DUDECT_IMPLEMENTATION
    #include <dudect.h>
    
    '''
    taint_file_content_block_main = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    \t{args_types[0]} {args_names[0]}[CRYPTO_PUBLICKEYBYTES] = {{0}};;
    \t{args_types[1]} {args_names[1]}[CRYPTO_SECRETKEYBYTES] = {{0}};;
    
    {function_return_type} \tresult = {function_name}({args_names[0]},{args_names[1]});
    \treturn result;
    }}
    
    void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {{
    \trandombytes(input_data, c->number_measurements * c->chunk_size);
    \tfor (size_t i = 0; i < c->number_measurements; i++) {{
    \t\tclasses[i] = randombit();
    \t\t\tif (classes[i] == 0) {{
    \t\t\t\tmemset(input_data + (size_t)i * c->chunk_size, 0x00, c->chunk_size);
    \t\t\t}} else {{
        // leave random
    \t\t\t}}
    \t\t}}
    \t}}
    
    int main(int argc, char **argv)
    {{
    \t(void)argc;
    \t(void)argv;

    \tdudect_config_t config = {{
    \t\t.chunk_size = 32,
    \t\t.number_measurements = 1e3,
    \t}};
    \tdudect_ctx_t ctx;

    \tdudect_init(&ctx, &config);

    \tdudect_state_t state = DUDECT_NO_LEAKAGE_EVIDENCE_YET;
    \twhile (state == DUDECT_NO_LEAKAGE_EVIDENCE_YET) {{
    \t\tstate = dudect_main(&ctx);
    \t}}
    \tdudect_free(&ctx);
    \treturn (int)state;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        if not sign == '""':
            t_file.write(f'#include {sign}\n')
        if not api == '""':
            t_file.write(f'#include {api}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


def dudect_sign_dude_content(taint_file, api,
                             sign, add_includes,
                             function_return_type,
                             function_name,
                             args_types,
                             args_names):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #define DUDECT_IMPLEMENTATION
    #include <dudect.h>
    
    '''
    type_msg = args_types[2].replace('const', '')
    type_msg = type_msg.strip()
    type_sk = args_types[4].replace('const', '')
    type_sk = type_sk.strip()
    sig_msg = args_names[0]
    sig_msg_len = args_names[1]
    msg = args_names[2]
    msg_len = args_names[3]
    sk = args_names[4]
    ret_type = function_return_type
    taint_file_content_block_main = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    \t{args_types[0]} *{sig_msg};
    \t{args_types[1]} {sig_msg_len};
    \t{type_msg} *{msg};
    \t{args_types[3]} {msg_len};
    \t{type_sk} {sk}[CRYPTO_SECRETKEYBYTES]= {{0}};
    
    \tuint8_t length ;
    \tmemcpy(length, data, 1);
    \tmsg_len = length+(length>>2) # See how to generate randomly the message length 
    \tmemcpy({msg}, data+1, {msg_len});
    \tmemcpy({sk}, data+{msg_len}, CRYPTO_SECRETKEYBYTES);
    
    \t\t{ret_type} result = {function_name}({sig_msg}, &{sig_msg_len}, {msg}, {msg_len}, {sk});
    \treturn result;
    }}
    
    void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {{
    \trandombytes(input_data, c->number_measurements * c->chunk_size);
    \tfor (size_t i = 0; i < c->number_measurements; i++) {{
    \t\tclasses[i] = randombit();
    \t\t\tif (classes[i] == 0) {{
    \t\t\t\tmemset(input_data + (size_t)i * c->chunk_size, 0x00, c->chunk_size);
    \t\t\t}} else {{
        // leave random
    \t\t\t}}
    \t\t}}
    \t}}
    
    int main(int argc, char **argv)
    {{
    \t(void)argc;
    \t(void)argv;

    \tdudect_config_t config = {{
    \t\t.chunk_size = 32,
    \t\t.number_measurements = 1e3,
    \t}};
    \tdudect_ctx_t ctx;

    \tdudect_init(&ctx, &config);

    \tdudect_state_t state = DUDECT_NO_LEAKAGE_EVIDENCE_YET;
    \twhile (state == DUDECT_NO_LEAKAGE_EVIDENCE_YET) {{
    \t\tstate = dudect_main(&ctx);
    \t}}
    \tdudect_free(&ctx);
    \treturn (int)state;
    }}
    '''
    print("---------sign:", sign)
    print("---------api:", api)
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        if not sign == '""':
            t_file.write(f'#include {sign}\n')
        if not api == '""':
            t_file.write(f'#include {api}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


def flowtracker_keypair_xml_content(taint_file, api,
                                    sign, add_includes,
                                    function_return_type,
                                    function_name,
                                    args_types,
                                    args_names):
    pk = args_names[0]
    sk = args_names[1]
    crypto_keypair = function_name
    xml_file_content = f'''
    <functions>
        <sources>
            <function>
                <name>{crypto_keypair}</name>
                <return>false</return>
                <public>
                    <parameter>{pk}</parameter>
                </public>
                <secret>
                    <parameter>{sk}</parameter>       <!--Secret key-->
                </secret>
            </function>
        </sources>
    </functions>
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(xml_file_content))
        # if not add_includes == []:
        #     for include in add_includes:
        #         t_file.write(f'#include {include}\n')
        # if not sign == '""':
        #     t_file.write(f'#include {sign}\n')
        # if not api == '""':
        #     t_file.write(f'#include {api}\n')
        # t_file.write(textwrap.dedent(taint_file_content_block_main))


def flowtracker_sign_xml_content(taint_file, api,
                                 sign, add_includes,
                                 function_return_type,
                                 function_name,
                                 args_types,
                                 args_names):

    sig_msg = args_names[0]
    sig_msg_len = args_names[1]
    msg = args_names[2]
    msg_len = args_names[3]
    sk = args_names[4]
    ret_type = function_return_type
    crypto_sign = function_name
    xml_file_content = f'''
    <functions>
        <sources>
            <function>
                <name>{crypto_sign}</name>
                <return>false</return>
                <public>
                    <parameter>{sig_msg}</parameter>
                    <parameter>{sig_msg_len}</parameter>
                    <parameter>{msg}</parameter>
                    <parameter>{msg_len}</parameter>
                </public>
                <secret>
                    <parameter>{sk}</parameter>       <!--Secret key-->
                </secret>
            </function>
        </sources>
    </functions>
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(xml_file_content))
        # if not add_includes == []:
        #     for include in add_includes:
        #         t_file.write(f'#include {include}\n')
        # if not sign == '""':
        #     t_file.write(f'#include {sign}\n')
        # if not api == '""':
        #     t_file.write(f'#include {api}\n')
        # t_file.write(textwrap.dedent(taint_file_content_block_main))

# ======================CONFIGURATION FILES =================================
# ===========================================================================


def sign_configuration_file_content_deprecated(cfg_file_sign, crypto_sign_args_names):
    sig_msg = crypto_sign_args_names[0]
    sig_msg_len = crypto_sign_args_names[1]
    msg = crypto_sign_args_names[2]
    msg_len = crypto_sign_args_names[3]
    sk = crypto_sign_args_names[4]
    cfg_file_content = f'''
    starting from <main>
    concretize stack
    secret global {sk}
    public global {sig_msg},{sig_msg_len},{msg},{msg_len}
    halt at <exit>
    reach all
    '''
    with open(cfg_file_sign, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))


def sign_configuration_file_content(cfg_file_sign, crypto_sign_args_names):
    sig_msg = crypto_sign_args_names[0]
    sig_msg_len = crypto_sign_args_names[1]
    msg = crypto_sign_args_names[2]
    msg_len = crypto_sign_args_names[3]
    sk = crypto_sign_args_names[4]
    cfg_file_content = f'''
    starting from <main>
    with concrete stack pointer
    secret global {sk}
    public global {sig_msg}, {sig_msg_len}, {msg}, {msg_len}
    halt at <exit>
    explore all
    '''
    with open(cfg_file_sign, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))


def cfg_content_keypair_deprecated(cfg_file_keypair):
    cfg_file_content = f'''
    starting from <main>
    concretize stack
    secret global sk
    public global pk
    halt at <exit>
    reach all
    '''
    with open(cfg_file_keypair, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))


def cfg_content_keypair(cfg_file_keypair):
    cfg_file_content = f'''
    starting from <main>
    with concrete stack pointer
    secret global sk
    public global pk
    halt at <exit>
    explore all
    '''
    with open(cfg_file_keypair, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))


# ======================CREATE folders ==================================
# =======================================================================

# Create same sub-folders in each folder of a given list of folders
def generic_create_tests_folders(list_of_path_to_folders):
    for t_folder in list_of_path_to_folders:
        if not os.path.isdir(t_folder):
            cmd = ["mkdir", "-p", t_folder]
            subprocess.call(cmd, stdin=sys.stdin)


# ======================== COMPILATION ====================================
# =========================================================================

def compile_with_cmake(build_folder_full_path, optional_flags=None):
    if optional_flags is None:
        optional_flags = []
    cwd = os.getcwd()
    os.chdir(build_folder_full_path)
    cmd = ["cmake"]
    if not optional_flags == []:
        cmd.extend(optional_flags)
    cmd_ext = ["../"]
    cmd.extend(cmd_ext)
    subprocess.call(cmd, stdin=sys.stdin)
    cmd = ["make", "-j"]
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)


def compile_with_makefile(path_to_makefile, default=""):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make"]
    if not default == "":
        cmd.append(default)
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)


def compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,
                                                                 path_to_makefile,
                                                                 path_to_build_folder,
                                                                 default=""):
    if not path_to_cmakelist_file == "":
        compile_with_cmake(path_to_build_folder)
    else:
        compile_with_makefile(path_to_makefile, default)


def compile_with_makefile_all(path_to_makefile):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make"]
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)


# ==================== EXECUTION =====================================
# ====================================================================

def run_binsec_deprecated(executable_file, cfg_file, stats_files, output_file, depth):
    command = f'''binsec -checkct -checkct-depth  {depth}   -checkct-script  {cfg_file}
     -checkct-stats-file   {stats_files}  {executable_file} '''
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file, "w") as file:
        for line in output_decode.split('\n'):
            file.write(line + '\n')


def run_binsec(executable_file, cfg_file, stats_files, output_file, depth):
    command = f'''binsec -sse -checkct -sse-depth  {depth} {cfg_file}
        -checkct-stats-file   {stats_files}  {executable_file} '''
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file, "w") as file:
        for line in output_decode.split('\n'):
            file.write(line + '\n')


def run_ctgrind(binary_file, output_file):
    command = f'''valgrind -s --track-origins=yes --leak-check=full 
                --show-leak-kinds=all --verbose --log-file={output_file} ./{binary_file}'''
    cmd_args_lst = command.split()
    subprocess.call(cmd_args_lst, stdin=sys.stdin)


def run_dudect(executable_file, output_file):
    command = f'./{executable_file}'
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file, "w") as file:
        for line in output_decode.split('\n'):
            file.write(line + '\n')


def binsec_generic_run(binsec_folder, signature_type, candidate,
                       optimized_imp_folder, opt_src_folder_list_dir,
                       depth, build_folder, binary_patterns):
    optimized_imp_folder_full_path = signature_type + '/' + candidate + '/' + optimized_imp_folder
    binsec_folder_full_path = optimized_imp_folder_full_path + '/' + binsec_folder
    cfg_pattern = ".cfg"
    if not opt_src_folder_list_dir:
        path_to_subfolder = binsec_folder_full_path
        path_to_build_folder = path_to_subfolder + '/' + build_folder
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            binsec_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{binsec_folder_basename}'
            path_to_pattern_subfolder = f'{path_to_subfolder}/{binsec_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                bin_basename = executable.split('test_harness_')[-1]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                stats_file = f'{path_to_pattern_subfolder}/{bin_pattern}.toml'
                cfg_file = find_ending_pattern(path_to_pattern_subfolder, cfg_pattern)
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                run_binsec(abs_path_to_executable, cfg_file, stats_file, output_file, depth)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = binsec_folder_full_path + '/' + subfold
            path_to_build_folder = path_to_subfolder + '/' + build_folder
            path_to_binary_files = path_to_build_folder
            for bin_pattern in binary_patterns:
                binsec_folder_basename = f'{candidate}_{bin_pattern}'
                path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{binsec_folder_basename}'
                path_to_pattern_subfolder = f'{path_to_subfolder}/{binsec_folder_basename}'
                bin_files = os.listdir(path_to_binary_pattern_subfolder)
                for executable in bin_files:
                    bin_basename = executable.split('test_harness_')[-1]
                    output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                    stats_file = f'{path_to_pattern_subfolder}/{bin_pattern}.toml'
                    cfg_file = find_ending_pattern(path_to_pattern_subfolder, cfg_pattern)
                    abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                    run_binsec(abs_path_to_executable, cfg_file, stats_file, output_file, depth)


def ctgrind_generic_run(ctgrind_folder, signature_type,
                        candidate, optimized_imp_folder,
                        opt_src_folder_list_dir,
                        build_folder, binary_patterns):
    optimized_imp_folder_full_path = signature_type + '/' + candidate + '/' + optimized_imp_folder
    ctgrind_folder_full_path = optimized_imp_folder_full_path + '/' + ctgrind_folder
    if not opt_src_folder_list_dir:
        path_to_build_folder = f'{ctgrind_folder_full_path}/{build_folder}'
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            ctgrind_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{ctgrind_folder_basename}'
            path_to_pattern_subfolder = f'{ctgrind_folder_full_path}/{ctgrind_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                bin_basename = executable.split('taint_')[-1]
                bin_basename = bin_basename.split('.o')[0]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                print("-------------Running: ", abs_path_to_executable)
                run_ctgrind(abs_path_to_executable, output_file)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = ctgrind_folder_full_path + '/' + subfold
            path_to_build_folder = path_to_subfolder + '/' + build_folder
            path_to_binary_files = path_to_build_folder
            for bin_pattern in binary_patterns:
                ctgrind_folder_basename = f'{candidate}_{bin_pattern}'
                path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{ctgrind_folder_basename}'
                path_to_pattern_subfolder = f'{path_to_subfolder}/{ctgrind_folder_basename}'
                bin_files = os.listdir(path_to_binary_pattern_subfolder)
                for executable in bin_files:
                    bin_basename = executable.split('taint_')[-1]
                    bin_basename = bin_basename.split('.o')[0]
                    output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                    abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                    print("-------------Running:", abs_path_to_executable)
                    run_ctgrind(abs_path_to_executable, output_file)


def dudect_generic_run(dudect_folder, signature_type,
                       candidate, optimized_imp_folder,
                       opt_src_folder_list_dir,
                       build_folder, binary_patterns):
    optimized_imp_folder_full_path = signature_type + '/' + candidate + '/' + optimized_imp_folder
    dudect_folder_full_path = optimized_imp_folder_full_path + '/' + dudect_folder
    if not opt_src_folder_list_dir:
        path_to_build_folder = f'{dudect_folder_full_path}/{build_folder}'
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            dudect_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{dudect_folder_basename}'
            path_to_pattern_subfolder = f'{dudect_folder_full_path}/{dudect_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                bin_basename = executable.split('dude_')[-1]
                bin_basename = bin_basename.split('.o')[0]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                print("-------------Running: ", abs_path_to_executable)
                run_ctgrind(abs_path_to_executable, output_file)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = dudect_folder_full_path + '/' + subfold
            path_to_build_folder = path_to_subfolder + '/' + build_folder
            path_to_binary_files = path_to_build_folder
            for bin_pattern in binary_patterns:
                dudect_folder_basename = f'{candidate}_{bin_pattern}'
                path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{dudect_folder_basename}'
                path_to_pattern_subfolder = f'{path_to_subfolder}/{dudect_folder_basename}'
                bin_files = os.listdir(path_to_binary_pattern_subfolder)
                for executable in bin_files:
                    bin_basename = executable.split('dude_')[-1]
                    bin_basename = bin_basename.split('.o')[0]
                    output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                    abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                    print("-------------Running:", abs_path_to_executable)
                    run_dudect(abs_path_to_executable, output_file)


def generic_run(tools_list, signature_type,
                candidate, optimized_imp_folder,
                opt_src_folder_list_dir, depth,
                build_folder, binary_patterns):
    for tool_name in tools_list:
        if 'binsec' in tool_name.lower():
            binsec_folder = tool_name
            binsec_generic_run(binsec_folder, signature_type,
                               candidate, optimized_imp_folder,
                               opt_src_folder_list_dir, depth,
                               build_folder, binary_patterns)
    for tool_name in tools_list:
        if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
            ctgrind_folder = tool_name
            ctgrind_generic_run(ctgrind_folder, signature_type,
                                candidate, optimized_imp_folder,
                                opt_src_folder_list_dir, build_folder,
                                binary_patterns)
    for tool_name in tools_list:
        if 'dudect' in tool_name.lower():
            dudect_folder = tool_name
            dudect_generic_run(dudect_folder, signature_type,
                               candidate, optimized_imp_folder,
                               opt_src_folder_list_dir, build_folder,
                               binary_patterns)

# ========================== INITIALIZATION ==============================
# ========================================================================


def find_candidate_instance_api_sign_relative_path_good_until_4_oct(instance_folder,
                                                                    rel_path_to_api,
                                                                    rel_path_to_sign,
                                                                    rel_path_to_rng):
    api_relative = rel_path_to_api
    sign_relative = rel_path_to_sign
    rng_relative = rel_path_to_rng
    if not instance_folder == "":
        if not rel_path_to_api == "":
            rel_path_to_api_split = rel_path_to_api.split('/')
            for i in range(1, len(rel_path_to_api_split)):
                if not rel_path_to_api_split[i] == '..':
                    rel_path_to_api_split.insert(i, instance_folder)
                    break
            api_relative = '/'.join(rel_path_to_api_split)
        else:
            api_relative = ""
        if not rel_path_to_sign == "":
            rel_path_to_sign_split = rel_path_to_sign.split('/')
            for i in range(1, len(rel_path_to_sign_split)):
                if not rel_path_to_sign_split[i] == '..':
                    rel_path_to_sign_split.insert(i, instance_folder)
                    break
            sign_relative = '/'.join(rel_path_to_sign_split)
        else:
            sign_relative = ""
        # relative path to rng
        rel_path_to_rng_split = rel_path_to_rng.split('/')
        for i in range(1, len(rel_path_to_rng_split)):
            if not rel_path_to_rng_split[i] == '..':
                rel_path_to_rng_split.insert(i, instance_folder)
                break
        rng_relative = '/'.join(rel_path_to_rng_split)
    return api_relative, sign_relative, rng_relative


def find_candidate_instance_api_sign_relative_path(instance_folder, rel_path_to_api,
                                                   rel_path_to_sign, rel_path_to_rng,
                                                   rng_outside_instance_folder="no"):
    api_relative = rel_path_to_api
    sign_relative = rel_path_to_sign
    rng_relative = rel_path_to_rng
    if not instance_folder == "":
        if not rel_path_to_api == "":
            rel_path_to_api_split = rel_path_to_api.split('/')
            for i in range(1, len(rel_path_to_api_split)):
                if not rel_path_to_api_split[i] == '..':
                    rel_path_to_api_split.insert(i, instance_folder)
                    break
            api_relative = '/'.join(rel_path_to_api_split)
        else:
            api_relative = ""
        if not rel_path_to_sign == "":
            rel_path_to_sign_split = rel_path_to_sign.split('/')
            for i in range(1, len(rel_path_to_sign_split)):
                if not rel_path_to_sign_split[i] == '..':
                    rel_path_to_sign_split.insert(i, instance_folder)
                    break
            sign_relative = '/'.join(rel_path_to_sign_split)
        else:
            sign_relative = ""
        # relative path to rng
        if rng_outside_instance_folder == "yes":
            instance_folder_split = instance_folder.split('/')
            if len(instance_folder_split) == 1:
                rng_relative = rel_path_to_rng
            else:
                instance_folder_split.pop()
                instance_folder_parent_folder = '/'.join(instance_folder_split)
                rel_path_to_rng_split = rel_path_to_rng.split('/')
                for i in range(1, len(rel_path_to_rng_split)):
                    if not rel_path_to_rng_split[i] == '..':
                        rel_path_to_rng_split.insert(i, instance_folder_parent_folder)
                        break
                rng_relative = '/'.join(rel_path_to_rng_split)
        else:
            rel_path_to_rng_split = rel_path_to_rng.split('/')
            for i in range(1, len(rel_path_to_rng_split)):
                if not rel_path_to_rng_split[i] == '..':
                    rel_path_to_rng_split.insert(i, instance_folder)
                    break
            rng_relative = '/'.join(rel_path_to_rng_split)
    return api_relative, sign_relative, rng_relative


def find_api_sign_abs_path(path_to_opt_src_folder, api, sign, opt_implementation_name,
                           ref_implementation_name="Reference_Implementation"):
    folder = path_to_opt_src_folder
    ref_implementation_name.strip()
    opt_implementation_name.strip()
    abs_path_to_api_or_sign = ""
    if not api == '""':
        api_folder_split = api.split("../")
        api_folder = api_folder_split[-1]
        api_folder = api_folder.split('"')
        api_folder = api_folder[0]
        abs_path_to_api_or_sign = f'{folder}/{api_folder}'
    if not sign == '""':
        sign_folder_split = sign.split("../")
        sign_folder = sign_folder_split[-1]
        sign_folder = sign_folder.split('"')
        sign_folder = sign_folder[0]
        abs_path_to_api_or_sign = f'{folder}/{sign_folder}'
    if ref_implementation_name in abs_path_to_api_or_sign:
        candidate_folder_list = abs_path_to_api_or_sign.split("/")
        if opt_implementation_name in candidate_folder_list:
            candidate_folder_list.remove(opt_implementation_name)
        candidate_folder = "/".join(candidate_folder_list)
        abs_path_to_api_or_sign = candidate_folder
    return abs_path_to_api_or_sign


def binsec_initialize_candidate(path_to_opt_src_folder,
                                path_to_binsec_folder,
                                path_to_binsec_keypair_folder,
                                path_to_binsec_sign_folder, api,
                                sign, add_includes):
    list_of_path_to_folders = [path_to_binsec_folder,
                               path_to_binsec_keypair_folder,
                               path_to_binsec_sign_folder]
    generic_create_tests_folders(list_of_path_to_folders)
    tool_type = "binsec"
    opt_implementation_name = os.path.basename(path_to_opt_src_folder)
    abs_path_to_api_or_sign = find_api_sign_abs_path(path_to_opt_src_folder, api,
                                                     sign, opt_implementation_name)
    binsec_tool = GenericPatterns(tool_type)
    test_harness_keypair_basename = f'{binsec_tool.binsec_test_harness_keypair}.c'
    test_harness_sign_basename = f'{binsec_tool.binsec_test_harness_sign}.c'
    cfg_file = binsec_tool.binsec_configuration_file_keypair
    cfg_file_keypair = f'{path_to_binsec_keypair_folder}/{cfg_file}.cfg'
    cfg_content_keypair(cfg_file_keypair)
    test_harness_keypair = f'{path_to_binsec_keypair_folder}/{test_harness_keypair_basename}'
    ret_kp = keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type, f_basename, args_types, args_names = ret_kp
    test_harness_content_keypair(test_harness_keypair, api, sign, add_includes, return_type, f_basename)
    ret_sign = sign_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type, f_basename, args_types, args_names = ret_sign
    cfg_file_sign = f'{path_to_binsec_sign_folder}/{binsec_tool.binsec_configuration_file_sign}.cfg'
    crypto_sign_args_names = args_names
    sign_configuration_file_content(cfg_file_sign, crypto_sign_args_names)
    test_harness_sign = f'{path_to_binsec_sign_folder}/{test_harness_sign_basename}'
    sign_test_harness_content(test_harness_sign, api, sign, add_includes, return_type, f_basename, args_types,
                              args_names)


def ctgrind_initialize_candidate(path_to_opt_src_folder,
                                 path_to_ctgrind_folder,
                                 path_to_ctgrind_keypair_folder,
                                 path_to_ctgrind_sign_folder, api,
                                 sign, rng, add_includes):
    list_of_path_to_folders = [path_to_ctgrind_folder,
                               path_to_ctgrind_keypair_folder,
                               path_to_ctgrind_sign_folder]
    generic_create_tests_folders(list_of_path_to_folders)
    tool_type = "ctgrind"
    opt_implementation_name = os.path.basename(path_to_opt_src_folder)
    abth_p = find_api_sign_abs_path(path_to_opt_src_folder, api,
                                    sign, opt_implementation_name)
    abs_path_to_api_or_sign = abth_p
    ctgrind_tool = GenericPatterns(tool_type)
    taint_keypair_basename = f'{ctgrind_tool.ctgrind_taint}.c'
    test_sign_basename = f'{ctgrind_tool.ctgrind_taint}.c'
    taint_keypair = f'{path_to_ctgrind_keypair_folder}/{taint_keypair_basename}'
    ret_kp = keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type, f_basename, args_types, args_names = ret_kp
    ctgrind_keypair_taint_content(taint_keypair, api, sign,
                                  add_includes, return_type,
                                  f_basename, args_types, args_names)
    taint_sign = f'{path_to_ctgrind_sign_folder}/{test_sign_basename}'
    ret_sign = sign_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type, f_basename, args_types, args_names = ret_sign
    ctgrind_sign_taint_content(taint_sign, api, sign, rng,
                               add_includes, return_type,
                               f_basename, args_types, args_names)




# api, sign, rng = find_candidate_instance_api_sign_relative_path(instance_folder,
#                                                                 rel_path_to_api,
#                                                                 rel_path_to_sign,
#                                                                 rel_path_to_rng,
#                                                                 rng_outside_instance_folder)
# path_to_opt_src_folder = "mpc-in-the-head/mira/Optimized_Implementation"
# path_to_tool_folder = f'{path_to_opt_src_folder}/binsec'
# path_to_tool_keypair_folder = f'{path_to_tool_folder}/MIRA-128f/mira_keypair'
# path_to_tool_sign_folder = f'{path_to_tool_folder}/MIRA-128f/mira_sign'
# api = '"../../MIRA-128f/src/api.h"'
# sign = '""'
# rng = '"../../MIRA-128f/lib/randombytes/randombytes.h"'
# add_includes = []
#
#
# tool_initialize_candidate(path_to_opt_src_folder,
#                           path_to_tool_folder,
#                           path_to_tool_keypair_folder,
#                           path_to_tool_sign_folder, api,
#                           sign, rng, add_includes)



def dudect_initialize_candidate(path_to_opt_src_folder,
                                path_to_dudect_folder,
                                path_to_dudect_keypair_folder,
                                path_to_dudect_sign_folder, api,
                                sign, rng, add_includes):
    list_of_path_to_folders = [path_to_dudect_folder,
                               path_to_dudect_keypair_folder,
                               path_to_dudect_sign_folder]
    generic_create_tests_folders(list_of_path_to_folders)
    tool_type = "dudect"
    opt_implementation_name = os.path.basename(path_to_opt_src_folder)
    abth_p = find_api_sign_abs_path(path_to_opt_src_folder, api,
                                    sign, opt_implementation_name)
    abs_path_to_api_or_sign = abth_p
    dudect_tool = GenericPatterns(tool_type)
    dude_keypair_basename = f'{dudect_tool.dudect_dude}.c'
    test_sign_basename = f'{dudect_tool.dudect_dude}.c'
    dude_keypair = f'{path_to_dudect_keypair_folder}/{dude_keypair_basename}'
    ret_kp = keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type, f_basename, args_types, args_names = ret_kp
    dudect_keypair_dude_content(dude_keypair, api, sign,
                                add_includes, return_type,
                                f_basename, args_types, args_names)
    dude_sign = f'{path_to_dudect_sign_folder}/{test_sign_basename}'
    ret_sign = sign_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type, f_basename, args_types, args_names = ret_sign
    dudect_sign_dude_content(dude_sign, api, sign,
                             add_includes, return_type,
                             f_basename, args_types, args_names)


def tool_initialize_candidate(path_to_opt_src_folder,
                              path_to_tool_folder,
                              path_to_tool_keypair_folder,
                              path_to_tool_sign_folder, api,
                              sign, rng, add_includes):
    list_of_path_to_folders = [path_to_tool_folder,
                               path_to_tool_keypair_folder,
                               path_to_tool_sign_folder]
    generic_create_tests_folders(list_of_path_to_folders)
    tool_name = os.path.basename(path_to_tool_folder)
    opt_implementation_name = os.path.basename(path_to_opt_src_folder)
    abth_p = find_api_sign_abs_path(path_to_opt_src_folder, api,
                                    sign, opt_implementation_name)
    abs_path_to_api_or_sign = abth_p
    tool_type = tool.Tools(tool_name)
    tes_keypair_basename, tes_sign_basename = tool_type.get_tool_test_file_name()
    if tool_name == 'flowtracker':
        test_keypair_basename = f'{tes_keypair_basename}.xml'
        test_sign_basename = f'{tes_sign_basename}.xml'
    else:
        test_keypair_basename = f'{tes_keypair_basename}.c'
        test_sign_basename = f'{tes_sign_basename}.c'
    test_keypair = f'{path_to_tool_keypair_folder}/{test_keypair_basename}'
    ret_kp = keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type_kp, f_basename_kp, args_types_kp, args_names_kp = ret_kp

    test_sign = f'{path_to_tool_sign_folder}/{test_sign_basename}'
    ret_sign = sign_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type_s, f_basename_s, args_types_s, args_names_s = ret_sign

    if tool_name == 'ctgrind':
        ctgrind_keypair_taint_content(test_keypair, api, sign,
                                      add_includes, return_type_kp,
                                      f_basename_kp, args_types_kp, args_names_kp)
        ctgrind_sign_taint_content(test_sign, api, sign, rng,
                                   add_includes, return_type_s,
                                   f_basename_s, args_types_s, args_names_s)
    if tool_name == 'binsec':
        cfg_file_kp, cfg_file_sign = tool_type.binsec_configuration_files()
        cfg_file_keypair = f'{path_to_tool_keypair_folder}/{cfg_file_kp}.cfg'
        cfg_content_keypair(cfg_file_keypair)
        test_harness_content_keypair(test_keypair, api, sign, add_includes, return_type_kp,
                                     f_basename_kp)
        crypto_sign_args_names = args_names_s
        cfg_file_sign = f'{path_to_tool_sign_folder}/{cfg_file_sign}.cfg'
        sign_configuration_file_content(cfg_file_sign, crypto_sign_args_names)
        sign_test_harness_content(test_sign, api, sign, add_includes, return_type_s, f_basename_s,
                                  args_types_s, args_names_s)

    if tool_name == 'dudect':
        dudect_keypair_dude_content(test_keypair, api, sign,
                                    add_includes, return_type_kp,
                                    f_basename_kp, args_types_kp, args_names_kp)
        dudect_sign_dude_content(test_sign, api, sign,
                                 add_includes, return_type_s,
                                 f_basename_s, args_types_s, args_names_s)
    if tool_name == 'flowtracker':
        flowtracker_keypair_xml_content(test_keypair, api, sign,
                                        add_includes, return_type_kp,
                                        f_basename_kp, args_types_kp, args_names_kp)
        flowtracker_sign_xml_content(test_sign, api, sign,
                                     add_includes, return_type_s,
                                     f_basename_s, args_types_s, args_names_s)


def initialization(tools_list, signature_type,
                   candidate, optimized_imp_folder,
                   instance_folder, api, sign,
                   rng, add_includes):
    path_to_opt_src_folder = signature_type + '/' + candidate + '/' + optimized_imp_folder
    tools_list_lowercase = [tool.lower() for tool in tools_list]

    for tool_name in tools_list_lowercase:
        tool_folder = tool_name
        path_to_tool_folder = path_to_opt_src_folder + '/' + tool_folder
        tool_keypair_folder_basename = candidate + '_keypair'
        tool_sign_folder_basename = candidate + '_sign'
        path_to_instance = path_to_tool_folder
        if not instance_folder == "":
            path_to_instance = path_to_instance + '/' + instance_folder
        path_to_tool_keypair_folder = path_to_instance + '/' + tool_keypair_folder_basename
        path_to_tool_sign_folder = path_to_instance + '/' + tool_sign_folder_basename
        tool_initialize_candidate(path_to_opt_src_folder,
                                  path_to_tool_folder,
                                  path_to_tool_keypair_folder,
                                  path_to_tool_sign_folder, api,
                                  sign, rng, add_includes)


def initialize_nist_candidate(tools_list, signature_type,
                              candidate, optimized_imp_folder,
                              instance_folder, api, sign,
                              rng, add_includes):
    path_to_opt_src_folder = signature_type + '/' + candidate + '/' + optimized_imp_folder
    tools_list_lowercase = [tool.lower() for tool in tools_list]
    binsec_folder = ""
    ctgrind_folder = ""
    dudect_folder = ""
    for tool_name in tools_list_lowercase:
        if 'binsec' in tool_name:
            binsec_folder = tool_name
        if 'ctgrind' in tool_name or 'ct_grind' in tool_name:
            ctgrind_folder = tool_name
        if 'dudect' in tool_name:
            dudect_folder = tool_name
    binsec = "binsec"
    ctgrind = "ctgrind"
    dudect = "dudect"
    if binsec in tools_list_lowercase:
        path_to_binsec_folder = path_to_opt_src_folder + '/' + binsec_folder
        binsec_keypair_folder_basename = candidate + '_keypair'
        binsec_sign_folder_basename = candidate + '_sign'
        path_to_instance = path_to_binsec_folder
        if not instance_folder == "":
            path_to_instance = path_to_instance + '/' + instance_folder
        path_to_binsec_keypair_folder = path_to_instance + '/' + binsec_keypair_folder_basename
        path_to_binsec_sign_folder = path_to_instance + '/' + binsec_sign_folder_basename
        binsec_initialize_candidate(path_to_opt_src_folder,
                                    path_to_binsec_folder,
                                    path_to_binsec_keypair_folder,
                                    path_to_binsec_sign_folder, api,
                                    sign, add_includes)
    if ctgrind in tools_list_lowercase or 'ct_grind' in tools_list_lowercase:
        path_to_ctgrind_folder = path_to_opt_src_folder + '/' + ctgrind_folder
        ctgrind_keypair_folder_basename = candidate + '_keypair'
        ctgrind_sign_folder_basename = candidate + '_sign'
        path_to_instance = path_to_ctgrind_folder
        if not instance_folder == "":
            path_to_instance = path_to_instance + '/' + instance_folder
        path_to_ctgrind_keypair_folder = path_to_instance + '/' + ctgrind_keypair_folder_basename
        path_to_ctgrind_sign_folder = path_to_instance + '/' + ctgrind_sign_folder_basename
        ctgrind_initialize_candidate(path_to_opt_src_folder,
                                     path_to_ctgrind_folder,
                                     path_to_ctgrind_keypair_folder,
                                     path_to_ctgrind_sign_folder,
                                     api, sign, rng, add_includes)
    if dudect in tools_list_lowercase:
        path_to_dudect_folder = path_to_opt_src_folder + '/' + dudect_folder
        dudect_keypair_folder_basename = candidate + '_keypair'
        dudect_sign_folder_basename = candidate + '_sign'
        path_to_instance = path_to_dudect_folder
        if not instance_folder == "":
            path_to_instance = path_to_instance + '/' + instance_folder
        path_to_dudect_keypair_folder = path_to_instance + '/' + dudect_keypair_folder_basename
        path_to_dudect_sign_folder = path_to_instance + '/' + dudect_sign_folder_basename
        dudect_initialize_candidate(path_to_opt_src_folder,
                                    path_to_dudect_folder,
                                    path_to_dudect_keypair_folder,
                                    path_to_dudect_sign_folder,
                                    api, sign, rng, add_includes)


def generic_initialize_nist_candidate(tools_list, signature_type, candidate,
                                      optimized_imp_folder, instance_folders_list,
                                      rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                                      add_includes, rng_outside_instance_folder="no"):
    if not instance_folders_list:
        instance_folder = ""
        api, sign, rng = find_candidate_instance_api_sign_relative_path(instance_folder,
                                                                        rel_path_to_api,
                                                                        rel_path_to_sign,
                                                                        rel_path_to_rng,
                                                                        rng_outside_instance_folder)
        initialization(tools_list, signature_type,
                       candidate, optimized_imp_folder,
                       instance_folder, api, sign,
                       rng, add_includes)
    else:
        for instance_folder in instance_folders_list:
            api, sign, rng = find_candidate_instance_api_sign_relative_path(instance_folder,
                                                                            rel_path_to_api,
                                                                            rel_path_to_sign,
                                                                            rel_path_to_rng,
                                                                            rng_outside_instance_folder)
            initialization(tools_list, signature_type,
                           candidate, optimized_imp_folder,
                           instance_folder, api, sign,
                           rng, add_includes)


def set_include_correct_format(api, sign, rng):
    if not api.startswith('"'):
        api = f'"{api}"'
    if not sign.startswith('"'):
        sign = f'"{sign}"'
    if not rng.startswith('"'):
        rng = f'"{rng}"'
    return api, sign, rng


def generic_init_compile(tools_list, signature_type, candidate,
                         optimized_imp_folder, instance_folders_list,
                         rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                         add_includes, build_folder, with_cmake,
                         rng_outside_instance_folder="no"):
    api, sign, rng = set_include_correct_format(rel_path_to_api, rel_path_to_sign, rel_path_to_rng)
    rel_path_to_api = api
    rel_path_to_sign = sign
    rel_path_to_rng = rng
    cmd = []
    path_to_opt_impl_folder = signature_type + '/' + candidate + '/' + optimized_imp_folder
    if not instance_folders_list:
        generic_initialize_nist_candidate(tools_list, signature_type,
                                          candidate, optimized_imp_folder,
                                          instance_folders_list, rel_path_to_api,
                                          rel_path_to_sign, rel_path_to_rng,
                                          add_includes, rng_outside_instance_folder)
        instance = '""'
        for tool_type in tools_list:
            if with_cmake == 'yes':
                path_to_cmakelist_file = path_to_opt_impl_folder + '/' + tool_type
                path_to_build_folder = path_to_cmakelist_file + '/' + build_folder
                path_to_makefile_folder = ""
                function_pattern = "cmake"
                path_function_pattern_file = path_to_cmakelist_file
            else:
                path_to_makefile_folder = path_to_opt_impl_folder + '/' + tool_type
                path_to_build_folder = path_to_makefile_folder + '/' + build_folder
                path_to_cmakelist_file = ""
                function_pattern = "makefile"
                path_function_pattern_file = path_to_makefile_folder
            arguments = f'{path_function_pattern_file},{instance},{tool_type},{candidate}'
            funct = f'{function_pattern}_{candidate}({arguments})'
            exec(f'{funct}')
            if not os.path.isdir(path_to_build_folder):
                cmd = ["mkdir", "-p", path_to_build_folder]
                subprocess.call(cmd, stdin=sys.stdin)
            compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,
                                                                         path_to_makefile_folder,
                                                                         path_to_build_folder,
                                                                         "all")
    else:
        for instance in instance_folders_list:
            generic_initialize_nist_candidate(tools_list, signature_type,
                                              candidate, optimized_imp_folder,
                                              instance_folders_list, rel_path_to_api,
                                              rel_path_to_sign, rel_path_to_rng,
                                              add_includes, rng_outside_instance_folder)
            for tool_type in tools_list:
                if with_cmake == 'yes':
                    path_to_cmakelist_file = path_to_opt_impl_folder + '/' + tool_type + '/' + instance
                    path_to_build_folder = path_to_cmakelist_file + '/' + build_folder
                    path_to_makefile_folder = ""
                    function_pattern = "cmake"
                    path_function_pattern_file = path_to_cmakelist_file
                else:
                    path_to_makefile_folder = f'{path_to_opt_impl_folder}/{tool_type}/{instance}'
                    path_to_build_folder = f'{path_to_makefile_folder}/{build_folder}'
                    path_to_cmakelist_file = ""
                    function_pattern = "makefile"
                    path_function_pattern_file = path_to_makefile_folder
                arguments = f'path_function_pattern_file,instance,tool_type,candidate'
                funct = f'{function_pattern}_{candidate}({arguments})'
                exec(funct)
                if not os.path.isdir(path_to_build_folder):
                    cmd = ["mkdir", "-p", path_to_build_folder]
                subprocess.call(cmd, stdin=sys.stdin)
                compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,
                                                                             path_to_makefile_folder,
                                                                             path_to_build_folder,
                                                                             "all")


def generic_compile_run_candidate(tools_list, signature_type, candidate,
                                  optimized_imp_folder, instance_folders_list,
                                  rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                                  with_cmake, add_includes, to_compile, to_run,
                                  depth, build_folder, binary_patterns,
                                  rng_outside_instance_folder="no"):
    candidate = candidate
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        generic_init_compile(tools_list, signature_type, candidate,
                             optimized_imp_folder, instance_folders_list,
                             rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                             add_includes, build_folder, with_cmake,
                             rng_outside_instance_folder)
        generic_run(tools_list, signature_type, candidate, optimized_imp_folder,
                    instance_folders_list, depth, build_folder, binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        generic_init_compile(tools_list, signature_type, candidate,
                             optimized_imp_folder, instance_folders_list,
                             rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                             add_includes, build_folder, with_cmake,
                             rng_outside_instance_folder)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list, signature_type, candidate, optimized_imp_folder,
                    instance_folders_list, depth, build_folder, binary_patterns)


def add_cli_arguments(subparser,
                      signature_type,
                      candidate,
                      optimized_imp_folder,
                      rel_path_to_api='""',
                      rel_path_to_sign='""',
                      rel_path_to_rng='""',
                      is_rng_in_cwd="no",
                      candidate_default_list_of_folders=None):
    if candidate_default_list_of_folders is None:
        candidate_default_list_of_folders = []
    candidate_parser = subparser.add_parser(f'{candidate}',
                                            help=f'{candidate}:...',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Default tools list
    default_tools_list = ["binsec", "ctgrind", "dudect", "flowtracker"]
    # Default algorithms pattern to test
    default_binary_patterns = ["keypair", "sign"]

    arguments = f"'--tools', '-tools', dest='tools', nargs='+', default={default_tools_list}, help = 'tools'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--signature_type', '-type',dest='type',type=str,default=f'{signature_type}',help=' type'"
    add_args_commdand = f"candidate_parser.add_argument(f{arguments})"
    exec(add_args_commdand)
    arguments = f"'--candidate', '-candidate',dest='candidate',type=str,default=f'{candidate}',help ='{candidate}'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default=f'{optimized_imp_folder}'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--instance_folders_list', nargs='+', default={candidate_default_list_of_folders}"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--rel_path_to_api', '-api',dest='api',type=str, default=f'{rel_path_to_api}',help = 'api'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--rel_path_to_sign', '-sign', dest='sign',type=str,default=f'{rel_path_to_sign}',help = 'sign'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--rel_path_to_rng', '-rng', dest='rng',type=str,default=f'{rel_path_to_rng}'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--compile', '-c', dest='compile',default='Yes'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--run', '-r', dest='run',default='Yes'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--depth', '-depth', dest='depth',default='1000000',help = 'depth'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--build', '-build', dest='build',default='build'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--algorithms_patterns', nargs='+', default={default_binary_patterns},help = 'algorithms_patterns'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--is_rng_outside_folder','-rng_outside',dest='rng_outside', default=f'{is_rng_in_cwd}',help = 'no'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
