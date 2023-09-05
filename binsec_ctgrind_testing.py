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



#================== List of src subfolders and generate those subfolders into binsec folder ==========

def list_of_subfolders(folder):
    src_folder_content = os.listdir(folder)
    return src_folder_content

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

# def test_harness_content_keypair(test_harness_file,api,sign,add_includes):
#     with open(test_harness_file, "w") as t_harness_file:
#         t_harness_file.write('#include <stdio.h>\n')
#         t_harness_file.write('#include <stdlib.h>\n')
#         t_harness_file.write('#include <string.h>\n')
#         t_harness_file.write('#include <stdint.h>\n')
#         t_harness_file.write('#include <ctype.h>\n')
#         if not add_includes == []:
#             for include in add_includes:
#                 t_harness_file.write(f'#include {include}\n')
#         if not sign == "":
#             t_harness_file.write(f'#include {sign}\n')
#         if not api == "":
#             t_harness_file.write(f'#include {api}\n')
#         t_harness_file.write('\n\n')
#         t_harness_file.write('uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;\n')
#         t_harness_file.write('uint8_t sk[CRYPTO_SECRETKEYBYTES] ;\n')
#         t_harness_file.write('\n\n')
#         t_harness_file.write('int main(){\n')
#         t_harness_file.write('      int result =  crypto_sign_keypair(pk, sk);\n')
#         t_harness_file.write('      exit(result);\n')
#         t_harness_file.write('}\n')


# def sign_test_harness_content1(test_harness_file,api,sign,add_includes,args_types,args_names):
#     args_types[2] = re.sub("const ","",args_types[2])
#     with open(test_harness_file, "w") as t_harness_file:
#         t_harness_file.write('#include <stdio.h>\n')
#         t_harness_file.write('#include <stdlib.h>\n')
#         t_harness_file.write('#include <string.h>\n')
#         t_harness_file.write('#include <stdint.h>\n')
#         t_harness_file.write('#include <ctype.h>\n')
#         if not add_includes == []:
#             for include in add_includes:
#                 t_harness_file.write(f'#include {include}\n')
#         if not sign == "":
#             t_harness_file.write(f'#include {sign}\n')
#         if not api == "":
#             t_harness_file.write(f'#include {api}\n')
#         t_harness_file.write('\n\n')
#         t_harness_file.write('#define msg_length  256\n')
#         t_harness_file.write(f'{args_types[0]} {args_names[0]}[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len\n')
#         t_harness_file.write(f'{args_types[1]} {args_names[1]} ;\n')
#         t_harness_file.write(f'{args_types[3]} {args_names[3]} = msg_length ;\n')
#         t_harness_file.write(f'{args_types[2]} {args_names[2]}[msg_length] ;\n')
#         t_harness_file.write(f'{args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES] ;\n')
#         t_harness_file.write('\n\n')
#         t_harness_file.write('int main(){\n')
#         t_harness_file.write(f'\tint result =  crypto_sign({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]});\n')
#         t_harness_file.write('\texit(result);\n')
#         t_harness_file.write('}\n')

def sign_test_harness_content(test_harness_file,api,sign,add_includes,args_types,args_names):
    args_types[2] = re.sub("const ","",args_types[2])
    test_harness_file_content_block1 = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h> 
    '''
    test_harness_file_content_block2 = f'''
    #define msg_length  256
    {args_types[0]} {args_names[0]}[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len
    {args_types[1]} {args_names[1]} ;
    {args_types[3]} {args_names[3]} = msg_length ;
    {args_types[2]} {args_names[2]}[msg_length] ;
    {args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES] ;
    int main(){{
    \tint result =  crypto_sign({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]});
    \texit(result);
    }}
    '''
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block1))
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
            t_harness_file.write(f'#include {api}\n')
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block2))




#==========================================CONFIGURATION FILES =========================================================
#=======================================================================================================================
#=======================================================================================================================

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



