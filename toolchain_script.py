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


class GenericPatterns(object):
    def __init__(self,tool_type,test_harness_keypair="test_harness_crypto_sign_keypair",test_harness_sign="test_harness_crypto_sign",ctgrind_taint = "taint"):
        self.tool_type = tool_type
        self.binsec_test_harness_keypair = test_harness_keypair
        self.binsec_test_harness_sign = test_harness_sign
        self.binsec_configuration_file_keypair = "cfg_keypair"
        self.binsec_configuration_file_sign = "cfg_sign"
        self.ctgrind_taint = ctgrind_taint


#********************************************************************************************
# A candidate is a string. It refers to as the declaration of a function.
# An object of type Candidate has many attributes like the base name of a given candidate,
# its list of arguments in the (type name) format, the list of its names of arguments, etc.
# Such type of object also incorporate many methods used to set some attributes. For example,
# the arguments names are given by the method get_candidate_arguments_names().
#********************************************************************************************

#Call it Target instead of Candidate
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

    #Return the list of the candidate argument names. For e.g ['plaintext','ith_round','round_key']
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


# Take into account the case in which one have a pointer input that points to just one value (not really as an array)

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

def group_multiple_lines_new_to_check(file_content_list,starting_pattern,ending_pattern,exclude_pattern,starting_index,ending_index):
    matching_string_list = []
    break_index = -1
    found_start_index = 0
    found_end_index = 0
    i = starting_index
    line = file_content_list[i]
    line.strip()
    exclude_pattern = exclude_pattern.strip()
    exclude_pattern_list = exclude_pattern.split()
    while (i <= ending_index) and (break_index<0):
        for word in exclude_pattern_list:
            print("+++++++ word ", word)
            if word in line :
                print("~~~~~~~~ WORD in line here: line = ",line)
                i+=1
                line = file_content_list[i]
            if starting_pattern in line and word in line:
                i+=1
                line = file_content_list[i]
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
    exclude_pattern = "open _seed_"
    ending_pattern = ");"
    included_pattern_keypair = "sign_keypair("
    starting_index = 0
    ending_index = len(file_content_line_by_line)
    keypair_def, start,end = group_multiple_lines(file_content_line_by_line,included_pattern_keypair,ending_pattern,exclude_pattern,starting_index,ending_index)
    print("-------keypair_def ",keypair_def)
    included_pattern_sign = "_sign("
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
    cand_basename = cand_obj.get_candidate_basename()
    cand_return_type = cand_obj.candidate_return_type
    return cand_return_type,cand_basename,args_types,args_names

def keypair_find_args_types_and_names(abs_path_to_api_or_sign):
    keypair_sign_def = find_sign_and_keypair_definition_from_api_or_sign(abs_path_to_api_or_sign)
    keypair_candidate = keypair_sign_def[0]
    cand_obj = Candidate(keypair_candidate)
    args_names = cand_obj.candidate_args_names
    args_types = cand_obj.candidate_types
    cand_basename = cand_obj.get_candidate_basename()
    cand_return_type = cand_obj.candidate_return_type
    return cand_return_type,cand_basename,args_types,args_names


#==========================================TEST HARNESS ================================================================
#=======================================================================================================================
#=======================================================================================================================
def test_harness_content_keypair(test_harness_file,api,sign,add_includes,function_return_type,function_name):
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


def sign_test_harness_content(test_harness_file,api,sign,add_includes,function_return_type,function_name,args_types,args_names):
    if 'const' in args_types[2]:
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
    \t{function_return_type} result =  {function_name}({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]});
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


def ctgrind_keypair_taint_content(taint_file,api,sign,add_includes,function_return_type,function_name,args_types,args_names):
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


def ctgrind_sign_taint_content_original_until_26_sept(taint_file,api,sign,rng,add_includes,function_return_type,function_name,args_types,args_names):
    args_types[2] = args_types[2].replace('const','')
    args_types[2] = args_types[2].strip()
    args_types[4] =args_types[4].replace('const','')
    args_types[4] = args_types[4].strip()
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    #include <ctgrind.h>
    #include <openssl/rand.h>
    #include <time.h> 
    
    '''
    taint_file_content_block_main = f'''    
    #define CTGRIND_SAMPLE_SIZE 100
    #define max_message_length 3300
    
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} *{args_names[1]};
    {args_types[2]} {args_names[2]}[max_message_length];
    {args_types[3]} {args_names[3]};
    {args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES];
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \trandombytes({args_names[2]}, {args_names[3]});
    \trandombytes({args_names[4]}, CRYPTO_SECRETKEYBYTES);
    }} 
    
    int main() {{
    
    \t{args_names[1]} = ({args_types[1]} *)calloc(1, sizeof({args_types[1]}));
    \t{args_names[0]} = ({args_types[0]} *)calloc(*{args_names[1]}, sizeof({args_types[0]})); 
    
    \t{function_return_type} result = 2 ; 
    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\t{args_names[3]} = 33*(i+1);
    \t\tgenerate_test_vectors(); 
    \t\tct_poison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tresult = {function_name}({args_names[0]}, {args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]}); 
    \t\tct_unpoison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
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
        t_file.write(f'#include {rng}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))



def ctgrind_sign_taint_content(taint_file,api,sign,rng,add_includes,function_return_type,function_name,args_types,args_names):
    args_types[2] = args_types[2].replace('const','')
    args_types[2] = args_types[2].strip()
    args_types[4] =args_types[4].replace('const','')
    args_types[4] = args_types[4].strip()
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



#==========================================CONFIGURATION FILES =========================================================
#=======================================================================================================================
#=======================================================================================================================

def sign_configuration_file_content_deprecated(cfg_file_sign,crypto_sign_args_names):
    cfg_file_content = f'''
    starting from <main>
    concretize stack
    secret global {crypto_sign_args_names[4]}
    public global {crypto_sign_args_names[0]},{crypto_sign_args_names[1]},{crypto_sign_args_names[2]},{crypto_sign_args_names[3]}
    halt at <exit>
    reach all
    '''
    with open(cfg_file_sign, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))
def sign_configuration_file_content(cfg_file_sign,crypto_sign_args_names):
    cfg_file_content = f'''
    starting from <main>
    with concrete stack pointer
    secret global {crypto_sign_args_names[4]}
    public global {crypto_sign_args_names[0]},{crypto_sign_args_names[1]},{crypto_sign_args_names[2]},{crypto_sign_args_names[3]}
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

#==========================================CREATE folders =========================================================
#=======================================================================================================================
#=======================================================================================================================

#Create same sub-folders in each folder of a given list of folders
def generic_create_tests_folders(list_of_path_to_folders):
    for t_folder in list_of_path_to_folders:
        if not os.path.isdir(t_folder):
            cmd = ["mkdir","-p",t_folder]
            subprocess.call(cmd, stdin = sys.stdin)

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

def compile_with_makefile(path_to_makefile,default=""):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make"]
    if not default == "":
        cmd.append(default)
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)

def compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile,path_to_build_folder,default=""):
    if not path_to_cmakelist_file == "":
        compile_with_cmake(path_to_build_folder)
    else:
        compile_with_makefile(path_to_makefile,default)

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

def run_ctgrind(binary_file,output_file):
    command = f'''valgrind -s --track-origins=yes --leak-check=full --show-leak-kinds=all --verbose --log-file={output_file} ./{binary_file}'''
    cmd_args_lst = command.split()
    subprocess.call(cmd_args_lst, stdin = sys.stdin)


def binsec_generic_run(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth,build_folder,binary_patterns):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
    if opt_src_folder_list_dir == []:
        path_to_subfolder = binsec_folder_full_path
        path_to_build_folder = path_to_subfolder+'/'+build_folder
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
                cfg_file =  find_ending_pattern(path_to_pattern_subfolder,cfg_pattern)
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                run_binsec(abs_path_to_executable,cfg_file,stats_file,output_file,depth)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = binsec_folder_full_path+'/'+subfold
            path_to_build_folder = path_to_subfolder+'/'+build_folder
            #path_to_binary_files = path_to_build_folder+'/'+"bin"
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
                    cfg_file =  find_ending_pattern(path_to_pattern_subfolder,cfg_pattern)
                    abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                    run_binsec(abs_path_to_executable,cfg_file,stats_file,output_file,depth)

def ctgrind_generic_run(ctgrind_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,build_folder,binary_patterns):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    ctgrind_folder_full_path = optimized_imp_folder_full_path+'/'+ctgrind_folder
    if opt_src_folder_list_dir == []:
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
                print("-------------Running: ",abs_path_to_executable)
                run_ctgrind(abs_path_to_executable,output_file)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = ctgrind_folder_full_path+'/'+subfold
            path_to_build_folder = path_to_subfolder+'/'+build_folder
            #path_to_binary_files = path_to_build_folder+'/'+"bin"
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
                    run_ctgrind(abs_path_to_executable,output_file)
def generic_run(tools_list,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth,build_folder,binary_patterns):
    for tool_name in tools_list:
        if 'binsec' in tool_name.lower():
            binsec_folder = tool_name
            binsec_generic_run(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth,build_folder,binary_patterns)
    for tool_name in tools_list:
        if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
            ctgrind_folder = tool_name
            ctgrind_generic_run(ctgrind_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,build_folder,binary_patterns)


#========================================== INITIALIZATION =============================================================
#=======================================================================================================================
#=======================================================================================================================
def find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign,rel_path_to_rng):
    api_relative = rel_path_to_api
    sign_relative = rel_path_to_sign
    rng_relative = rel_path_to_rng
    if not instance_folder == "":
        if not rel_path_to_api == "":
            rel_path_to_api_split = rel_path_to_api.split('/')
            for i in range(1,len(rel_path_to_api_split)):
                if not rel_path_to_api_split[i] == '..':
                    rel_path_to_api_split.insert(i,instance_folder)
                    break
            api_relative = '/'.join(rel_path_to_api_split)
        else:
            api_relative = ""
        if not rel_path_to_sign == "":
            rel_path_to_sign_split = rel_path_to_sign.split('/')
            for i in range(1,len(rel_path_to_sign_split)):
                if not rel_path_to_sign_split[i] == '..':
                    rel_path_to_sign_split.insert(i,instance_folder)
                    break
            sign_relative = '/'.join(rel_path_to_sign_split)
        else:
            sign_relative = ""
        #relative path to rng
        rel_path_to_rng_split = rel_path_to_rng.split('/')
        for i in range(1,len(rel_path_to_rng_split)):
            if not rel_path_to_rng_split[i] == '..':
                rel_path_to_rng_split.insert(i,instance_folder)
                break
        rng_relative = '/'.join(rel_path_to_rng_split)
    return api_relative,sign_relative,rng_relative

def find_api_sign_abs_path_modif_22_sept(path_to_opt_src_folder,api,sign,opt_implementation_name,ref_implementation_name = "Reference_Implementation"):
    folder = path_to_opt_src_folder
    ref_implementation_name.strip()
    opt_implementation_name.strip()
    api_folder = ""
    sign_folder = ""
    abs_path_to_api_or_sign = ""
    if not api == "":
        api_folder_split = api.split("../")
        api_folder = api_folder_split[-1]
        api_folder = api_folder.split('"')
        api_folder = api_folder[0]
        abs_path_to_api_or_sign = f'{folder}/{api_folder}'
    if not sign == "":
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
        folder = candidate_folder
    return abs_path_to_api_or_sign

def find_api_sign_abs_path(path_to_opt_src_folder,api,sign,opt_implementation_name,ref_implementation_name = "Reference_Implementation"):
    folder = path_to_opt_src_folder
    ref_implementation_name.strip()
    opt_implementation_name.strip()
    api_folder = ""
    sign_folder = ""
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
        folder = candidate_folder
    return abs_path_to_api_or_sign


def binsec_initialize_candidate(path_to_opt_src_folder,path_to_binsec_folder,path_to_binsec_keypair_folder,path_to_binsec_sign_folder,api,sign,add_includes):
    list_of_path_to_folders = [path_to_binsec_folder,path_to_binsec_keypair_folder,path_to_binsec_sign_folder]
    generic_create_tests_folders(list_of_path_to_folders)
    tool_type = "binsec"
    opt_implementation_name = os.path.basename(path_to_opt_src_folder)
    abs_path_to_api_or_sign = find_api_sign_abs_path(path_to_opt_src_folder,api,sign,opt_implementation_name)
    binsec_tool = GenericPatterns(tool_type)
    test_harness_keypair_basename = f'{binsec_tool.binsec_test_harness_keypair}.c'
    test_harness_sign_basename = f'{binsec_tool.binsec_test_harness_sign}.c'
    cfg_file_keypair = f'{path_to_binsec_keypair_folder}/{binsec_tool.binsec_configuration_file_keypair}.cfg'
    cfg_content_keypair(cfg_file_keypair)
    test_harness_keypair = f'{path_to_binsec_keypair_folder}/{test_harness_keypair_basename}'
    return_type,f_basename,args_types,args_names =  keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    test_harness_content_keypair(test_harness_keypair,api,sign,add_includes,return_type,f_basename)

    return_type,f_basename,args_types,args_names =  sign_find_args_types_and_names(abs_path_to_api_or_sign)
    cfg_file_sign = f'{path_to_binsec_sign_folder}/{binsec_tool.binsec_configuration_file_sign}.cfg'
    crypto_sign_args_names = args_names
    sign_configuration_file_content(cfg_file_sign,crypto_sign_args_names)
    test_harness_sign = f'{path_to_binsec_sign_folder}/{test_harness_sign_basename}'
    sign_test_harness_content(test_harness_sign,api,sign,add_includes,return_type,f_basename,args_types,args_names)



def ctgrind_initialize_candidate(path_to_opt_src_folder,path_to_ctgrind_folder,path_to_ctgrind_keypair_folder,path_to_ctgrind_sign_folder,api,sign,rng,add_includes):
    list_of_path_to_folders = [path_to_ctgrind_folder,path_to_ctgrind_keypair_folder,path_to_ctgrind_sign_folder]
    generic_create_tests_folders(list_of_path_to_folders)
    tool_type = "ctgrind"
    opt_implementation_name = os.path.basename(path_to_opt_src_folder)
    abs_path_to_api_or_sign = find_api_sign_abs_path(path_to_opt_src_folder,api,sign,opt_implementation_name)
    ctgrind_tool = GenericPatterns(tool_type)
    taint_keypair_basename = f'{ctgrind_tool.ctgrind_taint}.c'
    test_sign_basename = f'{ctgrind_tool.ctgrind_taint}.c'
    taint_keypair = f'{path_to_ctgrind_keypair_folder}/{taint_keypair_basename}'
    return_type,f_basename,args_types,args_names =  keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    ctgrind_keypair_taint_content(taint_keypair,api,sign,add_includes,return_type,f_basename,args_types,args_names)
    taint_sign = f'{path_to_ctgrind_sign_folder}/{test_sign_basename}'
    return_type,f_basename,args_types,args_names =  sign_find_args_types_and_names(abs_path_to_api_or_sign)
    ctgrind_sign_taint_content(taint_sign,api,sign,rng,add_includes,return_type,f_basename,args_types,args_names)


def initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,rng,add_includes):
    path_to_opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    tools_list_lowercase = [tool.lower() for tool in tools_list]
    binsec_folder = ""
    ctgrind_folder = ""
    for tool_name in tools_list_lowercase:
        if 'binsec' in tool_name:
            binsec_folder = tool_name
        elif 'grind' or 'ct_grind' in tool_name:
            ctgrind_folder = tool_name
    binsec = "binsec"
    ctgrind = "ctgrind"
    if binsec in tools_list_lowercase:
        path_to_binsec_folder = path_to_opt_src_folder+'/'+binsec_folder
        binsec_keypair_folder_basename = candidate+'_keypair'
        binsec_sign_folder_basename = candidate+'_sign'
        path_to_instance = path_to_binsec_folder
        if not instance_folder == "":
            path_to_instance = path_to_instance+'/'+instance_folder
        path_to_binsec_keypair_folder = path_to_instance+'/'+binsec_keypair_folder_basename
        path_to_binsec_sign_folder = path_to_instance+'/'+binsec_sign_folder_basename
        binsec_initialize_candidate(path_to_opt_src_folder,path_to_binsec_folder,path_to_binsec_keypair_folder,path_to_binsec_sign_folder,api,sign,add_includes)
    if ctgrind or 'ct_grind' in tools_list_lowercase:
        path_to_ctgrind_folder = path_to_opt_src_folder+'/'+ctgrind_folder
        ctgrind_keypair_folder_basename = candidate+'_keypair'
        ctgrind_sign_folder_basename = candidate+'_sign'
        path_to_instance = path_to_ctgrind_folder
        if not instance_folder == "":
            path_to_instance = path_to_instance+'/'+instance_folder
        path_to_ctgrind_keypair_folder = path_to_instance+'/'+ctgrind_keypair_folder_basename
        path_to_ctgrind_sign_folder = path_to_instance+'/'+ctgrind_sign_folder_basename
        ctgrind_initialize_candidate(path_to_opt_src_folder,path_to_ctgrind_folder,path_to_ctgrind_keypair_folder,path_to_ctgrind_sign_folder,api,sign,rng,add_includes)


def generic_initialize_nist_candidate_modif_22_sept(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes):
    if instance_folders_list == []:
        print("--------instance_folders_list = []",instance_folders_list)
        instance_folder = ""
        api, sign = find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign)
        initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,add_includes)
    else:
        print("--------instance_folders_list = []",instance_folders_list)
        for instance_folder in instance_folders_list:
            api, sign = find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign)
            initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,add_includes)

def generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,add_includes):
    if instance_folders_list == []:
        instance_folder = ""
        api, sign,rng = find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign,rel_path_to_rng)
        initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,rng,add_includes)
    else:
        for instance_folder in instance_folders_list:
            api, sign,rng = find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign,rel_path_to_rng)
            initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,rng,add_includes)


def generic_compile_run_candidate1(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
    candidate = candidate
    compile_run = f'init_compile_{candidate}({tools_list},{signature_type},{candidate},{optimized_imp_folder},{instance_folders_list},{rel_path_to_api},{rel_path_to_sign})'
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        f'{compile_run}'
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        f'{compile_run}'
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)

def generic_init_compile1(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes,build_folder,compile_with_cmake):
    generic_init = f'generic_initialize_nist_candidate({tools_list},{signature_type},{candidate},{optimized_imp_folder},{instance_folders_list},{rel_path_to_api},{rel_path_to_sign},{add_includes})'
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    makefile_candidate = ''
    path_to_optimized_implementation_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if instance_folders_list == []:
        f'{generic_init}'
        instance = ""
        for tool_type in tools_list:
            if compile_with_cmake == 'yes':
                path_to_cmakelist_file = path_to_optimized_implementation_folder+'/'+tool_type
                path_to_build_folder = path_to_cmakelist_file+'/'+build_folder
                path_to_makefile_folder = ""
            else:
                path_to_makefile_folder = path_to_optimized_implementation_folder+'/'+tool_type
                path_to_build_folder = path_to_makefile_folder+'/'+build_folder
                path_to_cmakelist_file = ""
            makefile_candidate = f'makefile_{candidate}({path_to_makefile_folder},{instance},{tool_type},{candidate})'
            f'{makefile_candidate}'
            compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder,"all")
    else:
        for instance in instance_folders_list:
            f'{generic_init}'
            for tool_type in tools_list:
                if compile_with_cmake == 'yes':
                    path_to_cmakelist_file = path_to_optimized_implementation_folder+'/'+tool_type+'/'+instance
                    path_to_build_folder = path_to_cmakelist_file+'/'+build_folder
                    path_to_makefile_folder = ""
                else:
                    path_to_makefile_folder = path_to_optimized_implementation_folder+'/'+tool_type+'/'+instance
                    path_to_build_folder = path_to_makefile_folder+'/'+build_folder
                    path_to_cmakelist_file = ""
                makefile_candidate = f'makefile_{candidate}({path_to_makefile_folder},{instance},{tool_type},{candidate})'
                f'{makefile_candidate}'
                compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder,"all")

def generic_init_compile(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,add_includes,build_folder,compile_with_cmake):
    generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,add_includes)
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    makefile_candidate = ''
    function_pattern = ""
    path_function_pattern_file = ""
    cmd = []
    path_to_optimized_implementation_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if instance_folders_list == []:
        generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,add_includes)
        instance = '""'
        for tool_type in tools_list:
            if compile_with_cmake == 'yes':
                path_to_cmakelist_file = path_to_optimized_implementation_folder+'/'+tool_type
                path_to_build_folder = path_to_cmakelist_file+'/'+build_folder
                path_to_makefile_folder = ""
                function_pattern = "cmake"
                path_function_pattern_file = path_to_cmakelist_file
            else:
                path_to_makefile_folder = path_to_optimized_implementation_folder+'/'+tool_type
                path_to_build_folder = path_to_makefile_folder+'/'+build_folder
                path_to_cmakelist_file = ""
                function_pattern = "makefile"
                path_function_pattern_file = path_to_makefile_folder
            exec(f'{function_pattern}_{candidate}(path_function_pattern_file,instance,tool_type,candidate)')
            if not os.path.isdir(path_to_build_folder):
                cmd = ["mkdir","-p",path_to_build_folder]
                subprocess.call(cmd, stdin = sys.stdin)
            compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder,"all")
    else:
        for instance in instance_folders_list:
            generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,add_includes)
            for tool_type in tools_list:
                if compile_with_cmake == 'yes':
                    path_to_cmakelist_file = path_to_optimized_implementation_folder+'/'+tool_type+'/'+instance
                    path_to_build_folder = path_to_cmakelist_file+'/'+build_folder
                    path_to_makefile_folder = ""
                    function_pattern = "cmake"
                    path_function_pattern_file = path_to_cmakelist_file
                else:
                    path_to_makefile_folder = path_to_optimized_implementation_folder+'/'+tool_type+'/'+instance
                    path_to_build_folder = path_to_makefile_folder+'/'+build_folder
                    path_to_cmakelist_file = ""
                    function_pattern = "makefile"
                    path_function_pattern_file = path_to_makefile_folder
                exec(f'{function_pattern}_{candidate}(path_function_pattern_file,instance,tool_type,candidate)')
                if not os.path.isdir(path_to_build_folder):
                    cmd = ["mkdir","-p",path_to_build_folder]
                subprocess.call(cmd, stdin = sys.stdin)
                compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder,"all")

def generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns):
    candidate = candidate
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        generic_init_compile(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,add_includes,build_folder,compile_with_cmake)
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        generic_init_compile(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,add_includes,build_folder,compile_with_cmake)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)

#========= New generic =========================
def add_cli_arguments_modif_22_sept(signature_type,candidate,optimized_imp_folder,rel_path_to_api = '""',rel_path_to_sign = '""',rel_path_to_rng = '""' ):
    candidate_sub_parser = f'{candidate}_init_compile_run'
    exec(f"{candidate_sub_parser}.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list,help = f'{candidate} tools')")
    exec(f"{candidate_sub_parser}.add_argument('--signature_type', '-type',dest='type',type=str,default=f'{signature_type}',help=f'{candidate} type')")
    exec(f"{candidate_sub_parser}.add_argument('--candidate', '-candidata',dest='candidate',type=str,default=f'{candidate}',help = f'{candidate} candidate')")
    exec(f"{candidate_sub_parser}.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default=f'{optimized_imp_folder}')")
    exec(f"{candidate_sub_parser}.add_argument('--instance_folders_list', nargs='+', default=f'{candidate}_default_list_of_folders')")
    exec(f"{candidate_sub_parser}.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default=f'{rel_path_to_api}')")
    exec(f"{candidate_sub_parser}.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default=f'{rel_path_to_sign}')")
    exec(f"{candidate_sub_parser}.add_argument('--rel_path_to_rng', '-rng', dest='rng',type=str,default=f'{rel_path_to_rng}')")
    exec(f"{candidate_sub_parser}.add_argument('--compile', '-c', dest='compile',default='Yes')")
    exec(f"{candidate_sub_parser}.add_argument('--run', '-r', dest='run',default='Yes')")
    exec(f"{candidate_sub_parser}.add_argument('--depth', '-depth', dest='depth',default='1000000',help = f'{candidate} depth')")
    exec(f"{candidate_sub_parser}.add_argument('--build', '-build', dest='build',default='build')")
    exec(f"{candidate_sub_parser}.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns,help = f'{candidate} algorithms_patterns')")

def add_cli_arguments(signature_type,candidate,optimized_imp_folder,rel_path_to_api = '""',rel_path_to_sign = '""',rel_path_to_rng = '""' ):
    candidate_sub_parser = f'{candidate}_init_compile_run'
    candidate_default_list_of_folders = f'{candidate}_default_list_of_folders'
    # print("~~~~~~~~~candidate_default_list_of_folders",f'{candidate_default_list_of_folders}')
    # print("~~~~~~~~~candidate_default_list_of_folders",candidate_default_list_of_folders)
    # t = f'{candidate_default_list_of_folders}'
    # print("----t = ",t)
    # print(exec(f'candidate_default_list_of_folders'))
    exec(f"{candidate_sub_parser}.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list,help = f'{candidate} tools')")
    exec(f"{candidate_sub_parser}.add_argument('--signature_type', '-type',dest='type',type=str,default=f'{signature_type}',help=f'{candidate} type')")
    # sig_type = f"{candidate_sub_parser}.add_argument('--signature_type', '-type',dest='type',type=str,default=f'{signature_type}',help=f'{candidate} type')"
    # exec(sig_type)
    exec(f"{candidate_sub_parser}.add_argument('--candidate', '-candidata',dest='candidate',type=str,default=f'{candidate}',help = f'{candidate} candidate')")
    exec(f"{candidate_sub_parser}.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default=f'{optimized_imp_folder}')")
    exec(f"{candidate_sub_parser}.add_argument('--instance_folders_list', nargs='+', default=candidate_default_list_of_folders)")
    exec(f"{candidate_sub_parser}.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default=f'{rel_path_to_api}',help = f'{rel_path_to_api} api')")
    exec(f"{candidate_sub_parser}.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default=f'{rel_path_to_sign}',help = f'{rel_path_to_sign} sign')")
    exec(f"{candidate_sub_parser}.add_argument('--rel_path_to_rng', '-rng', dest='rng',type=str,default=f'{rel_path_to_rng}')")
    exec(f"{candidate_sub_parser}.add_argument('--compile', '-c', dest='compile',default='Yes')")
    exec(f"{candidate_sub_parser}.add_argument('--run', '-r', dest='run',default='Yes')")
    exec(f"{candidate_sub_parser}.add_argument('--depth', '-depth', dest='depth',default='1000000',help = f'{candidate} depth')")
    exec(f"{candidate_sub_parser}.add_argument('--build', '-build', dest='build',default='build')")
    exec(f"{candidate_sub_parser}.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns,help = f'{candidate} algorithms_patterns')")


def run_cli_candidate(candidate):
    if args.binsec_test == f"compile_run_{candidate}":
        tools_list = args.tools
        signature_type = args.type
        print("---type(signature_type) = ",type(signature_type))
        print("---signature_type = ",signature_type)
        candidate = args.candidate
        optimization_folder = args.ref_opt
        instance_folders_list = args.instance_folders_list
        rel_path_to_api = args.api
        rel_path_to_sign = args.sign
        rel_path_to_rng = args.rng
        compile = args.compile
        run = args.run
        depth = args.depth
        build_folder = args.build
        binary_patterns = args.algorithms_patterns
        print("---AGAIN ----signature_type = ",signature_type)
        test = f'compile_run_{candidate}({tools_list},{signature_type},{candidate},{optimization_folder},{instance_folders_list},{rel_path_to_api},{rel_path_to_sign},{compile},{run},{depth},{build_folder},{binary_patterns})'
        print("--",test)
        exec(test)
    #exec(f'compile_run_{candidate}({tools_list},{signature_type},{candidate},{optimization_folder},{instance_folders_list},{rel_path_to_api},{rel_path_to_sign},{rel_path_to_rng},{compile},{run},{depth},{build_folder},{binary_patterns})')


def get_default_list_of_folders(candidate_default_list_of_folders,tools_list):
    for tool_name in tools_list:
        if tool_name in candidate_default_list_of_folders:
            candidate_default_list_of_folders.remove(tool_name)
    return candidate_default_list_of_folders


#######################################################################################################################################################
#########################################################################  A  #########################################################################
#######################################################################################################################################################
#========================================== MPC-IN-THE-HEAD ============================================================
#=======================================================================================================================
#========================================== MIRITH =====================================================================
def makefile_mirith(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block1 = f'''
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
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
    
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
    
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    makefile_content_block_object_files = f'''
    %.o: %.s
    \t$(CC) -c $(ASMFLAGS) -o $@ $<
    
    %.o: %.c $(DEPS)
    \t$(CC) -c $(CFLAGS) -o $@ $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).o $(OBJ)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LIBDIR) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) $(BINSEC_STATIC_FLAG)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).o $(OBJ)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LIBDIR) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) $(BINSEC_STATIC_FLAG)
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).o $(OBJ)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) ${{LIBDIR}} $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) -L. -lctgrind 
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).o $(OBJ)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) ${{LIBDIR}} $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) -L. -lctgrind  
        '''
    makefile_content_block_clean = f'''
    .PHONY: clean
      
    clean:
    \trm -f $(BASE_DIR)/*.o $(BASE_DIR)/*.su
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block1))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_mirith(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== PERK =======================================================================
def makefile_perk(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block1 = f'''   
    CC = gcc
    CFLAGS:= -std=c99 -pedantic -Wall -Wextra -O3 -funroll-all-loops -march=native -Wimplicit-function-declaration -Wredundant-decls \
         -Wundef -Wshadow  -mavx2 -mpclmul -msse4.2 -maes
        #-Wno-newline-eof
    ASMFLAGS := -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
    LDFLAGS:= -lcrypto
    ADDITIONAL_CFLAGS:= -Wno-missing-prototypes -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter
    
    BASE_DIR = ../../{subfolder}
    # Directories
    BUILD_DIR:=build
    BIN_DIR:=$(BUILD_DIR)/bin
    LIB_DIR:=$(BASE_DIR)/lib
    SRC_DIR:=$(BASE_DIR)/src
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        
        BUILD					= $(BUILD_DIR)
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm 
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
    
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}  
        
        BUILD					= $(BUILD_DIR)
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign  
        '''
    makefile_content_block_object_files = f'''    
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
    default: $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN)
    all: $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN)   
    
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
    \t$(CC) $(CFLAGS) -c $< $(PERK_INCLUDE) -o $@'''

    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        # main targets
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c  $(PERK_OBJS) $(LIB_OBJS)
        \t@echo -e "### Compiling PERK Test harness keypair"
        \t@mkdir -p $(dir $@)
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -Wno-strict-prototypes -Wno-unused-result $^ $(PERK_INCLUDE) -o $(BUILD)/$@ $(LDFLAGS)
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c  $(PERK_OBJS) $(LIB_OBJS)
        \t@echo -e "### Compiling PERK Test harness sign"
        \t@mkdir -p $(dir $@) 
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -Wno-strict-prototypes -Wno-unused-result $^ $(PERK_INCLUDE) -o $(BUILD)/$@ $(LDFLAGS)
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        # main targets
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c  $(PERK_OBJS) $(LIB_OBJS)
        \t@echo -e "### Compiling PERK Taint keypair"
        \t@mkdir -p $(dir $@)
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) $^ $(PERK_INCLUDE) -o $(BUILD)/$@ $^ $(LDFLAGS) -L. -lctgrind 
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c  $(PERK_OBJS) $(LIB_OBJS)
        \t@echo -e "### Compiling PERK Taint sign"
        \t@mkdir -p $(dir $@)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) $^ $(PERK_INCLUDE) -o $(BUILD)/$@ $^ $(LDFLAGS) -L. -lctgrind
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -rf $(BUILD_DIR) 
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block1))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

# def compile_perk(path_to_makefile):
#     cwd = os.getcwd()
#     os.chdir(path_to_makefile)
#     cmd = ["make","all"]
#     subprocess.call(cmd, stdin = sys.stdin)
#     os.chdir(cwd)
#
#
# def init_compile_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
#     path_to_cmakelist_file = ""
#     path_to_build_folder = ""
#     add_includes = []
#     for instance in instance_folders_list:
#         generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
#         for tool_type in tools_list:
#             path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type+'/'+instance
#             makefile_perk(path_to_makefile_folder,instance,tool_type,candidate)
#             compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)
#
#
# def compile_run_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
#     if 'y' in to_compile.lower() and 'y' in to_run.lower():
#         init_compile_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
#         generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
#     elif 'y' in to_compile.lower() and 'n' in to_run.lower():
#         init_compile_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
#     if 'n' in to_compile.lower() and 'y' in to_run.lower():
#         generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)

def compile_run_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== MQOM =======================================================================
def makefile_mqom(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_Cflags_obj_files = f'''    
    CC?=gcc
    ALL_FLAGS?=-O3 -flto -fPIC -std=c11 -march=native -Wall -Wextra -Wpedantic -Wshadow -DPARAM_HYPERCUBE_7R -DPARAM_GF31 -DPARAM_L1 -DPARAM_RND_EXPANSION_X4 -DHASHX4 -DXOFX4 -DPRGX4 -DNDEBUG -mavx
    ALL_FLAGS+=$(EXTRA_ALL_FLAGS) -g 
    
    BASE_DIR = ../../{subfolder}
    
    SYM_OBJ= $(BASE_DIR)/rnd.o $(BASE_DIR)/hash.o $(BASE_DIR)/xof.o
    ARITH_OBJ= $(BASE_DIR)/gf31-matrix.o $(BASE_DIR)/gf31.o
    MPC_OBJ= $(BASE_DIR)/mpc.o $(BASE_DIR)/witness.o $(BASE_DIR)/serialization-specific.o $(BASE_DIR)/precomputed.o
    CORE_OBJ= $(BASE_DIR)/keygen.o $(BASE_DIR)/sign.o $(BASE_DIR)/views.o $(BASE_DIR)/commit.o $(BASE_DIR)/sign-mpcith-hypercube.o $(BASE_DIR)/tree.o
    
    HASH_PATH=$(BASE_DIR)/sha3
    HASH_MAKE_OPTIONS=PLATFORM=avx2 
    HASH_INCLUDE=-I$(BASE_DIR)/sha3 -I. -I$(BASE_DIR)/sha3/avx2
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        
        EXECUTABLE_KEYPAIR_OBJ	    = {candidate}keypair/{test_harness_kpair}.o $(BASE_DIR)/generator/rng.o
        EXECUTABLE_SIGN_OBJ		    = {candidate}_sign/{test_harness_sign}.o $(BASE_DIR)/generator/rng.o
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm 
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
    
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}  
        
        EXECUTABLE_KEYPAIR_OBJ	    = {candidate}_keypair/{taint}.o $(BASE_DIR)/generator/rng.o
        EXECUTABLE_SIGN_OBJ		    = {candidate}_sign/{taint}.o $(BASE_DIR)/generator/rng.o
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign  
        '''

    makefile_content_block_object_files = f'''
    
    %.o : %.c
    \t$(CC) -c $(ALL_FLAGS) $(HASH_INCLUDE) -I. $< -o $@
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    
    libhash:
    \t$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
        \tmkdir -p $(BUILD) 
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(BINSEC_STATIC_FLAG) $(ALL_FLAGS) -L$(HASH_PATH) -L. -lhash -lcrypto -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(BINSEC_STATIC_FLAG) $(ALL_FLAGS) -L$(HASH_PATH) -L. -lhash -lcrypto -o $(BUILD)/$@
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(CT_GRIND_FLAGS) $(ALL_FLAGS) -L$(HASH_PATH) -L. -lhash -lcrypto -lctgrind -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(CT_GRIND_FLAGS) $(ALL_FLAGS) -L$(HASH_PATH) -L. -lhash -lcrypto -lctgrind -o $(BUILD)/$@
        # Cleaning
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ)
    \trm -f $(EXECUTABLE_KEYPAIR_OBJ) $(EXECUTABLE_SIGN_OBJ)  
    \trm -rf unit-*
    \t$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH) clean
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_Cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_mqom(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== RYDE =======================================================================
def makefile_ryde(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f''' 
    SCRIPT_VERSION=v1.0
    SCRIPT_AUTHOR=RYDE team
    
    CC=gcc
    C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4
    C_FLAGS_VERBOSE:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -DVERBOSE
    
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
    
    #BUILD:=bin/build
    #BIN:=bin
    BUILD:=build
    BIN:=build/bin
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tKEYPAIR_FOLDER 			= {candidate}_keypair
        \tSIGN_FOLDER 			= {candidate}_sign
        \tEXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        \tEXECUTABLE_SIGN		    = {test_harness_sign}
        
        \tSRC_KEYPAIR	    		= {candidate}_keypair/{test_harness_kpair}.c
        \tSRC_SIGN		    	= {candidate}_sign/{test_harness_sign}.c
        
        \tBUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        \tBUILD_SIGN			= $(BUILD)/{candidate}_sign
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        
        \tSRC_KEYPAIR	    	= {candidate}_keypair/{taint}.c
        \tSRC_SIGN		    	= {candidate}_sign/{taint}.c  
        
        \tBUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        \tBUILD_SIGN			= $(BUILD)/{candidate}_sign 
        '''
    makefile_content_block_creating_folders = f'''
    folders:
    \t@echo -e "### Creating build folders"
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BIN)
    
    randombytes.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BIN)/$@
    
    SimpleFIPS202.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER) -o $(BIN)/SimpleFIPS202.o
    
    xkcp: folders
    \t@echo -e "### Compiling XKCP"
    \tmake -C $(XKCP_SRC)
    
    rbc_%.o: $(RBC_SRC)/rbc_%.c | folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $< $(RBC_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BIN)/$@
    
    %.o: $(SRC)/%.c | folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BIN)/$@ '''

    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        
    
        $(EXECUTABLE_KEYPAIR): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build {test_harness_kpair}
        \t@echo -e "### Compiling test harness keypair"
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) $(C_FLAGS) $(SRC_KEYPAIR) $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@
    
        $(EXECUTABLE_SIGN): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build {test_harness_sign}
        \t@echo -e "### Compiling test harness sign"
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) $(C_FLAGS) $(SRC_SIGN) $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)   
        
        $(EXECUTABLE_KEYPAIR): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build {test_harness_kpair}
        \t@echo -e "### Compiling {taint} for keypair"
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(SRC_KEYPAIR) $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@ -L. -lctgrind 
    
        $(EXECUTABLE_SIGN): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build {test_harness_sign}
        \t@echo -e "### Compiling {taint} for sign"
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(SRC_SIGN) $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@ -L. -lctgrind 
        '''
    makefile_content_block_clean = f'''
    .PHONY: clean
    clean: ##@Miscellaneous Clean data
    \tmake -C $(XKCP_SRC) clean
    \trm -f $(EXECUTABLE_KEYPAIR)
    \trm -f $(EXECUTABLE_SIGN)
    \trm -rf $(BIN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_folders))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

# def compile_ryde(path_to_makefile):
#     cwd = os.getcwd()
#     os.chdir(path_to_makefile)
#     cmd = ["make","all"]
#     subprocess.call(cmd, stdin = sys.stdin)
#     os.chdir(cwd)
#
# def init_compile_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
#     path_to_cmakelist_file = ""
#     path_to_build_folder = ""
#     add_includes = []
#     for instance in instance_folders_list:
#         generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
#         for tool_type in tools_list:
#             path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type+'/'+instance
#             makefile_ryde(path_to_makefile_folder,instance,tool_type,candidate)
#             compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder,"all")
#
#
# def compile_run_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
#     if 'y' in to_compile.lower() and 'y' in to_run.lower():
#         init_compile_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
#         generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
#     elif 'y' in to_compile.lower() and 'n' in to_run.lower():
#         init_compile_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
#     if 'n' in to_compile.lower() and 'y' in to_run.lower():
#         generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
#


#========================================== MIRA =======================================================================
def makefile_mira(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    SCRIPT_VERSION=v1.0
    SCRIPT_AUTHOR=MIRA team
    
    CC=gcc
    C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -g 
    
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
    
    BUILD:=build
    BIN:=build/bin
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG      = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_folders_and_object_files = f'''
    folders:
    \t@echo -e "### Creating build/bin folders"
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BIN)
    \tmkdir -p $(BUILD_KEYPAIR)
    \tmkdir -p $(BUILD_SIGN) 
    
    
    randombytes.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BIN)/$@
    
    SimpleFIPS202.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER) -o $(BIN)/SimpleFIPS202.o
    
    xkcp: folders
    \t@echo -e "### Compiling XKCP"
    \tmake -C $(XKCP_SRC)
    
    
    finite_fields.o: $(FFI_SRC)/finite_fields.c | folders
    \t@echo -e "### Compiling finite_fields"
    \t$(CC) $(C_FLAGS) -c $< $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BIN)/$@
    
    %.o: $(SRC)/%.c | folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BIN)/$@
    
    
    all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)  ##@Build Build all the project
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files: PQCsignKAT_XX.req and PQCsignKAT_XX.rsp
        \t@echo -e "### Compiling MIRA-128F (test harness keypair)"
        \t$(CC) $(BINSEC_STATIC_FLAG) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files: PQCsignKAT_XX.req and PQCsignKAT_XX.rsp
        \t@echo -e "### Compiling MIRA-128F (test harness sign)"
        \t$(CC) $(BINSEC_STATIC_FLAG) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders 
        \t@echo -e "### Compiling MIRA-128F (taint keypair)"
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -L. -lctgrind -o $(BUILD)/$@ 

        $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders 
        \t@echo -e "### Compiling MIRA-128F (taint sign)"
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -L. -lctgrind -o $(BUILD)/$@
        '''

    makefile_content_block_clean = f'''
    .PHONY: clean
    clean:
    \tmake -C $(XKCP_SRC) clean
    \trm -f $(EXECUTABLE_KEYPAIR)
    \trm -f $(EXECUTABLE_SIGN)
    \trm -rf $(BUILD)/bin
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_folders_and_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

# def init_compile_mira(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
#     path_to_cmakelist_file = ""
#     path_to_build_folder = ""
#     add_includes = []
#     for instance in instance_folders_list:
#         generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
#         for tool_type in tools_list:
#             path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type+'/'+instance
#             makefile_mira(path_to_makefile_folder,instance,tool_type,candidate)
#             compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder,"all")

def compile_run_mira(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== SDITH =======================================================================
def makefile_sdith(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    SCRIPT_VERSION=v1.0
    SCRIPT_AUTHOR=MIRA team
    
    CC=gcc
    C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -g 
    
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
    
    BUILD:=build
    BIN:=build/bin
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG      = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_folders_and_object_files = f'''
    folders:
    \t@echo -e "### Creating build/bin folders"
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BIN)
    \tmkdir -p $(BUILD_KEYPAIR)
    \tmkdir -p $(BUILD_SIGN) 
    
    
    randombytes.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BIN)/$@
    
    SimpleFIPS202.o: folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER) -o $(BIN)/SimpleFIPS202.o
    
    xkcp: folders
    \t@echo -e "### Compiling XKCP"
    \tmake -C $(XKCP_SRC)
    
    
    finite_fields.o: $(FFI_SRC)/finite_fields.c | folders
    \t@echo -e "### Compiling finite_fields"
    \t$(CC) $(C_FLAGS) -c $< $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BIN)/$@
    
    %.o: $(SRC)/%.c | folders
    \t@echo -e "### Compiling $@"
    \t$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BIN)/$@
    
    
    all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)  ##@Build Build all the project
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files: PQCsignKAT_XX.req and PQCsignKAT_XX.rsp
        \t@echo -e "### Compiling MIRA-128F (test harness keypair)"
        \t$(CC) $(BINSEC_STATIC_FLAG) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files: PQCsignKAT_XX.req and PQCsignKAT_XX.rsp
        \t@echo -e "### Compiling MIRA-128F (test harness sign)"
        \t$(CC) $(BINSEC_STATIC_FLAG) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders 
        \t@echo -e "### Compiling MIRA-128F (taint keypair)"
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -L. -lctgrind -o $(BUILD)/$@ 

        $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders 
        \t@echo -e "### Compiling MIRA-128F (taint sign)"
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -L. -lctgrind -o $(BUILD)/$@
        '''

    makefile_content_block_clean = f'''
    .PHONY: clean
    clean:
    \tmake -C $(XKCP_SRC) clean
    \trm -f $(EXECUTABLE_KEYPAIR)
    \trm -f $(EXECUTABLE_SIGN)
    \trm -rf $(BUILD)/bin
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_folders_and_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_sdith(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)
#========================================== CROSS ======================================================================

def cmake_cross(path_to_cmake_lists,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    cmake_file_content_src_block1 = f'''
    cmake_minimum_required(VERSION 3.7)
    project(CROSS C)
    set(CMAKE_C_STANDARD 11)
    
    set(CC gcc)
    
    set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -march=haswell -O3 -g") 
    
    set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} ${{SANITIZE}}")
    message("Compilation flags:" ${{CMAKE_C_FLAGS}})
    
    # default compilation picks reference codebase
    if(NOT DEFINED REFERENCE)
       set(REFERENCE 0)
    endif()
    
    set(CSPRNG_ALGO SHAKE_CSPRNG)
    set(HASH_ALGO SHA3_HASH)
    
    find_library(KECCAK_LIB keccak)
    if(NOT KECCAK_LIB)
     set(STANDALONE_KECCAK 1)
    endif()
    '''
    cmake_file_content_find_ctgrind_lib = ""
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        cmake_file_content_find_ctgrind_lib = f'''
        find_library(CT_GRIND_LIB ctgrind)
        if(NOT CT_GRIND_LIB)
        \tmessage("${{CT_GRIND_LIB}} library not found")
        endif()
        find_library(CT_GRIND_SHARED_LIB ctgrind.so)
        if(NOT CT_GRIND_SHARED_LIB)
        \tmessage("${{CT_GRIND_SHARED_LIB}} library not found")
        \tset(CT_GRIND_SHARED_LIB /usr/lib/libctgrind.so)
        endif()
        '''
    cmake_file_content_src_block2 = f'''
    # selection of specialized compilation units differing between ref and opt
    # implementations.
    set(REFERENCE_CODE_DIR ../../Reference_Implementation) 
    set(OPTIMIZED_CODE_DIR ../../Optimized_Implementation) 
    
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
    set(BUILD build)
    set(BUILD_KEYPAIR {candidate}_keypair)
    set(BUILD_SIGN {candidate}_sign)
    '''
    cmake_file_content_block_loop = f'''
    foreach(category RANGE 1 5 2)
        set(RSDP_VARIANTS RSDP RSDPG)
        foreach(RSDP_VARIANT ${{RSDP_VARIANTS}})
            set(PARAM_TARGETS SIG_SIZE SPEED)
            foreach(optimiz_target ${{PARAM_TARGETS}})
            '''
    cmake_file_content_loop_content_block_keypair = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        cmake_file_content_loop_content_block_keypair = f'''
                 #crypto_sign_keypair test harness binary
                 set(TARGET_BINARY_NAME {test_harness_kpair}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./{candidate}_keypair/{test_harness_kpair}.c)
                target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static) 
                target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        cmake_file_content_loop_content_block_keypair = f'''
                 #crypto_sign_keypair taint binary
                 set(TARGET_BINARY_NAME {taint}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./{candidate}_keypair/{taint}.c)
                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''
    cmake_file_content_loop_content_block2 = f'''
                 set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
                 set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                     COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 -D${{CSPRNG_ALGO}}=1 -D${{HASH_ALGO}}=1 -D${{RSDP_VARIANT}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
                '''
    cmake_file_content_loop_content_block_sign = ""
    if tool_type.lower() == 'binsec':
        test_harness_sign = tool.binsec_test_harness_sign
        cmake_file_content_loop_content_block_sign = f'''            
                 #crypto_sign test harness binary
                 set(TARGET_BINARY_NAME {test_harness_sign}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./{candidate}_sign/{test_harness_sign}.c)
                 target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        cmake_file_content_loop_content_block_sign = f'''
                 #crypto_sign test harness binary
                 set(TARGET_BINARY_NAME {taint}_sign_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./{candidate}_sign/{taint}.c)
                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
        '''
    cmake_file_content_loop_content_block3 = f'''
                 set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}})   
                 set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                     COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 -D${{CSPRNG_ALGO}}=1 -D${{HASH_ALGO}}=1 -D${{RSDP_VARIANT}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
                '''
    cmake_file_content_block_loop_end = f'''             
            endforeach(optimiz_target) 
        endforeach(RSDP_VARIANT)
    endforeach(category)
    '''
    with open(path_to_cmake_lists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block1))
        if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
            cmake_file.write(textwrap.dedent(cmake_file_content_find_ctgrind_lib))
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_keypair))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_sign))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block3))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop_end))



# def init_compile_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
#     path_to_makefile_folder = ""
#     path_to_build_folder = ""
#     add_includes = []
#     generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
#     for tool_type in tools_list:
#         path_to_tool_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type
#         path_to_opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
#         path_to_cmake_lists = path_to_tool_folder+'/'+'CMakeLists.txt'
#         cmake_cross(path_to_cmake_lists,tool_type,candidate)
#         path_to_build_folder = path_to_tool_folder+'/build'
#         if not os.path.isdir(path_to_build_folder):
#             cmd = ["mkdir","-p",path_to_build_folder]
#             subprocess.call(cmd, stdin = sys.stdin)
#         compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_build_folder,path_to_makefile_folder,path_to_build_folder)


# def compile_run_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
#     if 'y' in to_compile.lower() and 'y' in to_run.lower():
#         init_compile_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
#         generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
#     elif 'y' in to_compile.lower() and 'n' in to_run.lower():
#         init_compile_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
#     if 'n' in to_compile.lower() and 'y' in to_run.lower():
#         generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)


# def compile_run_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
#     add_includes = []
#     compile_with_cmake = 'yes'
#     generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

def compile_run_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'yes'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)
#=========================================  CODE =======================================================================
#=======================================================================================================================

#=========================================  PQSIGRM ====================================================================
def makefile_pqsigRM(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_pqsigRM(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=============================== LESS ==================================================================================
def cmake_less(path_to_cmakelist,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder  = ""
    path_to_cmakelist = path_to_cmakelist+'/CMakeLists.txt'
    cmake_file_content_src_block1 = f'''
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
    
    #set(BASE_DIR  ../Optimized_Implementation) 
    set(BASE_DIR  ../)  
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
    
    '''
    cmake_file_content_find_ctgrind_lib = ""
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        cmake_file_content_find_ctgrind_lib = f'''
        find_library(CT_GRIND_LIB ctgrind)
        if(NOT CT_GRIND_LIB)
        \tmessage("${{CT_GRIND_LIB}} library not found")
        endif()
        find_library(CT_GRIND_SHARED_LIB ctgrind.so)
        if(NOT CT_GRIND_SHARED_LIB)
        \tmessage("${{CT_GRIND_SHARED_LIB}} library not found")
        \tset(CT_GRIND_SHARED_LIB /usr/lib/libctgrind.so)
        endif()
        '''
    cmake_file_content_src_block2 = f'''
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
    set(BUILD build)
    set(BUILD_KEYPAIR {candidate}_keypair)
    set(BUILD_SIGN {candidate}_sign)
    '''
    cmake_file_content_block_loop = f'''
    foreach(category RANGE 1 5 2)
        if(category EQUAL 1)
            set(PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE)
        else()
            set(PARAM_TARGETS SIG_SIZE PK_SIZE)
        endif()
        foreach(optimiz_target ${{PARAM_TARGETS}})
        '''# settings for benchmarking binary
    cmake_file_content_loop_content_block_keypair = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        cmake_file_content_loop_content_block_keypair = f'''
            set(TEST_HARNESS ./{tool_type}/{candidate}_keypair/{test_harness_kpair}.c ./{tool_type}/{candidate}_sign/{test_harness_sign}.c)
            set(TARGET_BINARY_NAME {test_harness_kpair}_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_keypair/{test_harness_kpair}.c)
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        cmake_file_content_loop_content_block_keypair = f'''
        set(TARGET_BINARY_NAME {taint}_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_keypair/{taint}.c)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''

    cmake_file_content_loop_content_block2 = f'''
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
            '''
    cmake_file_content_loop_content_block_sign = ""
    if tool_type.lower() == 'binsec':
        test_harness_sign = tool.binsec_test_harness_sign
        cmake_file_content_loop_content_block_sign = f'''
            #Test harness for crypto_sign
            set(TARGET_BINARY_NAME {test_harness_sign}_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_sign/{test_harness_sign}.c)   
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        cmake_file_content_loop_content_block_sign = f'''    
        #Test harness for crypto_sign
            set(TARGET_BINARY_NAME {taint}_sign_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_sign/{taint}.c)   
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''
    cmake_file_content_loop_content_block3 = f'''
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}}) 
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}}")
            '''
    cmake_file_content_block_loop_end = f'''
            #endforeach(t_harness)
        endforeach(optimiz_target)
    endforeach(category)
    '''
    with open(path_to_cmakelist, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block1))
        if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
            cmake_file.write(textwrap.dedent(cmake_file_content_find_ctgrind_lib))
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_keypair))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_sign))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block3))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop_end))

def compile_run_less(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'yes'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=============================== FULEECA ===============================================================================
#[TODO]
def makefile_fuleeca(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_fuleeca(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)
#=============================== MEDS ==================================================================================
#[TODO]
def makefile_meds(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_meds(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)
#=============================== WAVE ==================================================================================
#[TODO]
def makefile_Wave(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_Wave(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== LATTICE ====================================================================
#=======================================================================================================================
#=========================================  SQUIRRELS ==================================================================
#[TODO]
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
def makefile_squirrels(path_to_makefile_folder,subfolder,tool_type,candidate):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    level = squirrels_level(subfolder)
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""

    makefile_content_block_Cflags_obj_files = f'''
    .POSIX:

    NIST_LEVEL?={level}
    
    BASE_DIR = ../../{subfolder}
    CC = gcc
    CFLAGS = -W -Wall -O3 -march=native -I../../../lib/build/mpfr/include -I../../../lib/build/mpfr/include -I../../../lib/build/gmp/include -I../../../lib/build/flint/include/flint -I../../../lib/build/fplll/include \
        -DSQUIRRELS_LEVEL=$(NIST_LEVEL)
    LD = gcc -v
    LDFLAGS = 
    
    LIBSRPATH = '$$ORIGIN'../../../../../lib/build
    LIBS = -lm \
    \t-L../../../lib/build/mpfr/lib -Wl,-rpath,$(LIBSRPATH)/mpfr/lib -lmpfr \
    \t-L../../../lib/build/gmp/lib -Wl,-rpath,$(LIBSRPATH)/gmp/lib -lgmp \
    \t-L../../../lib/build/flint/lib -Wl,-rpath,$(LIBSRPATH)/flint/lib -lflint \
    \t-L../../../lib/build/fplll/lib -Wl,-rpath,$(LIBSRPATH)/fplll/lib -lfplll \
    \t-lstdc++
    
    OBJ1 = $(BASE_DIR)/build/codec.o $(BASE_DIR)/build/common.o $(BASE_DIR)/build/keygen_lll.o $(BASE_DIR)/build/keygen.o  $(BASE_DIR)/build/minors.o $(BASE_DIR)/build/nist.o $(BASE_DIR)/build/normaldist.o $(BASE_DIR)/build/param.o $(BASE_DIR)/build/sampler.o $(BASE_DIR)/build/shake.o $(BASE_DIR)/build/sign.o $(BASE_DIR)/build/vector.o
    
    
    HEAD1 = $(BASE_DIR)/api.h $(BASE_DIR)/fpr.h $(BASE_DIR)/inner.h $(BASE_DIR)/param.h
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign 
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
    BINSEC_STATIC_FLAGS     = -static
    DEBUG_G_FLAG            = -g
    EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
    EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm 
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
    
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint} 
    '''
    makefile_content_block_object_files = f'''
    
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
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''

    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(HEAD1) $(BASE_DIR)/api.h 
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(CFLAGS) -I . -c -o $(BUILD)/$$(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_KEYPAIR).c 
    
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(HEAD1) $(BASE_DIR)/api.h 
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(CFLAGS) -I . -c -o $(BUILD)/$$(EXECUTABLE_SIGN)  $(EXECUTABLE_SIGN).c 
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(HEAD1) $(BASE_DIR)/api.h 
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -I . -c -o $(BUILD)/$$(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_KEYPAIR).c -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
    $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(HEAD1) $(BASE_DIR)/api.h 
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -I . -c -o $(BUILD)/$(EXECUTABLE_SIGN)  $(EXECUTABLE_SIGN).c -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl 
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_Cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))

def compile_run_squirrels(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=============================== HAETAE ================================================================================
#[TODO:Peaufine cmake]
def cmake_haetae(path_to_cmakelist,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder  = ""
    path_to_cmakelist = path_to_cmakelist+'/CMakeLists.txt'

def compile_run_haetae(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'yes'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=============================== EAGLESIGN =============================================================================
#[TODO]
def makefile_EagleSign(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_EagleSign(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)
#=============================== EHTv3v4 ===============================================================================
#[TODO]
def makefile_EHTv3v4(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_EHTv3v4(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)
#=============================== HAWK ==================================================================================
#[TODO]
def makefile_hawk(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_hawk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)
#=============================== HUFU ==================================================================================
#[TODO]
def makefile_hufu(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_hufu(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=============================== RACCOON ===============================================================================
#[TODO:Shell script compilation]
def makefile_Raccoon(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        CT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_Raccoon(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  MULTIVARIATE ===============================================================
#=======================================================================================================================

#=========================================  QR-UOV =====================================================================
#[TODO:Rename functions if needed/if not working with new script keep old script ...]
def run_qr_uov_makefile(path_to_qrUOV_makefile_folder):
    cwd = os.getcwd()
    os.chdir(path_to_qrUOV_makefile_folder)
    cwd1 = os.getcwd()
    cmd = ["make"]
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)



def main_makefile_qr_uov(tool_type,path_to_tool_folder,subfolder):
    #path_to_makefile = path_to_binsec_folder+'/Makefile'
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_tool_folder+'/Makefile'
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


def makefile_qr_uov(path_to_makefile_folder,subfolder):
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

def compile_run_qr_uov(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  snova ======================================================================
#[TODO:error after running binsec. Make sure binary is static]
def makefile_snova(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
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
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_snova(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  BISCUIT ====================================================================
#[TODO]
def makefile_biscuit(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
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
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_biscuit(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  dme_sign ===================================================================
#[TODO]
def makefile_dme_sign(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
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
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_dme_sign(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  hppc =======================================================================
#[TODO]
def makefile_hppc(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
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
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_hppc(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  MAYO =======================================================================
#[TODO]
def cmake_mayo(path_to_cmakelist,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder  = ""
    path_to_cmakelist = path_to_cmakelist+'/CMakeLists.txt'
    cmake_file_content_src_block1 = f'''
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
    
    #set(BASE_DIR  ../Optimized_Implementation) 
    set(BASE_DIR  ../)  
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
    
    '''
    cmake_file_content_find_ctgrind_lib = ""
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        cmake_file_content_find_ctgrind_lib = f'''
        find_library(CT_GRIND_LIB ctgrind)
        if(NOT CT_GRIND_LIB)
        \tmessage("${{CT_GRIND_LIB}} library not found")
        endif()
        find_library(CT_GRIND_SHARED_LIB ctgrind.so)
        if(NOT CT_GRIND_SHARED_LIB)
        \tmessage("${{CT_GRIND_SHARED_LIB}} library not found")
        \tset(CT_GRIND_SHARED_LIB /usr/lib/libctgrind.so)
        endif()
        '''
    cmake_file_content_src_block2 = f'''
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
    set(BUILD build)
    set(BUILD_KEYPAIR {candidate}_keypair)
    set(BUILD_SIGN {candidate}_sign)
    '''
    cmake_file_content_block_loop = f'''
    foreach(category RANGE 1 5 2)
        if(category EQUAL 1)
            set(PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE)
        else()
            set(PARAM_TARGETS SIG_SIZE PK_SIZE)
        endif()
        foreach(optimiz_target ${{PARAM_TARGETS}})
        '''# settings for benchmarking binary
    cmake_file_content_loop_content_block_keypair = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        cmake_file_content_loop_content_block_keypair = f'''
            set(TEST_HARNESS ./{tool_type}/{candidate}_keypair/{test_harness_kpair}.c ./{tool_type}/{candidate}_sign/{test_harness_sign}.c)
            set(TARGET_BINARY_NAME {test_harness_kpair}_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_keypair/{test_harness_kpair}.c)
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        cmake_file_content_loop_content_block_keypair = f'''
        set(TARGET_BINARY_NAME {taint}_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_keypair/{taint}.c)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''

    cmake_file_content_loop_content_block2 = f'''
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
            '''
    cmake_file_content_loop_content_block_sign = ""
    if tool_type.lower() == 'binsec':
        test_harness_sign = tool.binsec_test_harness_sign
        cmake_file_content_loop_content_block_sign = f'''
            #Test harness for crypto_sign
            set(TARGET_BINARY_NAME {test_harness_sign}_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_sign/{test_harness_sign}.c)   
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        cmake_file_content_loop_content_block_sign = f'''    
        #Test harness for crypto_sign
            set(TARGET_BINARY_NAME {taint}_sign_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_sign/{taint}.c)   
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''
    cmake_file_content_loop_content_block3 = f'''
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}}) 
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}}")
            '''
    cmake_file_content_block_loop_end = f'''
            #endforeach(t_harness)
        endforeach(optimiz_target)
    endforeach(category)
    '''
    with open(path_to_cmakelist, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block1))
        if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
            cmake_file.write(textwrap.dedent(cmake_file_content_find_ctgrind_lib))
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_keypair))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_sign))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block3))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop_end))

def compile_run_mayo(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'yes'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  PROV =======================================================================
#[TODO]
def makefile_prov(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
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
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_prov(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  TUOV =======================================================================
#[TODO]
def makefile_tuov(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
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
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_tuov(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  UOV ========================================================================
#[TODO]
def makefile_uov(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
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
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_uov(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  VOX ========================================================================
#[TODO]
def makefile_vox(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
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
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    clean_all: 
    \trm -f $(BASE_DIR)/build/*.o $(BASE_DIR)/*.a $(BASE_DIR)/*.log $(BASE_DIR)/*.req $(BASE_DIR)/*.rsp
    
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_vox(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  SYMMETRIC ==================================================================
#=======================================================================================================================

#=========================================  AIMER ======================================================================
def makefile_aimer(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    # SPDX-License-Identifier: MIT

    CC = gcc
    CFLAGS += -I. -O3 -g -Wall -Wextra -march=native -fomit-frame-pointer
    NISTFLAGS = -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter -Wno-unused-result
    AVX2FLAGS = -mavx2 -mpclmul
    
    BASE_DIR = ../../{subfolder}
    
    SHAKE_PATH = $(BASE_DIR)/shake
    SHAKE_LIB = libshake.a
    LDFLAGS = $(SHAKE_PATH)/$(SHAKE_LIB)
    
    
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    
    .PHONY: all
    
    all: $(SHAKE_LIB) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    $(BUILD)/.c.o:
    \t$(CC) -c $(CFLAGS) $< -o $@
    
    $(SHAKE_LIB):
    \t$(MAKE) -C $(SHAKE_PATH)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.c $(BASE_DIR)/field/field128.c $(BASE_DIR)/aim128.c $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(AVX2FLAGS)  -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.c $(BASE_DIR)/field/field128.c $(BASE_DIR)/aim128.c $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(AVX2FLAGS)  -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto -o $(BUILD)/$@
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.c $(BASE_DIR)/field/field128.c $(BASE_DIR)/aim128.c $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) $(AVX2FLAGS)  -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl -o $(BUILD)/$@
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.c $(BASE_DIR)/field/field128.c $(BASE_DIR)/aim128.c $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) $(AVX2FLAGS)  -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl -o $(BUILD)/$@

        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(wildcard *.o) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    \t$(MAKE) -C $(SHAKE_PATH) clean   
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


def compile_run_aimer(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== Ascon_sign =================================================================

def makefile_Ascon_sign(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    THASH = robust

    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
     
      
    SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c $(BASE_DIR)/sign.c
    
    SOURCES += $(BASE_DIR)/hash_ascon.c $(BASE_DIR)/ascon_opt64/ascon.c $(BASE_DIR)/ascon_opt64/permutations.c  $(BASE_DIR)/thash_ascon_$(THASH).c
    
    
    DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG      = -static
        DEBUG_G_FLAG          = -g
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    
        all:  $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN) 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
    
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    
        all:  $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN) 
        '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
    
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) $(DEBUG_G_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) $(DEBUG_G_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
            '''
    makefile_content_block_clean = f'''
    clean:
    \t-$(RM)  $(EXECUTABLE_SIGN)
    \t-$(RM)  $(EXECUTABLE_KEYPAIR) 
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


def compile_run_Ascon_sign(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)


#========================================== faest ======================================================================

def makefile_faest(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    CC?=gcc
    CXX?=g++
    CFLAGS+=-g -O2 -march=native -mtune=native -std=c11
    CPPFLAGS+=-DHAVE_OPENSSL -DNDEBUG -MMD -MP -MF $*.d
    
    SRC_DIR = ../../{subfolder} 
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    
    SOURCES=$(filter-out  $(SRC_DIR)/PQCgenKAT_sign.c ,$(wildcard $(SRC_DIR)/*.c)) $(wildcard $(SRC_DIR)/*.s)
    LIBFAEST=libfaest.a
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}  
        '''
    makefile_content_block_creating_object_files = f'''    
    
    all: $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    .PHONY: all
    
    $(LIBFAEST): $(SOURCES:.c=.o) $(SOURCES:.s=.o)
    \tar rcs $@ $^
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(LIBFAEST)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -o $(BUILD)/$(EXECUTABLE_KEYPAIR) $(EXECUTABLE_KEYPAIR).c $(BINSEC_STATIC_FLAG) $(LIBFAEST)
    
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(LIBFAEST)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -o $(BUILD)/$(EXECUTABLE_SIGN) $(EXECUTABLE_SIGN).c $(BINSEC_STATIC_FLAG) $(LIBFAEST)
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(LIBFAEST)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CT_GRIND_FLAGS) -o $(BUILD)/$(EXECUTABLE_KEYPAIR) $(EXECUTABLE_KEYPAIR).c  $(LIBFAEST) -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(LIBFAEST)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CT_GRIND_FLAGS) -o $(BUILD)/$(EXECUTABLE_SIGN) $(EXECUTABLE_SIGN).c  $(LIBFAEST) -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean: 
    \trm -f $(SRC_DIR)/*.d $(SRC_DIR)/*.o $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    .PHONY: clean
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


def compile_run_faest(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)


#========================================== Sphincs-alpha ==============================================================
def makefile_sphincs_alpha(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../{subfolder}
    '''
    makefile_content_block_object_files = f'''
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
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        
        '''
    makefile_content_block_all_target = f''' 
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        '''
    makefile_content_block_clean = f''' 
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))

def compile_run_sphincs_alpha(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#=========================================  OTHER ======================================================================
#=======================================================================================================================
#========================================== PREON ======================================================================
def preon_subfolder_parser(subfolder):
    subfold_basename = os.path.basename(subfolder)
    subfold_basename_split = subfold_basename.split('Preon')
    security_level_labeled = subfold_basename_split[-1]
    security_level = security_level_labeled[:3]
    return security_level,security_level_labeled

def makefile_preon(path_to_makefile_folder,subfolder,tool_type,candidate):
    security_level,security_level_labeled = preon_subfolder_parser(subfolder)
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f''' 
    CC = cc
    CFLAGS := ${{CFLAGS}} -DUSE_PREON{security_level_labeled} -DAES{security_level}=1 -DUSE_PRNG -O3
    LFLAGS := ${{LFLAGS}} -lm -lssl -lcrypto
    
   
    BASE_DIR = ../../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
    SRC_FILES := $(filter-out  $(BASE_DIR)/PQCgenKAT_sign.c ,$(wildcard $(BASE_DIR)/*.c))
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        '''
    makefile_content_block_all_target_and_object_files = f'''
    all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o: %.c
    \t@$(CC) $(CFLAGS) -c $< -o $@
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(SRC_FILES)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG)  -o $(BUILD)/$@ $(SRC_FILES) $< $(LFLAGS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(SRC_FILES)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(BINSEC_STATIC_FLAG) $(DEBUG_G_FLAG) -o $(BUILD)/$@ $(SRC_FILES) $< $(LFLAGS)
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(SRC_FILES)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS)  -o $(BUILD)/$@ $(SRC_FILES) $< $(LFLAGS) -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(SRC_FILES)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(SRC_FILES) $< $(LFLAGS) -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        '''
    makefile_content_block_clean = f'''
    .PHONY: clean  
    
    clean:
    \t@rm -f $(BASE_DIR)/*.o 
    \t@rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target_and_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


def compile_run_preon(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== ALTEQ ======================================================================
#[TODO]
def makefile_alteq(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../{subfolder}
    '''
    makefile_content_block_object_files = f'''
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
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        
        '''
    makefile_content_block_all_target = f''' 
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        '''
    makefile_content_block_clean = f''' 
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


def compile_run_alteq(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== EMLE2_0 ====================================================================
#[TODO]
def makefile_emle2_0(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../{subfolder}
    '''
    makefile_content_block_object_files = f'''
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
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        
        '''
    makefile_content_block_all_target = f''' 
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        '''
    makefile_content_block_clean = f''' 
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


def compile_run_emle2_0(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== kaz_sign ===================================================================
#[TODO]
def makefile_kaz_sign(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../{subfolder}
    '''
    makefile_content_block_object_files = f'''
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
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        
        '''
    makefile_content_block_all_target = f''' 
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        '''
    makefile_content_block_clean = f''' 
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


def compile_run_kaz_sign(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#========================================== xifrat =====================================================================
#[TODO]
def makefile_xifrat(path_to_makefile_folder,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../{subfolder}
    '''
    makefile_content_block_object_files = f'''
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
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        
        '''
    makefile_content_block_all_target = f''' 
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        '''
    makefile_content_block_clean = f''' 
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


def compile_run_xifrat(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'no'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)
#=========================================  ISOGENY ====================================================================
#=======================================================================================================================
#========================================== sqisign =====================================================================
#[TODO]
def cmake_sqisign(path_to_cmakelist,subfolder,tool_type,candidate):
    tool = GenericPatterns(tool_type)
    test_harness_kpair = ""
    test_harness_sign = ""
    taint = ""
    subfolder  = ""
    path_to_cmakelist = path_to_cmakelist+'/CMakeLists.txt'
    cmake_file_content_src_block1 = f'''
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
    
    #set(BASE_DIR  ../Optimized_Implementation) 
    set(BASE_DIR  ../)  
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
    
    '''
    cmake_file_content_find_ctgrind_lib = ""
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        cmake_file_content_find_ctgrind_lib = f'''
        find_library(CT_GRIND_LIB ctgrind)
        if(NOT CT_GRIND_LIB)
        \tmessage("${{CT_GRIND_LIB}} library not found")
        endif()
        find_library(CT_GRIND_SHARED_LIB ctgrind.so)
        if(NOT CT_GRIND_SHARED_LIB)
        \tmessage("${{CT_GRIND_SHARED_LIB}} library not found")
        \tset(CT_GRIND_SHARED_LIB /usr/lib/libctgrind.so)
        endif()
        '''
    cmake_file_content_src_block2 = f'''
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
    set(BUILD build)
    set(BUILD_KEYPAIR {candidate}_keypair)
    set(BUILD_SIGN {candidate}_sign)
    '''
    cmake_file_content_block_loop = f'''
    foreach(category RANGE 1 5 2)
        if(category EQUAL 1)
            set(PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE)
        else()
            set(PARAM_TARGETS SIG_SIZE PK_SIZE)
        endif()
        foreach(optimiz_target ${{PARAM_TARGETS}})
        '''# settings for benchmarking binary
    cmake_file_content_loop_content_block_keypair = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = tool.binsec_test_harness_keypair
        test_harness_sign = tool.binsec_test_harness_sign
        cmake_file_content_loop_content_block_keypair = f'''
            set(TEST_HARNESS ./{tool_type}/{candidate}_keypair/{test_harness_kpair}.c ./{tool_type}/{candidate}_sign/{test_harness_sign}.c)
            set(TARGET_BINARY_NAME {test_harness_kpair}_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_keypair/{test_harness_kpair}.c)
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        cmake_file_content_loop_content_block_keypair = f'''
        set(TARGET_BINARY_NAME {taint}_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_keypair/{taint}.c)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''

    cmake_file_content_loop_content_block2 = f'''
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
            '''
    cmake_file_content_loop_content_block_sign = ""
    if tool_type.lower() == 'binsec':
        test_harness_sign = tool.binsec_test_harness_sign
        cmake_file_content_loop_content_block_sign = f'''
            #Test harness for crypto_sign
            set(TARGET_BINARY_NAME {test_harness_sign}_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_sign/{test_harness_sign}.c)   
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = tool.ctgrind_taint
        cmake_file_content_loop_content_block_sign = f'''    
        #Test harness for crypto_sign
            set(TARGET_BINARY_NAME {taint}_sign_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_sign/{taint}.c)   
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''
    cmake_file_content_loop_content_block3 = f'''
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}}) 
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}}")
            '''
    cmake_file_content_block_loop_end = f'''
            #endforeach(t_harness)
        endforeach(optimiz_target)
    endforeach(category)
    '''
    with open(path_to_cmakelist, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block1))
        if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
            cmake_file.write(textwrap.dedent(cmake_file_content_find_ctgrind_lib))
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_keypair))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_sign))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block3))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop_end))

def compile_run_sqisign(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,to_compile,to_run,depth,build_folder,binary_patterns):
    add_includes = []
    compile_with_cmake = 'yes'
    generic_compile_run_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile_with_cmake,add_includes,to_compile,to_run,depth,build_folder,binary_patterns)

#######################################################################################################################################################
#########################################################################  B  #########################################################################
#######################################################################################################################################################
#======================================= CLI: use argparse module ======================================================
#=======================================================================================================================

# Create a parser
parser = argparse.ArgumentParser(prog="NIST-Signature" ,description="Constant-timeness Analysis with Binsec/Rel",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# parser = argparse.ArgumentParser(
#     # ... other options ...
#     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# Create a sub-parser
subparser = parser.add_subparsers(help="",dest='binsec_test')



#Common default arguments ==============================================================================================

#Default tools list
default_tools_list = ["binsec","ctgrind"]
#Default algorithms pattern to test
default_binary_patterns = ["keypair","sign"]


# Create a parser for every function in the sub-parser namespace
#********************** List of candidates *****************************************************************************

#********************** MPC-IN-THE-HEAD ********************************************************************************
cross_init_compile_run = subparser.add_parser('compile_run_cross', help='cross: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
mira_init_compile_run = subparser.add_parser('compile_run_mira', help='mira: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
mirith_init_compile_run = subparser.add_parser('compile_run_mirith', help='mirith: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
perk_init_compile_run = subparser.add_parser('compile_run_perk', help='perk: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
mqom_init_compile_run = subparser.add_parser('compile_run_mqom', help='mqom: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ryde_init_compile_run = subparser.add_parser('compile_run_ryde', help='ryde: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
sdith_init_compile_run = subparser.add_parser('compile_run_sdith', help='sdith: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#********************** CODE *******************************************************************************************
pqsigRM_init_compile_run = subparser.add_parser('compile_run_pqsigRM', help='pqsigRM: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
less_init_compile_run = subparser.add_parser('compile_run_less', help='less: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
fuleeca_init_compile_run = subparser.add_parser('compile_run_fuleeca', help='fuleeca: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
meds_init_compile_run = subparser.add_parser('compile_run_meds', help='meds: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
Wave_init_compile_run = subparser.add_parser('compile_run_Wave', help='Wave: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#********************** LATTICE ****************************************************************************************
squirrels_init_compile_run = subparser.add_parser('compile_run_squirrels', help='squirrels: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
haetae_init_compile_run = subparser.add_parser('compile_run_haetae', help='haetae: create test harness, configuration files,\
                                    and required CMakeLists to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
EagleSign_init_compile_run = subparser.add_parser('compile_run_EagleSign', help='EagleSign: create test harness, configuration files,\
                                    and required CMakeLists to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
EHTv3v4_init_compile_run = subparser.add_parser('compile_run_EHTv3v4', help='EHTv3v4: create test harness, configuration files,\
                                    and required CMakeLists to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
hawk_init_compile_run = subparser.add_parser('compile_run_hawk', help='hawk: create test harness, configuration files,\
                                    and required CMakeLists to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
hufu_init_compile_run = subparser.add_parser('compile_run_hufu', help='hufu: create test harness, configuration files,\
                                    and required CMakeLists to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
Raccoon_init_compile_run = subparser.add_parser('compile_run_Raccoon', help='Raccoon: create test harness, configuration files,\
                                    and required CMakeLists to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#********************** MULTIVARIATE ***********************************************************************************
snova_init_compile_run = subparser.add_parser('compile_run_snova', help='snova: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
biscuit_init_compile_run = subparser.add_parser('compile_run_biscuit', help='biscuit: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
dme_sign_init_compile_run = subparser.add_parser('compile_run_dme_sign', help='dme_sign: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
hppc_init_compile_run = subparser.add_parser('compile_run_hppc', help='hppc: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
mayo_init_compile_run = subparser.add_parser('compile_run_mayo', help='mayo: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
prov_init_compile_run = subparser.add_parser('compile_run_prov', help='prov: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
qr_uov_init_compile_run = subparser.add_parser('compile_run_qr_uov', help='qr_uov: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
tuov_init_compile_run = subparser.add_parser('compile_run_tuov', help='tuov: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
uov_init_compile_run = subparser.add_parser('compile_run_uov', help='uov: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
vox_init_compile_run = subparser.add_parser('compile_run_vox', help='vox: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#********************** SYMMETRIC **************************************************************************************
aimer_init_compile_run = subparser.add_parser('compile_run_aimer', help='aimer: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

Ascon_sign_init_compile_run = subparser.add_parser('compile_run_Ascon_sign', help='Ascon_sign: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

faest_init_compile_run = subparser.add_parser('compile_run_faest', help='faest: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

sphincs_alpha_init_compile_run = subparser.add_parser('compile_run_sphincs_alpha', help='sphincs: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#********************** OTHER *******************************************************************************************
preon_init_compile_run = subparser.add_parser('compile_run_preon', help='preon: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
alteq_init_compile_run = subparser.add_parser('compile_run_alteq', help='alteq: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
emle2_0_init_compile_run = subparser.add_parser('compile_run_emle2_0', help='emle2_0: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
kaz_sign_init_compile_run = subparser.add_parser('compile_run_kaz_sign', help='kaz_sign: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
xifrat_init_compile_run = subparser.add_parser('compile_run_xifrat', help='xifrat: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#********************** ISOGENY ****************************************************************************************
sqisign_init_compile_run = subparser.add_parser('compile_run_sqisign', help='sqisign: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#######################################################################################################################################################
#########################################################################  C  #########################################################################
#######################################################################################################################################################
#[TODO:Take into account the case where api.h and sign.h are both needed in function add_cli_arguments(...)]
#********************** MPC-IN-THE-HEAD ********************************************************************************
#===================== cross ===========================================================================================
cross_default_list_of_folders = []
# cross_init_compile_run.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list)
# cross_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
# cross_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='cross')
# cross_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
# cross_init_compile_run.add_argument('--instance_folders_list', nargs='+', default=cross_default_list_of_folders)
# cross_init_compile_run.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default='"../../../Reference_Implementation/include/api.h"')
# cross_init_compile_run.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default='')
# cross_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
# cross_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')
# cross_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
# cross_init_compile_run.add_argument('--build', '-build', dest='build',default='build')
# cross_init_compile_run.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns)

add_cli_arguments('mpc-in-the-head','cross','Optimized_Implementation','"../../../Reference_Implementation/include/api.h"','""','"../../../lib/randombytes/randombytes.h"')

#===================== mira ============================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
mira_opt_folder = "mpc-in-the-head/mira/Optimized_Implementation"
mira_default_list_of_folders = os.listdir(mira_opt_folder)
mira_default_list_of_folders.remove('README.md')
mira_default_list_of_folders = get_default_list_of_folders(mira_default_list_of_folders,default_tools_list)

add_cli_arguments('mpc-in-the-head','mira','Optimized_Implementation','"../../../src/api.h"','""','"../../../lib/randombytes/randombytes.h"')


#===================== Mirith ==========================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
mirith_opt_folder = "mpc-in-the-head/mirith/Optimized_Implementation"
mirith_default_list_of_folders = os.listdir(mirith_opt_folder)
mirith_default_list_of_folders = get_default_list_of_folders(mirith_default_list_of_folders,default_tools_list)

add_cli_arguments('mpc-in-the-head','mirith','Optimized_Implementation','"../../../api.h"','"../../../sign.h"','"../../../nist/rng.h"')


#===================== perk ============================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
perk_opt_folder = "mpc-in-the-head/perk/Optimized_Implementation"
perk_default_list_of_folders = os.listdir(perk_opt_folder)
perk_default_list_of_folders.remove('README')
perk_default_list_of_folders = get_default_list_of_folders(perk_default_list_of_folders,default_tools_list)

add_cli_arguments('mpc-in-the-head','perk','Optimized_Implementation','"../../../src/api.h"','""','"../../../lib/randombytes/rng.h"')

#===================== SDITH ===========================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
sdith_opt_folder = "mpc-in-the-head/sdith/Optimized_Implementation"
sdith_default_list_of_folders = os.listdir(sdith_opt_folder)
sdith_default_list_of_folders = get_default_list_of_folders(sdith_default_list_of_folders,default_tools_list)

add_cli_arguments('mpc-in-the-head','sdith','Optimized_Implementation','"../../../../api.h"','""','"../../../../rng.h"')

#===================== mqom ============================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
mqom_opt_folder = "mpc-in-the-head/mqom/Optimized_Implementation"
mqom_default_list_of_folders = os.listdir(mqom_opt_folder)
mqom_default_list_of_folders = get_default_list_of_folders(mqom_default_list_of_folders,default_tools_list)

add_cli_arguments('mpc-in-the-head','mqom','Optimized_Implementation','"../../../api.h"','""','"../../../generator/rng.h"')

#===================== ryde ============================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
ryde_opt_folder = "mpc-in-the-head/ryde/Optimized_Implementation"
ryde_default_list_of_folders = os.listdir(ryde_opt_folder)
ryde_default_list_of_folders.remove('README')
ryde_default_list_of_folders = get_default_list_of_folders(ryde_default_list_of_folders,default_tools_list)

add_cli_arguments('mpc-in-the-head','ryde','Optimized_Implementation','"../../../src/api.h"','""', '"../../../lib/randombytes/randombytes.h"')

#********************** CODE *******************************************************************************************
#===================== pqsigRM =========================================================================================
pqsigrm_default_list_of_folders = []

add_cli_arguments('code','pqsigRM','Optimized_Implementation','"../../pqsigrm613/src/api.h"','""', '"../../pqsigrm613/src/rng.h"')

#===================== fuleeca =========================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
fuleeca_opt_folder = "code/fuleeca/Reference_Implementation"
fuleeca_default_list_of_folders = os.listdir(fuleeca_opt_folder)
fuleeca_default_list_of_folders = get_default_list_of_folders(fuleeca_default_list_of_folders,default_tools_list)

add_cli_arguments('code','fuleeca','Optimized_Implementation','"../../../Reference_Implementation/api.h"','""', '"../../../Reference_Implementation/rng.h"')

#===================== less ============================================================================================
less_default_list_of_folders = []
# less_init_compile_run.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list)
# less_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='code')
# less_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='less')
# less_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
# less_init_compile_run.add_argument('--instance_folders_list', nargs='+', default=less_default_list_of_folders)
# less_init_compile_run.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default='"../../include/api.h"')
# less_init_compile_run.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default='')
# less_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
# less_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')
# less_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
# less_init_compile_run.add_argument('--build', '-build', dest='build',default='build')
# less_init_compile_run.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns)

add_cli_arguments('code','less','Optimized_Implementation','"../../include/api.h"','""', '"../../include/rng.h"')

#===================== meds ============================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
meds_opt_folder = "code/meds/Optimized_Implementation"
meds_default_list_of_folders = os.listdir(meds_opt_folder)
meds_default_list_of_folders = get_default_list_of_folders(meds_default_list_of_folders,default_tools_list)

add_cli_arguments('code','meds','Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')

#===================== Wave ============================================================================================
#In case of second run for example, where binsec or ctgrind folder is already created by the first run
Wave_opt_folder = "code/Wave/Optimized_Implementation"
Wave_default_list_of_folders = os.listdir(Wave_opt_folder)
Wave_default_list_of_folders.remove('README.md')
Wave_default_list_of_folders.remove('AUTHORS.md')
Wave_default_list_of_folders.remove('LICENSE')
Wave_default_list_of_folders = get_default_list_of_folders(Wave_default_list_of_folders,default_tools_list)

add_cli_arguments('code','Wave','Optimized_Implementation','"../../../api.h"','""', '"../../../NIST-kat/rng.h"')

#********************** LATTICE ****************************************************************************************
#===================== squirrels =======================================================================================
#[TODO:Path to /KAT/generator/katrng.h]
squirrels_opt_folder = "lattice/squirrels/Optimized_Implementation"
squirrels_default_list_of_folders = os.listdir(squirrels_opt_folder)
squirrels_default_list_of_folders = get_default_list_of_folders(squirrels_default_list_of_folders,default_tools_list)
#print("---------GLOBAL: squirrels_default_list_of_folders",squirrels_default_list_of_folders)
squirrels_signature_type = 'lattice'
add_cli_arguments('lattice','squirrels','Optimized_Implementation','"../../../api.h"','""', '"../../../NIST-kat/rng.h"')

#===================== haetae ==========================================================================================
haetae_default_list_of_folders = []
print("---------GLOBAL: haetae_default_list_of_folders",haetae_default_list_of_folders)
# if 'binsec' in haetae_default_list_of_folders:
#     haetae_default_list_of_folders.remove('binsec')
# if 'ctgrind' in haetae_default_list_of_folders:
#     haetae_default_list_of_folders.remove('ctgrind')
# if 'ct_grind' in haetae_default_list_of_folders:
#     haetae_default_list_of_folders.remove('ct_grind')
add_cli_arguments('lattice','haetae','Optimized_Implementation','"../../include/api.h"','""', '"../../../include/randombytes.h"')

#===================== EagleSign =======================================================================================
EagleSign_opt_folder = "lattice/EagleSign/Specifications_and_Supporting_Documentation/Optimized_Implementation"
EagleSign_default_list_of_folders = os.listdir(EagleSign_opt_folder)
EagleSign_default_list_of_folders = get_default_list_of_folders(EagleSign_default_list_of_folders,default_tools_list)

add_cli_arguments('lattice','EagleSign','Specifications_and_Supporting_Documentation/Optimized_Implementation','""','"../../../sign.h"','"../../../rng.h"')

#===================== EHTv3v4 =========================================================================================
EHTv3v4_opt_folder = "lattice/EHTv3v4/Optimized_Implementation/crypto_sign"
EHTv3v4_default_list_of_folders = os.listdir(EHTv3v4_opt_folder)
EHTv3v4_default_list_of_folders = get_default_list_of_folders(EHTv3v4_default_list_of_folders,default_tools_list)

add_cli_arguments('lattice','EHTv3v4','Optimized_Implementation/crypto_sign','"../../../../api.h"','""','"../../../../rng.h"')

#===================== HAWK ============================================================================================
hawk_opt_folder = "lattice/hawk/Optimized_Implementation/avx2"
hawk_default_list_of_folders = os.listdir(hawk_opt_folder)
hawk_default_list_of_folders = get_default_list_of_folders(hawk_default_list_of_folders,default_tools_list)

add_cli_arguments('lattice','hawk','Optimized_Implementation/avx2','"../../../../api.h"','""','"../../../../rng.h"')

#===================== hufu ============================================================================================
hufu_opt_folder = "lattice/hufu/HuFu/Optimized_Implementation/crypto_sign"
hufu_default_list_of_folders = os.listdir(hufu_opt_folder)
hufu_default_list_of_folders = get_default_list_of_folders(hufu_default_list_of_folders,default_tools_list)

add_cli_arguments('lattice','hufu','Optimized_Implementation/crypto_sign','"../../../../api.h"','""','"../../../../rng.h"')
#===================== Raccoon =========================================================================================
#[TODO]
Raccoon_opt_folder = "lattice/Raccoon/Optimized_Implementation"
Raccoon_default_list_of_folders = os.listdir(Raccoon_opt_folder)
Raccoon_default_list_of_folders = get_default_list_of_folders(Raccoon_default_list_of_folders,default_tools_list)
#print("---------GLOBAL: squirrels_default_list_of_folders",squirrels_default_list_of_folders)
squirrels_signature_type = 'lattice'
add_cli_arguments('lattice','Raccoon','Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')

#********************** MULTIVARIATE ***********************************************************************************
#===================== snova ===========================================================================================
snova_opt_folder = "multivariate/snova/Optimized_Implementation"
snova_default_list_of_folders = os.listdir(snova_opt_folder)
snova_default_list_of_folders = get_default_list_of_folders(snova_default_list_of_folders,default_tools_list)

add_cli_arguments('multivariate','snova','Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')

#===================== biscuit =========================================================================================
biscuit_opt_folder = "multivariate/biscuit/Optimized_Implementation"
biscuit_default_list_of_folders = os.listdir(biscuit_opt_folder)
biscuit_default_list_of_folders = get_default_list_of_folders(biscuit_default_list_of_folders,default_tools_list)
add_cli_arguments('multivariate','biscuit','Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')


#===================== dme_sign ========================================================================================
#[TODO: each subfolder of DME-SIGN_nist-pqc-2023 has Reference_Implementation and Optimized_Implementaton folder  ]
dme_sign_opt_folder = "multivariate/dme_sign/DME-SIGN_nist-pqc-2023/dme-3rnds-8vars-32bits-sign/Optimized_Implementation"
dme_sign_default_list_of_folders = os.listdir(dme_sign_opt_folder)
dme_sign_default_list_of_folders = get_default_list_of_folders(dme_sign_default_list_of_folders,default_tools_list)
add_cli_arguments('multivariate','dme_sign','DME-SIGN_nist-pqc-2023/dme-3rnds-8vars-32bits-sign/Optimized_Implementation','"../../../api.h"')

#===================== hppc ============================================================================================
hppc_opt_folder = "multivariate/hppc/Optimized_Implementation"
hppc_default_list_of_folders = os.listdir(hppc_opt_folder)
hppc_default_list_of_folders = get_default_list_of_folders(hppc_default_list_of_folders,default_tools_list)
add_cli_arguments('multivariate','hppc','Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')

#===================== mayo ============================================================================================
#[TODO: Optimized_Implementation/src has 4 instances mayo_1, mayo_2, mayo_3 and mayo_5]
mayo_default_list_of_folders = []
add_cli_arguments('multivariate','mayo','Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')


#===================== prov ============================================================================================
prov_opt_folder = "multivariate/prov/Optimized_Implementation"
prov_default_list_of_folders = os.listdir(prov_opt_folder)
prov_default_list_of_folders = get_default_list_of_folders(prov_default_list_of_folders,default_tools_list)
add_cli_arguments('multivariate','prov','QR_UOV/Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')

#===================== qr_uov ==========================================================================================
qruov_default_list_of_folders = ["qruov1q7L10v740m100","qruov1q31L3v165m60", "qruov1q31L10v600m70", "qruov1q127L3v156m54",
                                 "qruov3q7L10v1100m140", "qruov3q31L3v246m87",  "qruov3q31L10v890m100",  "qruov3q127L3v228m78",
                                 "qruov5q7L10v1490m190", "qruov5q31L3v324m114", "qruov5q31L10v1120m120", "qruov5q127L3v306m105"]
add_cli_arguments('multivariate','qr_uov','Optimized_Implementation','"../../binsec/qruov1q7L10v740m100/portable64/api.h"','""','"../../binsec/qruov1q7L10v740m100/portable64/rng.h"')

#===================== tuov ============================================================================================
tuov_opt_folder = "multivariate/tuov/TUOV/Optimized_Implementation"
tuov_default_list_of_folders = os.listdir(tuov_opt_folder)
tuov_default_list_of_folders = get_default_list_of_folders(tuov_default_list_of_folders,default_tools_list)
tuov_default_list_of_folders.remove('tests')
tuov_default_list_of_folders.remove('nistkat')
add_cli_arguments('multivariate','tuov','Optimized_Implementation','"../../../api.h"','""', '"../../../../nistkat/rng.h"')

#===================== uov =============================================================================================
uov_opt_folder = "multivariate/uov/UOV/Optimized_Implementation"
uov_amd64_avx2_neon_folders = os.listdir(uov_opt_folder)
uov_amd64_avx2_neon_folders = get_default_list_of_folders(uov_amd64_avx2_neon_folders,default_tools_list)

uov_amd64 = uov_amd64_avx2_neon_folders[0]
uov_avx2 = uov_amd64_avx2_neon_folders[1]
uov_neon = uov_amd64_avx2_neon_folders[2]
uov_default_list_of_folders = []
abs_path_to_uov_amd64 = uov_opt_folder+"/"+uov_amd64
abs_path_to_uov_avx2 = uov_opt_folder+"/"+uov_avx2
abs_path_to_uov_neon = uov_opt_folder+"/"+uov_neon
uov_default_list_of_folders.extend([uov_amd64+"/"+subfold for subfold in os.listdir(abs_path_to_uov_amd64)])
uov_default_list_of_folders.remove(uov_amd64+"/nistkat")
uov_default_list_of_folders.extend([uov_avx2+"/"+subfold for subfold in os.listdir(abs_path_to_uov_avx2)])
uov_default_list_of_folders.remove(uov_avx2+"/nistkat")
uov_default_list_of_folders.extend([uov_neon+"/"+subfold for subfold in os.listdir(abs_path_to_uov_neon)])
uov_default_list_of_folders.remove(uov_neon+"/nistkat")

add_cli_arguments('multivariate','uov','UOV/Optimized_Implementation','"../../../../api.h"','""', '"../../../../../nistkat/rng.h"')

#===================== vox =============================================================================================
vox_opt_folder = "multivariate/vox/Additional_Implementations"
vox_avx2_flint_folders = os.listdir(vox_opt_folder)
vox_avx2_flint_folders = get_default_list_of_folders(vox_avx2_flint_folders,default_tools_list)

vox_default_list_of_folders = ["multivariate/vox/Additional_Implementations/avx2/vox_sign","multivariate/vox/Additional_Implementations/flint/vox_sign"]

add_cli_arguments('multivariate','vox','Additional_Implementations','"../../../../api.h"','""','"../../../../rng/api.h"')


#********************** SYMMETRIC **************************************************************************************
#===================== aimer ===========================================================================================
aimer_opt_folder = "symmetric/aimer/AIMer_submission/Optimized_Implementation"
aimer_default_list_of_folders = os.listdir(aimer_opt_folder)
aimer_default_list_of_folders = get_default_list_of_folders(aimer_default_list_of_folders,default_tools_list)

add_cli_arguments('symmetric','aimer','AIMer_submission/Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')

#===================== Ascon_sign ======================================================================================
ascon_opt_folder = "symmetric/Ascon_sign/Optimized_Implementation"
ascon_default_robust_and_simple_folders = os.listdir(ascon_opt_folder)
ascon_default_robust_and_simple_folders.remove('Readme')
ascon_default_robust_and_simple_folders = get_default_list_of_folders(ascon_default_robust_and_simple_folders,default_tools_list)

ascon_robust = ascon_default_robust_and_simple_folders[0]
ascon_simple = ascon_default_robust_and_simple_folders[1]
ascon_default_list_of_folders = []
abs_path_to_ascon_robust = ascon_opt_folder+"/"+ascon_robust
abs_path_to_ascon_simple = ascon_opt_folder+"/"+ascon_simple
ascon_default_list_of_folders.extend([ascon_robust+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_robust)])
ascon_default_list_of_folders.extend([ascon_simple+"/"+subfold for subfold in os.listdir(abs_path_to_ascon_simple)])

add_cli_arguments('symmetric','Ascon_sign','Optimized_Implementation','"../../../../api.h"','""', '"../../../../rng.h"')

#===================== faest ===========================================================================================
faest_opt_folder = "symmetric/faest/Additional_Implementations/avx2"
faest_default_list_of_folders = os.listdir(faest_opt_folder)
faest_default_list_of_folders = get_default_list_of_folders(faest_default_list_of_folders,default_tools_list)

add_cli_arguments('symmetric','faest','Additional_Implementations/avx2','"../../../api.h"','""', '"../../../NIST-KATs/rng.h"')

#===================== Sphincs_alpha ===================================================================================
sphincs_opt_folder = "symmetric/sphincs_alpha/Optimized_Implementation"
sphincs_default_list_of_folders = os.listdir(sphincs_opt_folder)
sphincs_default_list_of_folders = get_default_list_of_folders(sphincs_default_list_of_folders,default_tools_list)

add_cli_arguments('symmetric','sphincs_alpha','Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')


#********************** OTHER ******************************************************************************************
#===================== preon ===========================================================================================
preon_opt_folder = "other/preon/Optimized_Implementation"
preon_default_128_192_256_folders = os.listdir(preon_opt_folder)
preon_default_128_192_256_folders = get_default_list_of_folders(preon_default_128_192_256_folders,default_tools_list)

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

add_cli_arguments('other','preon','Optimized_Implementation','"../../../../api.h"','""', '"../../../../rng.h"')
#===================== alteq ===========================================================================================
#[TODO:figure out and modify path to api]
alteq_opt_folder = "other/alteq/Optimized_Implementation"
alteq_default_list_of_folders = []

add_cli_arguments('other','alteq','Optimized_Implementation','"../../../api/api.h"','""', '"../../../include/rng.h"')

#===================== emle2_0 ===================================================================================
emle2_0_opt_folder = "other/emle2_0/Additional_Implementations/aesni/crypto_sign"
emle2_0_default_list_of_folders = os.listdir(emle2_0_opt_folder)
emle2_0_default_list_of_folders = get_default_list_of_folders(emle2_0_default_list_of_folders,default_tools_list)

add_cli_arguments('other','emle2_0','Additional_Implementations/aesni/crypto_sign','"../../../../../api.h"','""', '"../../../../../rng.h"')

#===================== kaz_sign ===================================================================================
kaz_sign_opt_folder = "other/kaz_sign/Optimized_Implementation"
kaz_sign_default_list_of_folders = os.listdir(kaz_sign_opt_folder)
kaz_sign_default_list_of_folders = get_default_list_of_folders(kaz_sign_default_list_of_folders,default_tools_list)

add_cli_arguments('other','kaz_sign','Optimized_Implementation','"../../../api.h"','""', '"../../../rng.h"')

#===================== xifrat ===================================================================================
xifrat_opt_folder = "other/xifrat/Optimized_Implementation"
xifrat_default_list_of_folders = []

add_cli_arguments('other','xifrat','Optimized_Implementation','"../../../Reference_Implementation/api.h"','""', '"../../../Reference_Implementation/rng.h"')

#********************** ISOGENY ****************************************************************************************
#===================== sqisign =========================================================================================
#[TODO: to test and to round up]
sqisign_opt_folder = "isogeny/sqisign/Additional_Implementations/broadwell"
sqisign_default_list_of_folders = []

add_cli_arguments('isogeny','sqisign','Additional_Implementations/broadwell','"../../../src/nistapi/lvl1/api.h"','""', '"../../../include/rng.h"')

#######################################################################################################################################################
#########################################################################  D  #########################################################################
#######################################################################################################################################################

#set all the command-line arguments into the object args
args = parser.parse_args()
#********************** mpc-in-the-head ********************************************************************************
if args.binsec_test == "compile_run_cross":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_cross(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_mira":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_mira(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_mirith":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_mirith(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_perk":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_perk(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_mqom":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_mqom(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_ryde":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_ryde(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_sdith":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_sdith(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
#********************** CODE *******************************************************************************************
if args.binsec_test == "compile_run_pqsigRM":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_pqsigRM(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_less":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_less(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_fuleeca":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_fuleeca(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_meds":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_meds(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_Wave":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_Wave(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
#********************** LATTICE ****************************************************************************************
if args.binsec_test == "compile_run_squirrels":
    #add_cli_arguments(squirrels_signature_type,'squirrels','Optimized_Implementation','"../../include/api.h"')
    #run_cli_candidate('squirrels')
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_squirrels(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_haetae":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_haetae(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_EagleSign":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_EagleSign(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_EHTv3v4":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_EHTv3v4(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_hawk":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_hawk(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_hufu":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_hufu(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_Raccoon":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_Raccoon(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)

#********************** MULTIVARIATE ***********************************************************************************
if args.binsec_test == "compile_run_snova":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_snova(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_biscuit":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_biscuit(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_dme_sign":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_dme_sign(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_hppc":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_hppc(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_mayo":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_mayo(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_prov":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_prov(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_tuov":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_tuov(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_qr_uov":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_qr_uov(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_uov":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_uov(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_vox":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_vox(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
#********************** SYMMETRIC **************************************************************************************
if args.binsec_test == "compile_run_aimer":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_aimer(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_Ascon_sign":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_Ascon_sign(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_faest":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_faest(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_sphincs_alpha":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_sphincs_alpha(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
#********************** OTHER ****************************************************************************************
if args.binsec_test == "compile_run_preon":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_preon(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_alteq":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_alteq(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_emle2_0":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_emle2_0(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_kaz_sign":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_kaz_sign(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_xifrat":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_xifrat(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)

#********************** ISOGENY ****************************************************************************************
if args.binsec_test == "compile_run_sqisign":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    rel_path_to_rng = args.rng
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_sqisign(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,rel_path_to_rng,compile,run,depth,build_folder,binary_patterns)
