#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: gilbertndollanedione
"""

import os
import glob
import re
import subprocess
import sys
import argparse
import time
import textwrap





#********************************************************************************************
#********************************************************************************************
def find_starting_pattern(folder,pattern):
    test_folder = glob.glob(folder+'/'+pattern+'*')
    return test_folder[0]



def find_ending_pattern(folder,pattern):
    test_folder = glob.glob(folder+'/*'+pattern)
    return test_folder[0]


def tokenize_argument(argument:str):
    type_arg = ""
    name_arg = ""
    argument_declaration = ""
    default_length = "1000"
    is_pointer = False
    is_array = False
    is_array_with_special_length = False
    if ("*" in argument) and not  ("[" in argument):
        is_pointer = True
    elif ("[" in argument) and not  ("*" in argument):
        is_array = True
    elif ("*" in argument) and ("[" in argument):
        is_array_with_special_length = True

    argument = argument.strip()
    argument_split = re.split(r"[\s]",argument)
    argument_split_without_space = [el for el in argument_split if el != '']
    if is_pointer:
        argument_split_without_space = [re.sub("\*","",strg) for strg in argument_split_without_space]
        argument_split_without_space = [el for el in argument_split_without_space if el != '']
        if len(argument_split_without_space)>2:
            type_arg = " ".join(argument_split_without_space[0:-1])
        else:
            type_arg = argument_split_without_space[0]
        name_arg = argument_split_without_space[-1]
        argument_declaration = type_arg + " " + name_arg + "["+default_length+"];"
    elif is_array:
        initial_length_array = re.search("\[(.+?)\]",argument)
        if initial_length_array:
            if initial_length_array.group(1)=="" or initial_length_array.group(1)==" ":
                default_length = default_length
            else:
                default_length = initial_length_array.group(1)
                argument_split_without_space = [re.sub("\[","",strg) for strg in argument_split_without_space]
                argument_split_without_space = [re.sub("\]","",strg) for strg in argument_split_without_space]
                argument_split_without_space = [el for el in argument_split_without_space if el != '']
                if argument_split_without_space[-1] == default_length:
                    name_arg = argument_split_without_space[-2]
                    if len(argument_split_without_space)>3:
                        type_arg = " ".join(argument_split_without_space[0:-2])
                    else:
                        type_arg = argument_split_without_space[0]
                    argument_declaration = type_arg + " " + name_arg + "["+default_length+"];"
                else:
                    n_arg =re.split(default_length,argument_split_without_space[-1])
                    name_arg = n_arg[0]
                    if len(argument_split_without_space)>2:
                        type_arg = " ".join(argument_split_without_space[0:-1])
                    else:
                        type_arg = argument_split_without_space[0]
                    argument_declaration = type_arg + " " + name_arg + "["+default_length+"];"
        else:
            argument_split_without_space = [re.sub("\[","",strg) for strg in argument_split_without_space]
            argument_split_without_space = [re.sub("\]","",strg) for strg in argument_split_without_space]
            argument_split_without_space = [el for el in argument_split_without_space if el != '']
            if len(argument_split_without_space)>2:
                type_arg = " ".join(argument_split_without_space[0:-1])
            else:
                type_arg = argument_split_without_space[0]
            name_arg = argument_split_without_space[-1]
            argument_declaration = type_arg + " " + name_arg + "["+default_length+"];"
    elif is_array_with_special_length:
        initial_length_array = re.search("\[(.+?)\]",argument)
        default_length = initial_length_array.group(1)
        initial_length_array = initial_length_array.group(0)
        argument_split_without_space = re.split(r"[\[]",argument)
        argument_split_without_space = argument_split_without_space[0:-1]
        argument_split = re.split(r"[\s]",argument_split_without_space[0])
        argument_split_without_space = [el for el in argument_split if el != '']
        name_arg = argument_split_without_space[-1]
        if len(argument_split_without_space)>2:
            type_arg = " ".join(argument_split_without_space[0:-1])
        else:
            type_arg = argument_split_without_space[0]
        argument_declaration = type_arg + " " + name_arg + "["+default_length+"];"
    else :
        if len(argument_split_without_space)>2:
            type_arg = " ".join(argument_split_without_space[0:-1])
        else:
            type_arg = argument_split_without_space[0]
        name_arg = argument_split_without_space[-1]
        argument_declaration = type_arg + " " + name_arg + ";"

    return type_arg,name_arg,argument_declaration


#********************************************************************************************
# An candidate is a string. It refers to as the declaration of a function.
# An object of type Candidate has many attributes like the base name of a given candidate,
# its list of arguments in the (type name) format, the list of its names of arguments, etc.
# Such type of object also incorporate many methods used to set some attributes. For example,
# the arguments names are given by the method get_candidate_arguments_names().
#********************************************************************************************

def tokenize_candidate(candidate: str):
    has_arguments = True
    candidate_split = re.split(r"[()]\s*", candidate)
    ret_type_basename = candidate_split[0].split(" ")
    candidate_return_type = ret_type_basename[0]
    #candidate_base_name =  candidate_split[1]
    candidate_base_name =  ret_type_basename[1]
    candidate_args =  candidate_split[1]
    if candidate_args =='' or candidate_args ==' ':
        has_arguments = False
        print("The function {} has no arguments",candidate_base_name)
    else:
        candidate_input_names = []
        candidate_input_initialization = []
        candidate_all_types_of_input = []
        for input in re.split(r"[,]", candidate_args):
            type_arg,name_arg,input_declaration = tokenize_argument(input)
            candidate_all_types_of_input.append(type_arg)
            candidate_input_names.append(name_arg)
            candidate_input_initialization.append(input_declaration)
        return candidate_return_type,candidate_base_name,candidate_all_types_of_input,candidate_input_names,candidate_input_initialization



class Candidate(object):
    def __init__(self,candidate):
        self.candidate = candidate
        self.candidate_arguments_with_types = {}
        self.candidate_return_type = ""
        self.candidate_types = ""
        self.candidate_args_names = ""
        self.candidate_args_declaration = ""
        self.candidate_basename = ""
        self.candidate_test_harness_name = ""
        self.candidate_source_file_name = ""
        self.candidate_executable = "" # One call it "base_name-candidate_bin"
        self.candidate_configuration_file = ""
        self.candidate_stats_file = ""
        self.candidate_assumption = ""
        self.parent_header_file = ""
        self.parent_source_file = ""
        self.candidate_secret_data = [] #Call a function that reads from memory edit file
        self.candidate_public_data = [] #Call a function that reads from memory edit file
        self.cmd_binsec_compilation_candidate = [] #Call a function that reads from memory edit file
        self.cmd_binsec_run_candidate = []

        self.candidate_has_arguments_status = True
        self.candidate_split = re.split(r"[()]\s*", candidate)
        self.candidate_args = self.candidate_split[1]
        self.get_candidate_has_arguments_status()


    def get_candidate_has_arguments_status(self):
        if self.candidate_args =='' or self.candidate_args == ' ':
            self.candidate_has_arguments_status = False
        else:
            self.candidate_has_arguments_status = True
            self.candidate_return_type ,self.candidate_basename,self.candidate_types, self.candidate_args_names, self.candidate_args_declaration =  tokenize_candidate(self.candidate)
        return  self.candidate_has_arguments_status

    def get_candidate_basename(self):
        return self.candidate_basename

    def get_candidate_source_file_basename(self):
        return self.candidate_basename+".c"
    def get_candidate_test_harness_basename(self):
        return "test_harness_"+self.candidate_basename+".c"

    def get_candidate_memory_init_basename(self):
        return "memory_edit_"+self.candidate_basename+".txt"

    def get_candidate_configuration_basename(self):
        #return "configuration_file_"+self.candidate_basename+".cfg"
        return self.candidate_basename+".cfg"

    def get_candidate_stats_file_basename(self):
        #return "statistics_file_"+self.candidate_basename+".toml"
        return self.candidate_basename+".toml"

    def get_candidate_executable_basename(self):
        return self.candidate_basename+"_bin"

    def get_arg_names(self):
        return self.candidate_args_names

    #Return the list of the candidtae argument names. For e.g ['plaintext','ith_round','round_key']
    def get_candidate_arguments_names(self):
        return self.candidate_args_names

    def get_candidate_secret_data(self):
        for el in self.candidate_secret_data:
            if not el in self.candidate_args_names:
                print("{0} is not an argument of the function {1}".format(el,self.candidate_basename))
                self.candidate_secret_data = []
                return self.candidate_secret_data
        return self.candidate_secret_data

    def get_candidate_public_data(self):
        for el in self.candidate_public_data:
            if not el in self.candidate_args_names:
                print("{0} is not an argument of the function {1}".format(el,self.candidate_basename))
                self.candidate_secret_data = []
                return self.candidate_secret_data
        return self.candidate_public_data

    def candidate_arguments_initialization(self,file):
        pass
    #Contain the list of the argument declarations. For e.g. ['uint_8t tab[length];','int length;','const int numbers[10];']
    def candidate_arguments_declaration(self):
        return self.candidate_args_declaration


    def binsec_compile_candidate(self,folder):
        cand_src_file = glob.glob(folder+'/binsec_' + '*' + '*.c')[0]
        candidate_src_file = os.path.basename(cand_src_file)
        candidate_executable_file = "candidate_exec"
        t_harness = find_starting_pattern(folder,"test_h")
        candidate_exec = candidate_executable_file
        if self.cmd_binsec_compilation_candidate:
            subprocess.call(self.cmd_binsec_compilation_candidate)
        else:
            cmd = ["gcc","-g","-m32","-static",t_harness,folder+'/'+candidate_src_file,"-o"+folder+'/'+candidate_exec]
            subprocess.call(cmd)

    def binsec_run_candidate(self,folder,memory_init_file=""):
        candidate_executable_file = find_ending_pattern(folder,"_exec")
        config_file = glob.glob(folder +'/*.cfg')[0] # There's a unique header file
        stats_file = glob.glob(folder +'/*.toml')[0] # There's a unique header file
        with open(stats_file,'w') as st_file:  # Empty the initial content of the statistic file
            pass
        if self.cmd_binsec_run_candidate:
            subprocess.call(self.cmd_binsec_run_candidate, stdin = sys.stdin) # Run the executable file
        else:
            cmd = ["binsec","-checkct","-checkct-script",config_file,"-checkct-stats-file",stats_file,candidate_executable_file]
            subprocess.call(cmd, stdin = sys.stdin)


    def run_pqclib_candidate(self,folder):
        self.binsec_compile_candidate(folder)
        self.binsec_run_candidate(folder,memory_init_file="")





#================== List of src subfolders and generate those subfolders into binsec folder ==========

def list_of_subfolders(folder):
    src_folder_content = os.listdir(folder)
    return src_folder_content


def group_multiple_lines_good_17_Aug(file_content_list,starting_pattern,ending_pattern,exclude_pattern,starting_index,ending_index):
    matching_string_list = []
    break_index = -1
    found_start_index = 0
    found_end_index = 0
    i = starting_index
    line = file_content_list[i]
    line.strip()
    while (i <= ending_index) and (break_index<0):
        if exclude_pattern in line:
            i+=1
        line = file_content_list[i]
        line.strip()
        if starting_pattern in line:
            found_start_index = i
            if not "int" in line:
                matching_string_list.append("int")
            matching_string_list.append(line)
            if ending_pattern in line:
                found_end_index = i
                break_index = i
                break
            for j in range(found_start_index+1,ending_index):
                line = file_content_list[j]
                line.strip()
                matching_string_list.append(line)
                if ending_pattern in line:
                    found_end_index = j
                    break_index = j
                    break
        i+=1

    matching_string_list_strip = [word.strip() for word in matching_string_list]
    matching_string = " ".join(matching_string_list_strip)
    return matching_string,found_start_index,found_end_index


def group_multiple_lines(file_content_list,starting_pattern,ending_pattern,exclude_pattern,starting_index,ending_index):
    matching_string_list = []
    break_index = -1
    found_start_index = 0
    found_end_index = 0
    i = starting_index
    line = file_content_list[i]
    line.strip()
    while (i <= ending_index) and (break_index<0):
        if exclude_pattern in line :
            i+=1
        # if '/' in line or '#' in line:
        #     i+=1
        line = file_content_list[i]
        line.strip()
        if starting_pattern in line:
            found_start_index = i
            if not "int" in line:
                matching_string_list.append("int")
            matching_string_list.append(line)
            if ending_pattern in line:
                found_end_index = i
                break_index = i
                break
            for j in range(found_start_index+1,ending_index):
                line = file_content_list[j]
                line.strip()
                matching_string_list.append(line)
                if ending_pattern in line:
                    found_end_index = j
                    break_index = j
                    break
        i+=1

    matching_string_list_strip = [word.strip() for word in matching_string_list]
    matching_string = " ".join(matching_string_list_strip)
    return matching_string,found_start_index,found_end_index



def find_sign_and_keypair_definition_from_api_or_sign_good_17_Aug(api_sign_header_file):
    pattern_keypair = "keypair"
    file = open(api_sign_header_file,'r')
    file_content = file.read()
    file_content_line_by_line = file_content.split('\n')
    exclude_pattern = "open"
    ending_pattern = ");"
    included_pattern_keypair = "keypair"
    starting_index = 0
    ending_index = len(file_content_line_by_line)
    keypair_def, start,end = group_multiple_lines(file_content_line_by_line,included_pattern_keypair,ending_pattern,exclude_pattern,starting_index,ending_index)
    included_pattern_sign = "sign"
    starting_index = end+1
    sign_def, start,end = group_multiple_lines(file_content_line_by_line,included_pattern_sign,ending_pattern,exclude_pattern,starting_index,ending_index)
    file.close()
    keypair_sign_def = [keypair_def,sign_def]
    return keypair_sign_def


def find_sign_and_keypair_definition_from_api_or_sign(api_sign_header_file):
    pattern_keypair = "keypair("
    file = open(api_sign_header_file,'r')
    file_content = file.read()
    file_content_line_by_line = file_content.split('\n')
    exclude_pattern = "open"
    ending_pattern = ");"
    included_pattern_keypair = "keypair("
    starting_index = 0
    ending_index = len(file_content_line_by_line)
    keypair_def, start,end = group_multiple_lines(file_content_line_by_line,included_pattern_keypair,ending_pattern,exclude_pattern,starting_index,ending_index)
    included_pattern_sign = "sign("
    starting_index = end+1
    sign_def, start,end = group_multiple_lines(file_content_line_by_line,included_pattern_sign,ending_pattern,exclude_pattern,starting_index,ending_index)
    file.close()
    keypair_sign_def = [keypair_def,sign_def]
    return keypair_sign_def

def sign_find_args_types_and_names(abs_path_to_api_or_sign):
    keypair_sign_def = find_sign_and_keypair_definition_from_api_or_sign(abs_path_to_api_or_sign)
    sign_candidate = keypair_sign_def[1]
    cand_obj = Candidate(sign_candidate)
    args_names = cand_obj.candidate_args_names
    args_types = cand_obj.candidate_types
    return args_types,args_names

#==========================================TEST HARNESS ================================================================
#=======================================================================================================================
#=======================================================================================================================
def set_test_harness_sign_keypair(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,subfolder,api,sign):
    if subfolder =="":
        SRC = "../../"+src_folder
    else:
        SRC = "../../"+src_folder+'/'+subfolder
    binsec_candidate_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+src_folder
    test_harness_file = binsec_candidate_folder+'/test_harness_crypto_sign_keypair.c'
    if not os.path.isdir(binsec_candidate_folder):
        cmd = ["mkdir","-p",binsec_candidate_folder]
        subprocess.call(cmd, stdin = sys.stdin)

    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write('#include <stdio.h>\n')
        t_harness_file.write('#include <stdlib.h>\n')
        t_harness_file.write('#include <string.h>\n')
        t_harness_file.write('#include <stdint.h>\n')
        t_harness_file.write('#include <ctype.h>\n')
        t_harness_file.write(f'#include "{SRC}/prng.h"\n')
        if not sign == "":
            t_harness_file.write(f'#include "{SRC}/{sign}.h"\n')
        if not api == "":
            t_harness_file.write(f'#include "{SRC}/{api}.h"\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;\n')
        t_harness_file.write('uint8_t sk[CRYPTO_SECRETKEYBYTES] ;\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('int main(){\n')
        t_harness_file.write('      int result =  crypto_sign_keypair(pk, sk);\n')
        t_harness_file.write('      exit(result);\n')
        t_harness_file.write('}\n')


def test_harness_content_keypair(test_harness_file,api,sign,add_includes):
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write('#include <stdio.h>\n')
        t_harness_file.write('#include <stdlib.h>\n')
        t_harness_file.write('#include <string.h>\n')
        t_harness_file.write('#include <stdint.h>\n')
        t_harness_file.write('#include <ctype.h>\n')
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;\n')
        t_harness_file.write('uint8_t sk[CRYPTO_SECRETKEYBYTES] ;\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('int main(){\n')
        t_harness_file.write('      int result =  crypto_sign_keypair(pk, sk);\n')
        t_harness_file.write('      exit(result);\n')
        t_harness_file.write('}\n')


def test_harness_content_keypair_sqisign(test_harness_file,api,sign,add_includes):
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write('#include <stdio.h>\n')
        t_harness_file.write('#include <stdlib.h>\n')
        t_harness_file.write('#include <string.h>\n')
        t_harness_file.write('#include <stdint.h>\n')
        t_harness_file.write('#include <ctype.h>\n')
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;\n')
        t_harness_file.write('uint8_t sk[CRYPTO_SECRETKEYBYTES] ;\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('int main(){\n')
        t_harness_file.write('      int result =  sqisign_keypair(pk, sk);\n')
        t_harness_file.write('      exit(result);\n')
        t_harness_file.write('}\n')

def set_test_harness_sign(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,subfolder,api,sign):
    if subfolder =="":
        SRC = "../../"+src_folder
    else:
        SRC = "../../"+src_folder+'/'+subfolder
    binsec_candidate_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+src_folder
    test_harness_file = binsec_candidate_folder+'/test_harness_crypto_sign.c'
    if not os.path.isdir(binsec_candidate_folder):
        cmd = ["mkdir","-p",binsec_candidate_folder]
        subprocess.call(cmd, stdin = sys.stdin)

    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write('#include <stdio.h>\n')
        t_harness_file.write('#include <stdlib.h>\n')
        t_harness_file.write('#include <string.h>\n')
        t_harness_file.write('#include <stdint.h>\n')
        t_harness_file.write('#include <ctype.h>\n')
        t_harness_file.write(f'#include "{SRC}/prng.h"\n')
        t_harness_file.write(f'#include "{SRC}/{sign}.h"\n')
        t_harness_file.write(f'#include "{SRC}/{api}.h"\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('#define msg_length  (1<<5)\n')
        t_harness_file.write('uint8_t sk[CRYPTO_SECRETKEYBYTES] ;\n')
        t_harness_file.write('size_t sig_msg_len ;\n')
        t_harness_file.write('size_t msg_len = msg_length ;\n')
        t_harness_file.write('//const unsigned long long msg_len ;\n')
        t_harness_file.write('uint8_t sig_msg[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len\n')
        t_harness_file.write('uint8_t msg[msg_length] ;\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('int main(){\n')
        t_harness_file.write('      int result =  crypto_sign(sig_msg, &sig_msg_len, msg, msg_len, sk);\n')
        t_harness_file.write('      exit(result);\n')
        t_harness_file.write('}\n')


def test_harness_content_sign(test_harness_file,api,sign,add_includes):
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write('#include <stdio.h>\n')
        t_harness_file.write('#include <stdlib.h>\n')
        t_harness_file.write('#include <string.h>\n')
        t_harness_file.write('#include <stdint.h>\n')
        t_harness_file.write('#include <ctype.h>\n')
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('#define msg_length  (1<<5)\n')
        t_harness_file.write('uint8_t sk[CRYPTO_SECRETKEYBYTES] ;\n')
        t_harness_file.write('size_t sig_msg_len ;\n')
        t_harness_file.write('size_t msg_len = msg_length ;\n')
        t_harness_file.write('//const unsigned long long msg_len ;\n')
        t_harness_file.write('uint8_t sig_msg[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len\n')
        t_harness_file.write('uint8_t msg[msg_length] ;\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('int main(){\n')
        t_harness_file.write('      int result =  crypto_sign(sig_msg, &sig_msg_len, msg, msg_len, sk);\n')
        t_harness_file.write('      exit(result);\n')
        t_harness_file.write('}\n')




def test_harness_content_sign_new(test_harness_file,api,sign,add_includes,abs_path_to_api_or_sign):
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write('#include <stdio.h>\n')
        t_harness_file.write('#include <stdlib.h>\n')
        t_harness_file.write('#include <string.h>\n')
        t_harness_file.write('#include <stdint.h>\n')
        t_harness_file.write('#include <ctype.h>\n')
        keypair_sign_def = find_sign_and_keypair_definition_from_api_or_sign(abs_path_to_api_or_sign)
        sign_candidate = keypair_sign_def[1]
        cand_obj = Candidate(sign_candidate)
        args_names = cand_obj.candidate_args_names
        args_types = cand_obj.candidate_types

        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('#define msg_length  (1<<5)\n')
        t_harness_file.write(f'{args_types[0]} {args_names[0]}[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len\n')
        t_harness_file.write(f'{args_types[1]} {args_names[1]} ;\n')
        t_harness_file.write(f'{args_types[3]} {args_names[3]} = msg_length ;\n')
        t_harness_file.write(f'{args_types[2]} {args_names[2]}[{args_names[3]}] ;\n')
        t_harness_file.write(f'{args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES] ;\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('int main(){\n')
        t_harness_file.write(f'\tint result =  crypto_sign({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]});\n')
        t_harness_file.write('\texit(result);\n')
        t_harness_file.write('}\n')




def sign_test_harness_content(test_harness_file,api,sign,add_includes,args_types,args_names):
    args_types[2] = re.sub("const ","",args_types[2])
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write('#include <stdio.h>\n')
        t_harness_file.write('#include <stdlib.h>\n')
        t_harness_file.write('#include <string.h>\n')
        t_harness_file.write('#include <stdint.h>\n')
        t_harness_file.write('#include <ctype.h>\n')
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('#define msg_length  256\n')
        t_harness_file.write(f'{args_types[0]} {args_names[0]}[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len\n')
        t_harness_file.write(f'{args_types[1]} {args_names[1]} ;\n')
        t_harness_file.write(f'{args_types[3]} {args_names[3]} = msg_length ;\n')
        t_harness_file.write(f'{args_types[2]} {args_names[2]}[msg_length] ;\n')
        t_harness_file.write(f'{args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES] ;\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('int main(){\n')
        t_harness_file.write(f'\tint result =  crypto_sign({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]});\n')
        t_harness_file.write('\texit(result);\n')
        t_harness_file.write('}\n')




def sign_test_harness_content_sqisign(test_harness_file,api,sign,add_includes):
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write('#include <stdio.h>\n')
        t_harness_file.write('#include <stdlib.h>\n')
        t_harness_file.write('#include <string.h>\n')
        t_harness_file.write('#include <stdint.h>\n')
        t_harness_file.write('#include <ctype.h>\n')
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('#define msg_length  256\n')
        t_harness_file.write(f'unsigned char sm[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len\n')
        t_harness_file.write(f'unsigned long long smlen ;\n')
        t_harness_file.write(f'unsigned long long mlen = msg_length ;\n')
        t_harness_file.write(f'unsigned char m[msg_length] ;\n')
        t_harness_file.write(f'unsigned char sk[CRYPTO_SECRETKEYBYTES] ;\n')
        t_harness_file.write('\n\n')
        t_harness_file.write('int main(){\n')
        t_harness_file.write(f'\tint result =  sqisign_sign(sm, &smlen, m, mlen, sk);\n')
        t_harness_file.write('\texit(result);\n')
        t_harness_file.write('}\n')




#==========================================CONFIGURATION FILES =========================================================
#=======================================================================================================================
#=======================================================================================================================

def config_files_crypto_sign_and_keypair(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder):
    binsec_candidate_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+src_folder
    cfg_file_sign = binsec_candidate_folder+'/sign.cfg'
    cfg_file_keypair = binsec_candidate_folder+'/keypair.cfg'
    with open(cfg_file_keypair, "w") as cfg_file:
        cfg_file.write('starting from <main>\n')
        cfg_file.write('with concrete stack pointer\n')
        cfg_file.write('secret global sk\n')
        cfg_file.write('public global pk\n')
        cfg_file.write('halt at <exit>\n')
        cfg_file.write('explore all\n')
    with open(cfg_file_sign, "w") as cfg_file:
        cfg_file.write('starting from <main>\n')
        cfg_file.write('with concrete stack pointer\n')
        cfg_file.write('secret global sk\n')
        cfg_file.write('public global sig_msg,sig_msg_len,msg,msg_len\n')
        cfg_file.write('halt at <exit>\n')
        cfg_file.write('explore all\n')

def config_file_crypto_sign(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder):
    binsec_candidate_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+src_folder
    cfg_file_sign = binsec_candidate_folder+'/sign.cfg'
    with open(cfg_file_sign, "w") as cfg_file:
        cfg_file.write('starting from <main>\n')
        cfg_file.write('with concrete stack pointer\n')
        cfg_file.write('secret global sk\n')
        cfg_file.write('public global sig_msg,sig_msg_len,msg,msg_len\n')
        cfg_file.write('halt at <exit>\n')
        cfg_file.write('explore all\n')
def config_file_crypto_sign_keypair(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder):
    binsec_candidate_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+src_folder
    cfg_file_keypair = binsec_candidate_folder+'/keypair.cfg'
    with open(cfg_file_keypair, "w") as cfg_file:
        cfg_file.write('starting from <main>\n')
        cfg_file.write('with concrete stack pointer\n')
        cfg_file.write('secret global sk\n')
        cfg_file.write('public global pk\n')
        cfg_file.write('halt at <exit>\n')
        cfg_file.write('explore all\n')



def cfg_content_sign(cfg_file_sign):
    with open(cfg_file_sign, "w") as cfg_file:
        cfg_file.write('starting from <main>\n')
        cfg_file.write('with concrete stack pointer\n')
        cfg_file.write('secret global sk\n')
        cfg_file.write('public global sig_msg,sig_msg_len,msg,msg_len\n')
        cfg_file.write('halt at <exit>\n')
        cfg_file.write('explore all\n')


def sign_configuration_file_content(cfg_file_sign,crypto_sign_args_names):
    with open(cfg_file_sign, "w") as cfg_file:
        cfg_file.write('starting from <main>\n')
        cfg_file.write('with concrete stack pointer\n')
        cfg_file.write(f'secret global {crypto_sign_args_names[4]}\n')
        cfg_file.write(f'public global {crypto_sign_args_names[0]},{crypto_sign_args_names[1]},{crypto_sign_args_names[2]},{crypto_sign_args_names[3]}\n')
        cfg_file.write('halt at <exit>\n')
        cfg_file.write('explore all\n')


def cfg_content_keypair(cfg_file_keypair):
    with open(cfg_file_keypair, "w") as cfg_file:
        cfg_file.write('starting from <main>\n')
        cfg_file.write('with concrete stack pointer\n')
        cfg_file.write('secret global sk\n')
        cfg_file.write('public global pk\n')
        cfg_file.write('halt at <exit>\n')
        cfg_file.write('explore all\n')


def cfg_content_keypair_deprecated(cfg_file_keypair):
    with open(cfg_file_keypair, "w") as cfg_file:
        cfg_file.write('starting from <main>\n')
        cfg_file.write('concretize stack\n')
        cfg_file.write('secret global sk\n')
        cfg_file.write('public global pk\n')
        cfg_file.write('halt at <exit>\n')
        cfg_file.write('reach all\n')



#==========================================CREATE folders =========================================================
#=======================================================================================================================
#=======================================================================================================================

def create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder):
    if not os.path.isdir(binsec_folder_full_path):
        cmd = ["mkdir","-p",binsec_folder_full_path]
        subprocess.call(cmd, stdin = sys.stdin)
    if not os.path.isdir(binsec_keypair_folder):
        cmd = ["mkdir","-p",binsec_keypair_folder]
        subprocess.call(cmd, stdin = sys.stdin)
    if not os.path.isdir(binsec_sign_folder):
        cmd = ["mkdir","-p",binsec_sign_folder]
        subprocess.call(cmd, stdin = sys.stdin)


def create_path_to_optimization_src_folder(signature_type,candidate,optimized_imp_folder,src_folder):
    opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if not src_folder == "":
        opt_src_folder = opt_src_folder+'/'+src_folder
    return opt_src_folder

def create_path_to_optimization(signature_type,candidate,optimized_imp_folder,optimized_parent_folder):
    opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if not optimized_parent_folder == "":
        opt_src_folder = opt_src_folder+'/'+optimized_parent_folder
    return opt_src_folder

#==========================================CREATE CMakeLists.txt =========================================================
#=======================================================================================================================
#=======================================================================================================================
def create_CMakeList_and_link_to_library(cmakelists,library_name,test_harness):
    executable_name = test_harness.split(".")[0]
    with open(cmakelists, "w") as cmakelists_file:
        cmakelists_file.write('add_executable('+executable_name+ '  ' +test_harness+')'+'\n')
        cmakelists_file.write('target_link_libraries('+executable_name+ '  PRIVATE  '+library_name+')'+'\n')




#========================================== COMPILATION =========================================================+++++++
#=======================================================================================================================
#=======================================================================================================================

def compile_with_cmake(build_folder_full_path,optional_flags = []):
    cwd = os.getcwd()
    os.chdir(build_folder_full_path)
    cmd = ["cmake"]
    if not optional_flags == []:
        cmd.extend(optional_flags)
    cmd_ext = ["../"]
    cmd.extend(cmd_ext)
    subprocess.call(cmd, stdin = sys.stdin)
    cmd = ["make","-j"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)

def compile_with_makefile(path_to_makefile):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)

def compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile,path_to_build_folder):
    if not path_to_cmakelist_file == "":
        compile_with_cmake(path_to_build_folder)
    else:
        compile_with_makefile(path_to_makefile)

def compile_with_makefile_all(path_to_makefile):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)



#========================================== EXECUTION ==================================================================
#=======================================================================================================================
#=======================================================================================================================
def run_binsec_deprecated(executable_file,cfg_file,stats_files,output_file,depth):
    command = f'''binsec -checkct -checkct-depth  {depth}   -checkct-script  {cfg_file} 
               -checkct-stats-file   {stats_files}  {executable_file} '''
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file,"w") as file:
        for line in output_decode.split('\n'):
            file.write(line+'\n')
def run_binsec(executable_file,cfg_file,stats_files,output_file,depth):
    command = f'''binsec -sse -checkct -sse-depth  {depth}   -sse-script  {cfg_file} 
               -checkct-stats-file   {stats_files}  {executable_file} '''
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file,"w") as file:
        for line in output_decode.split('\n'):
            file.write(line+'\n')


def run_nist_signature_candidate(binsec_keypair_folder,binsec_sign_folder,path_to_keypair_bin_files,path_to_sign_bin_files,depth):
    cfg_pattern = ".cfg"
    #run crypto_sign_keypair
    cfg_file_sign = find_ending_pattern(binsec_keypair_folder,cfg_pattern)
    keypair_bin_files = os.listdir(path_to_keypair_bin_files)
    for binary in keypair_bin_files:
        basename = binary.split("harness_")[1]
        print("-------------Running: {}".format(basename))
        stats_file_keypair = binsec_keypair_folder+'/'+basename+'.toml'
        with open(stats_file_keypair,'w') as st_file:
            pass
        output_file_keypair = binsec_keypair_folder+'/'+basename+'.txt'
        keypair_bin_full_path = path_to_keypair_bin_files+'/'+binary
        run_binsec(keypair_bin_full_path,cfg_file_sign,stats_file_keypair,output_file_keypair,depth)
    #run crypto_sign
    cfg_file_sign = find_ending_pattern(binsec_sign_folder,cfg_pattern)
    sign_bin_files = os.listdir(path_to_sign_bin_files)
    for binary in sign_bin_files:
        basename = binary.split("harness_")[1]
        print("-------------Running: {}".format(basename))
        stats_file_sign = binsec_sign_folder+'/'+basename+'.toml'
        with open(stats_file_sign,'w') as st_file:
            pass
        output_file_sign = binsec_sign_folder+'/'+basename+'.txt'
        sign_bin_full_path = path_to_sign_bin_files+'/'+binary
        run_binsec(sign_bin_full_path,cfg_file_sign,stats_file_sign,output_file_sign,depth)


def run_nist_signature_candidate_compiled_with_cmake(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,build_folder,depth):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if not src_folder == "":
        optimized_imp_folder_full_path+='/'+src_folder
    build_folder_full_path = optimized_imp_folder_full_path+'/'+build_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
    path_to_binary_files = build_folder_full_path+'/'+"bin"
    #run crypto_sign_keypair
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    path_to_keypair_bin_files = path_to_binary_files+'/'+binsec_keypair_folder_basename
    #run crypto_sign
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    cfg_file_sign = find_ending_pattern(binsec_sign_folder,cfg_pattern)
    path_to_sign_bin_files = path_to_binary_files+'/'+binsec_sign_folder_basename
    run_nist_signature_candidate(binsec_keypair_folder,binsec_sign_folder,path_to_keypair_bin_files,path_to_sign_bin_files,depth)

def run_nist_signature_candidate_compiled_with_makefile(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,depth):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if not src_folder == "":
        optimized_imp_folder_full_path+='/'+src_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
    #run crypto_sign_keypair
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    path_to_binary_keypair = binsec_folder_full_path+'/test_harness_crypto_sign_keypair'
    stats_file_keypair = binsec_folder_full_path+'/'+binsec_keypair_folder_basename+'/keypair.toml'
    output_file_keypair = binsec_folder_full_path+'/'+binsec_keypair_folder_basename+'/keypair_output.txt'
    cfg_file_keypair =  find_ending_pattern(binsec_keypair_folder,cfg_pattern)
    print("------Running binary file: {} ---- ".format(path_to_binary_keypair))
    run_binsec(path_to_binary_keypair,cfg_file_keypair,stats_file_keypair,output_file_keypair,depth)
    #run crypto_sign
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    path_to_binary_sign = binsec_folder_full_path+'/test_harness_crypto_sign'
    stats_file_sign = binsec_folder_full_path+'/'+binsec_sign_folder_basename+'/sign.toml'
    output_file_sign = binsec_folder_full_path+'/'+binsec_sign_folder_basename+'/sign_output.txt'
    cfg_file_sign =  find_ending_pattern(binsec_sign_folder,cfg_pattern)
    print("------Running binary file: {} ---- ".format(path_to_binary_sign))
    run_binsec(path_to_binary_sign,cfg_file_sign,stats_file_sign,output_file_sign,depth)


def run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
    for subfold in opt_src_folder_list_dir:
        path_to_subfolder = binsec_folder_full_path+'/'+subfold
        #run crypto_sign_keypair
        binsec_keypair_folder_basename = candidate+'_keypair'
        binsec_keypair_folder = path_to_subfolder+'/'+binsec_keypair_folder_basename
        path_to_binary_keypair = binsec_keypair_folder+'/test_harness_crypto_sign_keypair'
        stats_file_keypair = binsec_keypair_folder+'/keypair.toml'
        output_file_keypair = binsec_keypair_folder+'/keypair_output.txt'
        cfg_file_keypair =  find_ending_pattern(binsec_keypair_folder,cfg_pattern)
        print("------Running binary file: {} ---- ".format(path_to_binary_keypair))
        run_binsec(path_to_binary_keypair,cfg_file_keypair,stats_file_keypair,output_file_keypair,depth)
        #run crypto_sign
        binsec_sign_folder_basename = candidate+'_sign'
        binsec_sign_folder = path_to_subfolder+'/'+binsec_sign_folder_basename
        path_to_binary_sign = binsec_sign_folder+'/test_harness_crypto_sign'
        stats_file_sign = binsec_sign_folder+'/sign.toml'
        output_file_sign = binsec_sign_folder+'/sign_output.txt'
        cfg_file_sign =  find_ending_pattern(binsec_sign_folder,cfg_pattern)
        print("------Running binary file: {} ---- ".format(path_to_binary_sign))
        run_binsec(path_to_binary_sign,cfg_file_sign,stats_file_sign,output_file_sign,depth)





#========================================== INITIALIZATION =============================================================
#=======================================================================================================================
#=======================================================================================================================
def initialize_candidate_22_aug(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes):
    create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
    test_harness_keypair_basename = 'test_harness_crypto_sign_keypair.c'
    test_harness_sign_basename = 'test_harness_crypto_sign.c'
    cfg_file_keypair = binsec_keypair_folder+'/cfg_file.cfg'
    cfg_content_keypair(cfg_file_keypair)
    test_harness_keypair = binsec_keypair_folder+'/'+test_harness_keypair_basename
    test_harness_content_keypair(test_harness_keypair,api,sign,add_includes)
    folder = opt_src_folder
    api_folder = ""
    sign_folder = ""
    if not api == "":
        api_folder_split = api.split("../")
        api_folder = api_folder_split[-1]
        api_folder = api_folder.split('"')
        api_folder = api_folder[0]
        abs_path_to_api_or_sign = folder+'/'+api_folder
    if not sign == "":
        sign_folder_split = sign.split("../")
        sign_folder = sign_folder_split[-1]
        sign_folder = sign_folder.split('"')
        sign_folder = sign_folder[0]
        abs_path_to_api_or_sign = folder+'/'+sign_folder

    if 'Reference_Implementation' in api_folder:
        candidate_folder_list = opt_src_folder.split("/")
        candidate_folder_list.pop()
        candidate_folder = "/".join(candidate_folder_list)
        folder = candidate_folder
    args_types,args_names =  sign_find_args_types_and_names(abs_path_to_api_or_sign)
    cfg_file_sign = binsec_sign_folder+'/cfg_file.cfg'
    crypto_sign_args_names = args_names
    sign_configuration_file_content(cfg_file_sign,crypto_sign_args_names)
    test_harness_sign = binsec_sign_folder+'/'+test_harness_sign_basename
    sign_test_harness_content(test_harness_sign,api,sign,add_includes,args_types,args_names)

def initialize_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes):
    create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
    test_harness_keypair_basename = 'test_harness_crypto_sign_keypair.c'
    test_harness_sign_basename = 'test_harness_crypto_sign.c'
    cfg_file_keypair = binsec_keypair_folder+'/cfg_file.cfg'
    cfg_content_keypair(cfg_file_keypair)
    test_harness_keypair = binsec_keypair_folder+'/'+test_harness_keypair_basename
    test_harness_content_keypair(test_harness_keypair,api,sign,add_includes)
    folder = opt_src_folder
    api_folder = ""
    sign_folder = ""
    abs_path_to_api_or_sign = ""
    if not api == "":
        api_folder_split = api.split("../")
        api_folder = api_folder_split[-1]
        api_folder = api_folder.split('"')
        api_folder = api_folder[0]
        abs_path_to_api_or_sign = folder+'/'+api_folder
    if not sign == "":
        sign_folder_split = sign.split("../")
        sign_folder = sign_folder_split[-1]
        sign_folder = sign_folder.split('"')
        sign_folder = sign_folder[0]
        abs_path_to_api_or_sign = folder+'/'+sign_folder
    if 'Reference_Implementation' in abs_path_to_api_or_sign:
        candidate_folder_list = abs_path_to_api_or_sign.split("/")
        #candidate_folder_list.pop()
        candidate_folder_list.remove('Optimized_Implementation')
        candidate_folder = "/".join(candidate_folder_list)
        abs_path_to_api_or_sign = candidate_folder
        folder = candidate_folder
    args_types,args_names =  sign_find_args_types_and_names(abs_path_to_api_or_sign)
    cfg_file_sign = binsec_sign_folder+'/cfg_file.cfg'
    crypto_sign_args_names = args_names
    sign_configuration_file_content(cfg_file_sign,crypto_sign_args_names)
    test_harness_sign = binsec_sign_folder+'/'+test_harness_sign_basename
    sign_test_harness_content(test_harness_sign,api,sign,add_includes,args_types,args_names)



def init_nist_signature_candidate_20_Aug(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,add_includes):
    opt_src_folder = create_path_to_optimization_src_folder(signature_type,candidate,optimized_imp_folder,src_folder)
    binsec_folder_full_path = opt_src_folder+'/'+binsec_folder
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
    initialize_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes)


def init_nist_signature_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_subfolder,src_folder,api,sign,add_includes):
    opt_src_folder = create_path_to_optimization_src_folder(signature_type,candidate,optimized_imp_folder,opt_subfolder)
    #opt_src_folder = create_path_to_optimization_src_folder(signature_type,candidate,optimized_imp_folder,src_folder)
    binsec_folder_full_path = opt_src_folder+'/'+binsec_folder
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
    initialize_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes)



def init_nist_signature_candidate_type2_15_Aug(binsec_folder,signature_type,candidate,optimized_imp_folder,api,sign,add_includes):
    opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    opt_src_folder_list_dir = os.listdir(opt_src_folder)
    binsec_folder_full_path = opt_src_folder+'/'+binsec_folder
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_sign_folder_basename = candidate+'_sign'
    if 'binsec' in opt_src_folder_list_dir:
        opt_src_folder_list_dir.remove('binsec')
    for subfold in opt_src_folder_list_dir:
        binsec_keypair_folder =""
        binsec_sign_folder = ""
        binsec_keypair_folder = binsec_folder_full_path+'/'+subfold+'/'+binsec_keypair_folder_basename
        binsec_sign_folder = binsec_folder_full_path+'/'+subfold+'/'+binsec_sign_folder_basename
        create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
        initialize_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes)


def init_nist_signature_candidate_type2_good_17_Aug(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,add_includes):
    opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    binsec_folder_full_path = opt_src_folder+'/'+binsec_folder
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_sign_folder_basename = candidate+'_sign'
    if binsec_folder in opt_src_folder_list_dir:
        opt_src_folder_list_dir.remove(binsec_folder)
    for subfold in opt_src_folder_list_dir:
        binsec_keypair_folder =""
        binsec_sign_folder = ""
        binsec_keypair_folder = binsec_folder_full_path+'/'+subfold+'/'+binsec_keypair_folder_basename
        binsec_sign_folder = binsec_folder_full_path+'/'+subfold+'/'+binsec_sign_folder_basename
        create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)

        if not abs_path_api == "":
            api = f'"{abs_path_api}{subfold}/api.h"'
        else:
            api = ""
        if not abs_path_sign == "":
            sign = f'"{abs_path_sign}{subfold}/sign.h"'
        else:
            sign = ""
        initialize_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes)

def init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,subfolder_src_files,abs_path_api,abs_path_sign,add_includes):
    opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    binsec_folder_full_path = opt_src_folder+'/'+binsec_folder
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_sign_folder_basename = candidate+'_sign'
    if binsec_folder in opt_src_folder_list_dir:
        opt_src_folder_list_dir.remove(binsec_folder)
    for subfold in opt_src_folder_list_dir:
        binsec_keypair_folder =""
        binsec_sign_folder = ""
        binsec_keypair_folder = binsec_folder_full_path+'/'+subfold+'/'+binsec_keypair_folder_basename
        binsec_sign_folder = binsec_folder_full_path+'/'+subfold+'/'+binsec_sign_folder_basename
        create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
        if not subfolder_src_files == "":
            relative_path_to_src_subfold = f'{subfold}/{subfolder_src_files}'
            if not abs_path_api == "":
                api = f'"{abs_path_api}{relative_path_to_src_subfold}/api.h"'
            else:
                api = ""
            if not abs_path_sign == "":
                sign = f'"{abs_path_sign}{relative_path_to_src_subfold}/sign.h"'
            else:
                sign = ""
        else:
            if not abs_path_api == "":
                api = f'"{abs_path_api}{subfold}/api.h"'
            else:
                api = ""
            if not abs_path_sign == "":
                sign = f'"{abs_path_sign}{subfold}/sign.h"'
            else:
                sign = ""
        print("---api----",api)
        initialize_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes)



def init_compile_nist_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign, \
                                build_folder,path_to_cmakelist_file,path_to_makefile,path_to_build_folder,add_includes):
    init_nist_signature_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,add_includes)
    compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile,path_to_build_folder)


def init_compile_nist_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,api,sign, \
                                      build_folder,path_to_cmakelist_file,path_to_makefile,path_to_build_folder,add_includes):
    init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,api,sign,add_includes)
    compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile,path_to_build_folder)








#========================================== NIST CANDIDATES ============================================================
#=======================================================================================================================
#=======================================================================================================================

#========================================== CODE ==================================================================
#=======================================================================================================================




#========================================== SYMMETRIC ==================================================================
#=======================================================================================================================

#========================================== AIMER ==================================================================
def makefile_aimer(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    # SPDX-License-Identifier: MIT

    CC = gcc
    CFLAGS += -I. -O3 -g -Wall -Wextra -march=native -fomit-frame-pointer
    NISTFLAGS = -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter -Wno-unused-result
    AVX2FLAGS = -mavx2 -mpclmul
    SHAKE_PATH = shake
    SHAKE_LIB = libshake.a
    LDFLAGS = $(SHAKE_PATH)/$(SHAKE_LIB)
    
    EXECUTABLE_TESTTREE = tests/test_tree
    EXECUTABLE_TESTAIM  = tests/test_aim
    EXECUTABLE_TESTSIGN = tests/test_sign
    EXECUTABLE_KAT      = PQCgenKAT_sign
    
    BINSEC_STATIC_FLAG = -static
    EXECUTABLE_KEYPAIR		= ../binsec/{subfolder}/aimer_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		= ../binsec/{subfolder}/aimer_sign/test_harness_crypto_sign
    
    .PHONY: all
    
    all: $(SHAKE_LIB) $(EXECUTABLE_TESTTREE) $(EXECUTABLE_TESTAIM) $(EXECUTABLE_TESTSIGN) $(EXECUTABLE_KAT) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    .c.o:
    \t$(CC) -c $(CFLAGS) $< -o $@
    
    $(SHAKE_LIB):
    \t$(MAKE) -C $(SHAKE_PATH)
    
    $(EXECUTABLE_TESTTREE): $(EXECUTABLE_TESTTREE).c hash.c tree.c
    \t$(CC) $(CFLAGS) $(AVX2FLAGS) $^ $(LDFLAGS) -o $@
    
    $(EXECUTABLE_TESTAIM): $(EXECUTABLE_TESTAIM).c field/field128.c aim128.c hash.c
    \t$(CC) $(CFLAGS) $(AVX2FLAGS) -D_AIMER_L=1 $^ $(LDFLAGS) -o $@
    
    $(EXECUTABLE_TESTSIGN): $(EXECUTABLE_TESTSIGN).c field/field128.c aim128.c rng.c hash.c tree.c aimer_internal.c aimer_instances.c aimer.c
    \t$(CC) $(CFLAGS) $(AVX2FLAGS) -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto -o $@
    
    $(EXECUTABLE_KAT): $(EXECUTABLE_KAT).c api.c field/field128.c aim128.c rng.c hash.c tree.c aimer_internal.c aimer_instances.c aimer.c
    \t$(CC) $(CFLAGS) $(AVX2FLAGS) -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto -o $@
    
    
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c api.c field/field128.c aim128.c rng.c hash.c tree.c aimer_internal.c aimer_instances.c aimer.c
    \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(AVX2FLAGS)  -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto -o $@
        
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c api.c field/field128.c aim128.c rng.c hash.c tree.c aimer_internal.c aimer_instances.c aimer.c
    \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(AVX2FLAGS)  -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto -o $@
    
    clean:
    \trm -f $(wildcard *.o) $(EXECUTABLE_TESTTREE) $(EXECUTABLE_TESTAIM) $(EXECUTABLE_TESTSIGN) $(EXECUTABLE_KAT) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) PQCsignKAT_*.rsp PQCsignKAT_*.req
    \t$(MAKE) -C $(SHAKE_PATH) clean   
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))

def init_compile_aimer_single_subfolder(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder,api,sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    #path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfolder
    path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+subfolder
    init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,api,sign,add_includes)
    makefile_aimer(path_to_makefile_folder,subfolder)
    #makefile_aimer(path_to_makefile_folder)
    compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)

def init_compile_aimer(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    subfolder_src_files = ""
    # api = f'"../../../AIMer-l1-param1-avx2/api.h"'
    # init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,api,sign,add_includes)
    #init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,api,sign,add_includes)
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolders_list,subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        #init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolders_list,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+subfold
        makefile_aimer(path_to_makefile_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)


def run_aimer(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)

def compile_run_aimer(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_aimer(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_aimer(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_aimer(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_aimer(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)



#========================================== FAEST ======================================================================
def makefile_faest1(path_to_makefile_folder,src_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC?=gcc
    CXX?=g++
    CFLAGS+=-g -O3 -std=gnu11 -march=native
    CPPFLAGS+=-I. -Isha3 -DNDEBUG -DHAVE_OPENSSL
    
    SRC_DIR = ../../{src_folder}/{subfolder} 
    
    
    SOURCES=$(filter-out $(SRC_DIR)/randomness.c,$(wildcard $(SRC_DIR)/*.c)) $(wildcard $(SRC_DIR)/sha3/*.c) $(wildcard $(SRC_DIR)/sha3/*.s)
    
    
    BINSEC_STATIC_FLAG  = -static
    # EXECUTABLE_KEYPAIR	= {subfolder}/faest_keypair/test_harness_crypto_sign_keypair
    # EXECUTABLE_SIGN		= {subfolder}/faest_sign/test_harness_crypto_sign
    EXECUTABLE_KEYPAIR	    = faest_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = faest_sign/test_harness_crypto_sign
    
    
    LIBFAEST=libfaest.a
    NISTKAT_SOURCES=$(wildcard NIST-KATs/*.c)
    
    all: $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    $(LIBFAEST): $(SOURCES:.c=.o) $(SOURCES:.s=.o)
    \tar rcs $@ $^
    
    %.c.o: %.c
    \t$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@
    
    $(EXECUTABLE_NISTKAT): CPPFLAGS+=-DHAVE_RANDOMBYTES
    $(EXECUTABLE_NISTKAT): CFLAGS+=-Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter -Wno-unused-result
    
    $(EXECUTABLE_APITEST): $(EXECUTABLE_APITEST).c.o $(LIBFAEST) randomness.c.o
    \t$(CC) $(CPPFLAGS) $(LDFLAGS) $^ -lcrypto -o $@
        
        
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c.o $(LIBFAEST) randomness.c.o
    \t$(CC) $(CPPFLAGS) $(LDFLAGS) $^ -lcrypto -o $@
        
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c.o $(LIBFAEST) randomness.c.o
    \t$(CC) $(CPPFLAGS) $(LDFLAGS) $^ -lcrypto -o $@
    
    
    $(EXECUTABLE_NISTKAT): $(addsuffix .o, $(NISTKAT_SOURCES)) $(LIBFAEST) randomness.c
    \t$(CC) $(CPPFLAGS) $(LDFLAGS) $^ -lcrypto -o $@
    
    clean:
    \trm -f \
    \t$(wildcard $(SRC_DIR)/*.o) \
    \t$(wildcard $(SRC_DIR)/sha3/*.o) \
    \t$(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    .PHONY: clean
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))

def makefile_faest(path_to_makefile_folder,src_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC?=gcc
    CXX?=g++
    CFLAGS+=-g -O2 -march=native -mtune=native -std=c11
    CPPFLAGS+=-DHAVE_OPENSSL -DNDEBUG -MMD -MP -MF $*.d
    BINSEC_STATIC_FLAG  = -static
    
    SRC_DIR = ../../{src_folder}/{subfolder} 
    
    SOURCES=$(filter-out  $(SRC_DIR)/PQCgenKAT_sign.c ,$(wildcard $(SRC_DIR)/*.c)) $(wildcard $(SRC_DIR)/*.s)
    LIBFAEST=libfaest.a
    
    
    EXECUTABLE_KEYPAIR	    = faest_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = faest_sign/test_harness_crypto_sign
    
    
    all: $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    .PHONY: all
    
    $(LIBFAEST): $(SOURCES:.c=.o) $(SOURCES:.s=.o)
    \tar rcs $@ $^
    
    
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(LIBFAEST)
    \t$(CC) -o $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_KEYPAIR).c $(BINSEC_STATIC_FLAG) $(LIBFAEST)
    
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(LIBFAEST)
    \t$(CC) -o $(EXECUTABLE_SIGN) $(EXECUTABLE_SIGN).c $(BINSEC_STATIC_FLAG) $(LIBFAEST)
    
    
    clean: 
    \trm -f $(SRC_DIR)/*.d $(SRC_DIR)/*.o $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    .PHONY: clean
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def init_compile_faest(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolders_list,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_faest(path_to_makefile_folder,src_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)


def run_faest(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_faest(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_faest(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_faest(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_faest(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_faest(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)



#========================================== Ascon_sign ======================================================================

def makefile_ascon(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    THASH = robust

    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BINSEC_STATIC_FLAG  = -static
    DEBUG_G_FLAG = -g
    BASE_DIR = ../../../{subfolder}
     
      
    SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c $(BASE_DIR)/sign.c
    
    SOURCES += $(BASE_DIR)/hash_ascon.c $(BASE_DIR)/ascon_opt64/ascon.c $(BASE_DIR)/ascon_opt64/permutations.c  $(BASE_DIR)/thash_ascon_$(THASH).c
    
    
    DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
    
 
    
    EXECUTABLE_KEYPAIR	    = Ascon_sign_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = Ascon_sign_sign/test_harness_crypto_sign
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) #PQCgenKAT_sign
    
    all:  $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN) #PQCgenKAT_sign tests benchmarks
    
    
    
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES)
    \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -o $@ $(DET_SOURCES) $< -lcrypto
    
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES)
    \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -o $@ $(DET_SOURCES) $< -lcrypto
    
    clean:
    \t-$(RM)  $(EXECUTABLE_SIGN)
    \t-$(RM)  $(EXECUTABLE_KEYPAIR) 
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))





def init_compile_ascon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    subfolder_src_files = ""
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_ascon(path_to_makefile_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)



def run_ascon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_ascon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_ascon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_ascon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_ascon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_ascon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)




#========================================== Sphincs-alpha ======================================================================

def makefile_sphincs(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BINSEC_STATIC_FLAG  = -static
    DEBUG_G_FLAG = -g
    BASE_DIR = ../../{subfolder}
    
    
    SOURCES =          $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c
    HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h $(BASE_DIR)/merkle.h $(BASE_DIR)/wots.h $(BASE_DIR)/wotsx1.h $(BASE_DIR)/utils.h $(BASE_DIR)/utilsx1.h $(BASE_DIR)/fors.h $(BASE_DIR)/api.h  $(BASE_DIR)/hash.h $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h
    
    ifneq (,$(findstring shake,$(PARAMS)))
    \tSOURCES += $(BASE_DIR)/fips202.c $(BASE_DIR)/hash_shake.c $(BASE_DIR)/thash_shake_$(THASH).c
    \tHEADERS += $(BASE_DIR)/fips202.h
    endif
    ifneq (,$(findstring haraka,$(PARAMS)))
    \tSOURCES += $(BASE_DIR)/haraka.c $(BASE_DIR)/hash_haraka.c $(BASE_DIR)/thash_haraka_$(THASH).c
    \tHEADERS += $(BASE_DIR)/haraka.h
    endif
    ifneq (,$(findstring sha2,$(PARAMS)))
    \tSOURCES += $(BASE_DIR)/sha2.c $(BASE_DIR)/hash_sha2.c $(BASE_DIR)/thash_sha2_$(THASH).c
    \tHEADERS += $(BASE_DIR)/sha2.h
    endif
    
    DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
    DET_HEADERS = $(HEADERS:randombytes.%=rng.%)
    
    
    EXECUTABLE_KEYPAIR	    = sphincs-alpha_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = sphincs-alpha_sign/test_harness_crypto_sign
    
    
    
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
    \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $@ $(DET_SOURCES) $< -lcrypto
        
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
    \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $@ $(DET_SOURCES) $< -lcrypto
        
        
    
    PQCgenKAT_sign: PQCgenKAT_sign.c $(DET_SOURCES) $(DET_HEADERS)
    \t$(CC) $(CFLAGS) -o $@ $(DET_SOURCES) $< -lcrypto
    
    
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))

def init_compile_sphincs(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    subfolder_src_files = ""
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_sphincs(path_to_makefile_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)



def run_sphincs(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_sphincs(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_sphincs(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_sphincs(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_sphincs(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_sphincs(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)





#========================================== MIRA ======================================================================

def makefile_mira(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    SCRIPT_VERSION=v1.0
    SCRIPT_AUTHOR=MIRA team
    
    CC=gcc
    C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -g 
    BINSEC_STATIC_FLAG  = -static
    
    BASE_DIR = ../../{subfolder}
    
    RANDOMBYTES_SRC:=$(BASE_DIR)/lib/randombytes/randombytes.c
    RANDOMBYTES_INCLUDE:=-I $(BASE_DIR)/lib/randombytes -lcrypto
    
    XKCP_SRC:=$(BASE_DIR)/lib/XKCP
    XKCP_SRC_SIMPLE:=$(XKCP_SRC)/SimpleFIPS202.c
    XKCP_INCLUDE:=-I$(XKCP_SRC) -I$(XKCP_SRC)/avx2
    XKCP_INCLUDE_SIMPLE:=-I $(XKCP_SRC)
    XKCP_LINKER:=-L$(XKCP_SRC) -lshake
    
    WRAPPER_SRC:=$(BASE_DIR)/src/wrapper
    WRAPPER_INCLUDE:=-I $(WRAPPER_SRC)
    
    FFI_SRC:=$(BASE_DIR)/src/finite_fields
    FFI_INCLUDE:=-I $(FFI_SRC)
    
    SRC:=$(BASE_DIR)/src
    INCLUDE:=-I $(BASE_DIR)/src $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) $(RANDOMBYTES_INCLUDE)
    
    
    MIRA_OBJS:=finite_fields.o keygen.o sign.o verify.o nist_sign.o mpc.o parsing.o tree.o
    LIB_OBJS:=SimpleFIPS202.o randombytes.o
    
    BUILD:=bin/build
    BIN:=bin
    
    
    EXECUTABLE_KEYPAIR	    = mira_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = mira_sign/test_harness_crypto_sign
    
    
    folders:
    \t@echo -e "### Creating build folders"
    \tmkdir -p $(BUILD)
    
    randombytes.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BUILD)/$@
    
    SimpleFIPS202.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER) -o $(BUILD)/SimpleFIPS202.o
    
    xkcp: folders
    \t@echo -e "### Compiling XKCP"
    \tmake -C $(XKCP_SRC)
    
    
    finite_fields.o: $(FFI_SRC)/finite_fields.c | folders
    \t@echo -e "### Compiling finite_fields"
    \t$(CC) $(C_FLAGS) -c $< $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BUILD)/$@
    
    %.o: $(SRC)/%.c | folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BUILD)/$@
    
    
    all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)  ##@Build Build all the project
    

    #.PHONY: $(EXECUTABLE_KEYPAIR)
    $(EXECUTABLE_KEYPAIR): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files: PQCsignKAT_XX.req and PQCsignKAT_XX.rsp
    \t@echo -e "### Compiling MIRA-128F (test harness keypair)"
    \t$(CC) $(BINSEC_STATIC_FLAG) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BUILD)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $@
    
    $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files: PQCsignKAT_XX.req and PQCsignKAT_XX.rsp
    \t@echo -e "### Compiling MIRA-128F (test harness sign)"
    \t$(CC) $(BINSEC_STATIC_FLAG) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BUILD)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $@
    

    .PHONY: clean
    clean:
    \tmake -C $(XKCP_SRC) clean
    \trm -f $(EXECUTABLE_KEYPAIR)
    \trm -f $(EXECUTABLE_SIGN)
    \trm -rf ./bin
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def compile_mira(path_to_makefile):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make","all"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)

def init_compile_mira(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_build_folder = ""
    add_includes = []
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir, \
                                            subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        #init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolders_list,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_mira(path_to_makefile_folder,subfold)
        compile_mira(path_to_makefile_folder)


def run_mira(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_mira(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_mira(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_mira(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_mira(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_mira(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)



#========================================== MQOM ======================================================================
def makefile_mqom(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''    
    CC?=gcc
    ALL_FLAGS?=-O3 -flto -fPIC -std=c11 -march=native -Wall -Wextra -Wpedantic -Wshadow -DPARAM_HYPERCUBE_7R -DPARAM_GF31 -DPARAM_L1 -DPARAM_RND_EXPANSION_X4 -DHASHX4 -DXOFX4 -DPRGX4 -DNDEBUG -mavx
    ALL_FLAGS+=$(EXTRA_ALL_FLAGS) -g 
    
    BINSEC_STATIC_FLAG  = -static
    BASE_DIR = ../../{subfolder}
    
    SYM_OBJ= $(BASE_DIR)/rnd.o $(BASE_DIR)/hash.o $(BASE_DIR)/xof.o
    ARITH_OBJ= $(BASE_DIR)/gf31-matrix.o $(BASE_DIR)/gf31.o
    MPC_OBJ= $(BASE_DIR)/mpc.o $(BASE_DIR)/witness.o $(BASE_DIR)/serialization-specific.o $(BASE_DIR)/precomputed.o
    CORE_OBJ= $(BASE_DIR)/keygen.o $(BASE_DIR)/sign.o $(BASE_DIR)/views.o $(BASE_DIR)/commit.o $(BASE_DIR)/sign-mpcith-hypercube.o $(BASE_DIR)/tree.o
    
    HASH_PATH=$(BASE_DIR)/sha3
    HASH_MAKE_OPTIONS=PLATFORM=avx2
    
    EXECUTABLE_KEYPAIR	    = mqom_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = mqom_sign/test_harness_crypto_sign
    
    EXECUTABLE_KEYPAIR_OBJ	    = mqom_keypair/test_harness_crypto_sign_keypair.o $(BASE_DIR)/generator/rng.o
    EXECUTABLE_SIGN_OBJ		    = mqom_sign/test_harness_crypto_sign.o $(BASE_DIR)/generator/rng.o
    
    HASH_INCLUDE=-I$(BASE_DIR)/sha3 -I. -I$(BASE_DIR)/sha3/avx2

    
    %.o : %.c
    \t$(CC) -c $(ALL_FLAGS) $(HASH_INCLUDE) -I. $< -o $@
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    
    libhash:
    \t$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH)
    
    
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
    \t$(CC) $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(BINSEC_STATIC_FLAG) $(ALL_FLAGS) -L$(HASH_PATH) -L. -lhash -lcrypto -o $@
    
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
    \t$(CC) $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(BINSEC_STATIC_FLAG) $(ALL_FLAGS) -L$(HASH_PATH) -L. -lhash -lcrypto -o $@
    
    
    # Cleaning
    
    clean:
    \trm -f $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ)
    \trm -f $(EXECUTABLE_KEYPAIR_OBJ) $(EXECUTABLE_SIGN_OBJ)  
    \trm -rf unit-*
    \t$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH) clean
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))



def init_compile_mqom(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    subfolder_src_files = ""
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_mqom(path_to_makefile_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)



def run_mqom(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_mqom(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_mqom(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_mqom(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_mqom(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_mqom(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)



#========================================== PERK ======================================================================
def makefile_perk(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''   
    CC = gcc
    CFLAGS:= -std=c99 -pedantic -Wall -Wextra -O3 -funroll-all-loops -march=native -Wimplicit-function-declaration -Wredundant-decls -Wmissing-prototypes -Wstrict-prototypes -Wundef -Wshadow -Wno-newline-eof \
                      -mavx2 -mpclmul -msse4.2 -maes
    ASMFLAGS := -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
    LDFLAGS:= -lcrypto
    ADDITIONAL_CFLAGS:= -Wno-missing-prototypes -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter
    
    BINSEC_STATIC_FLAG  = -static
    DEBUG_G_FLAG = -g
    BASE_DIR = ../../{subfolder}
    
    # Directories
    BUILD_DIR:=build
    BIN_DIR:=$(BUILD_DIR)/bin
    LIB_DIR:=$(BASE_DIR)/lib
    SRC_DIR:=$(BASE_DIR)/src
    
    # main files and executables
    
    MAIN_PERK_SRC:=$(SRC_DIR)/main.c
    MAIN_KAT_SRC:=$(SRC_DIR)/PQCgenKAT_sign.c
    
    
    EXECUTABLE_KEYPAIR	    = perk_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = perk_sign/test_harness_crypto_sign
    
    # exclude sources from "find"
    EXCL_SRC:=! -name $(notdir $(MAIN_PERK_SRC)) \
              ! -name $(notdir $(MAIN_KAT_SRC))
    
    # PERK sources
    PERK_SRC:= $(shell find $(SRC_DIR) -name "*.c" $(EXCL_SRC))
    # Lib sources
    LIB_CSRC := $(shell find $(LIB_DIR) -name "*.c" ! -path  "lib/djbsort/*")
    SORT_CSRC := $(shell find $(LIB_DIR)/djbsort -name "*.c")
    LIB_SSRC := $(shell find $(LIB_DIR) -name "*.s")
    
    
    # PERK objects
    PERK_OBJS:=$(PERK_SRC:%.c=$(BUILD_DIR)/%$(EXT).o)
    # Lib objects
    LIB_COBJS:=$(LIB_CSRC:%.c=$(BUILD_DIR)/%.o)
    SORT_COBJS:=$(SORT_CSRC:%.c=$(BUILD_DIR)/%.o)
    LIB_SOBJS:=$(LIB_SSRC:%.s=$(BUILD_DIR)/%.o)
    LIB_OBJS:=$(LIB_COBJS) $(LIB_SOBJS) $(SORT_COBJS)
    
    
    # include directories
    LIB_INCLUDE:=-I $(LIB_DIR)/cryptocode -I $(LIB_DIR)/XKCP -I $(LIB_DIR)/randombytes -I $(LIB_DIR)/djbsort
    PERK_INCLUDE:=-I $(SRC_DIR) $(LIB_INCLUDE)
    
    .PHONY: all
    all: $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN)   #perk-128-fast-3 perk-128-fast-3-verbose perk-128-fast-3-kat
    
    # build rules
    $(LIB_COBJS): $(BUILD_DIR)/%.o: %.c
    \t@echo -e "### Compiling external library file $@"
    \t@mkdir -p $(dir $@)
    \t$(CC) $(CFLAGS) $(ADDITIONAL_CFLAGS) -c $< $(LIB_INCLUDE) -o $@
    
    $(SORT_COBJS): $(BUILD_DIR)/%.o: %.c
    \t@echo -e "### Compiling external library file $@"
    \t@mkdir -p $(dir $@)
    \t$(CC) $(CFLAGS) -fwrapv $(ADDITIONAL_CFLAGS) -c $< $(LIB_INCLUDE) -o $@
    
    $(LIB_SOBJS): $(BUILD_DIR)/%.o: %.s
    \t@echo -e "### Assembling external library file $@"
    \t@mkdir -p $(dir $@)
    \t$(CC) $(ASMFLAGS) -c $< -o $@
    
    $(PERK_OBJS): $(BUILD_DIR)/%$(EXT).o: %.c
    \t@echo -e "### Compiling perk-128-fast-3 file $@"
    \t@mkdir -p $(dir $@)
    \t$(CC) $(CFLAGS) -c $< $(PERK_INCLUDE) -o $@
    
    # main targets
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c  $(PERK_OBJS) $(LIB_OBJS)
    \t@echo -e "### Compiling PERK Test harness keypair"
    \t@mkdir -p $(dir $@)
    \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -Wno-strict-prototypes -Wno-unused-result $^ $(PERK_INCLUDE) -o $@ $(LDFLAGS)
        
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c  $(PERK_OBJS) $(LIB_OBJS)
    \t@echo -e "### Compiling PERK Test harness sign"
    \t@mkdir -p $(dir $@)
    \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -Wno-strict-prototypes -Wno-unused-result $^ $(PERK_INCLUDE) -o $@ $(LDFLAGS)
    
    clean:
    \trm -rf $(BUILD_DIR) 
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))



def compile_perk(path_to_makefile):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make","all"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)

def init_compile_perk(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_build_folder = ""
    add_includes = []
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir, \
                                            subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_perk(path_to_makefile_folder,subfold)
        compile_perk(path_to_makefile_folder)


def run_perk(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_perk(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_perk(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_perk(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_perk(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_perk(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)



#========================================== RYDE =======================================================================

def makefile_ryde(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f''' 
    SCRIPT_VERSION=v1.0
    SCRIPT_AUTHOR=RYDE team
    
    CC=gcc
    C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4
    C_FLAGS_VERBOSE:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -DVERBOSE
    
    BINSEC_STATIC_FLAG  = -static
    DEBUG_G_FLAG = -g
    BASE_DIR = ../../{subfolder}
    
    RANDOMBYTES_SRC:=$(BASE_DIR)/lib/randombytes/randombytes.c
    RANDOMBYTES_INCLUDE:=-I $(BASE_DIR)/lib/randombytes -lcrypto
    
    XKCP_SRC:=$(BASE_DIR)/lib/XKCP
    XKCP_SRC_SIMPLE:=$(XKCP_SRC)/SimpleFIPS202.c
    XKCP_INCLUDE:=-I$(XKCP_SRC) -I$(XKCP_SRC)/avx2
    XKCP_INCLUDE_SIMPLE:=-I $(XKCP_SRC)
    XKCP_LINKER:=-L$(XKCP_SRC) -lshake
    
    WRAPPER_SRC:=$(BASE_DIR)/src/wrapper
    WRAPPER_INCLUDE:=-I $(WRAPPER_SRC)
    
    RBC_SRC:=$(BASE_DIR)/src/rbc-31
    RBC_INCLUDE:=-I $(RBC_SRC)
    
    SRC:=$(BASE_DIR)/src
    INCLUDE:=-I $(BASE_DIR)/src $(RBC_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) $(RANDOMBYTES_INCLUDE)
    
    RYDE_OBJS:=rbc_31_elt.o rbc_31_vec.o rbc_31_qpoly.o rbc_31_vspace.o rbc_31_mat.o keypair.o signature.o verification.o mpc.o parsing.o tree.o sign.o
    LIB_OBJS:=SimpleFIPS202.o randombytes.o
    
    BUILD:=bin/build
    BIN:=bin
    
    
    KEYPAIR_FOLDER 			= ryde_keypair
    SIGN_FOLDER 			= ryde_sign
    EXECUTABLE_KEYPAIR	    = test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = test_harness_crypto_sign
    
    SRC_KEYPAIR	    		= ryde_keypair/test_harness_crypto_sign_keypair.c
    SRC_SIGN		    	= ryde_sign/test_harness_crypto_sign.c
    
    folders:
    \t@echo -e "### Creating build folders"
    \tmkdir -p $(BUILD)
    
    randombytes.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BUILD)/$@
    
    SimpleFIPS202.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER) -o $(BUILD)/SimpleFIPS202.o
    
    xkcp: folders
    \t@echo -e "### Compiling XKCP"
    \tmake -C $(XKCP_SRC)
    
    
    
    rbc_%.o: $(RBC_SRC)/rbc_%.c | folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $< $(RBC_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BUILD)/$@
    
    %.o: $(SRC)/%.c | folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BUILD)/$@
    
    
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    

    $(EXECUTABLE_KEYPAIR): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build test harness keypair
	\t@echo -e "### Compiling test harness keypair"
	\t$(CC) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) $(C_FLAGS) $(SRC_KEYPAIR) $(addprefix $(BUILD)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(KEYPAIR_FOLDER)/$@

    $(EXECUTABLE_SIGN): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build test harness sign
	\t@echo -e "### Compiling test harness sign"
	\t$(CC) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) $(C_FLAGS) $(SRC_SIGN) $(addprefix $(BUILD)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(SIGN_FOLDER)/$@
    
    
    .PHONY: clean
    clean: ##@Miscellaneous Clean data
    \tmake -C $(XKCP_SRC) clean
    \trm -f $(EXECUTABLE_KEYPAIR)
    \trm -f $(EXECUTABLE_SIGN)
    \trm -rf ./bin
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))



def compile_ryde(path_to_makefile):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make","all"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)

def init_compile_ryde(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_build_folder = ""
    add_includes = []
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir, \
                                            subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_ryde(path_to_makefile_folder,subfold)
        compile_ryde(path_to_makefile_folder)


def run_ryde(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_ryde(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_ryde(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_ryde(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_ryde(binsec_folder,signature_type,candidate,optimized_imp_folder,subfolder_src_files,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_ryde(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)





#========================================== ISOGENY ==================================================================
#=======================================================================================================================

def main_CMakeList_and_cmakeFlags_sqisign(cmakelists,flags_cmake_file,binsec_folder):
    with open(cmakelists, "a") as cmakelists_file:
        cmakelists_file.write('#Add binsec folder\n')
        cmakelists_file.write('add_subdirectory('+binsec_folder+')'+'\n')

    with open(flags_cmake_file, "a") as flags:
        flags.write('\n')
        flags.write('#construct static lib for binsec\n')
        flags.write('set(CMAKE_FIND_LIBRARY_SUFFIXES  ".a")\n')
        flags.write('set(BUILD_SHARED_LIBS OFF)'+'\n')
        flags.write('set(CMAKE_EXE_LINKER_FLAGS "-static")\n')

def cmakelists_sqisign(path_to_cmakelists_folder,candidate):
    path_to_cmakelists = path_to_cmakelists_folder+'/CMakeLists.txt'
    cmakelists_content = f'''
    set(KEYPAIR_FOLDER {candidate}_keypair)
    set(SIGN_FOLDER {candidate}_sign) 
    
    add_subdirectory(${{KEYPAIR_FOLDER}}) 
    add_subdirectory(${{SIGN_FOLDER}}) 
    '''
    with open(path_to_cmakelists, "w") as mfile:
        mfile.write(textwrap.dedent(cmakelists_content))


def compile_sqisign(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,build_folder):
    opt_src_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+src_folder
    cwd = os.getcwd()
    if not os.path.isdir(opt_src_folder):
        print("------{} is not a directory".format(opt_src_folder))
    os.chdir(opt_src_folder)
    cmakelists = 'CMakeLists.txt'
    flags_cmake_file = '.cmake/flags.cmake'
    with open(cmakelists, "r") as cmakelists_file:
        cmakelists_file_content = cmakelists_file.read()
        if not 'add_subdirectory('+binsec_folder+')' in cmakelists_file_content.split("\n"):
            main_CMakeList_and_cmakeFlags_sqisign(cmakelists,flags_cmake_file,binsec_folder)
    cmd = ["cmake","-DCMAKE_BUILD_TYPE=Release", "-DENABLE_DOC_TARGET=OFF", "-DSQISIGN_BUILD_TYPE=broadwell", "-B"+build_folder]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(build_folder)
    cmd = ["make","-j"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)


def init_sqisign(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,api,sign,add_includes,build_folder,library_name):
    binsec_folder_full_path = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+src_folder+'/'+binsec_folder
    binsec_keypair_folder_basename = candididate+'_keypair'
    binsec_sign_folder_basename = candididate+'_sign'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
    binsec_folder_cmakelist = binsec_folder_full_path+'/'+'CMakeLists.txt'
    with open(binsec_folder_cmakelist, "w") as cmake_file:
        cmake_file.write('add_subdirectory('+binsec_keypair_folder_basename+')'+'\n')
        cmake_file.write('add_subdirectory('+binsec_sign_folder_basename+')'+'\n')
    cwd = os.getcwd()

    test_harness_keypair_basename = 'test_harness_crypto_sign_keypair.c'
    test_harness_sign_basename = 'test_harness_crypto_sign.c'
    cfg_file_keypair = binsec_keypair_folder+'/cfg_file.cfg'
    cfg_content_keypair(cfg_file_keypair)
    test_harness_keypair = binsec_keypair_folder+'/'+test_harness_keypair_basename
    test_harness_content_keypair_sqisign(test_harness_keypair,api,sign,add_includes)
    cfg_file_sign = binsec_sign_folder+'/cfg_file.cfg'
    cfg_content_sign(cfg_file_sign)
    test_harness_sign = binsec_sign_folder+'/'+test_harness_sign_basename
    sign_folder_split = sign.split("../")
    sign_folder = sign_folder_split[-1]
    sign_folder = sign_folder.split('"')
    sign_folder = sign_folder[0]
    folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+src_folder
    sign_test_harness_content_sqisign(test_harness_sign,api,sign,add_includes)
    cmakelists_keypair = binsec_keypair_folder+'/'+'CMakeLists.txt'
    create_CMakeList_and_link_to_library(cmakelists_keypair,library_name,test_harness_keypair_basename)
    cmakelists_sign = binsec_sign_folder+'/'+'CMakeLists.txt'
    create_CMakeList_and_link_to_library(cmakelists_sign,library_name,test_harness_sign_basename)
    compile_sqisign(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,build_folder)



def init_compile_sqisign(binsec_folder,signature_type,candidate,optimized_imp_folder,broadwell_folder,subfolder_src_files,abs_path_api,abs_path_sign):
    add_includes = []
    init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,broadwell_folder,subfolder_src_files,abs_path_api,abs_path_sign,add_includes)



#========================================== LATTICE ==================================================================
#=======================================================================================================================

#========================================== haetae =====================================================================

def create_CMakeList(path_to_cmakelists,library_name,test_harness):
    executable_name = test_harness.split(".")[0]
    with open(path_to_cmakelists, "w") as cmakelists_file:
        cmakelists_file.write('add_executable('+executable_name+ '  ' +test_harness+')'+'\n')
        cmakelists_file.write('target_link_libraries('+executable_name+ '  PRIVATE  '+library_name+')'+'\n')

def create_keypair_sign_haetae_CMakeList(path_to_cmakelists,test_harness,sign_keypair_pattern):
    executable_name = test_harness.split(".")[0]
    cmakelists_content = f'''
    # set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/binsec/bin/haetae_sign/)
    # set(EXECUTABLE_OUTPUT_PATH ${{CMAKE_BINARY_DIR}}/binsec/bin/haetae_sign/)
    
    set(KEYPAIR_OR_SIGN_FOLDER {candidate}_{sign_keypair_pattern})
    
    
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/binsec/${{KEYPAIR_OR_SIGN_FOLDER}}/)
    set(EXECUTABLE_OUTPUT_PATH ${{CMAKE_BINARY_DIR}}/binsec/${{KEYPAIR_OR_SIGN_FOLDER}}/)
    
    add_executable({executable_name}_2 {test_harness})
    target_link_libraries({executable_name}_2 ${{LIB_NAME2}})
    
    add_executable({executable_name}_3 {test_harness})
    target_link_libraries({executable_name}_3 ${{LIB_NAME2}})
    
    add_executable({executable_name}_5 {test_harness})
    target_link_libraries({executable_name}_5 ${{LIB_NAME2}})
    '''
    with open(path_to_cmakelists, "w") as mfile:
        mfile.write(textwrap.dedent(cmakelists_content))


def cmakelists_haetae(path_to_cmakelists_folder,candidate):
    path_to_cmakelists = path_to_cmakelists_folder+'/CMakeLists.txt'
    cmakelists_content = f'''
    set(KEYPAIR_FOLDER {candidate}_keypair)
    set(SIGN_FOLDER {candidate}_sign) 
    
    add_subdirectory(${{KEYPAIR_FOLDER}}) 
    add_subdirectory(${{SIGN_FOLDER}}) 
    '''
    with open(path_to_cmakelists, "w") as mfile:
        mfile.write(textwrap.dedent(cmakelists_content))

def cmakelists_haetae1(path_to_cmakelists_folder,candidate):
    path_to_cmakelists = path_to_cmakelists_folder+'/CMakeLists.txt'
    cmakelists_content = f'''
    cmake_minimum_required(VERSION 3.18)
    project(haetae LANGUAGES ASM C CXX) # CXX for the google test
    
    enable_testing() # Enables running `ctest`
    
    set(BASE_DIR ../src)
    
    set(CMAKE_C_STANDARD 11)
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/libs/)
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/libs/)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/bin/)
    set(EXECUTABLE_OUTPUT_PATH ${{CMAKE_BINARY_DIR}}/bin/)
    set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
    
    set(HAETAE_SRCS
      ${{BASE_DIR}}/src/consts.c
      ${{BASE_DIR}}/src/poly.c
      ${{BASE_DIR}}/src/ntt.S
      ${{BASE_DIR}}/src/invntt.S
      ${{BASE_DIR}}/src/pointwise.S
      ${{BASE_DIR}}/src/shuffle.S
      ${{BASE_DIR}}/src/fft.c
      ${{BASE_DIR}}/src/reduce.c
      ${{BASE_DIR}}/src/polyvec.c
      ${{BASE_DIR}}/src/polymat.c
      ${{BASE_DIR}}/src/polyfix.c
      ${{BASE_DIR}}/src/decompose.c
      ${{BASE_DIR}}/src/sampler.c
      ${{BASE_DIR}}/src/packing.c
      ${{BASE_DIR}}/src/sign.c
      ${{BASE_DIR}}/src/fixpoint.c
      ${{BASE_DIR}}/src/encoding.c
    )
    
    set(HAETAE_FIPS202_SRCS
      ${{HAETAE_SRCS}}
      ${{BASE_DIR}}/src/symmetric-shake.c
    )
    set(FIPS202_SRCS ${{BASE_DIR}}/src/fips202.c ${{BASE_DIR}}/src/fips202x4.c ${{BASE_DIR}}/src/f1600x4.S)
    
    if(MSVC)
      set(C_FLAGS /nologo /O2 /W4 /wd4146 /wd4244)
    else()
      set(C_FLAGS -O3 -fomit-frame-pointer -mavx2 -Wall -Wextra -Wpedantic)
    endif()
    
    find_package(OpenSSL REQUIRED)
    
    include_directories(${{BASE_DIR}}/include)
    include_directories(${{BASE_DIR}}/api)
    link_directories(${{BASE_DIR}}/libs)
    
    add_library(fips202 SHARED ${{FIPS202_SRCS}})
    target_compile_options(fips202 PRIVATE -O3 -mavx2 -fomit-frame-pointer -fPIC)
    add_library(RNG SHARED ${{PROJECT_SOURCE_DIR}}/${{BASE_DIR}}//src/randombytes.c)
    target_compile_options(RNG PRIVATE -O3 -fomit-frame-pointer -fPIC)
    target_link_libraries(RNG PUBLIC OpenSSL::Crypto)
    
    
    # HAETAE 2 SHAKE ONLY
    set(LIB_NAME2 ${{PROJECT_NAME}}2)
    add_library(${{LIB_NAME2}} SHARED ${{HAETAE_FIPS202_SRCS}})
    target_compile_definitions(${{LIB_NAME2}} PUBLIC HAETAE_MODE=2)
    target_compile_options(${{LIB_NAME2}} PRIVATE ${{C_FLAGS}})
    target_link_libraries(${{LIB_NAME2}} INTERFACE fips202 m)
    target_link_libraries(${{LIB_NAME2}} PUBLIC RNG)
    
    # HAETAE 3 SHAKE ONLY
    set(LIB_NAME3 ${{PROJECT_NAME}}3)
    add_library(${{LIB_NAME3}} SHARED ${{HAETAE_FIPS202_SRCS}})
    target_compile_definitions(${{LIB_NAME3}} PUBLIC HAETAE_MODE=3)
    target_compile_options(${{LIB_NAME3}} PRIVATE ${{C_FLAGS}})
    target_link_libraries(${{LIB_NAME3}} INTERFACE fips202 m)
    target_link_libraries(${{LIB_NAME3}} PUBLIC RNG)
    
    # HAETAE 5 SHAKE ONLY
    set(LIB_NAME5 ${{PROJECT_NAME}}5)
    add_library(${{LIB_NAME5}} SHARED ${{HAETAE_FIPS202_SRCS}})
    target_compile_definitions(${{LIB_NAME5}} PUBLIC HAETAE_MODE=5)
    target_compile_options(${{LIB_NAME5}} PRIVATE ${{C_FLAGS}})
    target_link_libraries(${{LIB_NAME5}} INTERFACE fips202 m)
    target_link_libraries(${{LIB_NAME5}} PUBLIC RNG)
    
    add_subdirectory(${{BASE_DIR}}/test)
    add_subdirectory(${{BASE_DIR}}/kat)
    add_subdirectory(${{BASE_DIR}}/benchmark)
    
    
    set(KEYPAIR_FOLDER {candidate}_keypair)
    set(SIGN_FOLDER {candidate}_sign)
    
    add_subdirectory(${{KEYPAIR_FOLDER}}) 
    add_subdirectory(${{SIGN_FOLDER}}) 
    '''
    with open(path_to_cmakelists, "w") as mfile:
        mfile.write(textwrap.dedent(cmakelists_content))

def main_CMakeList_haetae(cmakelists,flags_cmake_file,binsec_folder):
    with open(cmakelists, "a") as cmakelists_file:
        cmakelists_file.write('#Add binsec folder\n')
        cmakelists_file.write('add_subdirectory('+binsec_folder+')'+'\n')

    with open(flags_cmake_file, "a") as flags:
        flags.write('\n')
        flags.write('#construct static lib for binsec\n')
        flags.write('set(CMAKE_FIND_LIBRARY_SUFFIXES  ".a")\n')
        flags.write('set(BUILD_SHARED_LIBS OFF)'+'\n')
        flags.write('set(CMAKE_EXE_LINKER_FLAGS "-static")\n')



#
def init_compile_haetae(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,abs_path_api,abs_path_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    subfolder_src_files = ""
    opt_subfolder = ""
    init_nist_signature_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_subfolder,src_folder,abs_path_api,abs_path_sign,add_includes)
    path_to_main_cmakefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder
    cmakelists_haetae(path_to_main_cmakefile_folder,candidate)
    test_harness_keypair_basename = 'test_harness_crypto_sign_keypair.c'
    test_harness_sign_basename = 'test_harness_crypto_sign.c'
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_keypair_folder = path_to_main_cmakefile_folder+'/'+binsec_keypair_folder_basename
    binsec_sign_folder = path_to_main_cmakefile_folder+'/'+binsec_sign_folder_basename
    cmakelists_keypair = binsec_keypair_folder+'/'+'CMakeLists.txt'
    keypair_pat = "keypair"
    create_keypair_sign_haetae_CMakeList(cmakelists_keypair,test_harness_keypair_basename,keypair_pat)
    cmakelists_sign = binsec_sign_folder+'/'+'CMakeLists.txt'
    sign_pat = "sign"
    create_keypair_sign_haetae_CMakeList(cmakelists_sign,test_harness_sign_basename,sign_pat)



#========================================== MPC-IN-THE-HEAD ==================================================================
#=======================================================================================================================

#========================================== MIRITH ======================================================================

def mirith_makefile1(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,subfolder,api,sign):
    if subfolder =="":
        SRC = "../../"+src_folder
    else:
        SRC = "../../"+src_folder+'/'+subfolder
    binsec_candidate_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+src_folder
    makefile = binsec_candidate_folder+'/Makefile'
    if not os.path.isdir(binsec_candidate_folder):
        cmd = ["mkdir","-p",binsec_candidate_folder]
        subprocess.call(cmd, stdin = sys.stdin)

    binsec_folder_content = os.listdir(binsec_candidate_folder)
    if not makefile in binsec_folder_content:
        cmd = ["touch",makefile]
        subprocess.call(cmd, stdin = sys.stdin)
    with open(makefile, "w") as file:
        file.write('CC=gcc\n')
        file.write('CFLAGS=-std=c11 -Wall -Wextra -pedantic -mavx2 -g -static\n')
        file.write(f'DEPS=$(wildcard {SRC}/*.h)\n')
        file.write(f'OBJ=$(patsubst {SRC}/%.c,{SRC}/%.o,$(wildcard {SRC}/*.c))\n')
        file.write(f'OBJ+=$(patsubst {SRC}/%.s,{SRC}/%.o,$(wildcard {SRC}/*.s))\n')
        file.write('\n')
        file.write('UNAME_S := $(shell uname -s)\n')
        file.write('ifeq ($(UNAME_S),Linux)\n')
        file.write('\tASMFLAGS := ${CFLAGS}\n')
        file.write('endif\n')
        file.write('ifeq ($(UNAME_S),Darwin)\n')
        file.write('\tASMFLAGS := ${CFLAGS} -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1\n')
        file.write('endif\n')
        file.write('\n\n')
        file.write('all: test_harness_crypto_sign_keypair test_harness_crypto_sign\n')
        file.write('\n')
        file.write('%.o: %.s\n')
        file.write('\t$(CC) -c $(ASMFLAGS) -o $@ $<\n')
        file.write('\n')
        file.write('%.o: %.c $(DEPS)\n')
        file.write('\t$(CC) -c $(CFLAGS) -o $@ $<\n')
        file.write('\n\n')
        file.write('test_harness_crypto_sign_keypair: test_harness_crypto_sign_keypair.o $(OBJ)\n')
        file.write('\t$(CC) ${LIBDIR} -o $@ $^ $(CFLAGS) $(LIBS)\n')
        file.write('\n')
        file.write('test_harness_crypto_sign: test_harness_crypto_sign.o $(OBJ)\n')
        file.write('\t$(CC) ${LIBDIR} -o $@ $^ $(CFLAGS) $(LIBS)\n')
        file.write('\n')
        file.write('run: test_harness_crypto_sign\n')
        file.write('\t./test_harness_crypto_sign\n')
        file.write('\n')
        file.write('.PHONY: clean\n')
        file.write('\n')
        file.write('clean:\n')
        file.write('\trm -f *.o *.su\n')
        file.write(f'\trm -f {SRC}/*.o {SRC}/*.su\n')
        file.write('\trm -f ./test_harness_crypto_sign\n')
        file.write('\trm -f ./test_harness_crypto_sign_keypair\n')



def compile_mirith(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,subfolder,api,sign):
    binsec_candidate_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+src_folder
    if not os.path.isdir(binsec_candidate_folder):
        cmd = ["mkdir","-p",binsec_candidate_folder]
        subprocess.call(cmd, stdin = sys.stdin)
    set_test_harness_sign_keypair(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,subfolder,api,sign)
    set_test_harness_sign(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,subfolder,api,sign)
    mirith_makefile1(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder,subfolder,api,sign)
    cwd = os.getcwd()
    os.chdir(binsec_candidate_folder)
    cmd = ["make"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)




def make_clean_mirith(binsec_folder,signature_type,candididate,optimized_imp_folder,src_folder):
    binsec_candidate_folder = signature_type+'/'+candididate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+src_folder
    cwd = os.getcwd()
    os.chdir(binsec_candidate_folder)
    cmd = ["make", "clean"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)




def makefile_mirith(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC=gcc
    CFLAGS=-std=c11 -Wall -Wextra -pedantic -mavx2 -g 
    
    BASE_DIR = ../../{subfolder}
    
    
    DEPS=$(wildcard $(BASE_DIR)/*.h)
    OBJ=$(patsubst $(BASE_DIR)/%.c,$(BASE_DIR)/%.o,$(wildcard $(BASE_DIR)/*.c)) 
    OBJ+=$(patsubst $(BASE_DIR)/%.s,$(BASE_DIR)/%.o,$(wildcard $(BASE_DIR)/*.s))
    
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
    \tASMFLAGS := ${{CFLAGS}}
    endif
    ifeq ($(UNAME_S),Darwin)
    \tASMFLAGS := ${{CFLAGS}} -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
    endif
    
    BINSEC_STATIC_FLAG  = -static

    EXECUTABLE_KEYPAIR	    = mirith_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = mirith_sign/test_harness_crypto_sign
    
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o: %.s
    \t$(CC) -c $(ASMFLAGS) -o $@ $<
    
    %.o: %.c $(DEPS)
    \t$(CC) -c $(CFLAGS) -o $@ $<
    
    
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).o $(OBJ)
    \t$(CC) $(LIBDIR) -o $@ $^ $(CFLAGS) $(LIBS) $(BINSEC_STATIC_FLAG)
    
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).o $(OBJ)
    \t$(CC) $(LIBDIR) -o $@ $^ $(CFLAGS) $(LIBS) $(BINSEC_STATIC_FLAG)
    
    
    
    .PHONY: clean
  
    clean:
    \trm -f $(BASE_DIR)/*.o $(BASE_DIR)/*.su
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    \trm -f $(EXECUTABLE_KEYPAIR).o $(EXECUTABLE_SIGN).o 
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))

def init_compile_mirith(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    subfolder_src_files = ""
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_mirith(path_to_makefile_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)


def run_mirith(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_mirith(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_mirith(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_mirith(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_mirith(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_mirith(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)



#========================================= CANDIDATE 4:  CROSS =========================================================
#=======================================================================================================================


def cmake_cross(cmake_lists):
    cmake_file_content = f'''
    cmake_minimum_required(VERSION 3.7)
    project(CROSS C)
    set(CMAKE_C_STANDARD 11)
    
    set(CC gcc)
    # set(CC clang)
    
    set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -march=haswell -O3 -g") 
    #set(SANITIZE "-fsanitize=address")
    
    set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} ${{SANITIZE}}")
    message("Compilation flags:" ${{CMAKE_C_FLAGS}})
    
    # default compilation picks reference codebase
    if(NOT DEFINED REFERENCE)
       set(REFERENCE 0)
    endif()
    
    set(CSPRNG_ALGO SHAKE_CSPRNG)
    set(HASH_ALGO SHA3_HASH)
    # set(CSPRNG_ALGO AES_CTR_CSPRNG)
    # set(HASH_ALGO SHA2_HASH)
    
    find_library(KECCAK_LIB keccak)
    if(NOT KECCAK_LIB)
     set(STANDALONE_KECCAK 1)
    endif()
    
    
    # selection of specialized compilation units differing between ref and opt
    # implementations.
    set(REFERENCE_CODE_DIR ../Reference_Implementation) 
    set(OPTIMIZED_CODE_DIR ../Optimized_Implementation) 
    
    # if(REFERENCE)
    # message("Compiling portable reference code")
    # set(SPEC_HEADERS  )
    # set(SPEC_SOURCES
    #         ${{REFERENCE_CODE_DIR}}/lib/aes256.c
    # )
    # else()
    message("Compiling optimized code")
    set(SPEC_HEADERS )
    set(SPEC_SOURCES
            ${{OPTIMIZED_CODE_DIR}}/lib/aes256.c
    )
    # endif()
    
    set(BASE_DIR ${{REFERENCE_CODE_DIR}})
    set(HEADERS
        ${{SPEC_HEADERS}}
        ${{BASE_DIR}}/include/api.h
        ${{BASE_DIR}}/include/aes256.h
        ${{BASE_DIR}}/include/aes256_ctr_drbg.h
        ${{BASE_DIR}}/include/CROSS.h
        ${{BASE_DIR}}/include/csprng_hash.h
        ${{BASE_DIR}}/include/pack_unpack.h
        ${{BASE_DIR}}/include/fips202.h
        ${{BASE_DIR}}/include/fq_arith.h
        ${{BASE_DIR}}/include/keccakf1600.h
        ${{BASE_DIR}}/include/parameters.h
        ${{BASE_DIR}}/include/seedtree.h
        ${{BASE_DIR}}/include/sha2.h
        ${{BASE_DIR}}/include/sha3.h
        ${{BASE_DIR}}/include/merkle_tree.h
        ${{BASE_DIR}}/include/merkle.h
    )
    
    if(STANDALONE_KECCAK)
      message("Employing standalone SHA-3")
      set(KECCAK_EXTERNAL_LIB "")
      set(KECCAK_EXTERNAL_ENABLE "")
      list(APPEND FALLBACK_SOURCES ${{BASE_DIR}}/lib/keccakf1600.c)
      list(APPEND FALLBACK_SOURCES ${{BASE_DIR}}/lib/fips202.c)
    else()
      message("Employing libkeccak")
      set(KECCAK_EXTERNAL_LIB keccak)
      set(KECCAK_EXTERNAL_ENABLE "-DSHA_3_LIBKECCAK")
    endif()
    
    
    set(SOURCES
        ${{SPEC_SOURCES}}
        ${{FALLBACK_SOURCES}}
        ${{BASE_DIR}}/lib/aes256_ctr_drbg.c
        ${{BASE_DIR}}/lib/CROSS.c
        ${{BASE_DIR}}/lib/csprng_hash.c
        ${{BASE_DIR}}/lib/pack_unpack.c
        ${{BASE_DIR}}/lib/keccakf1600.c
        ${{BASE_DIR}}/lib/fips202.c
        ${{BASE_DIR}}/lib/seedtree.c
        ${{BASE_DIR}}/lib/merkle.c
        ${{BASE_DIR}}/lib/sha2.c
        ${{BASE_DIR}}/lib/sign.c 
    )
    
    
    foreach(category RANGE 1 5 2)
        set(RSDP_VARIANTS RSDP RSDPG)
        foreach(RSDP_VARIANT ${{RSDP_VARIANTS}})
            set(PARAM_TARGETS SIG_SIZE SPEED)
            foreach(optimiz_target ${{PARAM_TARGETS}})
                 #crypto_sign_keypair test harness binary
                 #set(TARGET_BINARY_NAME CROSS_benchmark_cat_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}})
                 set(TARGET_BINARY_NAME t_harness_crypto_sign_keypair_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./binsec/cross_keypair/test_harness_crypto_sign_keypair.c)
                target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static) 
                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                 set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./bin/cross_keypair)
                 set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                     COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 -D${{CSPRNG_ALGO}}=1 -D${{HASH_ALGO}}=1 -D${{RSDP_VARIANT}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
                 
                 
                 #crypto_sign test harness binary
                 #set(TARGET_BINARY_NAME CROSS_benchmark_cat_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}})
                 set(TARGET_BINARY_NAME t_harness_crypto_sign_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./binsec/cross_sign/test_harness_crypto_sign.c)
                 target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                 set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./bin/cross_sign)  
                 set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                     COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 -D${{CSPRNG_ALGO}}=1 -D${{HASH_ALGO}}=1 -D${{RSDP_VARIANT}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
                 
            endforeach(optimiz_target)
        endforeach(RSDP_VARIANT)
    endforeach(category)
    '''
    with open(cmake_lists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content))



def init_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,add_includes):
    opt_src_folder = create_path_to_optimization_src_folder(signature_type,candidate,optimized_imp_folder,src_folder)
    binsec_folder_full_path = opt_src_folder+'/'+binsec_folder
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
    initialize_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes)
    cmakelists = opt_src_folder+'/'+'CMakeLists.txt'
    cmake_cross(cmakelists)


def init_compile_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,build_folder):
    add_includes = []
    init_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,add_includes)
    build_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+build_folder
    if not os.path.isdir(build_folder_full_path):
        cmd = ["mkdir","-p",build_folder_full_path]
        subprocess.call(cmd, stdin = sys.stdin)
    compile_with_cmake(build_folder_full_path)



def run_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,build_folder,depth):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    build_folder_full_path = optimized_imp_folder_full_path+'/'+build_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
    path_to_binary_files = build_folder_full_path+'/'+"bin"
    #run crypto_sign_keypair
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    path_to_keypair_bin_files = path_to_binary_files+'/'+binsec_keypair_folder_basename
    #run crypto_sign
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    cfg_file_sign = find_ending_pattern(binsec_sign_folder,cfg_pattern)
    path_to_sign_bin_files = path_to_binary_files+'/'+binsec_sign_folder_basename
    run_nist_signature_candidate(binsec_keypair_folder,binsec_sign_folder,path_to_keypair_bin_files,path_to_sign_bin_files,depth)



def compile_run_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,build_folder,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,build_folder)
        run_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,build_folder,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,build_folder)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_cross(binsec_folder,signature_type,candidate,optimized_imp_folder,build_folder,depth)




#========================================== MULTIVARIATE ==================================================================
#=======================================================================================================================



#========================================== OTHER ======================================================================
#=======================================================================================================================

#========================================== preon ======================================================================

def preon_subfolder_parser(subfolder):
    subfold_basename = os.path.basename(subfolder)
    subfold_basename_split = subfold_basename.split('Preon')
    security_level_labeled = subfold_basename_split[-1]
    security_level = security_level_labeled[:3]
    return security_level,security_level_labeled




def makefile_preon(path_to_makefile_folder,subfolder):
    security_level,security_level_labeled = preon_subfolder_parser(subfolder)
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f''' 
    CC = cc
    CFLAGS := ${{CFLAGS}} -DUSE_PREON{security_level_labeled} -DAES{security_level}=1 -DUSE_PRNG -O3
    LFLAGS := ${{LFLAGS}} -lm -lssl -lcrypto
    
    BINSEC_STATIC_FLAG  = -static
    DEBUG_G_FLAG = -g
    BASE_DIR = ../../../{subfolder}
    
    
    EXECUTABLE_KEYPAIR	    = preon_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = preon_sign/test_harness_crypto_sign

    
    SRC_FILES := $(filter-out  $(BASE_DIR)/PQCgenKAT_sign.c ,$(wildcard $(BASE_DIR)/*.c))
    
    
    all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    
    
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(SRC_FILES)
    \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG)  -o $@ $(SRC_FILES) $< $(LFLAGS)
    
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(SRC_FILES)
    \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -o $@ $(SRC_FILES) $< $(LFLAGS)
    
    
    %.o: %.c
    \t@$(CC) $(CFLAGS) -c $< -o $@
    
    .PHONY: clean  
    
    clean:
    \t@rm -f $(BASE_DIR)/*.o 
    \t@rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))





def init_compile_preon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    subfolder_src_files = ""
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_preon(path_to_makefile_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)



def run_preon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_preon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_preon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_preon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_preon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_preon(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)




#=========================================  LESS =======================================================================



def cmake_less(cmake_lists):
    cmake_file_content = f'''
    cmake_minimum_required(VERSION 3.9.4)
    project(LESS C)

    # build type can be case-sensitive!
    string(TOUPPER "${{CMAKE_BUILD_TYPE}}" UPPER_CMAKE_BUILD_TYPE)
    
    set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -Wsign-conversion -Wno-strict-prototypes")
    
    include(CheckCCompilerFlag)
    unset(COMPILER_SUPPORTS_MARCH_NATIVE CACHE)
    check_c_compiler_flag(-march=native COMPILER_SUPPORTS_MARCH_NATIVE)
    
    include(CheckIPOSupported)
    check_ipo_supported(RESULT lto_supported OUTPUT error)
    
    if(UPPER_CMAKE_BUILD_TYPE MATCHES DEBUG)
        message(STATUS "Building in Debug mode!")
    else() # Release, RELEASE, MINSIZEREL, etc
        set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -mtune=native -O3 -g")   
        if(COMPILER_SUPPORTS_MARCH_NATIVE)
            set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -march=native")
        endif()
        if(lto_supported)
            message(STATUS "IPO / LTO enabled")
            set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
        endif()
    endif()
    
    option(COMPRESS_CMT_COLUMNS "Enable COMPRESS_CMT_COLUMNS to compress commitment in SG and VY before hashing (reduces SHA-3 permutaitons by 12.5%, but adds overhead of encoding)" OFF)
    if(COMPRESS_CMT_COLUMNS)
        message(STATUS "COMPRESS_CMT_COLUMNS is enabled")
        add_definitions(-DCOMPRESS_CMT_COLUMNS)
    else()
        message(STATUS "COMPRESS_CMT_COLUMNS is disabled")
    endif()
    unset(COMPRESS_CMT_COLUMNS CACHE)
    
    set(SANITIZE "")
    message(STATUS "Compilation flags:" ${{CMAKE_C_FLAGS}})
    
    set(CMAKE_C_STANDARD 11)
    
    find_library(KECCAK_LIB keccak)
    if(NOT KECCAK_LIB)
        set(STANDALONE_KECCAK 1)
    endif()
    
    # selection of specialized compilation units differing between ref and opt implementations.
    option(AVX2_OPTIMIZED "Use the AVX2 Optimized Implementation. If not set the Reference Implementation will be used." OFF)
    
    set(BASE_DIR  ../Optimized_Implementation) 
    set(HEADERS
            ${{BASE_DIR}}/include/api.h
            ${{BASE_DIR}}/include/codes.h
            ${{BASE_DIR}}/include/fips202.h
            ${{BASE_DIR}}/include/fq_arith.h
            ${{BASE_DIR}}/include/keccakf1600.h
            ${{BASE_DIR}}/include/LESS.h
            ${{BASE_DIR}}/include/monomial_mat.h
            ${{BASE_DIR}}/include/parameters.h
            ${{BASE_DIR}}/include/rng.h
            ${{BASE_DIR}}/include/seedtree.h
            ${{BASE_DIR}}/include/sha3.h
            ${{BASE_DIR}}/include/utils.h
            )
    
    if(STANDALONE_KECCAK)
        message(STATUS "Employing standalone SHA-3")
        set(KECCAK_EXTERNAL_LIB "")
        set(KECCAK_EXTERNAL_ENABLE "")
        list(APPEND COMMON_SOURCES ${{BASE_DIR}}/lib/keccakf1600.c)
        list(APPEND COMMON_SOURCES ${{BASE_DIR}}/lib/fips202.c)
    else()
        message(STATUS "Employing libkeccak")
        set(KECCAK_EXTERNAL_LIB keccak)
        set(KECCAK_EXTERNAL_ENABLE "-DSHA_3_LIBKECCAK")
    endif()
    
    
    set(SOURCES
            ${{COMMON_SOURCES}}
            ${{BASE_DIR}}/lib/codes.c
            ${{BASE_DIR}}/lib/LESS.c
            ${{BASE_DIR}}/lib/monomial.c
            ${{BASE_DIR}}/lib/rng.c
            ${{BASE_DIR}}/lib/seedtree.c
            ${{BASE_DIR}}/lib/utils.c
            ${{BASE_DIR}}/lib/sign.c
            )
    
    
    foreach(category RANGE 1 5 2)
        if(category EQUAL 1)
            set(PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE)
        else()
            set(PARAM_TARGETS SIG_SIZE PK_SIZE)
        endif()
        foreach(optimiz_target ${{PARAM_TARGETS}})
            # settings for benchmarking binary
    
            set(TEST_HARNESS ./binsec/less_keypair/test_harness_crypto_sign_keypair.c ./binsec/less_sign/test_harness_crypto_sign.c)
            #Test harness for crypto_sign_keypair
            #foreach(t_harness ${{TEST_HARNESS}})
            #set(TARGET_BINARY_NAME ${{t_harness}}_${{category}}_${{optimiz_target}})
            set(TARGET_BINARY_NAME t_harness_crypto_sign_keypair_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./binsec/less_keypair/test_harness_crypto_sign_keypair.c)
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./bin/less_keypair)
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
            #Test harness for crypto_sign
            set(TARGET_BINARY_NAME t_harness_crypto_sign_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./binsec/less_sign/test_harness_crypto_sign.c)   
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./bin/less_sign) 
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}}")
    
            #endforeach(t_harness)
        endforeach(optimiz_target)
    endforeach(category)
    '''
    with open(cmake_lists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content))



def init_compile_less(binsec_folder,signature_type,candidate,optimized_imp_folder,abs_path_api,abs_path_sign,build_folder):
    add_includes = []
    opt_subfolder = ""
    src_folder = ""
    init_nist_signature_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_subfolder,src_folder,abs_path_api,abs_path_sign,add_includes)
    opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    cmakelists = opt_src_folder+'/'+'CMakeLists.txt'
    cmake_less(cmakelists)
    build_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+build_folder
    if not os.path.isdir(build_folder_full_path):
        cmd = ["mkdir","-p",build_folder_full_path]
        subprocess.call(cmd, stdin = sys.stdin)
    compile_with_cmake(build_folder_full_path)


def run_less(binsec_folder,signature_type,candidate,optimized_imp_folder,build_folder,depth):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    build_folder_full_path = optimized_imp_folder_full_path+'/'+build_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    path_to_binary_files = build_folder_full_path+'/'+"bin"
    path_to_keypair_bin_files = path_to_binary_files+'/'+binsec_keypair_folder_basename
    path_to_sign_bin_files = path_to_binary_files+'/'+binsec_sign_folder_basename
    run_nist_signature_candidate(binsec_keypair_folder,binsec_sign_folder,path_to_keypair_bin_files,path_to_sign_bin_files,depth)




def compile_run_less(binsec_folder,signature_type,candidate,optimized_imp_folder,abs_path_api,abs_path_sign,build_folder,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_less(binsec_folder,signature_type,candidate,optimized_imp_folder,abs_path_api,abs_path_sign,build_folder)
        run_less(binsec_folder,signature_type,candidate,optimized_imp_folder,build_folder,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_less(binsec_folder,signature_type,candidate,optimized_imp_folder,abs_path_api,abs_path_sign,build_folder)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_less(binsec_folder,signature_type,candidate,optimized_imp_folder,build_folder,depth)




#=========================================  PQSIGRM ====================================================================
#=======================================================================================================================

def makefile_pqsigRM(path_to_makefile_folder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    CFILES := $(shell find ../src -name '*.c' | sed -e 's/\.c/\.o/')
    BINSEC_STATIC_FLAGS = -static
    
    OBJS = ${{CFILES}}
    
    
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: test_harness_crypto_sign_keypair test_harness_crypto_sign
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    
    test_harness_crypto_sign_keypair: ${{OBJS}} pqsigRM_keypair/test_harness_crypto_sign_keypair.c
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $@ $^ $(LIBFLAGS)
    
    test_harness_crypto_sign: ${{OBJS}} pqsigRM_sign/test_harness_crypto_sign.c
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $@ $^ $(LIBFLAGS)
    
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h  
    
    clean:
    \tcd ../src; rm -f *.o; cd ..
    \trm -f *.o
    \trm -f  test_harness_crypto_sign_keypair test_harness_crypto_sign
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def init_compile_pqsigRM(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    opt_subfolder = "pqsigrm613"
    path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+src_folder+'/'+binsec_folder
    init_nist_signature_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_subfolder,src_folder,api,sign,add_includes)
    makefile_pqsigRM(path_to_makefile_folder)
    compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)




def run_nist_signature_candidate_compiled_with_cmake(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,build_folder,depth):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if not src_folder == "":
        optimized_imp_folder_full_path+='/'+src_folder
    build_folder_full_path = optimized_imp_folder_full_path+'/'+build_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
    path_to_binary_files = build_folder_full_path+'/'+"bin"
    #run crypto_sign_keypair
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    path_to_keypair_bin_files = path_to_binary_files+'/'+binsec_keypair_folder_basename
    #run crypto_sign
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    cfg_file_sign = find_ending_pattern(binsec_sign_folder,cfg_pattern)
    path_to_sign_bin_files = path_to_binary_files+'/'+binsec_sign_folder_basename
    run_nist_signature_candidate(binsec_keypair_folder,binsec_sign_folder,path_to_keypair_bin_files,path_to_sign_bin_files,depth)


def run_nist_signature_candidate_compiled_with_makefile(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,depth):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if not src_folder == "":
        optimized_imp_folder_full_path+='/'+src_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
    #run crypto_sign_keypair
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_keypair_folder = binsec_folder_full_path+'/'+binsec_keypair_folder_basename
    path_to_binary_keypair = binsec_folder_full_path+'/test_harness_crypto_sign_keypair'
    stats_file_keypair = binsec_folder_full_path+'/'+binsec_keypair_folder_basename+'/keypair.toml'
    output_file_keypair = binsec_folder_full_path+'/'+binsec_keypair_folder_basename+'/keypair_output.txt'
    cfg_file_keypair =  find_ending_pattern(binsec_keypair_folder,cfg_pattern)
    print("------Running binary file: {} ---- ".format(path_to_binary_keypair))
    run_binsec(path_to_binary_keypair,cfg_file_keypair,stats_file_keypair,output_file_keypair,depth)
    #run crypto_sign
    binsec_sign_folder_basename = candidate+'_sign'
    binsec_sign_folder = binsec_folder_full_path+'/'+binsec_sign_folder_basename
    path_to_binary_sign = binsec_folder_full_path+'/test_harness_crypto_sign'
    stats_file_sign = binsec_folder_full_path+'/'+binsec_sign_folder_basename+'/sign.toml'
    output_file_sign = binsec_folder_full_path+'/'+binsec_sign_folder_basename+'/sign_output.txt'
    cfg_file_sign =  find_ending_pattern(binsec_sign_folder,cfg_pattern)
    print("------Running binary file: {} ---- ".format(path_to_binary_sign))
    run_binsec(path_to_binary_sign,cfg_file_sign,stats_file_sign,output_file_sign,depth)



def run_pqsigRM(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,depth):
    run_nist_signature_candidate_compiled_with_makefile(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,depth)



def compile_run_pqsigRM(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_pqsigRM(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign)
        run_pqsigRM(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_pqsigRM(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_pqsigRM(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,depth)




#=========================================  snova ======================================================================
def makefile_snova(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native
    
    BINSEC_STATIC_FLAGS = -static
    DEBUG_G_FLAG = -g
    BASE_DIR = ../../{subfolder}
    
    
    
    EXECUTABLE_KEYPAIR	    = snova_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = snova_sign/test_harness_crypto_sign
    
    BUILD_OUT_PATH = $(BASE_DIR)/build/
    
    OLIST = $(BUILD_OUT_PATH)rng.o $(BUILD_OUT_PATH)snova.o
    
    
    # snova params
    SNOVA_V = 24
    SNOVA_O = 5
    SNOVA_L = 4
    SK_IS_SEED = 0 # 0: sk = ssk; 1: sk = esk
    TURBO = 1
    CRYPTO_ALGNAME = "SNOVA_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L)"
    SNOVA_PARAMS = -D v_SNOVA=$(SNOVA_V) -D o_SNOVA=$(SNOVA_O) -D l_SNOVA=$(SNOVA_L) -D sk_is_seed=$(SK_IS_SEED) -D CRYPTO_ALGNAME=$(CRYPTO_ALGNAME) -D TURBO=$(TURBO)
    
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    $(BASE_DIR)/build/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    
    $(EXECUTABLE_KEYPAIR): $(BASE_DIR)/build/sign.o
    \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BASE_DIR)/build/sign.o $(EXECUTABLE_KEYPAIR).c -o $(EXECUTABLE_KEYPAIR) -lcrypto
        
    
    $(EXECUTABLE_SIGN): $(BASE_DIR)/build/sign.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BASE_DIR)/build/sign.o $(EXECUTABLE_SIGN).c -o $(EXECUTABLE_SIGN) -lcrypto
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def init_compile_snova(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_build_folder = ""
    path_to_cmakelist_file = ""
    add_includes = []
    subfolder_src_files = ""
    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir, \
                                            subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_snova(path_to_makefile_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)



def run_snova(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_snova(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_snova(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_snova(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_snova(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_snova(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)



#=========================================  QR-UOV =====================================================================
def run_qrUOV_makefile(path_to_qrUOV_makefile_folder):
    cwd = os.getcwd()
    os.chdir(path_to_qrUOV_makefile_folder)
    cwd1 = os.getcwd()
    cmd = ["make"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)



def main_makefile_qrUOV(path_to_binsec_folder,subfolder):
    path_to_makefile = path_to_binsec_folder+'/Makefile'
    makefile_content = f'''
    platform := portable64
    
    BASE_DIR = ../..
    
    
    subdirs :={subfolder}
    
      
    .PHONY: all clean $(subdirs)
    
    #all: $(subdirs) 
    
    
    $(subdirs): $(BASE_DIR)/qruov_config.src
    #\tmkdir -p $@/$(platform)
    \tgrep $@ $(BASE_DIR)/qruov_config.src > $(platform)/qruov_config.txt 
    \tsh -c "cd $(platform) ; ln -s ../$(BASE_DIR)/$(platform)/* . || true"
    \tsh -c "cd $(platform) ; cp -R makefile_folder/Makefile . || true"
    #\tsh -c "cd $(platform) ; rm -r makefile_folder || true"
    \t$(MAKE) -C $(platform)   
    
    clean:
    \trm -rf $(subdirs)
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))



def makefile_qruov(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC=gcc
    CFLAGS=-O3 -fomit-frame-pointer -Wno-unused-result -Wno-aggressive-loop-optimizations -I. -fopenmp # -DQRUOV_HASH_LEGACY # -ggdb3 
    LDFLAGS=-lcrypto -Wl,-Bstatic -lcrypto -Wl,-Bdynamic -lm
    
    BINSEC_STATIC_FLAG  = -static
    DEBUG_G_FLAG = -g
    BASE_DIR = ../../{subfolder}/portable64
    
    EXECUTABLE_KEYPAIR	    = ../qr_uov_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = ../qr_uov_sign/test_harness_crypto_sign
    
    
    OBJS=$(BASE_DIR)/Fql.o $(BASE_DIR)/mgf.o  $(BASE_DIR)/qruov.o $(BASE_DIR)/rng.o $(BASE_DIR)/sign.o $(BASE_DIR)/matrix.o
    
    .SUFFIXES:
    .SUFFIXES: .rsp .req .diff .c .o .h
    
    .PHONY: all clean
    
    all: $(BASE_DIR)/qruov_config.h $(BASE_DIR)/api.h 
    #\t./PQCgenKAT_sign
        
    
    $(BASE_DIR)/qruov_config.h: $(BASE_DIR)/qruov_config_h_gen.c
    \t${{CC}} @$(BASE_DIR)/qruov_config.txt -DQRUOV_PLATFORM=portable64 -DQRUOV_CONFIG_H_GEN ${{CFLAGS}} ${{LDFLAGS}} $(BASE_DIR)/qruov_config_h_gen.c
    \t./$(BASE_DIR)/a.out > $(BASE_DIR)/qruov_config.h
    \trm $(BASE_DIR)/a.out
    
    $(BASE_DIR)/api.h: $(BASE_DIR)/api_h_gen.c
    \t${{CC}} -DAPI_H_GEN ${{CFLAGS}} ${{LDFLAGS}} $(BASE_DIR)/api_h_gen.c
    \t./$(BASE_DIR)/a.out > $(BASE_DIR)/api.h
    \trm $(BASE_DIR)/a.out
    
    clean:
    \trm -f $(BASE_DIR)/PQCgenKAT_sign PQCsignKAT_*.req $(BASE_DIR)/PQCsignKAT_*.rsp $(BASE_DIR)/${{OBJS}}
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def custom_makefile_qruov(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC=gcc
    CFLAGS=-O3 -fomit-frame-pointer -Wno-unused-result -Wno-aggressive-loop-optimizations -I. -fopenmp # -DQRUOV_HASH_LEGACY # -ggdb3 
    LDFLAGS=-lcrypto -Wl,-Bstatic -lcrypto -Wl,-Bdynamic -lm
    
    BINSEC_STATIC_FLAG  = -static
    DEBUG_G_FLAG = -g
    BASE_DIR = ../../../{subfolder}/portable64
    
    EXECUTABLE_KEYPAIR	    = ../../qr_uov_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = ../../qr_uov_sign/test_harness_crypto_sign
    
    
    OBJS=$(BASE_DIR)/Fql.o $(BASE_DIR)/mgf.o  $(BASE_DIR)/qruov.o $(BASE_DIR)/rng.o $(BASE_DIR)/sign.o $(BASE_DIR)/matrix.o
    
    .PHONY: all clean
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    $(EXECUTABLE_KEYPAIR): Makefile $(EXECUTABLE_KEYPAIR).c ${{OBJS}}
    \t${{CC}} ${{OBJS}} ${{CFLAGS}} $(BINSEC_STATIC_FLAG) ${{LDFLAGS}} $(EXECUTABLE_KEYPAIR).c -o $@

    $(EXECUTABLE_SIGN): Makefile $(EXECUTABLE_SIGN).c ${{OBJS}}
    \t${{CC}} ${{OBJS}} ${{CFLAGS}} $(BINSEC_STATIC_FLAG) ${{LDFLAGS}} $(EXECUTABLE_SIGN).c -o $@
    
    clean:
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))



def custom_initialize_qrUOV_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,api,sign,add_includes):
    create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
    test_harness_keypair_basename = 'test_harness_crypto_sign_keypair.c'
    test_harness_sign_basename = 'test_harness_crypto_sign.c'
    cfg_file_keypair = binsec_keypair_folder+'/cfg_file.cfg'
    cfg_content_keypair(cfg_file_keypair)
    test_harness_keypair = binsec_keypair_folder+'/'+test_harness_keypair_basename
    api = '"../portable64/api.h"'
    test_harness_content_keypair(test_harness_keypair,api,sign,add_includes)
    abs_path_to_api_or_sign = f'{binsec_folder_full_path}/qruov1q7L10v740m100/portable64/api.h'
    args_types,args_names =  sign_find_args_types_and_names(abs_path_to_api_or_sign)
    cfg_file_sign = binsec_sign_folder+'/cfg_file.cfg'
    crypto_sign_args_names = args_names
    sign_configuration_file_content(cfg_file_sign,crypto_sign_args_names)
    test_harness_sign = binsec_sign_folder+'/'+test_harness_sign_basename
    api = '"../portable64/api.h"'
    sign_test_harness_content(test_harness_sign,api,sign,add_includes,args_types,args_names)



def initiate_qruov_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    add_includes = []
    opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    binsec_folder_full_path = opt_src_folder+'/'+binsec_folder
    binsec_keypair_folder_basename = candidate+'_keypair'
    binsec_sign_folder_basename = candidate+'_sign'
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    if binsec_folder in opt_src_folder_list_dir:
        opt_src_folder_list_dir.remove(binsec_folder)
    for subfold in opt_src_folder_list_dir:
        binsec_keypair_folder =""
        binsec_sign_folder = ""
        path_to_subfolder = binsec_folder_full_path+'/'+subfold
        binsec_keypair_folder = binsec_folder_full_path+'/'+subfold+'/'+binsec_keypair_folder_basename
        binsec_sign_folder = binsec_folder_full_path+'/'+subfold+'/'+binsec_sign_folder_basename
        create_binsec_folders(binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder)
        portable_makefile_to_be_removed_folder = binsec_folder_full_path+'/'+subfold+'/'+"portable64"+'/makefile_folder'
        cmd = ["mkdir","-p",portable_makefile_to_be_removed_folder]
        subprocess.call(cmd, stdin = sys.stdin)
        makefile_qruov(portable_makefile_to_be_removed_folder,subfold)
        main_makefile_qrUOV(path_to_subfolder,subfold)
        run_qrUOV_makefile(path_to_subfolder)
        custom_initialize_qrUOV_candidate(opt_src_folder,binsec_folder_full_path,binsec_keypair_folder,binsec_sign_folder,abs_path_api,abs_path_sign,add_includes)
        custom_makefile_qruov(portable_makefile_to_be_removed_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,portable_makefile_to_be_removed_folder,path_to_build_folder)
        cmd = ["rm","-r",portable_makefile_to_be_removed_folder]
        subprocess.call(cmd, stdin = sys.stdin)


def run_qrUOV(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_qrUOV(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        initiate_qruov_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_qrUOV(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        initiate_qruov_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_qrUOV(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)



#=========================================  SQUIRRELS =====================================================================

def squirrels_level(subfolder):
    subfolder_split = subfolder.split("-")
    level_roman_digest = subfolder_split[-1]
    level = 0
    if level_roman_digest == "I":
        level = 1
    elif level_roman_digest == "II":
        level = 2
    elif level_roman_digest == "III":
        level = 3
    elif level_roman_digest == "IV":
        level = 4
    else:
        level = 5
    return level


def makefile_squirrels(path_to_makefile_folder,subfolder):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    level = squirrels_level(subfolder)
    makefile_content = f'''
    .POSIX:

    NIST_LEVEL?={level}
    
    BASE_DIR = ../../{subfolder}
    CC = gcc
    CFLAGS = -W -Wall -O3 -march=native -I../../../lib/build/mpfr/include -I../../../lib/build/mpfr/include -I../../../lib/build/gmp/include -I../../../lib/build/flint/include/flint -I../../../lib/build/fplll/include \
        -DSQUIRRELS_LEVEL=$(NIST_LEVEL)
    LD = gcc -v
    LDFLAGS = 
    
    BINSEC_STATIC_FLAGS     = -static
    DEBUG_G_FLAG            = -g
    EXECUTABLE_KEYPAIR	    = squirrels_keypair/test_harness_crypto_sign_keypair
    EXECUTABLE_SIGN		    = squirrels_sign/test_harness_crypto_sign
    
    LIBSRPATH = '$$ORIGIN'../../../../../lib/build
    LIBS = -lm \
    \t-L../../../lib/build/mpfr/lib -Wl,-rpath,$(LIBSRPATH)/mpfr/lib -lmpfr \
    \t-L../../../lib/build/gmp/lib -Wl,-rpath,$(LIBSRPATH)/gmp/lib -lgmp \
    \t-L../../../lib/build/flint/lib -Wl,-rpath,$(LIBSRPATH)/flint/lib -lflint \
    \t-L../../../lib/build/fplll/lib -Wl,-rpath,$(LIBSRPATH)/fplll/lib -lfplll \
    \t-lstdc++
    
    OBJ1 = $(BASE_DIR)/build/codec.o $(BASE_DIR)/build/common.o $(BASE_DIR)/build/keygen_lll.o $(BASE_DIR)/build/keygen.o  $(BASE_DIR)/build/minors.o $(BASE_DIR)/build/nist.o $(BASE_DIR)/build/normaldist.o $(BASE_DIR)/build/param.o $(BASE_DIR)/build/sampler.o $(BASE_DIR)/build/shake.o $(BASE_DIR)/build/sign.o $(BASE_DIR)/build/vector.o
    
    
    HEAD1 = $(BASE_DIR)/api.h $(BASE_DIR)/fpr.h $(BASE_DIR)/inner.h $(BASE_DIR)/param.h
    
    
    all: $(BASE_DIR)/lib $(BASE_DIR)/build $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    
    $(BASE_DIR)/lib:
    \tmake -C ../../../lib 
    
    $(BASE_DIR)/build:
    \t-mkdir $(BASE_DIR)/build
    
    clean:
    \t-rm -f  $(OBJ1)  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    
    
   
    $(BASE_DIR)/build/codec.o: $(BASE_DIR)/codec.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/codec.o $(BASE_DIR)/codec.c
    
    $(BASE_DIR)/build/common.o: $(BASE_DIR)/common.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/common.o $(BASE_DIR)/common.c
    
    $(BASE_DIR)/build/keygen_lll.o: $(BASE_DIR)/keygen_lll.cpp $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/keygen_lll.o $(BASE_DIR)/keygen_lll.cpp
    
    $(BASE_DIR)/build/keygen.o: $(BASE_DIR)/keygen.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/keygen.o $(BASE_DIR)/keygen.c
    
    $(BASE_DIR)/build/minors.o: $(BASE_DIR)/minors.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/minors.o $(BASE_DIR)/minors.c
    
    
    $(BASE_DIR)/build/normaldist.o: $(BASE_DIR)/normaldist.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/normaldist.o $(BASE_DIR)/normaldist.c
    
    $(BASE_DIR)/build/param.o: $(BASE_DIR)/param.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/param.o $(BASE_DIR)/param.c
    
    $(BASE_DIR)/build/sampler.o: $(BASE_DIR)/sampler.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/sampler.o $(BASE_DIR)/sampler.c
    
    $(BASE_DIR)/build/shake.o: $(BASE_DIR)/shake.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/shake.o $(BASE_DIR)/shake.c
    
    $(BASE_DIR)/build/sign.o: $(BASE_DIR)/sign.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c
    
    $(BASE_DIR)/build/vector.o: $(BASE_DIR)/vector.c $(HEAD1)
    \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/vector.o $(BASE_DIR)/vector.c
    

    
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(HEAD1) $(BASE_DIR)/api.h 
    \t$(CC) $(CFLAGS) -I . -c -o $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_KEYPAIR).c 
    
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(HEAD1) $(BASE_DIR)/api.h 
    \t$(CC) $(CFLAGS) -I . -c -o $(EXECUTABLE_SIGN)  $(EXECUTABLE_SIGN).c 
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))

def init_compile_squirrels(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign):
    path_to_build_folder = ""
    path_to_cmakelist_file = ""
    subfolder_src_files = ""
    add_includes = []

    subfolders_list = opt_src_folder_list_dir
    if binsec_folder in subfolders_list:
        subfolders_list.remove(binsec_folder)
    for subfold in subfolders_list:
        init_nist_signature_candidate_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir, \
                                            subfolder_src_files,abs_path_api,abs_path_sign,add_includes)
        path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+binsec_folder+'/'+subfold
        makefile_squirrels(path_to_makefile_folder,subfold)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)



def run_squirrels(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth):
    run_nist_signature_candidate_compiled_with_makefile_type2(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)


def compile_run_squirrels(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign,depth,compile_yes_or_no,run_yes_or_no):
    if 'y' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        init_compile_squirrels(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
        run_squirrels(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)
    elif 'y' in compile_yes_or_no.lower() and 'n' in run_yes_or_no.lower():
        init_compile_squirrels(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,abs_path_api,abs_path_sign)
    if 'n' in compile_yes_or_no.lower() and 'y' in run_yes_or_no.lower():
        run_squirrels(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth)





#======================================= CLI: use argparse module ======================================================
#=======================================================================================================================

# Create a parser
parser = argparse.ArgumentParser(prog="NIST-Signature" ,description="Constant-timeness Analysis with Binsec/Rel")
# Create a sub-parser
subparser = parser.add_subparsers(dest='binsec_test')

# Create a parser for every function in the sub-parser namespace

#********************** List of candidates *******************************************************************************

qruov_init_compile_run = subparser.add_parser('compile_run_qruov', help='qr_uov: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

snova_init_compile_run = subparser.add_parser('compile_run_snova', help='snova: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

#
cross_init_compile_run = subparser.add_parser('compile_run_cross', help='cross: create test harness, configuration files,\
                                     and CMakeLists.txt for the crypto_sign_keypair and crypto_sign functions (and run binsec on them)')
#
pqsigRM_init_compile_run = subparser.add_parser('compile_run_pqsigRM', help='pqsigRM: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

less_init_compile_run = subparser.add_parser('compile_run_less', help='less: create test harness, configuration files,\
                                    and required CMakeLists.txt to compile   (and) run binsec )')

aimer_init_compile_run = subparser.add_parser('compile_run_aimer', help='aimer: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

faest_init_compile_run = subparser.add_parser('compile_run_faest', help='faest: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

ascon_init_compile_run = subparser.add_parser('compile_run_ascon', help='ascon: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

sphincs_init_compile_run = subparser.add_parser('compile_run_sphincs', help='sphincs: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

mirith_init_compile_run = subparser.add_parser('compile_run_mirith', help='mirith: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

mira_init_compile_run = subparser.add_parser('compile_run_mira', help='mira: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

mqom_init_compile_run = subparser.add_parser('compile_run_mqom', help='mqom: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

perk_init_compile_run = subparser.add_parser('compile_run_perk', help='perk: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')

ryde_init_compile_run = subparser.add_parser('compile_run_ryde', help='ryde: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')


preon_init_compile_run = subparser.add_parser('compile_run_preon', help='preon: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')


squirrels_init_compile_run = subparser.add_parser('compile_run_squirrels', help='squirrels: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')


#===================== QR_UOV ============================================================================================

squirrels_opt_folder = "lattice/squirrels/Optimized_Implementation"
squirrels_default_list_of_folders = os.listdir(squirrels_opt_folder)
if 'binsec' in squirrels_default_list_of_folders:
    squirrels_default_list_of_folders.remove('binsec')

squirrels_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
squirrels_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='lattice')
squirrels_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='squirrels')
squirrels_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
squirrels_init_compile_run.add_argument('--list_of_folders', nargs='+', default=squirrels_default_list_of_folders)
squirrels_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../')
squirrels_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
squirrels_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
squirrels_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
squirrels_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')






#===================== QR_UOV ============================================================================================
qruov_default_list_of_folders = ["qruov1q7L10v740m100","qruov1q31L3v165m60", "qruov1q31L10v600m70", "qruov1q127L3v156m54",
                                 "qruov3q7L10v1100m140", "qruov3q31L3v246m87",  "qruov3q31L10v890m100",  "qruov3q127L3v228m78",
                                 "qruov5q7L10v1490m190", "qruov5q31L3v324m114", "qruov5q31L10v1120m120", "qruov5q127L3v306m105"]


qruov_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
qruov_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='multivariate')
qruov_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='qr_uov')
qruov_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='QR_UOV/Optimized_Implementation')
qruov_init_compile_run.add_argument('--list_of_folders', nargs='+', default=qruov_default_list_of_folders)
qruov_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='"../../binsec/qruov1q7L10v740m100/portable64/api.h"')
qruov_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
qruov_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
qruov_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
qruov_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')





#===================== snova ============================================================================================
snova_opt_folder = "multivariate/snova/Optimized_Implementation"
snova_default_list_of_folders = os.listdir(snova_opt_folder)
if 'binsec' in snova_default_list_of_folders:
    snova_default_list_of_folders.remove('binsec')

snova_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
snova_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='multivariate')
snova_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='snova')
snova_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
snova_init_compile_run.add_argument('--list_of_folders', nargs='+', default=snova_default_list_of_folders)
snova_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../')
snova_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
snova_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
snova_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
snova_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')


#===================== LESS ============================================================================================
less_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
less_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='code')
less_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='less')
less_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
less_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default="")
less_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default='"../../include/api.h"')
less_init_compile_run.add_argument('--build_folder', '-build', dest='build',default="build")
less_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
less_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
less_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')



#===================== CROSS ============================================================================================
# Add arguments (inputs) of the function
#===================== COMMENTS: Reference_Implementation folder has to be taken into account
cross_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
cross_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
cross_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='cross')
cross_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
cross_init_compile_run.add_argument('--src_folder', '-src',dest='source',type=str,default='')
cross_init_compile_run.add_argument('--api', '-api',dest='api',type=str, default='"../../../Reference_Implementation/include/api.h"')
cross_init_compile_run.add_argument('--sign', '-sign', dest='sign',type=str,default="")
cross_init_compile_run.add_argument('--build_folder', '-build', dest='build',default="build")
cross_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
cross_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
cross_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')


#
#
#
# #===================== pqsigRM ============================================================================================
# # Add arguments (inputs) of the function
# #===================== COMMENTS: Reference_Implementation folder has to be taken into account
pqsigRM_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
pqsigRM_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='code')
pqsigRM_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='pqsigRM')
pqsigRM_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
pqsigRM_init_compile_run.add_argument('--src_folder', '-src',dest='source',type=str,default='pqsigrm613')
pqsigRM_init_compile_run.add_argument('--api', '-api',dest='api',type=str, default='"../../src/api.h"')
pqsigRM_init_compile_run.add_argument('--sign', '-sign', dest='sign',type=str,default="")
pqsigRM_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
pqsigRM_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
pqsigRM_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')






#===================== Preon ============================================================================================
preon_opt_folder = "other/preon/Optimized_Implementation"
preon_default_128_192_256_folders = os.listdir(preon_opt_folder)
if 'binsec' in preon_default_128_192_256_folders:
    preon_default_128_192_256_folders.remove('binsec')

preon_128 = preon_default_128_192_256_folders[0]
preon_192 = preon_default_128_192_256_folders[1]
preon_256 = preon_default_128_192_256_folders[2]
preon_default_list_of_folders = []
abs_path_to_preon_128 = preon_opt_folder+"/"+preon_128
abs_path_to_ascon_192 = preon_opt_folder+"/"+preon_192
abs_path_to_ascon_256 = preon_opt_folder+"/"+preon_256
preon_default_list_of_folders.extend([preon_128+"/"+subfold for subfold in os.listdir(abs_path_to_preon_128)])
preon_default_list_of_folders.extend([preon_192+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_192)])
preon_default_list_of_folders.extend([preon_256+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_256)])


preon_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
preon_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='other')
preon_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='preon')
preon_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
preon_init_compile_run.add_argument('--list_of_folders', nargs='+', default=preon_default_list_of_folders)
preon_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../../')
preon_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
preon_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
preon_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
preon_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')




#===================== AIMer ============================================================================================
aimer_opt_folder = "symmetric/aimer/AIMer_submission/Optimized_Implementation"
aimer_default_list_of_folders = os.listdir(aimer_opt_folder)
if 'binsec' in aimer_default_list_of_folders:
    aimer_default_list_of_folders.remove('binsec')

aimer_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
aimer_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='symmetric')
aimer_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='aimer')
aimer_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='AIMer_submission/Optimized_Implementation')
aimer_init_compile_run.add_argument('--list_of_folders', nargs='+', default=aimer_default_list_of_folders)
aimer_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../')
aimer_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
aimer_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
aimer_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
aimer_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')


#===================== faest ============================================================================================
faest_opt_folder = "symmetric/faest/Additional_Implementations/avx2"
faest_default_list_of_folders = os.listdir(faest_opt_folder)
if 'binsec' in faest_default_list_of_folders:
    faest_default_list_of_folders.remove('binsec')

faest_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
faest_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='symmetric')
faest_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='faest')
faest_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Additional_Implementations')
faest_init_compile_run.add_argument('--src_folder', '-src_folder',dest='source',type=str,default='avx2')
faest_init_compile_run.add_argument('--list_of_folders', nargs='+', default=faest_default_list_of_folders)
faest_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../avx2/')
faest_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
faest_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
faest_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
faest_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')


#===================== Ascon_Sign ============================================================================================
ascon_opt_folder = "symmetric/Ascon_sign/Optimized_Implementation"
ascon_default_robust_and_simple_folders = os.listdir(ascon_opt_folder)
ascon_default_robust_and_simple_folders.remove('Readme')
if 'binsec' in ascon_default_robust_and_simple_folders:
    ascon_default_robust_and_simple_folders.remove('binsec')

ascon_robust = ascon_default_robust_and_simple_folders[0]
ascon_simple = ascon_default_robust_and_simple_folders[1]
ascon_default_list_of_folders = []
abs_path_to_ascon_robust = ascon_opt_folder+"/"+ascon_robust
abs_path_to_ascon_simple = ascon_opt_folder+"/"+ascon_simple
ascon_default_list_of_folders.extend([ascon_robust+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_robust)])
ascon_default_list_of_folders.extend([ascon_simple+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_simple)])


ascon_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
ascon_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='symmetric')
ascon_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='Ascon_sign')
ascon_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
ascon_init_compile_run.add_argument('--list_of_folders', nargs='+', default=ascon_default_list_of_folders)
ascon_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../../')
ascon_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
ascon_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
ascon_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
ascon_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')


#===================== Sphincs ============================================================================================
sphincs_opt_folder = "symmetric/sphincs-alpha/Optimized_Implementation"
sphincs_default_list_of_folders = os.listdir(sphincs_opt_folder)
if 'binsec' in sphincs_default_list_of_folders:
    sphincs_default_list_of_folders.remove('binsec')

sphincs_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
sphincs_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='symmetric')
sphincs_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='sphincs-alpha')
sphincs_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
sphincs_init_compile_run.add_argument('--list_of_folders', nargs='+', default=sphincs_default_list_of_folders)
sphincs_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../')
sphincs_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
sphincs_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
sphincs_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
sphincs_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')



#===================== Mirith ==========================================================================================
mirith_opt_folder = "mpc-in-the-head/mirith/Optimized_Implementation"
mirith_default_list_of_folders = os.listdir(mirith_opt_folder)
if 'binsec' in mirith_default_list_of_folders:
    mirith_default_list_of_folders.remove('binsec')


mirith_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
mirith_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
mirith_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='mirith')
mirith_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
mirith_init_compile_run.add_argument('--list_of_folders', nargs='+', default=preon_default_list_of_folders)
mirith_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default="")
mirith_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default='../../../')
mirith_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
mirith_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
mirith_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')





#===================== mira ============================================================================================
mira_opt_folder = "mpc-in-the-head/mira/Optimized_Implementation"
mira_default_list_of_folders = os.listdir(mira_opt_folder)
mira_default_list_of_folders.remove('README.md')
if 'binsec' in mira_default_list_of_folders:
    mira_default_list_of_folders.remove('binsec')


mira_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
mira_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
mira_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='mira')
mira_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
mira_init_compile_run.add_argument('--subfolder_src_files', '-src_folder',dest='source',type=str,default='src')
mira_init_compile_run.add_argument('--list_of_folders', nargs='+', default=faest_default_list_of_folders)
mira_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../')
mira_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
mira_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
mira_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
mira_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')



#===================== mqom ============================================================================================
mqom_opt_folder = "mpc-in-the-head/mqom/Optimized_Implementation"
mqom_default_list_of_folders = os.listdir(mqom_opt_folder)
if 'binsec' in mqom_default_list_of_folders:
    mqom_default_list_of_folders.remove('binsec')


mqom_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
mqom_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
mqom_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='mqom')
mqom_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
mqom_init_compile_run.add_argument('--list_of_folders', nargs='+', default=faest_default_list_of_folders)
mqom_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../')
mqom_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
mqom_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
mqom_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
mqom_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')




#===================== perk ============================================================================================
perk_opt_folder = "mpc-in-the-head/perk/Optimized_Implementation"
perk_default_list_of_folders = os.listdir(perk_opt_folder)
perk_default_list_of_folders.remove('README')
if 'binsec' in perk_default_list_of_folders:
    perk_default_list_of_folders.remove('binsec')


perk_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
perk_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
perk_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='perk')
perk_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
perk_init_compile_run.add_argument('--subfolder_src_files', '-src_folder',dest='source',type=str,default='src')
perk_init_compile_run.add_argument('--list_of_folders', nargs='+', default=faest_default_list_of_folders)
perk_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../')
perk_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
perk_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
perk_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
perk_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')




#===================== ryde ============================================================================================
ryde_opt_folder = "mpc-in-the-head/ryde/Optimized_Implementation"
ryde_default_list_of_folders = os.listdir(ryde_opt_folder)
ryde_default_list_of_folders.remove('README')
if 'binsec' in ryde_default_list_of_folders:
    ryde_default_list_of_folders.remove('binsec')


ryde_init_compile_run.add_argument('--binsec_folder', '-binsec_folder',type=str, default="binsec")
ryde_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
ryde_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='ryde')
ryde_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
ryde_init_compile_run.add_argument('--subfolder_src_files', '-src_folder',dest='source',type=str,default='src')
ryde_init_compile_run.add_argument('--list_of_folders', nargs='+', default=faest_default_list_of_folders)
ryde_init_compile_run.add_argument('--abs_path_api', '-api',dest='api',type=str, default='../../../')
ryde_init_compile_run.add_argument('--abs_path_sign', '-sign', dest='sign',type=str,default="")
ryde_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
ryde_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
ryde_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')





#set all the command-line arguments into the object args
args = parser.parse_args()

if args.binsec_test == "compile_run_squirrels":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_squirrels(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_qruov":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_qrUOV(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_snova":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_snova(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_less":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    abs_path_api = args.api
    abs_path_sign = args.sign
    build_folder = args.build
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_less(binsec_folder,signature_type,candidate,optimization_folder,abs_path_api,abs_path_sign,build_folder,depth,compile,run)
if args.binsec_test == "compile_run_cross":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    src_folder = args.source
    api = args.api
    sign = args.sign
    build_folder = args.build
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_cross(binsec_folder,signature_type,candidate,optimization_folder,src_folder,api,sign,build_folder,depth,compile,run)
if args.binsec_test == "compile_run_pqsigRM":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    src_folder = args.source
    api = args.api
    sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_pqsigRM(binsec_folder,signature_type,candidate,optimization_folder,src_folder,api,sign,depth,compile,run)
if args.binsec_test == "compile_run_preon":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_preon(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_aimer":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_aimer(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_faest":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    src_folder = args.source
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_faest(binsec_folder,signature_type,candidate,optimization_folder,src_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_ascon":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_ascon(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_sphincs":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_sphincs(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_mirith":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_mirith(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_mira":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    subfolder_src_files = args.source
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_mira(binsec_folder,signature_type,candidate,optimization_folder,subfolder_src_files,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_mqom":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_mqom(binsec_folder,signature_type,candidate,optimization_folder,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_perk":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    subfolder_src_files = args.source
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_perk(binsec_folder,signature_type,candidate,optimization_folder,subfolder_src_files,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
if args.binsec_test == "compile_run_ryde":
    binsec_folder = args.binsec_folder
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    subfolder_src_files = args.source
    list_of_folders = args.list_of_folders
    abs_path_api = args.api
    abs_path_sign = args.sign
    depth = args.depth
    compile = args.compile
    run = args.run
    compile_run_ryde(binsec_folder,signature_type,candidate,optimization_folder,subfolder_src_files,list_of_folders,abs_path_api,abs_path_sign,depth,compile,run)
