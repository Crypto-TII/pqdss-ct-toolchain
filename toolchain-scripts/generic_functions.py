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


def find_ending_pattern(folder, pattern):
    test_folder = glob.glob(folder + '/*' + pattern)
    return test_folder[0]


def get_default_list_of_folders(candidate_default_list_of_folders, tools_list):
    for tool_name in tools_list:
        if tool_name in candidate_default_list_of_folders:
            candidate_default_list_of_folders.remove(tool_name)
    return candidate_default_list_of_folders


# Patterns of test files (.c files) for binsec - ctgrind - dudect;
# and also for binsec script file (configuration file).
class GenericPatterns(object):
    def __init__(self, tool_type, test_harness_keypair="test_harness_crypto_sign_keypair",
                 test_harness_sign="test_harness_crypto_sign",
                 ctgrind_taint="taint", dudect_dude="dude"):
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
        self.candidate_types = []
        self.candidate_args_names = []
        self.candidate_args_declaration = []
        self.candidate_basename = ""
        self.candidate_test_harness_name = ""
        self.candidate_source_file_name = ""
        self.candidate_executable = ""  # One call it "base_name-candidate_bin"
        self.candidate_secret_data = []
        self.candidate_public_data = []
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

    def get_candidate_configuration_basename(self):
        return self.candidate_basename + ".cfg"

    def get_candidate_stats_file_basename(self):
        return self.candidate_basename + ".toml"

    def get_arg_names(self):
        return self.candidate_args_names

    def get_candidate_arguments_names(self):
        return self.candidate_args_names

    def candidate_arguments_declaration(self):
        return self.candidate_args_declaration


# Tools: object of type 'Tools' consists in:
# 1. tool name
# 2. tool's required flags and libraries for candidate compilation
# 3. tool's test files patterns
class Tools(object):
    """Create an object, tool, encapsulating its flags
    and execution method"""

    def __init__(self, tool_name):
        self.tool_flags = ""
        self.tool_libs = ""
        self.tool_test_file_name = ""
        self.tool_name = tool_name

    def get_tool_flags_and_libs(self):
        if self.tool_name == 'binsec':
            self.tool_flags = "-g" # -static
            return self.tool_flags, self.tool_libs
        if self.tool_name == 'ctgrind':
            self.tool_flags = "-Wall -ggdb  -std=c99  -Wextra"
            self.tool_libs = "-lctgrind -lm"
            return self.tool_flags, self.tool_libs
        if self.tool_name == 'dudect':
            self.tool_flags = "-std=c11"
            self.tool_libs = "-lm"
            return self.tool_flags, self.tool_libs
        if self.tool_name == 'flowtracker':
            self.tool_flags = "-emit-llvm -g"
            self.tool_libs = ""
            return self.tool_flags, self.tool_libs

    def get_tool_test_file_name(self):
        if self.tool_name == 'binsec':
            self.tool_test_file_name = "test_harness"
            keypair = f'{self.tool_test_file_name}_crypto_sign_keypair'
            sign = f'{self.tool_test_file_name}_crypto_sign'
            return keypair, sign
        if self.tool_name == 'ctgrind':
            self.tool_test_file_name = "taint"
            keypair = f'{self.tool_test_file_name}_crypto_sign_keypair'
            sign = f'{self.tool_test_file_name}_crypto_sign'
            return keypair, sign
        if self.tool_name == 'dudect':
            self.tool_test_file_name = "dude"
            keypair = f'{self.tool_test_file_name}_crypto_sign_keypair'
            sign = f'{self.tool_test_file_name}_crypto_sign'
            return keypair, sign
        if self.tool_name == 'flowtracker':
            self.tool_test_file_name = "rbc"
            keypair = f'{self.tool_test_file_name}_crypto_sign_keypair'
            sign = f'{self.tool_test_file_name}_crypto_sign'
            return keypair, sign

    @staticmethod
    def binsec_configuration_files():
        kp_cfg = "cfg_keypair"
        sign_cfg = "cfg_sign"
        return kp_cfg, sign_cfg


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


# tokenize_candidate: for a given function declaration (candidate), extracts:
# 1. function return type (void is excluded)
# 2. function name
# 3. arguments names
# 4. arguments types
# 5. default declaration/initialisation of arguments
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


# group_multiple_lines: deals with multiple lines function declaration. Reconstructs the
# function declaration as a single line.
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


# Get crypto_sign_keypair and crypto_sign functions declarations given the path to the header file (api.h/sign.h)
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


# sign_find_args_types_and_names: gets 'crypto_sign_keypair' arguments types/names and its return type
def sign_find_args_types_and_names(abs_path_to_api_or_sign):
    keypair_sign_def = find_sign_and_keypair_definition_from_api_or_sign(abs_path_to_api_or_sign)
    sign_candidate = keypair_sign_def[1]
    cand_obj = Candidate(sign_candidate)
    args_names = cand_obj.candidate_args_names
    args_types = cand_obj.candidate_types
    cand_basename = cand_obj.get_candidate_basename()
    cand_return_type = cand_obj.candidate_return_type
    return cand_return_type, cand_basename, args_types, args_names


# sign_find_args_types_and_names: get 'crypto_sign' arguments types/names and its return type
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

# BINSEC: Test harness for crypto_sign_keypair
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


# BINSEC: Test harness for crypto_sign
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
    #define msg_length  3300
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


# CTGRIND: taint for crypto_sign_keypair
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


# CTGRIND: taint for crypto_sign
def ctgrind_sign_taint_content(taint_file, api, sign,
                               rng, add_includes,
                               function_return_type,
                               function_name, args_types,
                               args_names):
    args_types[2] = re.sub("const ", "", args_types[2])
    args_types[4] = re.sub("const ", "", args_types[4])
    type_sk_with_no_const = args_types[4]
    secret_key = args_names[4]
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
    {args_types[1]} {args_names[1]} = 0;
    //{args_types[1]} *{args_names[1]};
    {args_types[2]} *{args_names[2]};
    {args_types[3]} {args_names[3]} = 0;
    {args_types[4]} {secret_key}[CRYPTO_SECRETKEYBYTES] = {{0}};
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \trandombytes({args_names[2]}, {args_names[3]});
    \t//randombytes({args_names[4]}, CRYPTO_SECRETKEYBYTES);
    \t{type_sk_with_no_const} public_key[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t(void)crypto_sign_keypair(public_key, {secret_key});
    }} 
    
    int main() {{
    \t{function_return_type} result = 2 ; 
    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\t{args_names[3]} = 33*(i+1);
    \t\t{args_names[2]} = ({args_types[2]} *)calloc({args_names[3]}, sizeof({args_types[2]}));
    \t\t{args_names[0]} = ({args_types[0]} *)calloc({args_names[3]}+CRYPTO_BYTES, sizeof({args_types[0]}));
    
    \t\tgenerate_test_vectors(); 
    \t\tct_poison({secret_key}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tresult = {function_name}({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {secret_key}); 
    \t\tct_unpoison({secret_key}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tfree({args_names[0]});
    \t\tfree({args_names[2]});
    \t}}
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


# DUDECT: for crypto_sign_keypair
def dudect_keypair_dude_content(taint_file, api,
                                sign, add_includes,
                                function_return_type,
                                function_name,
                                args_types,
                                args_names, number_of_measurements='1e4'):
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
    
    \t{function_return_type} result = {function_name}({args_names[0]},{args_names[1]});
    \treturn result;
    }}
    
    void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {{
    \trandombytes_dudect(input_data, c->number_measurements * c->chunk_size);
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
    \t\t.number_measurements = {number_of_measurements},
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


# DUDECT: for crypto_sign
def dudect_sign_dude_content(taint_file, api,
                             sign, add_includes,
                             function_return_type,
                             function_name,
                             args_types,
                             args_names, number_of_measurements='1e4'):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #define DUDECT_IMPLEMENTATION
    #include <dudect.h>
    
    #define MESSAGE_LENGTH 3300
    
    #define SECRET_KEY_BYTE_LENGTH CRYPTO_SECRETKEYBYTES
    #define SIGNATURE_MESSAGE_BYTE_LENGTH (MESSAGE_LENGTH + CRYPTO_BYTES)
    
    '''
    type_msg = args_types[2]
    type_sk = args_types[4]

    type_sk_with_no_const = type_sk.replace('const', '')
    type_sk_with_no_const = type_sk_with_no_const.strip()

    sig_msg = args_names[0]
    sig_msg_len = args_names[1]
    msg = args_names[2]
    msg_len = args_names[3]
    sk = args_names[4]
    ret_type = function_return_type
    taint_file_content_block_main = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    
    \t{args_types[1]} {sig_msg_len} = SIGNATURE_MESSAGE_BYTE_LENGTH; //the signature length could be initialized to 0.
    \t{args_types[0]} {sig_msg}[SIGNATURE_MESSAGE_BYTE_LENGTH] = {{0}};
    \t{args_types[3]} {msg_len} = MESSAGE_LENGTH; //  the message length could be also randomly generated.
    \t{type_msg} *{msg} = ({type_msg}*)data + 0; 
    \t{type_sk} *{sk} = ({type_sk}*)data + MESSAGE_LENGTH*sizeof({type_msg}) ; 
    
    \tuint8_t ret_val = 0;
    \tconst {ret_type} result = {function_name}({sig_msg}, &{sig_msg_len}, {msg}, {msg_len}, {sk});
    \tret_val ^= (uint8_t) result ^ {sig_msg}[0] ^ {sig_msg}[SIGNATURE_MESSAGE_BYTE_LENGTH - 1];
    \treturn ret_val;
    }}
    
    void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {{
    \trandombytes_dudect(input_data, c->number_measurements * c->chunk_size);
    \t{type_sk_with_no_const} public_key[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t{type_sk_with_no_const} fixed_secret_key[CRYPTO_SECRETKEYBYTES] = {{0}};
    \t(void)crypto_sign_keypair(public_key, fixed_secret_key);
    \tfor (size_t i = 0; i < c->number_measurements; i++) {{
    \t\tclasses[i] = randombit();
    \t\t\tif (classes[i] == 0) {{
     \t\t\t\t//Uncomment this line if you want to have a fixed message in this class.
    \t\t\t\t//memset(input_data + (size_t)i * c->chunk_size, 0x01, MESSAGE_LENGTH*sizeof({type_msg}));
    \t\t\t\tmemcpy(input_data + (size_t)i * c->chunk_size+MESSAGE_LENGTH*sizeof({type_msg}), 
    \t\t\t\t        fixed_secret_key, SECRET_KEY_BYTE_LENGTH*sizeof({type_sk}));
    \t\t\t}} else {{
    \t\t\t\t//Uncomment this line if you want to have a fixed message in this class.
    \t\t\t\t//memset(input_data + (size_t)i * c->chunk_size, 0x01, MESSAGE_LENGTH*sizeof({type_msg}));
    \t\t\t\tconst size_t offset = (size_t)i * c->chunk_size;
    \t\t\t\t{type_sk_with_no_const} pk[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t\t\t\t{type_sk_with_no_const} *sk = input_data + offset + MESSAGE_LENGTH;
    \t\t\t\t(void)crypto_sign_keypair(pk, sk);
    \t\t\t}}
    \t\t}}
    \t}}
    
    int main(int argc, char **argv)
    {{
    \t(void)argc;
    \t(void)argv;
    
    \tconst size_t chunk_size = sizeof({type_msg})*MESSAGE_LENGTH + SECRET_KEY_BYTE_LENGTH*sizeof({type_sk}); 

    \tdudect_config_t config = {{
    \t\t.chunk_size = chunk_size,
    \t\t.number_measurements = {number_of_measurements},
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


# FLOWTRACKER: xml file for crypto_sign_keypair
def flowtracker_keypair_xml_content(xml_file, api,
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
    with open(xml_file, "w") as t_file:
        t_file.write(textwrap.dedent(xml_file_content))


# FLOWTRACKER: xml file for crypto_sign
def flowtracker_sign_xml_content(xml_file, api,
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
                    <parameter>{sk}</parameter>   <!--Secret key-->
                </secret>
            </function>
        </sources>
    </functions>
    '''
    with open(xml_file, "w") as t_file:
        t_file.write(textwrap.dedent(xml_file_content))


# ======================CONFIGURATION FILES =================================
# ===========================================================================


# BINSEC: script for crypto_sign_keypair
def sign_configuration_file_content(cfg_file_sign, crypto_sign_args_names, with_core_dump="yes"):
    sig_msg = crypto_sign_args_names[0]
    sig_msg_len = crypto_sign_args_names[1]
    msg = crypto_sign_args_names[2]
    msg_len = crypto_sign_args_names[3]
    sk = crypto_sign_args_names[4]
    script_file = cfg_file_sign
    if 'no' in with_core_dump.lower():
        print("Binsec: only test with core dump is taken into account.")
    if not cfg_file_sign.endswith('.ini'):
        cfg_file_sign_split = cfg_file_sign.split('.')
        if len(cfg_file_sign_split) == 1:
            script_file = f'{cfg_file_sign}.ini'
        else:
            script_file = f'{cfg_file_sign_split[0:-1]}.ini'
    cfg_file_content = f'''
    starting from core
    replace <getrandom> (buf, buffen, _) by
        for i<64> in 0 to buffen -1 do
            @[buf + i] := nondet as urandom
        end
        return buffen
    end

    '''
    exploration_goal = f'''
    explore all'''
    cfg_file_content += f''' 
    secret global {sk}
    public global {sig_msg}, {sig_msg_len}, {msg}, {msg_len}
    halt at <exit>
    {exploration_goal}
    '''
    with open(script_file, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))


# BINSEC: script for crypto_sign
def cfg_content_keypair(cfg_file_keypair, with_core_dump="yes"):
    if 'no' in with_core_dump.lower():
        print("Binsec: only test with core dump is taken into account.")
    script_file = cfg_file_keypair
    if not cfg_file_keypair.endswith('.ini'):
        cfg_file_sign_split = cfg_file_keypair.split('.')
        if len(cfg_file_sign_split) == 1:
            script_file = f'{cfg_file_keypair}.ini'
        else:
            script_file = f'{cfg_file_keypair[0:-1]}.ini'
    cfg_file_content = f'''
    starting from core
    replace <getrandom> (buf, buffen, _) by
        for i<64> in 0 to buffen -1 do
            @[buf + i] := nondet as urandom
        end
        return buffen
    end
    '''
    exploration_goal = f'''
    explore all'''
    cfg_file_content += f'''
    secret global sk
    public global pk
    halt at <exit>
    {exploration_goal}
    '''
    with open(script_file, "w") as cfg_file:
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
    print("...........command cmake: ", cmd)
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
                                                                 default="", additional_cmake_definitions=None):

    if not path_to_cmakelist_file == "":
        compile_with_cmake(path_to_build_folder, additional_cmake_definitions)
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

# Run Binsec
def run_binsec(executable_file, cfg_file, stats_files, output_file, depth):
    command = f'''binsec -sse -checkct -sse-script {cfg_file} -sse-depth  {depth} -sse-self-written-enum 1
          '''
    command += f'{executable_file}'
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file, "w") as file:
        for line in output_decode.split('\n'):
            file.write(line + '\n')


# Generate gdb script
def binsec_generate_gdb_script(path_to_gdb_script: str, path_to_snapshot_file: str):
    snapshot_file = path_to_snapshot_file
    gdb_script = path_to_gdb_script
    if not snapshot_file.endswith('.snapshot'):
        snapshot_file = f'{snapshot_file}.snapshot'
    if not gdb_script.endswith('.gdb'):
        gdb_script = f'{gdb_script}.gdb'
    snapshot = f'''
    set pagination off
    set env LD_BIND_NOW=1
    set env GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX2_Usable
    b main
    start
    generate-core-file {snapshot_file}
    kill
    quit
    '''
    with open(gdb_script, "w+") as gdb_file:
        gdb_file.write(textwrap.dedent(snapshot))


# Given an executable, generate a core file (.snapshot) with a given gdb script
def binsec_generate_core_dump(path_to_executable_file: str, path_to_gdb_script: str):
    cwd = os.getcwd()
    path_to_executable_file_split = path_to_executable_file.split('/')
    executable_basename = os.path.basename(path_to_executable_file)
    gdb_script_basename = os.path.basename(path_to_gdb_script)
    if len(path_to_executable_file_split) == 1:
        executable_folder = "."
    else:
        executable_folder = '/'.join(path_to_executable_file_split[0:-1])

    os.chdir(executable_folder)
    cmd = f'gdb -x {gdb_script_basename} ./{executable_basename}'
    cmd_list = cmd.split()
    subprocess.call(cmd_list, stdin=sys.stdin)
    os.chdir(cwd)


# Run CTGRIND
def run_ctgrind(binary_file, output_file):
    command = f'''valgrind -s --track-origins=yes --leak-check=full 
                --show-leak-kinds=all --verbose --log-file={output_file} ./{binary_file}'''
    cmd_args_lst = command.split()
    subprocess.call(cmd_args_lst, stdin=sys.stdin)


# Run DUDECT
def run_dudect(executable_file, output_file, timeout='86400'):
    command = ""
    if timeout and timeout.lower() == 'no':
        command += f'./{executable_file}'
    elif timeout and timeout.lower() != 'no':
        command = f'timeout {timeout} ./{executable_file}'
    else:
        command = f'timeout 86400 ./{executable_file}'
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file, "w") as file:
        for line in output_decode.split('\n'):
            file.write(line + '\n')


# Run FLOWTRACKER
def run_flowtracker(rbc_file, xml_file, output_file, sh_file_folder):
    sh_command = f'''
    #!/bin/sh
    opt -basicaa -load AliasSets.so -load DepGraph.so -load bSSA2.so -bssa2\
    -xmlfile {xml_file} {rbc_file} 2>{output_file}
    '''
    shell_file = 'run_candidate.sh'
    with open(shell_file, 'w') as sh_file:
        sh_file.write(textwrap.dedent(sh_command))
    makefile_folder = sh_file_folder
    makefile_content = f'''
    RUN_CANDIDATE := (/bin/bash './run_candidate.sh')

    run:
    \t$(RUN_CANDIDATE)
    '''
    with open('Makefile', 'w') as makefile_to_run_candidate:
        makefile_to_run_candidate.write(textwrap.dedent(makefile_content))
    command = ["make"]
    subprocess.call(command, stdin=sys.stdin)


# binsec_generic_run - ctgrind_generic_run - dudecy_generic_run - flowtracker_generic_run
# Those functions call respectively: binsec_run - ctgrind_run - dudect_run and flowtracker_run
# For each of them, the path to the executable/binary file is obtained from:
# 1. binsec_folder:  binsec folder (same for ctggrind - dudect and flowtracker)
# 2. signature_type: signature type
# 3. candidate: candidate name
# 4. optimized_imp_folder: folder of optimisation implementation
# 5. opt_src_folder_list_dir: instance/scr folder of the given candidate with respect to optimized_imp_folder
# 6. build_folder: build folder
# 7. binary_patterns: sign/keypair, referring to crypto_sign_keypair and crypto_sign algorithms respectively

def binsec_generic_run(binsec_folder, signature_type, candidate,
                       optimized_imp_folder, opt_src_folder_list_dir,
                       depth, build_folder, binary_patterns, with_core_dump="yes"):
    optimized_imp_folder_full_path = f'{signature_type}/{candidate}/{optimized_imp_folder}'
    binsec_folder_full_path = f'{optimized_imp_folder_full_path}/{binsec_folder}'
    cfg_pattern = ".ini"
    list_of_instances = []
    if not opt_src_folder_list_dir:
        path_to_subfolder = binsec_folder_full_path
        list_of_instances.append(path_to_subfolder)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = f'{binsec_folder_full_path}/{subfold}'
            list_of_instances.append(path_to_subfolder)
    for instance in list_of_instances:
        path_to_build_folder = f'{instance}/{build_folder}'
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            binsec_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{binsec_folder_basename}'
            path_to_pattern_subfolder = f'{instance}/{binsec_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                binary = os.path.basename(executable)
                path_to_snapshot_file = f'{binary}.snapshot'
                path_to_gdb_script = f'{path_to_binary_pattern_subfolder}/{binary}.gdb'
                binsec_generate_gdb_script(path_to_gdb_script, path_to_snapshot_file)
                path_to_executable_file = f'{path_to_binary_pattern_subfolder}/{binary}'
                binsec_generate_core_dump(path_to_executable_file, path_to_gdb_script)
                bin_basename = binary.split('test_harness_')[-1]
                bin_basename = bin_basename.split('.snapshot')[0]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                stats_file = f'{path_to_pattern_subfolder}/{bin_pattern}.toml'
                cfg_file = find_ending_pattern(path_to_pattern_subfolder, cfg_pattern)
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{binary}.snapshot'
                print("::::Running:", abs_path_to_executable)
                run_binsec(abs_path_to_executable, cfg_file, stats_file, output_file, depth)


def ctgrind_generic_run(ctgrind_folder, signature_type,
                        candidate, optimized_imp_folder,
                        opt_src_folder_list_dir,
                        build_folder, binary_patterns):
    optimized_imp_folder_full_path = f'{signature_type}/{candidate}/{optimized_imp_folder}'
    ctgrind_folder_full_path = f'{optimized_imp_folder_full_path}/{ctgrind_folder}'
    list_of_instances = []
    if not opt_src_folder_list_dir:
        path_to_subfolder = ctgrind_folder_full_path
        list_of_instances.append(path_to_subfolder)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = f'{ctgrind_folder_full_path}/{subfold}'
            list_of_instances.append(path_to_subfolder)
    for instance in list_of_instances:
        path_to_build_folder = f'{instance}/{build_folder}'
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            ctgrind_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{ctgrind_folder_basename}'
            path_to_pattern_subfolder = f'{instance}/{ctgrind_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                bin_basename = executable.split('taint_')[-1]
                bin_basename = bin_basename.split('.o')[0]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                print("::::Running:", abs_path_to_executable)
                run_ctgrind(abs_path_to_executable, output_file)


def dudect_generic_run(dudect_folder, signature_type,
                       candidate, optimized_imp_folder,
                       opt_src_folder_list_dir,
                       build_folder, binary_patterns, timeout='86400'):
    optimized_imp_folder_full_path = f'{signature_type}/{candidate}/{optimized_imp_folder}'
    dudect_folder_full_path = f'{optimized_imp_folder_full_path}/{dudect_folder}'
    list_of_instances = []
    if not opt_src_folder_list_dir:
        path_to_subfolder = dudect_folder_full_path
        list_of_instances.append(path_to_subfolder)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = f'{dudect_folder_full_path}/{subfold}'
            list_of_instances.append(path_to_subfolder)
    for instance in list_of_instances:
        path_to_build_folder = f'{instance}/{build_folder}'
        for bin_pattern in binary_patterns:
            dudect_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_build_folder}/{dudect_folder_basename}'
            path_to_pattern_subfolder = f'{instance}/{dudect_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                bin_basename = executable.split('dude_')[-1]
                bin_basename = bin_basename.split('.o')[0]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                print("::::Running:", abs_path_to_executable)
                run_dudect(abs_path_to_executable, output_file, timeout)


def flowtracker_generic_run(flowtracker_folder, signature_type,
                            candidate, optimized_imp_folder,
                            opt_src_folder_list_dir,
                            build_folder, binary_patterns):
    cwd = os.getcwd()
    xml_pattern = '.xml'
    rbc_pattern = '.rbc'
    optimized_imp_folder_full_path = f'{signature_type}/{candidate}/{optimized_imp_folder}'
    flowtracker_folder_full_path = optimized_imp_folder_full_path + '/' + flowtracker_folder
    list_of_instances = []
    if not opt_src_folder_list_dir:
        path_to_subfolder = flowtracker_folder_full_path
        list_of_instances.append(path_to_subfolder)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = f'{flowtracker_folder_full_path}/{subfold}'
            list_of_instances.append(path_to_subfolder)
    for instance in list_of_instances:
        path_to_build_folder = f'{instance}/{build_folder}'
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            flowtracker_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{flowtracker_folder_basename}'
            path_to_pattern_subfolder = f'{instance}/{flowtracker_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            bin_files = [file for file in bin_files if file.endswith('.rbc')]
            for executable in bin_files:
                bin_basename = executable.split('rbc_')[-1]
                bin_basename = bin_basename.split('.rbc')[0]
                output_file = f'{bin_basename}_output.out'
                xml_file = find_ending_pattern(path_to_pattern_subfolder, xml_pattern)
                xml_file = os.path.basename(xml_file)

                rbc_file_folder = f'../{build_folder}/{flowtracker_folder_basename}'
                rbc_file = f'{rbc_file_folder}/{executable}'
                os.chdir(path_to_pattern_subfolder)
                sh_file_folder = flowtracker_folder_basename
                print("::::Running: ", rbc_file)
                run_flowtracker(rbc_file, xml_file, output_file, sh_file_folder)
            os.chdir(cwd)


# generic_run: this function, calls the previous ones, given the name of the name of
# the tool: binsec - ctgrind - dudect - flowtracker
def generic_run(tools_list, signature_type,
                candidate, optimized_imp_folder,
                opt_src_folder_list_dir, depth,
                build_folder, binary_patterns, with_core_dump='yes',
                timeout='86400'):
    for tool_name in tools_list:
        if 'binsec' in tool_name.lower():
            binsec_folder = tool_name
            binsec_generic_run(binsec_folder, signature_type,
                               candidate, optimized_imp_folder,
                               opt_src_folder_list_dir, depth,
                               build_folder, binary_patterns, with_core_dump)
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
                               binary_patterns, timeout)
    for tool_name in tools_list:
        if 'flowtracker' in tool_name.lower():
            flowtracker_folder = tool_name
            flowtracker_generic_run(flowtracker_folder, signature_type,
                                    candidate, optimized_imp_folder,
                                    opt_src_folder_list_dir, build_folder,
                                    binary_patterns)


# ========================== INITIALIZATION ==============================
# ========================================================================
# Find api.h, sign.h and rng.h relative paths to the instance folder of a candidate.
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
        outside_depth_of_rng_folder = 1
        rel_path_to_api_sign_split = []
        # relative path to rng
        if rng_outside_instance_folder == "yes":
            if not rel_path_to_sign == '""':
                rel_path_to_api_sign_split = rel_path_to_sign.split('/')
            elif not rel_path_to_api == '""':
                rel_path_to_api_sign_split = rel_path_to_api.split('/')
            instance_folder_split = instance_folder.split('/')
            if len(instance_folder_split) == 1:
                rng_relative = rel_path_to_rng
            else:
                instance_folder_split.pop()
                rel_path_to_rng_split = rel_path_to_rng.split('/')
                if len(rel_path_to_api_sign_split) == len(rel_path_to_rng_split)-2:
                    instance_folder_split.pop()
                    del rel_path_to_rng_split[1]
                instance_folder_parent_folder = '/'.join(instance_folder_split)
                for i in range(1, len(rel_path_to_rng_split)):
                    if not rel_path_to_rng_split[i] == '..':
                        if instance_folder_parent_folder:
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


# Find api.h/sign.h path taking into account the optimized implementation folder and the
# instance folder of a candidate. The file obtained is the path to api.h/sign.h, the header file
# needed to get crypto_sign_keypair and crypto_sign arguments names/types.
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
        if opt_implementation_name == ref_implementation_name:
            abs_path_to_api_or_sign = "/".join(candidate_folder_list)
        else:
            if opt_implementation_name in candidate_folder_list:
                candidate_folder_list.remove(opt_implementation_name)
        candidate_folder = "/".join(candidate_folder_list)
        abs_path_to_api_or_sign = candidate_folder
    return abs_path_to_api_or_sign


# tool_initialize_candidate: given  tool, instances, keypair and sign folders and also api.h - sign.h - rng.h paths,
# consists in creating:
# 1. a directory named accordingly the tool name
# 2. two subdirectories of the previous one, named accordingly to the instance of the candidate
# and the keypair/sign algorithms
# 3. the required files for the given tool (test harness, taint, etc.) into the previous folders.
def tool_initialize_candidate(path_to_opt_src_folder,
                              path_to_tool_folder,
                              path_to_tool_keypair_folder,
                              path_to_tool_sign_folder, api,
                              sign, rng, add_includes,
                              with_core_dump="yes",
                              number_of_measurements='1e4'):
    list_of_path_to_folders = [path_to_tool_folder,
                               path_to_tool_keypair_folder,
                               path_to_tool_sign_folder]
    generic_create_tests_folders(list_of_path_to_folders)
    tool_name = os.path.basename(path_to_tool_folder)
    opt_implementation_name = os.path.basename(path_to_opt_src_folder)
    abth_p = find_api_sign_abs_path(path_to_opt_src_folder, api,
                                    sign, opt_implementation_name)
    abs_path_to_api_or_sign = abth_p
    tool_type = Tools(tool_name)
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
        if 'yes' in with_core_dump.lower():
            cfg_file_keypair = f'{path_to_tool_keypair_folder}/{cfg_file_kp}.ini'
        cfg_content_keypair(cfg_file_keypair, with_core_dump)
        test_harness_content_keypair(test_keypair, api, sign, add_includes, return_type_kp,
                                     f_basename_kp)
        crypto_sign_args_names = args_names_s

        if 'yes' in with_core_dump.lower():
            cfg_file_sign = f'{path_to_tool_sign_folder}/{cfg_file_sign}.ini'
        else:
            cfg_file_sign = f'{path_to_tool_sign_folder}/{cfg_file_sign}.cfg'
        sign_configuration_file_content(cfg_file_sign, crypto_sign_args_names, with_core_dump)
        sign_test_harness_content(test_sign, api, sign, add_includes, return_type_s, f_basename_s,
                                  args_types_s, args_names_s)

    if tool_name == 'dudect':
        dudect_keypair_dude_content(test_keypair, api, sign,
                                    add_includes, return_type_kp,
                                    f_basename_kp, args_types_kp, args_names_kp)
        dudect_sign_dude_content(test_sign, api, sign,
                                 add_includes, return_type_s,
                                 f_basename_s, args_types_s,
                                 args_names_s, number_of_measurements)
    if tool_name == 'flowtracker':
        flowtracker_keypair_xml_content(test_keypair, api, sign,
                                        add_includes, return_type_kp,
                                        f_basename_kp, args_types_kp, args_names_kp)
        flowtracker_sign_xml_content(test_sign, api, sign,
                                     add_includes, return_type_s,
                                     f_basename_s, args_types_s, args_names_s)


# initialization: given a candidate and its details (signature type, etc.), creates required arguments (folders)
# for the function 'tool_initialize_candidate'.
# It takes into account a multiple of tools  and instances (folders) for a given candidate
def initialization(tools_list, signature_type,
                   candidate, optimized_imp_folder,
                   instance_folder, api, sign,
                   rng, add_includes, with_core_dump="yes",
                   number_of_measurements='1e4'):
    path_to_opt_src_folder = signature_type + '/' + candidate + '/' + optimized_imp_folder
    tools_list_lowercase = [tool_name.lower() for tool_name in tools_list]

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
                                  sign, rng, add_includes,
                                  with_core_dump, number_of_measurements)


# generic_initialize_nist_candidate: generalisation of the function 'initialization', taking into account the fact
# that some candidates have only 'one' instance
def generic_initialize_nist_candidate(tools_list, signature_type, candidate,
                                      optimized_imp_folder, instance_folders_list,
                                      rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                                      add_includes, rng_outside_instance_folder="no",
                                      with_core_dump="yes", number_of_measurements='1e4'):
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
                       rng, add_includes, with_core_dump,
                       number_of_measurements)
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
                           rng, add_includes, with_core_dump,
                           number_of_measurements)


def set_include_correct_format(api, sign, rng):
    if not api.startswith('"'):
        api = f'"{api}"'
    if not sign.startswith('"'):
        sign = f'"{sign}"'
    if not rng.startswith('"'):
        rng = f'"{rng}"'
    return api, sign, rng


# generic_init_compile: in addition to initializing a given candidate for desired tools and instances, generates
# a Makefile/CMakeLists.txt and performs compilation/build.
def generic_init_compile(tools_list, signature_type, candidate,
                         optimized_imp_folder, instance_folders_list,
                         rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                         add_includes, build_folder, with_cmake,
                         rng_outside_instance_folder="no", with_core_dump="yes",
                         additional_cmake_definitions=None, security_level=None,
                         number_of_measurements='1e4'):
    api, sign, rng = set_include_correct_format(rel_path_to_api, rel_path_to_sign, rel_path_to_rng)
    rel_path_to_api = api
    rel_path_to_sign = sign
    rel_path_to_rng = rng
    cmd = []
    path_to_opt_impl_folder = f'{signature_type}/{candidate}/{optimized_imp_folder}'
    if not instance_folders_list:
        generic_initialize_nist_candidate(tools_list, signature_type,
                                          candidate, optimized_imp_folder,
                                          instance_folders_list, rel_path_to_api,
                                          rel_path_to_sign, rel_path_to_rng,
                                          add_includes, rng_outside_instance_folder,
                                          with_core_dump, number_of_measurements)
        instance = '""'
        for tool_type in tools_list:
            path_to_build_folder = ""
            path_to_cmakelist_file = ""
            path_to_makefile_folder = ""
            if with_cmake == 'yes':
                path_to_cmakelist_file = path_to_opt_impl_folder + '/' + tool_type
                path_to_build_folder = path_to_cmakelist_file + '/' + build_folder
                path_to_makefile_folder = ""
                path_function_pattern_file = path_to_cmakelist_file
                arguments = f'path_function_pattern_file,instance,tool_type,candidate'
                funct = f'build_cand.cmake_candidate({arguments})'
                exec(f'{funct}')
            elif "sh" in with_cmake:
                cwd = os.getcwd()
                path_to_sh_folder = f'{path_to_opt_impl_folder}/{tool_type}'
                path_to_build_folder = f'{path_to_sh_folder}/{build_folder}'
                arguments = f'path_to_sh_folder, instance, tool_type, candidate'
                funct = f'build_cand.sh_candidate({arguments})'
                exec(f'{funct}')
                sh_script = find_ending_pattern(path_to_sh_folder, ".sh")
                sh_script = os.path.basename(sh_script)
                os.chdir(path_to_sh_folder)
                cmd_str = f"sudo chmod u+x ./{sh_script}"
                cmd = cmd_str.split()
                subprocess.call(cmd, stdin=sys.stdin)
                cmd_str = f"./{sh_script}"
                cmd = cmd_str.split()
                subprocess.call(cmd, stdin=sys.stdin, shell=True)
                os.chdir(cwd)
            else:
                path_to_makefile_folder = path_to_opt_impl_folder + '/' + tool_type
                path_to_build_folder = path_to_makefile_folder + '/' + build_folder
                path_to_cmakelist_file = ""
                path_function_pattern_file = path_to_makefile_folder
                arguments = f'path_function_pattern_file,instance,tool_type,candidate,security_level'
                funct = f'build_cand.makefile_candidate({arguments})'
                exec(f'{funct}')
            if not os.path.isdir(path_to_build_folder):
                cmd = ["mkdir", "-p", path_to_build_folder]
                subprocess.call(cmd, stdin=sys.stdin)
            if "sh" not in with_cmake:
                if not os.path.isdir(path_to_build_folder):
                    cmd = ["mkdir", "-p", path_to_build_folder]
                    subprocess.call(cmd, stdin=sys.stdin)
                compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,
                                                                             path_to_makefile_folder,
                                                                             path_to_build_folder,
                                                                             "all",
                                                                             additional_cmake_definitions)

    else:
        for instance in instance_folders_list:
            generic_initialize_nist_candidate(tools_list, signature_type,
                                              candidate, optimized_imp_folder,
                                              instance_folders_list, rel_path_to_api,
                                              rel_path_to_sign, rel_path_to_rng,
                                              add_includes, rng_outside_instance_folder,
                                              with_core_dump, number_of_measurements)
            for tool_type in tools_list:
                path_to_build_folder = ""
                path_to_cmakelist_file = ""
                path_to_makefile_folder = ""
                if with_cmake == 'yes':
                    path_to_cmakelist_file = path_to_opt_impl_folder + '/' + tool_type + '/' + instance
                    path_to_build_folder = path_to_cmakelist_file + '/' + build_folder
                    path_to_makefile_folder = ""
                    path_function_pattern_file = path_to_cmakelist_file
                    arguments = f'path_function_pattern_file,instance,tool_type,candidate'
                    funct = f'build_cand.cmake_candidate({arguments})'
                    exec(f'{funct}')
                elif "sh" in with_cmake:
                    cwd = os.getcwd()
                    path_to_sh_folder = f'{path_to_opt_impl_folder}/{tool_type}/{instance}'
                    path_to_build_folder = f'{path_to_sh_folder}/{build_folder}'
                    arguments = f'path_to_sh_folder, instance, tool_type, candidate'
                    funct = f'build_cand.sh_candidate({arguments})'
                    exec(f'{funct}')
                    sh_script = find_ending_pattern(path_to_sh_folder, ".sh")
                    sh_script = os.path.basename(sh_script)
                    os.chdir(path_to_sh_folder)
                    cmd_str = f"sudo chmod u+x ./{sh_script}"
                    cmd = cmd_str.split()
                    subprocess.call(cmd, stdin=sys.stdin)
                    cmd_str = f"./{sh_script}"
                    cmd = cmd_str.split()
                    subprocess.call(cmd, stdin=sys.stdin, shell=True)
                    os.chdir(cwd)
                else:
                    path_to_makefile_folder = f'{path_to_opt_impl_folder}/{tool_type}/{instance}'
                    path_to_build_folder = f'{path_to_makefile_folder}/{build_folder}'
                    path_to_cmakelist_file = ""
                    path_function_pattern_file = path_to_makefile_folder
                    arguments = f'path_function_pattern_file,instance,tool_type,candidate,security_level'
                    funct = f'build_cand.makefile_candidate({arguments})'
                    exec(funct)
                if "sh" not in with_cmake:
                    if not os.path.isdir(path_to_build_folder):
                        cmd = ["mkdir", "-p", path_to_build_folder]
                        subprocess.call(cmd, stdin=sys.stdin)
                    compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,
                                                                                 path_to_makefile_folder,
                                                                                 path_to_build_folder,
                                                                                 "all",
                                                                                 additional_cmake_definitions)


# generic_compile_run_candidate: initializes, compiles and runs given tools for the given instances
# of a given candidate.
def generic_compile_run_candidate(tools_list, signature_type, candidate,
                                  optimized_imp_folder, instance_folders_list,
                                  rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                                  with_cmake, add_includes, to_compile, to_run,
                                  depth, build_folder, binary_patterns,
                                  rng_outside_instance_folder="no",
                                  with_core_dump="yes", additional_cmake_definitions=None,
                                  security_level=None, number_of_measurements='1e4',
                                  timeout='86400'):
    candidate = candidate
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        generic_init_compile(tools_list, signature_type, candidate,
                             optimized_imp_folder, instance_folders_list,
                             rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                             add_includes, build_folder, with_cmake,
                             rng_outside_instance_folder, with_core_dump,
                             additional_cmake_definitions, security_level,
                             number_of_measurements)
        generic_run(tools_list, signature_type, candidate, optimized_imp_folder,
                    instance_folders_list, depth, build_folder, binary_patterns, with_core_dump, timeout)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        generic_init_compile(tools_list, signature_type, candidate,
                             optimized_imp_folder, instance_folders_list,
                             rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                             add_includes, build_folder, with_cmake,
                             rng_outside_instance_folder, with_core_dump,
                             additional_cmake_definitions, security_level,
                             number_of_measurements)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list, signature_type, candidate, optimized_imp_folder,
                    instance_folders_list, depth, build_folder, binary_patterns, with_core_dump, timeout)


# add_cli_arguments: creates a parser for a given candidate
def add_cli_arguments(subparser,
                      signature_type,
                      candidate,
                      optimized_imp_folder,
                      rel_path_to_api='""',
                      rel_path_to_sign='""',
                      rel_path_to_rng='""',
                      is_rng_in_cwd="no",
                      candidate_default_list_of_folders=None,
                      with_core_dump="yes",
                      additional_cmake_definitions=None,
                      security_level=None,
                      number_of_measurements='1e4',
                      timeout='86400'):
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
    arguments = f"'--with_core_dump','-core_dump',dest='core_dump', default=f'{with_core_dump}',help = 'no'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--cmake_addtional_definitions','-cmake_definition', nargs='+', dest='cmake_definition', \
    default={additional_cmake_definitions},help = 'List of CMake additional definitions if any'"
    add_args_commdand = f"candidate_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--security_level','-security_level', dest='security_level', default={security_level},\
    help = 'Instance security level'")
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
