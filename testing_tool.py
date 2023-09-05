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


class GenericPatterns(object):
    def __init__(self,tool_type,test_harness_keypair="test_harness_crypto_sign_keypair",test_harness_sign="test_harness_crypto_sign",ctgrind_taint = "taint"):
        self.tool_type = tool_type
        self.binsec_test_harness_keypair = test_harness_keypair
        self.binsec_test_harness_sign = test_harness_sign
        self.binsec_configuration_file_keypair = "cfg_keypair"
        self.binsec_configuration_file_sign = "cfg_sign"
        self.ctgrind_taint = ctgrind_taint



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

# abs_path_to_api_or_sign = "other/preon/Optimized_Implementation/Preon128/Preon128A/api.h"
# sign_find_args_types_and_names(abs_path_to_api_or_sign)

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
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
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
        if not sign == "":
            t_harness_file.write(f'#include {sign}\n')
        if not api == "":
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
        if not sign == "":
            t_file.write(f'#include {sign}\n')
        if not api == "":
            t_file.write(f'#include {api}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))



def ctgrind_sign_taint_content1(taint_file,api,sign,add_includes,function_return_type,function_name,args_types,args_names):
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
    {args_types[2]} *{args_names[2]};
    {args_types[3]} *{args_names[3]};
    {args_types[4]} *{args_names[4]};
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \trandombytes({args_names[1]}, 1 * sizeof({args_types[1]}));
    \trandombytes({args_names[0]}, (*{args_names[1]}) * sizeof({args_types[0]}));
    \trandombytes(&{args_names[3]}, 1 * sizeof({args_types[3]}));
    \trandombytes({args_names[2]}, (*{args_names[3]}) * sizeof({args_types[2]}));
    \trandombytes({args_names[4]}, CRYPTO_SECRETKEYBYTES* sizeof({args_types[4]}));
    }}
    
    int main() {{
    \t{args_names[1]} = calloc(1, sizeof({args_types[1]}));
    \t{args_names[0]} = calloc(*{args_names[1]}, sizeof({args_types[0]}));
    \t{args_names[3]} = calloc(1, sizeof({args_types[3]})); 
    \t{args_names[2]} = calloc({args_names[3]}, sizeof({args_types[2]}));
    \t{args_names[4]} = calloc(CRYPTO_SECRETKEYBYTES, sizeof({args_types[4]})); 

    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\tgenerate_test_vectors();
    \t\tct_poison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\t{function_return_type} result = {function_name}({args_names[0]}, {args_names[1]}, {args_names[2]}, *{args_names[3]}, {args_names[4]}); 
    \t\tct_unpoison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t}}

    \tfree({args_names[0]});
    \tfree({args_names[1]});
    \tfree({args_names[2]});
    \tfree({args_names[3]});
    \tfree({args_names[4]});
    \treturn 0;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        if not sign == "":
            t_file.write(f'#include {sign}\n')
        if not api == "":
            t_file.write(f'#include {api}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


def ctgrind_sign_taint_content_MODIFY_2_sept(taint_file,api,sign,add_includes,function_return_type,function_name,args_types,args_names):
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
    {args_types[2]} *{args_names[2]};
    {args_types[3]} {args_names[3]};
    {args_types[4]} *{args_names[4]};
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \t{args_types[3]} *message_length_p;
    \trandombytes(message_length_p, 1 * sizeof({args_types[3]}));
    \t{args_names[3]}   =  *message_length_p ; 
    \t//randombytes(&{args_names[3]}, 1 * sizeof({args_types[3]}));
    \trandombytes({args_names[2]}, {args_names[3]} * sizeof({args_types[2]}));
    \trandombytes({args_names[4]}, CRYPTO_SECRETKEYBYTES* sizeof({args_types[4]}));
    \t{args_types[1]} signature_message_length = CRYPTO_BYTES + {args_names[3]};
    \t{args_names[1]} = &signature_message_length;
    }}
    
    int main() {{
    
    \t{args_names[2]} = calloc({args_names[3]}, sizeof({args_types[2]}));
    \t{args_names[4]} = calloc(CRYPTO_SECRETKEYBYTES, sizeof({args_types[4]}));
    \t{args_names[1]} = calloc(1, sizeof({args_types[1]}));
    \t{args_names[0]} = calloc(*{args_names[1]}, sizeof({args_types[0]})); 

    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\tgenerate_test_vectors();
    \t\tct_poison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\t{function_return_type} result = {function_name}({args_names[0]}, {args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]}); 
    \t\tct_unpoison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t}}

    \tfree({args_names[0]});
    \tfree({args_names[1]});
    \tfree({args_names[2]});
    \tfree({args_names[4]});
    \treturn 0;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        if not sign == "":
            t_file.write(f'#include {sign}\n')
        if not api == "":
            t_file.write(f'#include {api}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


def ctgrind_sign_taint_content_modify_3_spt(taint_file,api,sign,add_includes,function_return_type,function_name,args_types,args_names):
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
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} *{args_names[1]};
    {args_types[2]} *{args_names[2]};
    {args_types[3]} {args_names[3]};
    {args_types[4]} *{args_names[4]};
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \tsrand(time(NULL));
    \t{args_names[3]} = rand(); 
    \t{args_names[3]} = 1024 ;//256 ; 
    \tfor ({args_types[3]} i=0;i<{args_names[3]};i++){{
    \t\t{args_types[2]} val = rand() &0xFF;
    \t\t{args_names[2]}[i] = val;
    \t}}
    \tfor (size_t i=0;i<CRYPTO_SECRETKEYBYTES;i++){{
    \t\t{args_types[4]} val = rand() &0xFF;
    \t\t{args_names[4]}[i] = val;
    \t}}
    \t*{args_names[1]} = {args_names[3]} + CRYPTO_BYTES ;
    }} 
    
    int main() {{
    
    \t{args_names[2]} = ({args_types[2]} *)calloc({args_names[3]}, sizeof({args_types[2]}));
    \t{args_names[4]} = ({args_types[4]} *)calloc(CRYPTO_SECRETKEYBYTES, sizeof({args_types[4]}));
    \t{args_names[1]} = ({args_types[1]} *)calloc(1, sizeof({args_types[1]}));
    \t{args_names[0]} = ({args_types[0]} *)calloc(*{args_names[1]}, sizeof({args_types[0]})); 

    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\tgenerate_test_vectors(); 
    \t\tct_poison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\t{function_return_type} result = {function_name}({args_names[0]}, {args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]}); 
    \t\tct_unpoison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t}}

    \tfree({args_names[0]});
    \tfree({args_names[1]});
    \tfree({args_names[2]});
    \tfree({args_names[4]});
    \treturn result;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        if not sign == "":
            t_file.write(f'#include {sign}\n')
        if not api == "":
            t_file.write(f'#include {api}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))



def ctgrind_sign_taint_content(taint_file,api,sign,add_includes,function_return_type,function_name,args_types,args_names):
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
    #define message_length_define 256
    
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} *{args_names[1]};
    {args_types[2]} {args_names[2]}[message_length_define];
    {args_types[3]} {args_names[3]} = message_length_define;
    {args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES];
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \tsrand(time(NULL));
    \t//{args_names[3]} = rand(); 
    \t//{args_names[3]} = 1024 ;//256 ; 
    \tfor ({args_types[3]} i=0;i<{args_names[3]};i++){{
    \t\t{args_types[2]} val = rand() &0xFF;
    \t\t{args_names[2]}[i] = val;
    \t}}
    \tfor (size_t i=0;i<CRYPTO_SECRETKEYBYTES;i++){{
    \t\t{args_types[4]} val = rand() &0xFF;
    \t\t{args_names[4]}[i] = val;
    \t}}
    \t//*{args_names[1]} = {args_names[3]} + CRYPTO_BYTES ;
    }} 
    
    int main() {{
    
    \t//{args_names[2]} = ({args_types[2]} *)calloc({args_names[3]}, sizeof({args_types[2]}));
    \t//{args_names[4]} = ({args_types[4]} *)calloc(CRYPTO_SECRETKEYBYTES, sizeof({args_types[4]}));
    \t{args_names[1]} = ({args_types[1]} *)calloc(1, sizeof({args_types[1]}));
    \t{args_names[0]} = ({args_types[0]} *)calloc(*{args_names[1]}, sizeof({args_types[0]})); 
    
    \t{function_return_type} result = 2 ; 
    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\tgenerate_test_vectors(); 
    \t\tct_poison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tresult = {function_name}({args_names[0]}, {args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]}); 
    \t\tct_unpoison({args_names[4]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t}}

    \tfree({args_names[0]}); 
    \tfree({args_names[1]});
    \t//free({args_names[2]});
    \t//free({args_names[4]});
    \treturn result;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        if not sign == "":
            t_file.write(f'#include {sign}\n')
        if not api == "":
            t_file.write(f'#include {api}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))



# test_harness_file = "try_test_harness.c"
# api= '"include/api.h"'
# sign = ""
# add_includes = ['"encrypt.h"']
# args_types = ['int', 'uint8_t', 'unsigned char','int','int']
# args_names = ['msg','len','msg_len', 'sk', 'pk']
# sign_test_harness_content(test_harness_file,api,sign,add_includes,args_types,args_names)

#==========================================CONFIGURATION FILES =========================================================
#=======================================================================================================================
#=======================================================================================================================

def sign_configuration_file_content(cfg_file_sign,crypto_sign_args_names):
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


def cfg_content_keypair(cfg_file_keypair):
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

#Create same sub-folders in each folder of a given list of folders
def create_tests_folders(path_to_common_folder,test_folders_list,subfolder_basenames_list):
    for t_folder in test_folders_list:
        full_path_to_test_folder = path_to_common_folder+'/'+t_folder
        if not os.path.isdir(full_path_to_test_folder):
            cmd = ["mkdir","-p",full_path_to_test_folder]
            subprocess.call(cmd, stdin = sys.stdin)
        for subfold in subfolder_basenames_list:
            full_path_to_sub_folder = full_path_to_test_folder+'/'+subfold
            if not os.path.isdir(full_path_to_sub_folder):
                cmd = ["mkdir","-p",full_path_to_sub_folder]
                subprocess.call(cmd, stdin = sys.stdin)

def generic_create_tests_folders1(path_to_common_folder,test_folders_list,main_subfolder_basename,subfolder_basenames_list):
    for t_folder in test_folders_list:
        full_path_to_test_folder = path_to_common_folder+'/'+t_folder
        if not os.path.isdir(full_path_to_test_folder):
            cmd = ["mkdir","-p",full_path_to_test_folder]
            subprocess.call(cmd, stdin = sys.stdin)
        for subfold in subfolder_basenames_list:
            full_path_to_sub_folder = full_path_to_test_folder+'/'+subfold
            if not main_subfolder_basename == "":
                full_path_to_sub_folder = full_path_to_test_folder+'/'+main_subfolder_basename+'/'+subfold
            if not os.path.isdir(full_path_to_sub_folder):
                cmd = ["mkdir","-p",full_path_to_sub_folder]
                subprocess.call(cmd, stdin = sys.stdin)


def generic_create_tests_folders(list_of_path_to_folders):
    for t_folder in list_of_path_to_folders:
        if not os.path.isdir(t_folder):
            cmd = ["mkdir","-p",t_folder]
            subprocess.call(cmd, stdin = sys.stdin)


# path_to_common_folder = "other/preon/Optimized_Implementation"
# test_folders_list = ["binsec","ctgrind","flowtracker","dudect"]
# subfolder_basenames_list = ["keypair","sign"]
# create_tests_folders(path_to_common_folder,test_folders_list,subfolder_basenames_list)



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
def run_binsec(executable_file,cfg_file,stats_files,output_file,depth):
    command = f'''binsec -checkct -checkct-depth  {depth}   -checkct-script  {cfg_file} 
               -checkct-stats-file   {stats_files}  {executable_file} '''
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file,"w") as file:
        for line in output_decode.split('\n'):
            file.write(line+'\n')
def run_binsec_deprecated(executable_file,cfg_file,stats_files,output_file,depth):
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


def binsec_run_signature_candidate_compiled_with_makefile(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth,binary_patterns):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
    for subfold in opt_src_folder_list_dir:
        path_to_subfolder = binsec_folder_full_path+'/'+subfold
        for bin_pattern in binary_patterns:
            #run crypto_sign_keypair
            binsec_folder_basename = f'{candidate}_keypair'
            binsec_folder = f'{path_to_subfolder}/{binsec_folder_basename}'
            path_to_binary = f'{binsec_folder}/test_harness_crypto_sign_keypair'
            if bin_pattern == "sign":
                path_to_binary = f'{binsec_folder}/test_harness_crypto_sign'
            stats_file = f'{binsec_folder}/{bin_pattern}.toml'
            output_file = f'{binsec_folder}/{bin_pattern}_output.txt'
            cfg_file =  find_ending_pattern(binsec_folder,cfg_pattern)
            print("------Running binary file: {} ---- ".format(path_to_binary))
            run_binsec(path_to_binary,cfg_file,stats_file,output_file,depth)


def ctgrind_run_signature_candidate(ctgrind_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,binary_patterns):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    ctgrind_folder_full_path = optimized_imp_folder_full_path+'/'+ctgrind_folder
    for subfold in opt_src_folder_list_dir:
        path_to_subfolder = ctgrind_folder_full_path+'/'+subfold
        for bin_pattern in binary_patterns:
            ctgrind_folder_basename = f'{candidate}_{bin_pattern}'
            ctgrind_folder = f'{path_to_subfolder}/{ctgrind_folder_basename}'
            output_file = f'{ctgrind_folder}/{bin_pattern}_output.txt'
            path_to_binary = f'{ctgrind_folder}/taint_crypto_sign_keypair.o'
            if bin_pattern == "sign":
                path_to_binary = f'{ctgrind_folder}/taint_crypto_sign.o'
            print("------Running binary file: {} ---- ".format(path_to_binary))
            run_ctgrind(path_to_binary,output_file)

def binsec_generic_run_modify_5_sept(binsec_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,depth,build_folder,binary_patterns):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    binsec_folder_full_path = optimized_imp_folder_full_path+'/'+binsec_folder
    cfg_pattern = ".cfg"
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
                run_binsec(executable,cfg_file,stats_file,output_file,depth)

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

def ctgrind_generic_run_modify_5_sept(ctgrind_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,build_folder,binary_patterns):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    ctgrind_folder_full_path = optimized_imp_folder_full_path+'/'+ctgrind_folder
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
                run_ctgrind(abs_path_to_executable,output_file)

def ctgrind_generic_run(ctgrind_folder,signature_type,candidate,optimized_imp_folder,opt_src_folder_list_dir,build_folder,binary_patterns):
    optimized_imp_folder_full_path = signature_type+'/'+candidate+'/'+optimized_imp_folder
    ctgrind_folder_full_path = optimized_imp_folder_full_path+'/'+ctgrind_folder
    if opt_src_folder_list_dir == []:
        path_to_subfolder = ctgrind_folder_full_path
        path_to_build_folder = path_to_subfolder
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
def find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign):
    api_relative = rel_path_to_api
    sign_relative = rel_path_to_sign
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
    return api_relative,sign_relative

def find_api_sign_abs_path(path_to_opt_src_folder,api,sign,opt_implementation_name,ref_implementation_name = "Reference_Implementation"):
    folder = path_to_opt_src_folder
    ref_implementation_name.strip()
    opt_implementation_name.strip()
    api_folder = ""
    sign_folder = ""
    abs_path_to_api_or_sign = ""
    if not api == "":
        print("----Into find_api_sign_abs_path:api ---",api)
        print("---api NOT NUL")
        print("--folder----",folder)
        api_folder_split = api.split("../")
        print("--api_folder_split----",api_folder_split)
        api_folder = api_folder_split[-1]
        print("--api_folder: 1----",api_folder)
        api_folder = api_folder.split('"')
        print("--api_folder: 2----",api_folder)
        api_folder = api_folder[0]
        print("--api_folder: 3----",api_folder)
        abs_path_to_api_or_sign = f'{folder}/{api_folder}'
        print("--abs_path_to_api_or_sign----",abs_path_to_api_or_sign)
    if not sign == "":
        print("---sign NOT NUL")
        sign_folder_split = sign.split("../")
        sign_folder = sign_folder_split[-1]
        sign_folder = sign_folder.split('"')
        sign_folder = sign_folder[0]
        abs_path_to_api_or_sign = f'{folder}/{sign_folder}'
    if ref_implementation_name in abs_path_to_api_or_sign:
        print("**********ref_implementation_name**************",ref_implementation_name)
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



def ctgrind_initialize_candidate(path_to_opt_src_folder,path_to_ctgrind_folder,path_to_ctgrind_keypair_folder,path_to_ctgrind_sign_folder,api,sign,add_includes):
    list_of_path_to_folders = [path_to_ctgrind_folder,path_to_ctgrind_keypair_folder,path_to_ctgrind_sign_folder]
    generic_create_tests_folders(list_of_path_to_folders)
    tool_type = "ctgrind"
    opt_implementation_name = os.path.basename(path_to_opt_src_folder)
    abs_path_to_api_or_sign = find_api_sign_abs_path(path_to_opt_src_folder,api,sign,opt_implementation_name)
    print("------Into ctgrind_initialize_candidate:abs_path_to_api_or_sign -----",abs_path_to_api_or_sign)
    ctgrind_tool = GenericPatterns(tool_type)
    taint_keypair_basename = f'{ctgrind_tool.ctgrind_taint}.c'
    test_sign_basename = f'{ctgrind_tool.ctgrind_taint}.c'
    taint_keypair = f'{path_to_ctgrind_keypair_folder}/{taint_keypair_basename}'
    return_type,f_basename,args_types,args_names =  keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    ctgrind_keypair_taint_content(taint_keypair,api,sign,add_includes,return_type,f_basename,args_types,args_names)
    taint_sign = f'{path_to_ctgrind_sign_folder}/{test_sign_basename}'
    return_type,f_basename,args_types,args_names =  sign_find_args_types_and_names(abs_path_to_api_or_sign)
    ctgrind_sign_taint_content(taint_sign,api,sign,add_includes,return_type,f_basename,args_types,args_names)


def initialize_nist_candidate_modify_4_sept(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,add_includes):
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
        path_to_instance = path_to_binsec_folder+'/'+instance_folder
        path_to_binsec_keypair_folder = path_to_instance+'/'+binsec_keypair_folder_basename
        path_to_binsec_sign_folder = path_to_instance+'/'+binsec_sign_folder_basename
        binsec_initialize_candidate(path_to_opt_src_folder,path_to_binsec_folder,path_to_binsec_keypair_folder,path_to_binsec_sign_folder,api,sign,add_includes)
    if ctgrind or 'ct_grind' in tools_list_lowercase:
        path_to_ctgrind_folder = path_to_opt_src_folder+'/'+ctgrind_folder
        ctgrind_keypair_folder_basename = candidate+'_keypair'
        ctgrind_sign_folder_basename = candidate+'_sign'
        path_to_instance = path_to_ctgrind_folder+'/'+instance_folder
        path_to_ctgrind_keypair_folder = path_to_instance+'/'+ctgrind_keypair_folder_basename
        path_to_ctgrind_sign_folder = path_to_instance+'/'+ctgrind_sign_folder_basename
        ctgrind_initialize_candidate(path_to_opt_src_folder,path_to_ctgrind_folder,path_to_ctgrind_keypair_folder,path_to_ctgrind_sign_folder,api,sign,add_includes)

def initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,add_includes):
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
        ctgrind_initialize_candidate(path_to_opt_src_folder,path_to_ctgrind_folder,path_to_ctgrind_keypair_folder,path_to_ctgrind_sign_folder,api,sign,add_includes)


def generic_initialize_nist_candidate_modify_4_sept(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes):
    for instance_folder in instance_folders_list:
        api, sign = find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign)
        print("---api----",api)
        print("---sign----",sign)
        initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,add_includes)

def generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes):
    if instance_folders_list == []:
        instance_folder = ""
        api, sign = find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign)
        initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,add_includes)
    else:
        for instance_folder in instance_folders_list:
            api, sign = find_candidate_instance_api_sign_relative_path(instance_folder,rel_path_to_api,rel_path_to_sign)
            print("---api----",api)
            print("---sign----",sign)
            initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folder,api,sign,add_includes)


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


def init_compile_nist_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign, \
                                build_folder,path_to_cmakelist_file,path_to_makefile,path_to_build_folder,add_includes):
    init_nist_signature_candidate(binsec_folder,signature_type,candidate,optimized_imp_folder,src_folder,api,sign,add_includes)
    compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile,path_to_build_folder)




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
        \t$(CC) ${{LIBDIR}} $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -L. -lctgrind 
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).o $(OBJ)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) ${{LIBDIR}} $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -L. -lctgrind -lcrypto -lssl
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



def init_compile_mirith(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    for instance in instance_folders_list:
        generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
        for tool_type in tools_list:
            path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type+'/'+instance
            makefile_mirith(path_to_makefile_folder,instance,tool_type,candidate)
            compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)

def run_mirith(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns):
    generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)

def compile_run_mirith(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        init_compile_mirith(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        init_compile_mirith(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)


#========================================== PERK ======================================================================
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
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS)  $^ $(PERK_INCLUDE) -o $(BUILD)/$@ $^ $(LDFLAGS) -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind #-lcrypto -lssl
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c  $(PERK_OBJS) $(LIB_OBJS)
        \t@echo -e "### Compiling PERK Taint sign"
        \t@mkdir -p $(dir $@)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS)  $^ $(PERK_INCLUDE) -o $(BUILD)/$@ $^ $(LDFLAGS) -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind #-lcrypto -lssl
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




def compile_perk(path_to_makefile):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make","all"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)


def init_compile_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    for instance in instance_folders_list:
        generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
        for tool_type in tools_list:
            path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type+'/'+instance
            makefile_perk(path_to_makefile_folder,instance,tool_type,candidate)
            compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)


def compile_run_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        init_compile_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        init_compile_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)


# binsec_folder = "binsec"
# ctgrind_folder = "ctgrind"
# dudect_folder = ""
# flowTracker_folder = ""
# signature_type = "mpc-in-the-head"
# candidate = "perk"
# optimized_imp_folder =  "Optimized_Implementation"
# instance_folders_list = ["perk-128-fast-3"]
# #instance_folders_list = ["broadwell"]
# #api = '"../../../MIRA-128f/src/api.h"'
# sign = ''
# api = '"../../../src/api.h"'
# add_includes = []
# #tools_list = ['binsec','ctgrind']
# tools_list = ['binsec']
# depth = 100
# build_folder = "build"
# binary_patterns = ["sign"]
# init_compile_perk(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,api,sign)



#========================================== MQOM ======================================================================
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
        \t$(CC) $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(CT_GRIND_FLAGS) $(ALL_FLAGS) -L$(HASH_PATH) -L. -lhash -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(CT_GRIND_FLAGS) $(ALL_FLAGS) -L$(HASH_PATH) -L. -lhash -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl -o $(BUILD)/$@
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

def init_compile_mqom(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    for instance in instance_folders_list:
        generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
        for tool_type in tools_list:
            path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type+'/'+instance
            makefile_mqom(path_to_makefile_folder,instance,tool_type,candidate)
            compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder)


def compile_run_mqom(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        init_compile_mqom(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        init_compile_mqom(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)



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
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(SRC_KEYPAIR) $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@ -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
    
        $(EXECUTABLE_SIGN): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build {test_harness_sign}
        \t@echo -e "### Compiling {taint} for sign"
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(SRC_SIGN) $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) -o $(BUILD)/$@ -L. $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
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



def compile_ryde(path_to_makefile):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    cmd = ["make","all"]
    subprocess.call(cmd, stdin = sys.stdin)
    os.chdir(cwd)

def init_compile_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    for instance in instance_folders_list:
        generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
        for tool_type in tools_list:
            path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type+'/'+instance
            makefile_ryde(path_to_makefile_folder,instance,tool_type,candidate)
            compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder,"all")


def compile_run_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        init_compile_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        init_compile_ryde(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)



#========================================== MIRA ======================================================================

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
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl -o $(BUILD)/$@ 

        $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders 
        \t@echo -e "### Compiling MIRA-128F (taint sign)"
        \t$(CC) $(CT_GRIND_FLAGS) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^) $(INCLUDE) $(XKCP_LINKER) $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl -o $(BUILD)/$@
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

def init_compile_mira(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
    path_to_cmakelist_file = ""
    path_to_build_folder = ""
    add_includes = []
    for instance in instance_folders_list:
        generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
        for tool_type in tools_list:
            path_to_makefile_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type+'/'+instance
            makefile_mira(path_to_makefile_folder,instance,tool_type,candidate)
            compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_cmakelist_file,path_to_makefile_folder,path_to_build_folder,"all")


def compile_run_mira(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        init_compile_mira(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        init_compile_mira(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)




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
                #target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static) 
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
                 #target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
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



def init_compile_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign):
    path_to_makefile_folder = ""
    path_to_build_folder = ""
    add_includes = []
    generic_initialize_nist_candidate(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,add_includes)
    for tool_type in tools_list:
        path_to_tool_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder+'/'+tool_type
        path_to_opt_src_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
        path_to_cmake_lists = path_to_tool_folder+'/'+'CMakeLists.txt'
        cmake_cross(path_to_cmake_lists,tool_type,candidate)
        path_to_build_folder = path_to_tool_folder+'/build'
        if not os.path.isdir(path_to_build_folder):
            cmd = ["mkdir","-p",path_to_build_folder]
            subprocess.call(cmd, stdin = sys.stdin)
        compile_nist_signature_candidate_with_cmakelists_or_makefile(path_to_build_folder,path_to_makefile_folder,path_to_build_folder)


def compile_run_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,to_compile,to_run,depth,build_folder,binary_patterns):
    if 'y' in to_compile.lower() and 'y' in to_run.lower():
        init_compile_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)
    elif 'y' in to_compile.lower() and 'n' in to_run.lower():
        init_compile_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign)
    if 'n' in to_compile.lower() and 'y' in to_run.lower():
        generic_run(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,depth,build_folder,binary_patterns)


# # binsec_folder = "binsec"
# # ctgrind_folder = "ctgrind"
# dudect_folder = ""
# flowTracker_folder = ""
# signature_type = "mpc-in-the-head"
# candidate = "cross"
# optimized_imp_folder =  "Optimized_Implementation"
# instance_folders_list = []
# #instance_folders_list = ["broadwell"]
# #api = '"../../../MIRA-128f/src/api.h"'
# sign = ''
# api = '"../../../Reference_Implementation/include/api.h"'
# add_includes = []
# #tools_list = ['binsec','ctgrind']
# tools_list = ['ctgrind']
# depth = 100
# build_folder = "build"
# binary_patterns = ["sign"]
# init_compile_cross(tools_list,signature_type,candidate,optimized_imp_folder,instance_folders_list,api,sign)
#




#======================================= CLI: use argparse module ======================================================
#=======================================================================================================================

# Create a parser
parser = argparse.ArgumentParser(prog="NIST-Signature" ,description="Constant-timeness Analysis with Binsec/Rel")
# Create a sub-parser
subparser = parser.add_subparsers(dest='binsec_test')



#Common default arguments ==============================================================================================

#Default tools list
default_tools_list = ["binsec","ctgrind"]
#Default algorithms pattern to test
default_binary_patterns = ["keypair","sign"]


# Create a parser for every function in the sub-parser namespace
#********************** List of candidates *******************************************************************************

cross_init_compile_run = subparser.add_parser('compile_run_cross', help='cross: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')
mira_init_compile_run = subparser.add_parser('compile_run_mira', help='mira: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')
mirith_init_compile_run = subparser.add_parser('compile_run_mirith', help='mirith: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')
perk_init_compile_run = subparser.add_parser('compile_run_perk', help='perk: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')
mqom_init_compile_run = subparser.add_parser('compile_run_mqom', help='mqom: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')
ryde_init_compile_run = subparser.add_parser('compile_run_ryde', help='ryde: create test harness, configuration files,\
                                    and required Makefile to compile   (and) run binsec )')



#===================== cross ============================================================================================
cross_default_list_of_folders = []
cross_init_compile_run.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list)
cross_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
cross_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='cross')
cross_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
cross_init_compile_run.add_argument('--instance_folders_list', nargs='+', default=cross_default_list_of_folders)
cross_init_compile_run.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default='"../../../Reference_Implementation/include/api.h"')
cross_init_compile_run.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default='')
cross_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
cross_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')
cross_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
cross_init_compile_run.add_argument('--build', '-build', dest='build',default='build')
cross_init_compile_run.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns)

#===================== mira ============================================================================================
mira_opt_folder = "mpc-in-the-head/mira/Optimized_Implementation"
mira_default_list_of_folders = os.listdir(mira_opt_folder)
mira_default_list_of_folders.remove('README.md')
if 'binsec' in mira_default_list_of_folders:
    mira_default_list_of_folders.remove('binsec')
if 'ctgrind' in mira_default_list_of_folders:
    mira_default_list_of_folders.remove('ctgrind')
if 'ct_grind' in mira_default_list_of_folders:
    mira_default_list_of_folders.remove('ct_grind')

mira_init_compile_run.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list)
mira_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
mira_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='mira')
mira_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
mira_init_compile_run.add_argument('--instance_folders_list', nargs='+', default=mira_default_list_of_folders)
mira_init_compile_run.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default='"../../../src/api.h"')
mira_init_compile_run.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default='')
mira_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
mira_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')
mira_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
mira_init_compile_run.add_argument('--build', '-build', dest='build',default='build')
mira_init_compile_run.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns)



#===================== Mirith ==========================================================================================
mirith_opt_folder = "mpc-in-the-head/mirith/Optimized_Implementation"
mirith_default_list_of_folders = os.listdir(mirith_opt_folder)
if 'binsec' in mirith_default_list_of_folders:
    mirith_default_list_of_folders.remove('binsec')
if 'ctgrind' in mirith_default_list_of_folders:
    mirith_default_list_of_folders.remove('ctgrind')
if 'ct_grind' in mirith_default_list_of_folders:
    mirith_default_list_of_folders.remove('ct_grind')


mirith_init_compile_run.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list)
mirith_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
mirith_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='mirith')
mirith_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
mirith_init_compile_run.add_argument('--instance_folders_list', nargs='+', default=mirith_default_list_of_folders)
mirith_init_compile_run.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default='"../../../api.h"')
mirith_init_compile_run.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default='"../../../sign.h"')
mirith_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
mirith_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')
mirith_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
mirith_init_compile_run.add_argument('--build', '-build', dest='build',default='build')
mirith_init_compile_run.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns)



#===================== perk ============================================================================================
perk_opt_folder = "mpc-in-the-head/perk/Optimized_Implementation"
perk_default_list_of_folders = os.listdir(perk_opt_folder)
perk_default_list_of_folders.remove('README')
if 'binsec' in perk_default_list_of_folders:
    perk_default_list_of_folders.remove('binsec')
if 'ctgrind' in perk_default_list_of_folders:
    perk_default_list_of_folders.remove('ctgrind')
if 'ct_grind' in perk_default_list_of_folders:
    perk_default_list_of_folders.remove('ct_grind')

perk_init_compile_run.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list)
perk_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
perk_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='perk')
perk_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
perk_init_compile_run.add_argument('--instance_folders_list', nargs='+', default=perk_default_list_of_folders)
perk_init_compile_run.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default='"../../../src/api.h"')
perk_init_compile_run.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default='')
perk_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
perk_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')
perk_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
perk_init_compile_run.add_argument('--build', '-build', dest='build',default='build')
perk_init_compile_run.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns)




#===================== mqom ============================================================================================
mqom_opt_folder = "mpc-in-the-head/mqom/Optimized_Implementation"
mqom_default_list_of_folders = os.listdir(mqom_opt_folder)
if 'binsec' in mqom_default_list_of_folders:
    mqom_default_list_of_folders.remove('binsec')
if 'ctgrind' in mqom_default_list_of_folders:
    mqom_default_list_of_folders.remove('ctgrind')
if 'ct_grind' in mqom_default_list_of_folders:
    mqom_default_list_of_folders.remove('ct_grind')

mqom_init_compile_run.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list)
mqom_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
mqom_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='mqom')
mqom_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
mqom_init_compile_run.add_argument('--instance_folders_list', nargs='+', default=mqom_default_list_of_folders)
mqom_init_compile_run.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default='"../../../api.h"')
mqom_init_compile_run.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default='')
mqom_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
mqom_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')
mqom_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
mqom_init_compile_run.add_argument('--build', '-build', dest='build',default='build')
mqom_init_compile_run.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns)


#===================== ryde ============================================================================================
ryde_opt_folder = "mpc-in-the-head/ryde/Optimized_Implementation"
ryde_default_list_of_folders = os.listdir(ryde_opt_folder)
ryde_default_list_of_folders.remove('README')
if 'binsec' in ryde_default_list_of_folders:
    ryde_default_list_of_folders.remove('binsec')
if 'ctgrind' in ryde_default_list_of_folders:
    ryde_default_list_of_folders.remove('ctgrind')
if 'ct_grind' in ryde_default_list_of_folders:
    ryde_default_list_of_folders.remove('ct_grind')

ryde_init_compile_run.add_argument('--tools','-tools' ,dest='tools', nargs='+', default=default_tools_list)
ryde_init_compile_run.add_argument('--signature_type', '-type',dest='type',type=str,default='mpc-in-the-head')
ryde_init_compile_run.add_argument('--candidate', '-candidata',dest='candidate',type=str,default='ryde')
ryde_init_compile_run.add_argument('--optimization_folder', '-opt_folder',dest='ref_opt', type=str,default='Optimized_Implementation')
ryde_init_compile_run.add_argument('--instance_folders_list', nargs='+', default=mqom_default_list_of_folders)
ryde_init_compile_run.add_argument('--rel_path_to_api', '-api',dest='api',type=str, default='"../../../src/api.h"')
ryde_init_compile_run.add_argument('--rel_path_to_sign', '-sign', dest='sign',type=str,default='')
ryde_init_compile_run.add_argument('--compile', '-c', dest='compile',default='Yes')
ryde_init_compile_run.add_argument('--run', '-r', dest='run',default='Yes')
ryde_init_compile_run.add_argument('--depth', '-depth', dest='depth',default="1000000")
ryde_init_compile_run.add_argument('--build', '-build', dest='build',default='build')
ryde_init_compile_run.add_argument('--algorithms_patterns', nargs='+', default=default_binary_patterns)

#set all the command-line arguments into the object args
args = parser.parse_args()
if args.binsec_test == "compile_run_cross":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_cross(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_mira":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_mira(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_mirith":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_mirith(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_perk":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_perk(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_mqom":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_mqom(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,compile,run,depth,build_folder,binary_patterns)
if args.binsec_test == "compile_run_ryde":
    tools_list = args.tools
    signature_type = args.type
    candidate = args.candidate
    optimization_folder = args.ref_opt
    instance_folders_list = args.instance_folders_list
    rel_path_to_api = args.api
    rel_path_to_sign = args.sign
    compile = args.compile
    run = args.run
    depth = args.depth
    build_folder = args.build
    binary_patterns = args.algorithms_patterns
    compile_run_ryde(tools_list,signature_type,candidate,optimization_folder,instance_folders_list,rel_path_to_api,rel_path_to_sign,compile,run,depth,build_folder,binary_patterns)