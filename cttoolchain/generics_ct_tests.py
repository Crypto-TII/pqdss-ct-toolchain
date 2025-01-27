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
from pathlib import Path

from typing import Optional, Union, List

import generics as gen
import utils as util


def parse_json_to_dict_generic_tests(path_to_json_file: str):
    with open(path_to_json_file) as json_file:
        data = json.load(json_file)
        targets = data['targets']
        tools = data['tools']
        return targets, tools


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


def generic_compilation(path_to_target_wrapper: str, path_to_target_binary: str,
                        path_to_test_library_directory: str, libraries_names: [Union[str, list]],
                        path_to_include_directories: Union[str, list], cflags: Union[list, str], compiler: str = 'gcc'):
    target_include_dir = path_to_include_directories
    target_link_libraries = []
    if libraries_names:
        if isinstance(libraries_names, str):
            target_link_libraries.extend(libraries_names.split())
        elif isinstance(libraries_names, list):
            target_link_libraries.extend(libraries_names.copy())
    target_link_libraries = list(set(target_link_libraries))
    target_link_libraries = list(map(lambda incs: f'{incs}' if '-l' in incs else f'-l{incs}', target_link_libraries))
    target_link_libraries = list(map(lambda incs: f'{incs}'.replace('lib', '') if '-llib' in incs
                            else f'{incs}', target_link_libraries))
    target_link_libraries_str = " ".join(target_link_libraries)
    all_flags_str = " ".join(cflags)
    cmd = f'{compiler} {all_flags_str} '
    if target_include_dir:
        if isinstance(target_include_dir, list):
            include_directories = target_include_dir.copy()
            include_directories = list(map(lambda incs: f'-I{incs}', include_directories))
            cmd += f' {" ".join(target_include_dir)}'
        else:
            include_directories = list(map(lambda incs: f'-I {incs}', target_include_dir.split()))
            cmd += f' {" ".join(include_directories)}'
    if not path_to_target_wrapper.endswith('.c'):
        path_to_target_wrapper = f'{path_to_target_wrapper}.c'
    cmd += f' {path_to_target_wrapper} -o {path_to_target_binary}'
    cmd += f' -L{path_to_test_library_directory} -Wl,-rpath,{path_to_test_library_directory}/ {target_link_libraries_str}'
    print("cmd: ")
    print(cmd)
    subprocess.call(cmd, stdin=sys.stdin, shell=True)


# ==================== EXECUTION =====================================
# ====================================================================
# Run Binsec
def run_binsec(executable_file, cfg_file, stats_files, output_file, depth, additional_options=None):
    command = f'''binsec -sse -checkct -sse-script {cfg_file} -sse-depth  {depth} -sse-self-written-enum 1 
          -checkct-stats-file {stats_files}'''
    command += f' {executable_file}'
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
    path_to_executable_file_split = path_to_executable_file.split('/')
    executable_basename = path_to_executable_file
    gdb_script_basename = path_to_gdb_script
    if len(path_to_executable_file_split) == 1:
        executable_folder = "."
    else:
        executable_folder = '/'.join(path_to_executable_file_split[0:-1])
    cmd = f'gdb -x {gdb_script_basename} ./{executable_basename}'
    cmd_list = cmd.split()
    subprocess.call(cmd_list, stdin=sys.stdin)


def binsec_update_declaration_17_jan(target_call: str, target_input_declaration: Union[list, str], random_data: dict):
    parameters_info = get_target_type_of_inputs(target_call, target_input_declaration)
    parameter_index = 0
    if random_data:
        for parameter, parameter_length in random_data.items():
            parameters_info[parameter][-1] = parameter_length
        parameter_index += 1
    random_data_block = f''''''
    deallocate_block = f''''''
    updated_declaration = f''''''
    for key_param, value_param in parameters_info.items():
        if random_data:
            if key_param in random_data.keys():
                key = key_param
                value = parameters_info[key]
                if value[0] == 'pointer' or value[0] == 'array':
                    updated_declaration += f'''
                    {value[1]} {key}[{value[2]}] = {{0}};'''
                elif value[0] == 'default':
                    updated_declaration += f'''
                    {value[1]} {key} = {value[2]}'''
        if key_param not in random_data.keys():
            if value_param[0] == 'pointer' or value_param[0] == 'array':
                updated_declaration += f'''
                {value_param[1]} {key_param}[{value_param[2]}] = {{0}};
                '''
            if value_param[0] == 'default':
                updated_declaration += f'''
                {value_param[1]} {key_param} = {value_param[2]} ;
                '''
    return updated_declaration, random_data_block, deallocate_block



def binsec_update_declaration_20(target_call: str, target_input_declaration: Union[list, str], random_data: dict):
    parameters_info = get_target_type_of_inputs(target_call, target_input_declaration)
    parameter_index = 0
    if random_data:
        for parameter, parameter_length in random_data.items():
            parameters_info[parameter][-1] = parameter_length
        parameter_index += 1
    random_data_block = f''''''
    deallocate_block = f''''''
    updated_declaration = f''''''
    print("------parameters_info: ", parameters_info)
    print("------target_input_declaration: ", target_input_declaration)
    print("------target_call: ", target_call)
    print("------random_data: ", random_data)
    for key_param, value_param in parameters_info.items():
        print("---key_param: {0} --- value_param: {1}".format(key_param, value_param))
        if random_data:
            if key_param in random_data.keys():
                key = key_param
                value = parameters_info[key]
                if value[0] == 'pointer' or value[0] == 'array':
                    updated_declaration += f'''
                    {value[1]} {key}[{value[2]}] = {{0}};'''
                elif value[0] == 'default':
                    updated_declaration += f'''
                    {value[1]} {key} = {value[2]}'''
        if random_data:
            if key_param not in random_data.keys():
                if value_param[0] == 'pointer' or value_param[0] == 'array':
                    updated_declaration += f'''
                    {value_param[1]} {key_param}[{value_param[2]}] = {{0}};
                    '''
                if value_param[0] == 'default':
                    updated_declaration += f'''
                    {value_param[1]} {key_param} = {value_param[2]} ;
                    '''
        else:
            if value_param[0] == 'pointer' or value_param[0] == 'array':
                updated_declaration += f'''
                    {value_param[1]} {key_param}[{value_param[2]}] = {{0}};
                    '''
            if value_param[0] == 'default':
                updated_declaration += f'''
                    {value_param[1]} {key_param} = {value_param[2]} ;
                    '''
    return updated_declaration, random_data_block, deallocate_block


def binsec_update_declaration(target_call: str, target_input_declaration: Union[list, str], random_data: dict):
    parameters_info = get_target_type_of_inputs(target_call, target_input_declaration)
    parameter_index = 0
    if random_data:
        for parameter, parameter_length in random_data.items():
            parameters_info[parameter][-1] = parameter_length
        parameter_index += 1
    random_data_block = f''''''
    deallocate_block = f''''''
    updated_declaration = f''''''
    for key_param, value_param in parameters_info.items():
        if random_data:
            if key_param in random_data.keys():
                key = key_param
                value = parameters_info[key]
                if value[0] == 'pointer' or value[0] == 'array':
                    updated_declaration += f'''
                    {value[1]} {key}[{value[2]}] = {{0}};'''
                elif value[0] == 'default':
                    updated_declaration += f'''
                    {value[1]} {key} = {value[2]}'''
        if random_data:
            if key_param not in random_data.keys():
                if value_param[0] == 'pointer' or value_param[0] == 'array':
                    updated_declaration += f'''
                    {value_param[1]} {key_param}[{value_param[2]}] = {{0}};
                    '''
                if value_param[0] == 'default':
                    updated_declaration += f'''
                    {value_param[1]} {key_param} = {value_param[2]} ;
                    '''
        else:
            if value_param[0] == 'pointer' or value_param[0] == 'array':
                updated_declaration += f'''
                    {value_param[1]} {key_param}[{value_param[2]}] = {{0}};
                    '''
            if value_param[0] == 'default':
                updated_declaration += f'''
                    {value_param[1]} {key_param} = {value_param[2]} ;
                    '''
    return updated_declaration, random_data_block, deallocate_block



# Run timecop
def run_timecop(binary_file, output_file):
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
                                 target_macro: Optional[Union[str, list]] = None, random_data: Optional[dict] = None) -> None:
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
    updated_declaration, random_data_block, deallocate_block = binsec_update_declaration(target_call,
                                                                                         target_input_declaration,
                                                                                         random_data)
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
    \t{updated_declaration}
    
    int main(){{
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


# random_data = {'VAR_NAME': ["VAR_TYPE", "VAR_LENGTH"]}
def timecop_allocate_data(random_data: dict):
    random_data_block = f''''''
    if random_data:
        for key, value in random_data.items():
            if value[0] == 'pointer':
                random_data_block += f'''
                {key} = ({value[1]} *)calloc({value[2]}, sizeof({value[1]}));'''
    return random_data_block


def timecop_update_declaration(target_call: str, target_input_declaration: Union[list, str],
                               random_data: dict, timecop_randomness: Optional[str] = 'ct_randombytes'):
    parameters_info = get_target_type_of_inputs(target_call, target_input_declaration)
    parameter_index = 0
    if random_data:
        for parameter, parameter_length in random_data.items():
            parameters_info[parameter][-1] = parameter_length
        parameter_index += 1
    random_data_block = f''''''
    deallocate_block = f''''''
    updated_declaration = f''''''
    total_size = '0'
    for key_param, value_param in parameters_info.items():
        if random_data:
            if key_param in random_data.keys():
                key = key_param
                value = parameters_info[key]
                if value[0] == 'pointer':
                    updated_declaration += f'''
                    {value[1]} *{key} = ({value[1]} *)calloc({value[2]}, sizeof({value[1]}));'''
                    random_data_block += f'''
                    {timecop_randomness}({key}, {value[2]} * sizeof({value[1]}));
                    '''
                    deallocate_block += f'''
                    free({key_param});
                    '''
                if value[0] == 'array':
                    updated_declaration += f'''
                    {value[1]} {key}[{value[2]}] = {{0}};'''
                    random_data_block += f'''
                    {timecop_randomness}({key}, {value[2]} * sizeof({value[1]}));
                    '''
                elif value[0] == 'default':
                    updated_declaration += f'''
                    {value[1]} {key} = *({value[1]} *)data + {total_size};'''
                    random_data_block += f'''
                    {timecop_randomness}(&{key}, sizeof({value[1]}))
                    '''
                total_size += f' + {value[2]} * sizeof({value[1]})'
        if key_param not in random_data.keys():
            if value_param[0] == 'pointer':
                updated_declaration += f'''
                {value_param[1]} *{key_param} = ({value_param[1]} *)calloc({value_param[2]}, sizeof({value_param[1]}));
                '''
                deallocate_block += f'''
                free({key_param});
                '''
            if value_param[0] == 'array':
                updated_declaration += f'''
                {value_param[1]} {key_param}[{value_param[2]}] = {{0}};
                '''
            if value_param[0] == 'default':
                updated_declaration += f'''
                {value_param[1]} {key_param} = {value_param[2]} ;
                '''
    return updated_declaration, random_data_block, total_size, deallocate_block


def is_variable_pointer_or_array(target_input_declaration, parameter):
    parameter_found = False
    for decl in target_input_declaration:
        if parameter in decl:
            parameter_found = True
            if f'{parameter}[' in decl or f'{parameter} [' in decl:
                return 'array'
            elif '*' in decl.split(parameter)[0]:
                return 'pointer'
    if parameter_found:
        return 'default'
    else:
        return 'Parameter not found'


# random_data = {'VAR_NAME': ["VAR_TYPE", "VAR_LENGTH"]}
def dudect_allocate_data(random_data: dict):
    random_data_block = f''''''
    total_size = '0'
    if random_data:
        for key, value in random_data.items():
            if value[0] == 'pointer':
                random_data_block += f'''
                {key} = ({value[1]} *)data + {total_size};'''
            elif value[0] == 'array':
                random_data_block += f'''
                //&{key}[0] = *({value[1]} *)data + {total_size};
                &{key}[0] = ({value[1]} *)data[{total_size}];'''
            elif value[0] == 'default':
                random_data_block += f'''
                {key} = *({value[1]} *)data + {total_size};'''
            total_size += f' + {value[2]} * sizeof({value[1]})'
    return random_data_block, total_size


def dudect_update_declaration(target_call: str, target_input_declaration: Union[list, str], random_data: dict):
    parameters_info = get_target_type_of_inputs(target_call, target_input_declaration)
    parameter_index = 0
    if random_data:
        for parameter, parameter_length in random_data.items():
            parameters_info[parameter][-1] = parameter_length
        parameter_index += 1
    random_data_block = f''''''
    total_size = '0'
    for key_param, value_param in parameters_info.items():
        if random_data:
            if key_param in random_data.keys():
                key = key_param
                value = parameters_info[key]
                if value[0] == 'pointer' or value[0] == 'array':
                    random_data_block += f'''
                    {value[1]} *{key} = ({value[1]} *)data + {total_size};'''
                elif value[0] == 'default':
                    random_data_block += f'''
                    {value[1]} {key} = *({value[1]} *)data + {total_size};'''
                total_size += f' + {value[2]} * sizeof({value[1]})'
        if key_param not in random_data.keys():
            if value_param[0] == 'pointer':
                random_data_block += f'''
                {value_param[1]} *{key_param} = ({value_param[1]} *)calloc({value_param[2]}, sizeof({value_param[1]}));
                '''
            if value_param[0] == 'array':
                random_data_block += f'''
                {value_param[1]} {key_param}[{value_param[2]}] = {{0}};
                '''
            if value_param[0] == 'default':
                random_data_block += f'''
                {value_param[1]} {key_param} = {value_param[2]} ;
                '''
    return random_data_block, total_size


# random_data = {'VAR_NAME': ["VAR_TYPE", "VAR_LENGTH"]}
def get_secret_input_lengths(secret_inputs: Union[str, list], random_data: dict,
                             target_input_declaration: Union[str, list]):
    secret_inputs_with_length = {}
    random_data_list = []
    if random_data:
        random_data_list = random_data.keys()
    for sec_param in secret_inputs:
        if sec_param in random_data_list:
            secret_inputs_with_length[sec_param] = random_data[sec_param]
        else:
            for decl in target_input_declaration:
                if f'{sec_param}[' in decl or f'{sec_param} [' in decl:
                    length = decl[decl.find("[")+1:decl.find("]")]
                    type_of_sec_param = decl.split(sec_param)[0]
                    secret_inputs_with_length[sec_param] = [type_of_sec_param, length]
                    break
    return secret_inputs_with_length


# secret_parameters = {'VAR_NAME': ["CATEGORY_TYPE", "VAR_TYPE", "VAR_LENGTH"]}
def timecop_poison_secret_data(secret_inputs: Union[str, list], random_data: dict,
                               target_input_declaration: Union[str, list], target_call: str):
    poison_block = f''''''
    unpoison_block = f''''''
    parameters_info = get_target_type_of_inputs(target_call, target_input_declaration)
    parameter_index = 0
    if random_data:
        for parameter, parameter_length in random_data.items():
            parameters_info[parameter][-1] = parameter_length
        parameter_index += 1
    if secret_inputs:
        for sec_param in secret_inputs:
            sec_param_info = parameters_info[sec_param]
            poison_block += f'''
            poison({sec_param}, {sec_param_info[2]} * sizeof({sec_param_info[1]}));'''
            unpoison_block += f'''
            unpoison({sec_param}, {sec_param_info[2]} * sizeof({sec_param_info[1]}));'''
    else:
        print("Attention: No secret parameters is given")
    return poison_block, unpoison_block


# output: {VAR_NAME: [VAR_CATEGORY, VAR_TYPE, VAR_SIZE]}
def timecop_get_type_of_inputs(target_function_call: str, target_input_declaration: Union[str, list]):
    target_call_custom = target_function_call.replace('&', '')
    target_call_custom = target_call_custom.replace(',', '')
    target_all_inputs = target_call_custom[target_call_custom.find("(")+1:target_call_custom.find(")")]
    target_all_inputs = target_all_inputs.split()
    # target_inputs_type = []
    target_inputs_type = {}
    parameter_found = False
    parameter_infos = []
    for i in range(len(target_input_declaration)):
        parameter_category = 'default'
        length = '0'  # we set length = 0  for a variable of type pointer
        decl = target_input_declaration[i].strip()
        parameter = target_all_inputs[i]
        if parameter in decl:
            input_type = ''
            if '[' not in decl and ']' not in decl:
                if '*' in decl:
                    input_type = decl.split('*')[0]
                    parameter_category = 'pointer'
                else:
                    input_type = decl.split(parameter)[0]
                    length = '1'
            else:
                parameter_category = 'array'
                input_type = decl.split(parameter)[0]
                length = decl[decl.find("[")+1:decl.find("]")]
            parameter_infos = [parameter_category, input_type.strip(), length]
            target_inputs_type[parameter] = parameter_infos
    return target_inputs_type


# output: {VAR_NAME: [VAR_CATEGORY, VAR_TYPE, VAR_SIZE]}
def get_target_type_of_inputs_20(target_function_call: str, target_input_declaration: Union[str, list]):
    target_call_custom = target_function_call.replace('&', '')
    target_call_custom = target_call_custom.replace(',', '')
    target_all_inputs = target_call_custom[target_call_custom.find("(")+1:target_call_custom.find(")")]
    target_all_inputs = target_all_inputs.split()
    print("------+++++++++target_all_inputs: ", target_all_inputs)
    print("------+++++++++target_input_declaration: ", target_input_declaration)
    target_inputs_type = {}
    parameter_found = False
    parameter_infos = []
    for i in range(len(target_input_declaration)):
        parameter_category = 'default'
        length = '0'  # we set length = 0  for a variable of type pointer
        decl = target_input_declaration[i].strip()
        parameter = target_all_inputs[i]
        if parameter in decl:
            input_type = ''
            if '[' not in decl and ']' not in decl:
                if '*' in decl:
                    input_type = decl.split('*')[0]
                    parameter_category = 'pointer'
                else:
                    input_type = decl.split(parameter)[0]
                    length = '0'
                    if '=' in decl:
                        length = decl.split('=')[-1]
            else:
                parameter_category = 'array'
                input_type = decl.split(parameter)[0]
                length = decl[decl.find("[")+1:decl.find("]")]
            parameter_infos = [parameter_category, input_type.strip(), length]
            target_inputs_type[parameter] = parameter_infos
    return target_inputs_type



def get_target_type_of_inputs(target_function_call: str, target_input_declaration: Union[str, list]):
    target_call_custom = target_function_call.replace('&', '')
    target_call_custom = target_call_custom.replace(',', '')
    target_all_inputs = target_call_custom[target_call_custom.find("(")+1:target_call_custom.find(")")]
    target_all_inputs = target_all_inputs.split()
    target_inputs_type = {}
    parameter_found = False
    parameter_infos = []
    for i in range(len(target_input_declaration)):
        parameter_category = 'default'
        length = '0'  # we set length = 0  for a variable of type pointer
        decl = target_input_declaration[i].strip()
        parameter = target_all_inputs[i]
        if parameter in decl:
            input_type = ''
            if '[' not in decl and ']' not in decl:
                if '*' in decl:
                    input_type = decl.split('*')[0]
                    parameter_category = 'pointer'
                else:
                    input_type = decl.split(parameter)[0]
                    length = '0'
                    if '=' in decl:
                        length = decl.split('=')[-1]
            else:
                parameter_category = 'array'
                input_type = decl.split(parameter)[0]
                length = decl[decl.find("[")+1:decl.find("]")]
            parameter_infos = [parameter_category, input_type.strip(), length]
            target_inputs_type[parameter] = parameter_infos
    return target_inputs_type


def timecop_test_harness_template(target_basename: str, target_call: str,  target_return_type: str,
                                  target_includes: Union[str, list], target_input_declaration: Union[str, list],
                                  secret_arguments: Union[str, list], random_data: Optional[Union[list, dict]],
                                  path_to_test_harness: Optional[str] = None,
                                  target_macro: Optional[Union[str, list, dict]] = None) -> None:
    """timecop_test_harness_template:  Generate a test harness template (default) for timecop"""
    test_harness_directory = f'timecop/{target_basename}'
    target_test_harness = path_to_test_harness
    if path_to_test_harness:
        test_harness_directory = os.path.dirname(path_to_test_harness)
    else:
        target_test_harness = f'{test_harness_directory}/{target_basename}.c'
    util.create_directory(test_harness_directory)
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
        elif isinstance(target_macro, dict):
            for macro_name, macro_value in target_macro.items():
                if not macro_name.startswith('#define'):
                    macro = f'#define {macro_name} {macro_value}'
                macros += f'{macro}'
    type_of_random_data = get_target_type_of_inputs(target_call, target_input_declaration)
    updated_declaration, random_data_block, total_size, deallocate_block = timecop_update_declaration(target_call,
                                                                                                      target_input_declaration, random_data)
    poison_block, unpoison_block = timecop_poison_secret_data(secret_arguments, random_data,
                                                              target_input_declaration, target_call)
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
        target_exit_point = 'return 0;'
    else:
        target_result = f'{target_return_type} ct_result = '
        target_exit_point = 'return ct_result;'
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
    
    #include <poison.h>
    #include "toolchain_randombytes.h"
    '''
    main_function_block = f'''
    int main(){{
    \t{updated_declaration}
    \t{random_data_block}
    \t{poison_block}
    \t{ct_test_target_call}
    \t{unpoison_block}
    \t{deallocate_block}
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


def dudect_test_harness_template(target_basename: str, target_call: str,  target_return_type: str,
                                 target_includes: Union[str, list], target_input_declaration: Union[str, list],
                                 secret_arguments: Union[str, list], random_data: Optional[Union[list, dict]],
                                 path_to_test_harness: Optional[str] = None,
                                 number_of_measurement: Optional[Union[str, int]] = '1e5',
                                 target_macro: Optional[Union[str, list, dict]] = None) -> None:
    """dudect_test_harness_template:  Generate a test harness template (default) for dudect"""
    test_harness_directory = f'dudect/{target_basename}'
    target_test_harness = path_to_test_harness
    if path_to_test_harness:
        test_harness_directory = os.path.dirname(path_to_test_harness)
    else:
        target_test_harness = f'{test_harness_directory}/{target_basename}.c'
    util.create_directory(test_harness_directory)
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
        elif isinstance(target_macro, dict):
            for macro_name, macro_value in target_macro.items():
                if not macro_name.startswith('#define'):
                    macro = f'#define {macro_name} {macro_value}'
                macros += f'{macro}'
    parameters_info = timecop_get_type_of_inputs(target_call, target_input_declaration)
    type_of_random_data = []
    for param, param_info in parameters_info.items():
        if param_info[0] == 'pointer':
            type_of_random_data.append([param, param_info[0], param_info[1], param_info[2]])
    declaration_random_data_block, total_data_size = dudect_update_declaration(target_call,
                                                                               target_input_declaration, random_data)

    target_call = target_call.strip()
    if not target_call.endswith(';'):
        target_call += ';'
    target_result = ''
    target_exit_point = ''
    if target_return_type.strip() == 'void':
        target_exit_point = 'return 0;'
    else:
        target_result = f'{target_return_type} ct_result = '
        target_exit_point = 'return ct_result;'
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

    do_one_computation_block = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    \t{declaration_random_data_block}
    \t{ct_test_target_call}
    \t{target_exit_point}
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
    main_function_block = f'''
    int main(int argc, char **argv)
    {{
    \t(void)argc;
    \t(void)argv;

    \tdudect_config_t config = {{
    \t\t.chunk_size = {total_data_size},
    \t\t.number_measurements = NUMBER_OF_MEASUREMENTS,
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
    dudect_test_harness_block = f'''
    {headers_block}
    {target_includes_headers}
    #define DUDECT_IMPLEMENTATION
    #include <dudect.h>
    {macros}
    #define NUMBER_OF_MEASUREMENTS {number_of_measurement}
    {do_one_computation_block}
    {prepare_inputs_block}
    {main_function_block}
    '''

    with open(target_test_harness, "w+") as t_harness_file:
        t_harness_file.write(textwrap.dedent(dudect_test_harness_block))


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


def generic_template(target_basename: str, tools: Union[str, list], targets_dict: dict,
                     number_of_measurement: Optional[Union[str, int]] = '1e5', template_only: Optional[bool] = False,
                     compile_test_harness_and_run: Optional[bool] = True, run_test_only: Optional[bool] = False):
    target_dict = parse_target_json_file(targets_dict, target_basename)
    target_dict = target_dict[target_basename]
    target_call = target_dict['target_call']
    target_return_type = target_dict['target_return_type']
    target_input_declaration = target_dict['target_input_declaration']
    target_includes = target_dict['target_include_header']
    target_secret_inputs = target_dict['secret_inputs']
    target_macro = target_dict['macro']
    random_data = target_dict['random_data']
    path_to_link_library = target_dict['link_binary']
    path_to_include_directory = target_dict['path_to_include_directory']
    compiler = target_dict['compiler']
    compilation_flags = target_dict['compilation_flags']
    if not compilation_flags:
        compilation_flags = []
    else:
        if isinstance(compilation_flags, str):
            compilation_flags = compilation_flags.split()
    # To be set as input parameters
    sse_timeout = '120'
    timeout = '300'
    depth = '1000000'
    extended_library = ''
    template_compilation_execution = True
    # To be set as input parameters
    for tool in tools:
        path_to_target_wrapper = f'{tool}/{target_basename}/{target_basename}.c'
        path_to_target_binary = f'{tool}/{target_basename}/{target_basename}'
        if template_only:
            template_compilation_execution = False
            if tool.strip() == 'binsec':
                binsec_test_harness_template(target_basename, target_call, target_return_type, target_includes,
                                             target_input_declaration, target_secret_inputs,
                                             None, target_macro, random_data)
            if tool.strip() == 'timecop':
                timecop_test_harness_template(target_basename, target_call,  target_return_type, target_includes,
                                              target_input_declaration, target_secret_inputs, random_data,
                                              None, target_macro)
            if tool.strip() == 'dudect':
                dudect_test_harness_template(target_basename, target_call,  target_return_type, target_includes,
                                             target_input_declaration, target_secret_inputs, random_data,
                                             None, number_of_measurement, target_macro)
        elif run_test_only:
            template_compilation_execution = False
            generic_run(tool, target_basename, depth, sse_timeout, timeout)
        elif compile_test_harness_and_run:
            template_compilation_execution = False
            cflags = ["-g"]
            if tool.strip() == 'dudect':
                extended_library = "m"
                cflags = ["-std=c11"]
            libraries_names = Path(path_to_link_library).stem
            libraries_names += f' {extended_library}'
            path_to_directory_link_library = os.path.dirname(path_to_link_library)
            compilation_flags.extend(cflags)
            generic_compilation(path_to_target_wrapper, path_to_target_binary, path_to_directory_link_library,
                                libraries_names, path_to_include_directory, cflags, compiler)
            generic_run(tool, target_basename, depth, sse_timeout, timeout)
        if template_compilation_execution:
            cflags = ["-g"]
            if tool.strip() == 'binsec':
                binsec_test_harness_template(target_basename, target_call, target_return_type, target_includes,
                                             target_input_declaration, target_secret_inputs,
                                             None, target_macro, random_data)
            if tool.strip() == 'timecop':
                timecop_test_harness_template(target_basename, target_call,  target_return_type, target_includes,
                                              target_input_declaration, target_secret_inputs, random_data,
                                              None, target_macro)
            if tool.strip() == 'dudect':
                dudect_test_harness_template(target_basename, target_call,  target_return_type, target_includes,
                                             target_input_declaration, target_secret_inputs, random_data,
                                             None, number_of_measurement, target_macro)
                extended_library = "m"
                cflags = ["-std=c11"]
            compilation_flags.extend(cflags)
            libraries_names = Path(path_to_link_library).stem
            libraries_names += f' {extended_library}'
            path_to_directory_link_library = os.path.dirname(path_to_link_library)
            generic_compilation(path_to_target_wrapper, path_to_target_binary, path_to_directory_link_library,
                                libraries_names, path_to_include_directory, cflags, compiler)
            generic_run(tool, target_basename, depth, sse_timeout, timeout)


def generic_run(tool: str, target_basename, depth: Optional[Union[str, int]] = '1000000',
                sse_timeout: Optional[Union[str, int]] = '120', timeout: Optional[Union[str, int]] = '300'):
    path_to_output_file = f'{tool}/{target_basename}/ct_test_output.txt'
    path_to_target_binary = f'{tool}/{target_basename}/{target_basename}'
    if tool.strip() == 'binsec':
        path_to_gdb_script = f'{tool}/{target_basename}/{target_basename}.gdb'
        path_to_snapshot_file = f'{tool}/{target_basename}/{target_basename}.snapshot'
        path_to_cfg_file = f'{tool}/{target_basename}/cfg.ini'
        path_to_stats_files_file = f'{tool}/{target_basename}/stats.toml'
        binsec_generate_gdb_script(path_to_gdb_script, path_to_snapshot_file)
        binsec_generate_core_dump(path_to_target_binary, path_to_gdb_script)
        run_binsec(path_to_snapshot_file, path_to_cfg_file,
                   path_to_stats_files_file, path_to_output_file, depth)
    if tool.strip() == 'timecop':
        run_timecop(path_to_target_binary, path_to_output_file)
    if tool.strip() == 'dudect':
        run_dudect(path_to_target_binary, path_to_output_file, timeout)


def generic_tests_templates(user_entry_point: str, targets: Optional[Union[str, list]] = None,
                            tools: Optional[Union[str, list]] = None,
                            number_of_measurement: Optional[Union[str, int]] = '1e5',
                            template_only: Optional[bool] = False,
                            compile_test_harness_and_run: Optional[bool] = True, run_test_only: Optional[bool] = False):
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
    else:
        for target in all_targets:
            targets_under_tests.append(list(target.keys())[0])
    for target in targets_under_tests:
        generic_template(target, chosen_tools, all_targets, number_of_measurement,
                         template_only, compile_test_harness_and_run, run_test_only)


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
