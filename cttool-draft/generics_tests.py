#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import subprocess
import sys
import textwrap
import re
import json

from typing import Optional, Union, List

import generics as gen
import utils as util


def parse_json_to_dict_generic_tests(path_to_json_file: str):
    with open(path_to_json_file) as json_file:
        data = json.load(json_file)
        targets = data['targets']
        tools = data['tools']
        return targets, tools


def find_target_by_basename1(target_basename: str, path_to_target_header_file: str) -> str:
    target = ''
    try:
        with open(path_to_target_header_file, 'r') as file:
            file_content = file.read()
            find_target_object = re.search(rf"[\w\s]*\W{target_basename}\W[\s*\(]*[\w\s*,\[\+\]\(\)-]*;", file_content)
            if find_target_object is not None:
                matching_string = find_target_object.group()
                matching_string_lines = matching_string.split('\n')
                target_basename_nb_of_occurrence = matching_string.count(target_basename)
                if target_basename_nb_of_occurrence >= 2:
                    for line in matching_string_lines:
                        if target_basename in line and (':' in line or '#' in line or 'define' in line):
                            matching_string_lines.remove(line)
                matching_string = "\n".join(matching_string_lines)
                matching_string_split = matching_string.split()
                matching_string_list_strip = [word.strip() for word in matching_string_split]
                target = " ".join(matching_string_list_strip)
            else:
                error_message = f'''
                Could not find {target_basename} into the file {path_to_target_header_file}
                '''
                print(print(textwrap.dedent(error_message)))
    except:
        print("Could not open file '{}' .".format(path_to_target_header_file))

    return target


def find_target_by_basename(target_basename: str, path_to_target_header_file: str) -> str:
    target = ''
    target_is_found = 0
    try:
        with open(path_to_target_header_file, 'r') as file:
            file_content = file.read()
            find_target_object = re.search(rf"[\w\s]*\W{target_basename}\W[\s*\(]*[\w\s*,\[\+\]\(\)-]*;", file_content)
            if find_target_object is not None:
                target_is_found = 1
                matching_string = find_target_object.group()
                matching_string_lines = matching_string.split('\n')
                target_basename_nb_of_occurrence = matching_string.count(target_basename)
                if target_basename_nb_of_occurrence >= 2:
                    for line in matching_string_lines:
                        if target_basename in line and (':' in line or '#' in line or 'define' in line):
                            matching_string_lines.remove(line)
                matching_string_lines = [line for line in matching_string_lines if line.strip() != '']
                find_target_index = 0
                find_return_type_index = 0
                for line in matching_string_lines:
                    if target_basename in line:
                        find_target_index = matching_string_lines.index(line)
                        find_return_type_index = find_target_index
                        if line.strip().startswith(target_basename):
                            find_return_type_index = find_target_index - 1
                matching_string_lines = matching_string_lines[find_return_type_index:]
                matching_string = "\n".join(matching_string_lines)
                matching_string_split = matching_string.split()
                matching_string_list_strip = [word.strip() for word in matching_string_split]
                target = " ".join(matching_string_list_strip)
            else:
                error_message = f'''
                Could not find {target_basename} into the file {path_to_target_header_file}
                '''
                print(textwrap.dedent(error_message))
    except:
        print("Could not open file '{}' .".format(path_to_target_header_file))

    return target



# A target is a string. It refers to as the declaration of a function.
# An object of type target has many attributes like the base name of a given target,
# its list of arguments in the (type name) format, the list of its names of arguments, etc.
# Such type of object also incorporate many methods used to set some attributes. For example,
# the arguments names are given by the method get_target_arguments_names().
class Target(object):
    """class: Target"""
    def __init__(self, target: str = None, target_basename: str = None, target_header_file: str = None):
        self.target = target
        self.target_basename = target_basename
        self.target_return_type = ''
        self.target_types = []
        self.target_args_length = []
        self.target_args_declaration = []
        self.target_args_names = []
        self.target_executable = ""
        self.target_test_file = f'test_{self.target_basename}.c'
        self.target_secret_data = []
        self.target_public_data = []
        self.path_to_target_header_file = target_header_file
        self.target_arguments_with_types = {}
        self.target_has_arguments = True
        # Set the attributes of the target
        self.get_target_attributes()

    def find_by_basename(self, basename, path_to_target_header_file: str) -> str:
        self.target = find_target_by_basename(basename, path_to_target_header_file)
        return self.target

    def is_valid_target(self):
        if '(' not in self.target or ')' not in self.target:
            if self.path_to_target_header_file is None or self.path_to_target_header_file.strip() == '':
                invalid_target_error_message = f'''
                '{self.target.upper()}' is not a valid target.
                Please give the target basename name and the path to its header file.
                Alternatively, give the full target declaration '''
                print(textwrap.dedent(invalid_target_error_message))
            else:
                self.target = self.find_by_basename(self.target_basename, self.path_to_target_header_file)
        if self.target.strip() == '':
            invalid_target_error_message = f'''
            The given target is empty
            '''
            print(textwrap.dedent(invalid_target_error_message))

    def get_target_attributes(self):
        self.is_valid_target()
        target_split = re.split(r"[()]\s*", self.target)
        target_args = target_split[-1]
        if target_args == '' or target_args == ' ':
            self.target_has_arguments = False
            print("Target '{}' has no arguments".format(self.target_basename.upper()))
        else:
            self.target_has_arguments = True
            token = gen.tokenize_target(self.target)
            self.target_return_type = token[0]
            self.target_basename = token[1]
            self.target_types = token[2]
            self.target_args_names = token[3]
            self.target_args_declaration = token[4]
            self.target_args_length = token[5]
        return self.target_has_arguments


# ==================== EXECUTION =====================================
# ====================================================================
# Run Binsec
def run_binsec(executable_file, cfg_file, stats_files, output_file, depth, additional_options=None):
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


def binsec_test_harness_template_29(target_basename: str, target_header_file: str,
                                 secret_arguments: list, path_to_test_harness: str, includes: list) -> None:
    """binsec_template_test_harness:  Generate a test harness template (default) for binsec"""

    test_harness_directory_split = path_to_test_harness.split('/')
    test_harness_directory = "/".join(test_harness_directory_split[:-1])
    if not os.path.isdir(test_harness_directory):
        print("Remark: {} is not a directory".format(test_harness_directory))
        print("--- creating {} directory".format(test_harness_directory))
        cmd = ["mkdir", "-p", test_harness_directory]
        subprocess.call(cmd, stdin=sys.stdin)
    target_obj = Target('', target_basename, target_header_file)
    arguments_declaration = target_obj.target_args_declaration
    args_names = target_obj.target_args_names
    targ_return_type = target_obj.target_return_type
    args_names_string = ", ".join(args_names)
    headers_block = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h>
    
    '''
    main_function_block = f'''
    
    int main(){{
    \t{targ_return_type} result =  {target_basename}({args_names_string});
    \texit(result);
    }}
    '''
    with open(path_to_test_harness, "w+") as t_harness_file:
        t_harness_file.write(textwrap.dedent(headers_block))
        if not includes == []:
            for incs in includes:
                t_harness_file.write(f'#include {incs}\n')
        for decl in arguments_declaration:
            decl_args = f'{decl}\n'
            t_harness_file.write(textwrap.dedent(decl_args))
        t_harness_file.write(textwrap.dedent(main_function_block))
    path_to_config_file = f'{test_harness_directory}/checkct.cfg'
    target_public_inputs = [arg for arg in args_names if arg not in secret_arguments]
    # binsec_configuration_file(path_to_config_file, secret_arguments, target_public_inputs)


def configuration_file(cfg_file_sign, secret_arguments: Union[str, list], public_arguments: Optional[Union[str, list]],
                       assumption: Optional[str] = None):

    script_file = cfg_file_sign
    target_secret_inputs = ''
    target_public_inputs = ''
    if isinstance(secret_arguments, list):
        for sec_input in secret_arguments:
            target_secret_inputs += f',{sec_input}'
    elif isinstance(secret_arguments, str):
        for sec_input in secret_arguments.split():
            target_secret_inputs += f',{sec_input}'
    if isinstance(public_arguments, list):
        for pub_input in public_arguments:
            target_public_inputs += f',{pub_input}'
    elif isinstance(public_arguments, str):
        for pub_input in public_arguments.split():
            target_public_inputs += f',{pub_input}'
    target_secret_inputs = target_secret_inputs.replace(',', '', 1)
    target_public_inputs = target_public_inputs.replace(',', '', 1)
    cfg_file_content = f''' 
    starting from core
    
    secret global {target_secret_inputs}
    public global {target_public_inputs}
    halt at <exit>
    explore all
    '''
    with open(script_file, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))


def binsec_test_harness_template(target_basename: str, target_call: str,  target_return_type: str,
                                 target_includes: Union[str, list], target_input_declaration: Union[str, list],
                                 secret_arguments: Union[str, list], path_to_test_harness: Optional[str] = None,
                                 target_macro: Optional[Union[str, list]] = None) -> None:
    """binsec_template_test_harness:  Generate a test harness template (default) for binsec"""
    test_harness_directory = f'binsec/{target_basename}'
    target_test_harness = path_to_test_harness
    if path_to_test_harness:
        test_harness_directory = os.path.dirname(path_to_test_harness)
    else:
        target_test_harness = f'{test_harness_directory}/{target_basename}.c'
    util.create_directory(test_harness_directory)
    path_to_config_file = f'{test_harness_directory}/cfg.ini'
    macros = ''
    macro = ''
    if target_macro:
        if isinstance(target_macro, list):
            for macro in target_macro:
                macro = macro.strip()
                if not macro.startswith('#define'):
                    macro = f'#define {macro}'
                macros += f'{macro}'
        elif isinstance(target_macro, str):
            if not target_macro.startswith('#define'):
                macro = f'#define {target_macro}'
            macros += f'{macro}'
    # target_inputs_declaration = f'''
    # '''
    target_inputs_declaration = f''''''
    for decl in target_input_declaration:
        if not decl.endswith(';'):
            decl += ';'
        target_inputs_declaration += f'''
        {decl}'''
    target_call = target_call.strip()
    if not target_call.endswith(';'):
        target_call += ';'
    target_result = ''
    target_exit_point = ''
    if target_return_type.strip() == 'void':
        target_exit_point = 'exit(0);'
    else:
        target_result = f'{target_return_type} ct_result ='
        target_exit_point = 'exit(ct_result);'
    ct_test_target_call = f'{target_result}{target_call}'
    target_includes_headers = ''
    if isinstance(target_includes, list):
        for incs in target_includes:
            target_includes_headers += f'#include "{incs}"'
    elif isinstance(target_includes, str):
        for incs in target_includes.split():
            target_includes_headers += f'{incs}'
    headers_block = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h>
    '''
    main_function_block = f'''
    int main(){{
    \t{target_inputs_declaration}
    \t{ct_test_target_call}
    \t{target_exit_point}
    }}
    '''
    target_test_harness_content = f'''
    {headers_block}
    {target_includes_headers}
    {macros}
    {main_function_block}
    '''

    with open(target_test_harness, "w+") as t_harness_file:
        t_harness_file.write(textwrap.dedent(target_test_harness_content))
    target_call_custom = target_call.replace('&', '')
    target_all_inputs = target_call_custom[target_call_custom.find("(")+1:target_call_custom.find(")")]
    target_public_inputs = [arg.strip() for arg in target_all_inputs.split(',') if arg not in secret_arguments]
    configuration_file(path_to_config_file, secret_arguments, target_public_inputs)


def parse_target_json_file1(targets_dict: dict, target: str):
    targets = targets_dict.keys()
    if target not in targets:
        # We should raise an error
        print("There is no target named {}".format(target))
        return None
    else:
        return targets_dict[target]


def parse_target_json_file(targets_dict: Optional[Union[list, dict]], target: str):
    if isinstance(targets_dict, dict):
        targets = targets_dict.keys()
        if target not in targets:
            # We should raise an error
            print("There is no target named {}".format(target))
            return None
        else:
            return targets_dict[target]
    elif isinstance(targets_dict, list):
        target_found = None
        all_targets = []
        for target_basename in targets_dict:
            if target_basename.get(target):
                target_found = target_basename
                return target_basename
        if target_found is None:
            # We should raise an error
            print("There is no target named {}".format(target))
            return None


def generic_template1(target_basename: str, tool: str, targets_dict: dict):
    print("----generic_template-------")
    print("......targets_dict: ", targets_dict)
    target_dict = parse_target_json_file(targets_dict, target_basename)
    print("<<<<<<<<<<...target_dict: ", target_dict)
    target_dict = target_dict[target_basename]
    target_call = target_dict['target_call']
    target_return_type = target_dict['target_return_type']
    target_input_declaration = target_dict['target_input_declaration']
    target_includes = target_dict['target_include_header']
    target_secret_inputs = target_dict['secret_inputs']
    target_macro = target_dict['macro']
    if tool.strip() == 'binsec':
        binsec_test_harness_template(target_basename, target_call, target_return_type, target_includes,
                                     target_input_declaration, target_secret_inputs,
                                     None, target_macro)
    if tool.strip() == 'timecop':
        print("-------IN PROGRESS: timecop")
    if tool.strip() == 'dudect':
        print("-------IN PROGRESS: dudect")


def generic_template(target_basename: str, tools: Union[str, list], targets_dict: dict):
    target_dict = parse_target_json_file(targets_dict, target_basename)
    target_dict = target_dict[target_basename]
    target_call = target_dict['target_call']
    target_return_type = target_dict['target_return_type']
    target_input_declaration = target_dict['target_input_declaration']
    target_includes = target_dict['target_include_header']
    target_secret_inputs = target_dict['secret_inputs']
    target_macro = target_dict['macro']
    for tool in tools:
        if tool.strip() == 'binsec':
            binsec_test_harness_template(target_basename, target_call, target_return_type, target_includes,
                                         target_input_declaration, target_secret_inputs,
                                         None, target_macro)
        if tool.strip() == 'timecop':
            print("-------IN PROGRESS: timecop")
        if tool.strip() == 'dudect':
            print("-------IN PROGRESS: dudect")


def generic_tests_templates(user_entry_point: str, targets: Optional[Union[str, list]] = None,
                            tools: Optional[Union[str, list]] = None):
    ret_gen_tests = parse_json_to_dict_generic_tests(user_entry_point)
    all_targets, generic_tests_chosen_tools = ret_gen_tests
    chosen_tools = generic_tests_chosen_tools
    if tools:
        chosen_tools = tools
    targets_under_tests = []
    all_targets_dict = {}
    if targets:
        if isinstance(targets, list):
            targets_under_tests = targets
        elif isinstance(targets, str):
            targets_under_tests.extend(targets.split())
    for target in targets_under_tests:
        generic_template(target, chosen_tools, all_targets)



def ctgrind_test_harness_template(target_basename: str, target_header_file: str,
                                  secret_arguments: list, path_to_test_harness: str, includes: list) -> None:
    """ctgrind_template_test_harness:  Generate a test harness template (default) for ctgrind"""

    test_harness_directory_split = path_to_test_harness.split('/')
    test_harness_directory = "/".join(test_harness_directory_split[:-1])
    if not os.path.isdir(test_harness_directory):
        print("Remark: {} is not a directory".format(test_harness_directory))
        print("--- creating {} directory".format(test_harness_directory))
        cmd = ["mkdir", "-p", test_harness_directory]
        subprocess.call(cmd, stdin=sys.stdin)
    target_obj = Target('', target_basename, target_header_file)
    arguments_declaration = target_obj.target_args_declaration
    args_names = target_obj.target_args_names
    args_types = target_obj.target_types
    targ_return_type = target_obj.target_return_type
    args_names_string = ", ".join(args_names)

    ct_poison_block = ""
    ct_unpoison_block = ""
    generate_random_inputs_block = ""
    for sec_arg in secret_arguments:
        sec_args_index = args_names.index(sec_arg)
        sec_args_type = args_types[sec_args_index]
        ct_poison_block += f'''
        \tct_poison({sec_arg}, CRYPTO_SECRETKEYBYTES * sizeof({sec_args_type}));
        '''
        ct_unpoison_block += f'''
        \tct_unpoison({sec_arg}, CRYPTO_SECRETKEYBYTES * sizeof({sec_args_type}));
        '''
        generate_random_inputs_block += f'''
        //randombytes({sec_arg}, DEFAULT_VALUE*long);'''
    declaration_initialization_block = f'''
    '''
    for decl in arguments_declaration:
        declaration_initialization_block += f'''
        {decl}
        '''
    additional_includes = f'''
    '''
    if not includes == []:
        for incs in includes:
            additional_includes += f'''
            #include {incs}
            '''
    headers_block = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h>
    
    #include <ctgrind.h>
    
    '''

    test_vector_block = f'''
    void generate_test_vectors() {{
    \t//DEFAULT: Fill randombytes
    \t{generate_random_inputs_block}
    }} 
    '''
    main_content_block = f'''
    int main() {{
    \t//DEFAULT:
    \t//{args_names[0]} = ({args_types[0]} *)calloc(DEFAULT_VALUE, sizeof({args_types[0]}));
    
    \t{targ_return_type} result ; 
    \tfor (int i = 0; i < DEFAULT_CTGRIND_SAMPLE_SIZE; i++) {{
    \t\tgenerate_test_vectors(); 
    \t\t{ct_poison_block}
    \t\tresult = {target_basename}({args_names_string}); 
    \t\t{ct_unpoison_block}
    \t}}
    
    \t//DEFAULT:
    \t//free({args_names[0]}); 
    \treturn result;
    }}
    '''
    with open(path_to_test_harness, "w+") as t_harness_file:
        t_harness_file.write(textwrap.dedent(headers_block))
        t_harness_file.write(textwrap.dedent(additional_includes))
        t_harness_file.write(textwrap.dedent(declaration_initialization_block))
        t_harness_file.write(textwrap.dedent(test_vector_block))
        t_harness_file.write(textwrap.dedent(main_content_block))


def dudect_test_harness_template(target_basename: str, target_header_file: str,
                                 secret_arguments: list, path_to_test_harness: str, includes: list) -> None:
    """dudect_template_test_harness:  Generate a test harness template (default) for dudect"""

    test_harness_directory_split = path_to_test_harness.split('/')
    test_harness_directory = "/".join(test_harness_directory_split[:-1])
    if not os.path.isdir(test_harness_directory):
        print("Remark: {} is not a directory".format(test_harness_directory))
        print("--- creating {} directory".format(test_harness_directory))
        cmd = ["mkdir", "-p", test_harness_directory]
        subprocess.call(cmd, stdin=sys.stdin)
    target_obj = Target('', target_basename, target_header_file)
    arguments_declaration = target_obj.target_args_declaration
    args_names = target_obj.target_args_names
    args_types = target_obj.target_types
    targ_return_type = target_obj.target_return_type
    target_inputs = ", ".join(args_names)

    ct_poison_block = ""
    ct_unpoison_block = ""
    generate_random_inputs_block = ""
    declaration_initialization_block = ""

    for decl in arguments_declaration:
        declaration_initialization_block += f'''
        {decl}
        '''
    for sec_arg in secret_arguments:
        sec_args_index = args_names.index(sec_arg)
        sec_args_type = args_types[sec_args_index]
        ct_poison_block += f'''
        \tct_poison({sec_arg}, CRYPTO_SECRETKEYBYTES * sizeof({sec_args_type}));
        '''
        ct_unpoison_block += f'''
        \tct_unpoison({sec_arg}, CRYPTO_SECRETKEYBYTES * sizeof({sec_args_type}));
        '''
        generate_random_inputs_block += f'''
        //randombytes({sec_arg}, DEFAULT_VALUE*long);'''
    additional_includes = f'''
    '''
    if not includes == []:
        for incs in includes:
            additional_includes += f'''
            #include {incs}
            '''
    do_one_computation_block = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    {declaration_initialization_block}
    \t//Do the needed process on the input <<data>>
    \t{targ_return_type} result = {target_basename}({target_inputs});
    \treturn result;
    }}
    '''
    prepare_inputs_block = f'''
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
    '''

    headers_block = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h>
    
    #define DUDECT_IMPLEMENTATION
    #include <dudect.h>
    
    '''
    main_function_block = f'''
    int main(int argc, char **argv)
    {{
    \t(void)argc;
    \t(void)argv;

    \tdudect_config_t config = {{
    \t\t.chunk_size = CRYPTO_SECRETKEYBYTES,
    \t\t.number_measurements = DEFAULT_VALUE,
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
    # Generate random inputs
    test_harness_test_vector_block = f'''
    void generate_test_vectors() {{
    \t//DEFAULT: Fill randombytes
    \t{generate_random_inputs_block}
    }} 
    '''
    with open(path_to_test_harness, "w+") as t_harness_file:
        t_harness_file.write(textwrap.dedent(headers_block))
        t_harness_file.write(textwrap.dedent(additional_includes))
        t_harness_file.write(textwrap.dedent(test_harness_test_vector_block))
        t_harness_file.write(textwrap.dedent(do_one_computation_block))
        t_harness_file.write(textwrap.dedent(prepare_inputs_block))
        t_harness_file.write(textwrap.dedent(main_function_block))


def flowtracker_test_harness_template(target_basename: str, target_header_file: str,
                                      secret_arguments: list, path_to_test_harness: str) -> None:
    """flowtracker_template_test_harness:  Generate a test harness template (default) for flowtracker"""

    test_harness_directory_split = path_to_test_harness.split('/')
    test_harness_directory = "/".join(test_harness_directory_split[:-1])
    if not os.path.isdir(test_harness_directory):
        print("Remark: {} is not a directory".format(test_harness_directory))
        print("--- creating {} directory".format(test_harness_directory))
        cmd = ["mkdir", "-p", test_harness_directory]
        subprocess.call(cmd, stdin=sys.stdin)
    target_obj = Target('', target_basename, target_header_file)
    args_names = target_obj.target_args_names
    public_arguments = [arg for arg in args_names if arg not in secret_arguments]

    public_inputs_block = f'''
    \t\t\t<public>
    '''
    for arg in public_arguments:
        public_inputs_block += f'''
        \t\t\t<parameter>{arg}</parameter>
        '''
    public_inputs_block += f'''
    \t\t\t</public>
    '''

    secret_inputs_block = f'''
    \t\t\t<secret>
    '''
    for arg in secret_arguments:
        secret_inputs_block += f'''
        \t\t\t\t<parameter>{arg}</parameter>
        '''
    secret_inputs_block += f'''
    \t\t\t</secret>
    '''
    xml_file_block = f'''
    <functions>
        <sources>
            <function>
                <name>{target_basename}</name>
                <return>false</return>
                {public_inputs_block}
                {secret_inputs_block}
            </function>
        </sources>
    </functions>
    '''
    with open(path_to_test_harness, "w+") as t_harness_file:
        t_harness_file.write(textwrap.dedent(xml_file_block))


def libfuzzer_fuzz_target_template(target_basename: str, target_header_file: str,
                                   path_to_fuzz_target: str, includes: list) -> None:
    """libfuzzer_fuzz_target_template:  Generate a fuzz target template (default) for libfuzzer"""

    fuzz_target_directory_split = path_to_fuzz_target.split('/')
    fuzz_target_directory = "/".join(fuzz_target_directory_split[:-1])
    if not os.path.isdir(fuzz_target_directory):
        print("Remark: {} is not a directory".format(fuzz_target_directory))
        print("--- creating {} directory".format(fuzz_target_directory))
        cmd = ["mkdir", "-p", fuzz_target_directory]
        subprocess.call(cmd, stdin=sys.stdin)
    target_obj = Target('', target_basename, target_header_file)
    arguments_declaration = target_obj.target_args_declaration
    args_names = target_obj.target_args_names
    args_names_string = ", ".join(args_names)
    headers_block = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h>
    
    '''
    main_function_block = f'''
    
    int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size){{
    \t{target_basename}({args_names_string});
    \treturn 0;
    }}
    '''
    with open(path_to_fuzz_target, "w+") as fuzz_file:
        fuzz_file.write(textwrap.dedent(headers_block))
        if not includes == []:
            for incs in includes:
                fuzz_file.write(f'#include {incs}\n')
        for decl in arguments_declaration:
            decl_args = f'{decl}\n'
            fuzz_file.write(textwrap.dedent(decl_args))
        fuzz_file.write(textwrap.dedent(main_function_block))


class Tools(object):
    """ Tools: create a template for a given candidate for the given tool
                Run a binary with the given tool"""
    def __init__(self, tool_name):
        self.tool_name = tool_name
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

    def tool_template(self, target_basename: str, target_header_file: str,
                      secret_arguments: list, path_to_test_harness: str, includes: list):
        if self.tool_name.lower() == 'binsec':
            binsec_test_harness_template(target_basename, target_header_file,
                                         secret_arguments, path_to_test_harness, includes)
        if self.tool_name.lower() == 'ctgrind':
            ctgrind_test_harness_template(target_basename, target_header_file,
                                          secret_arguments, path_to_test_harness, includes)
        if self.tool_name.lower() == 'dudect':
            dudect_test_harness_template(target_basename, target_header_file,
                                         secret_arguments, path_to_test_harness, includes)
        if self.tool_name.lower() == 'flowtracker':
            flowtracker_test_harness_template(target_basename, target_header_file,
                                              secret_arguments, path_to_test_harness)
        if self.tool_name.lower() == 'ctverif':
            pass
        if self.tool_name.lower() == 'libfuzzer':
            libfuzzer_fuzz_target_template(target_basename, target_header_file,
                                           path_to_test_harness, includes)

    def tool_execution(self, executable_file: str, config_file: str = None,
                       output_file: str = None, sse_depth: int = 1000000, stats_file: str = None,
                       timeout: str | None = None, additional_options: list | None = None) -> None:

        if self.tool_name.lower() == 'binsec':
            run_binsec(executable_file, config_file, stats_file, output_file, sse_depth, additional_options)
        if self.tool_name.lower() == 'ctgrind':
            run_ctgrind(executable_file, output_file)
        if self.tool_name.lower() == 'dudect':
            run_dudect(executable_file, output_file, timeout)
        if self.tool_name.lower() == 'flowtracker':
            # run_flowtracker(executable_file,config_file, output_file)
            pass
        if self.tool_name.lower() == 'ctverif':
            pass


# def generic_template(tools_list: list, target_basename: str, target_header_file,
#                      secret_arguments, path_to_test_harness, includes):
#     path_to_test_harness_split = path_to_test_harness.split('/')
#     if path_to_test_harness is None or path_to_test_harness == 'None':
#         path_to_test_harness_split = []
#         path_to_test_harness = ''
#     test_harness_basename = os.path.basename(path_to_test_harness)
#     test_file_basename = test_harness_basename
#     if not test_file_basename.endswith('.c'):
#         test_file_basename = f'test_{target_basename}.c'
#     for tool_name in tools_list:
#         tool_obj = Tools(tool_name)
#         full_path_to_test_harness = ''
#         path_to_test_harness_split_extend = path_to_test_harness_split.copy()
#         if not path_to_test_harness_split_extend:
#             full_path_to_test_harness = f'{tool_name}/{test_file_basename}'
#         else:
#             if tool_name.strip() not in path_to_test_harness_split:
#                 if len(path_to_test_harness_split) == 1:
#                     if test_harness_basename.endswith('.c'):
#                         path_to_test_harness_split_extend.insert(0, tool_name)
#                     else:
#                         path_to_test_harness_split_extend.append(tool_name)
#                         path_to_test_harness_split_extend.append(test_file_basename)
#                 else:
#                     if test_harness_basename.endswith('.c'):
#                         path_to_test_harness_split_extend.insert(len(path_to_test_harness_split_extend)-1, tool_name)
#                     else:
#                         path_to_test_harness_split_extend.append(tool_name)
#                         path_to_test_harness_split_extend.append(test_file_basename)
#             full_path_to_test_harness = "/".join(path_to_test_harness_split_extend)
#         tool_obj.tool_template(target_basename, target_header_file, secret_arguments, full_path_to_test_harness, includes)
#
