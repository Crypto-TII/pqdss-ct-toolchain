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

from subprocess import Popen

from typing import Optional, Union, List


def create_directory(path_to_directory: str) -> None:
    try:
        os.makedirs(path_to_directory, exist_ok=True)
    except FileNotFoundError:
        print("Error: Attempting to create a directory with no name ")


def create_file(path_to_file: str, default_file: Optional[str] = None):
    if path_to_file:
        if os.path.isdir(path_to_file):
            print("Error: {} is not a  directory, not a file".format(path_to_file))
            return None
        file_directory_split = path_to_file.split('/')
        file_directory = "/".join(file_directory_split[:-1])
        create_directory(file_directory)
    else:
        default_f = default_file
        file_basename_split = default_f.split('/')
        file_directory = "/".join(file_basename_split[:-1])
        if file_directory:
            path_to_file = f'{file_directory}/{default_file}.c'
        else:
            path_to_file = f'{default_file}.c'
    return path_to_file


def find_ending_pattern(folder, pattern):
    test_folder = glob.glob(folder + '/*' + pattern)
    return test_folder[0]


def get_default_list_of_folders(candidate_default_list_of_folders, tools_list):
    for tool_name in tools_list:
        if tool_name in candidate_default_list_of_folders:
            candidate_default_list_of_folders.remove(tool_name)
    return candidate_default_list_of_folders


# A candidate is a string. It refers to as the declaration of a function.
# An object of type Candidate has many attributes like the base name of a given candidate,
# its list of arguments in the (type name) format, the list of its names of arguments, etc.
# Such type of object also incorporate many methods used to set some attributes. For example,
# the arguments names are given by the method get_candidate_arguments_names().
class Target(object):
    def __init__(self, candidate):
        self.candidate = candidate
        self.candidate_arguments_with_types = {}
        self.candidate_return_type = ""
        self.candidate_types = []
        self.candidate_args_names = []
        self.candidate_args_declaration = []
        self.candidate_args_length = []
        self.candidate_basename = ""
        self.candidate_test_harness_name = ""
        self.candidate_source_file_name = ""
        self.candidate_executable = ""
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
            token = tokenize_target(self.candidate)
            self.candidate_return_type = token[0]
            self.candidate_basename = token[1]
            self.candidate_types = token[2]
            self.candidate_args_names = token[3]
            self.candidate_args_declaration = token[4]
            self.candidate_args_length = token[5]
        return self.candidate_has_arguments_status

    def get_candidate_basename(self):
        return self.candidate_basename

    def get_candidate_configuration_basename(self):
        return self.candidate_basename + ".cfg"

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
        if self.tool_name == 'ctverif' or self.tool_name == 'ct-verif':
            self.tool_flags = "--unroll 1 --loop-limit 1"
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
        if self.tool_name == 'ctverif' or self.tool_name == 'ct-verif':
            self.tool_test_file_name = "wrapper"
            keypair = f'crypto_sign_keypair_{self.tool_test_file_name}'
            sign = f'crypto_sign_{self.tool_test_file_name}'
            return keypair, sign

    @staticmethod
    def binsec_configuration_files():
        kp_cfg = "cfg_keypair"
        sign_cfg = "cfg_sign"
        return kp_cfg, sign_cfg


# tokenize_candidate: for a given function declaration (candidate), extracts:
# 1. function return type (void is excluded)
# 2. function name
# 3. arguments names
# 4. arguments types
# 5. default declaration/initialisation of arguments

# NOTE: Take into account the case in which one have a pointer input
# that points to just one value (not really as an array)
def tokenize_target(target: str) -> tuple:
    target_declaration_split = target.split('(', 1)
    target_args = target_declaration_split[-1]
    target_return_type_and_basename = target_declaration_split[0]
    target_return_type_and_basename_split = target_return_type_and_basename.split()
    target_basename = target_return_type_and_basename_split[-1].strip()
    target_return_type_and_basename_split.remove(target_basename)
    target_return_type = " ".join(target_return_type_and_basename_split)
    target_args = re.sub('\)\s*;', '', target_args)
    target_args_names = []
    target_args_types = []
    target_args_type_name_length = []
    target_input_names = []
    target_input_initialization = []
    target_args_length = []
    default_length = None
    arg_name = ''
    arg_type = ''
    target_all_types_of_input = []
    target_args_split = target_args.split(',')
    reconstructed_target_args_split = []
    arg_index = 0
    while arg_index < len(target_args_split):
        current_arg = target_args_split[arg_index]
        while current_arg.count('(') != current_arg.count(')'):
            current_arg = ",".join(target_args_split[arg_index:arg_index+2])
            arg_index += 1
        arg_index += 1
        reconstructed_target_args_split.append(current_arg)
    for input_arg in reconstructed_target_args_split:
        input_arg = input_arg.strip()
        default_length = None
        arg_match_array = re.search(r'\s*\[(.*)]', input_arg)
        if arg_match_array is not None:
            arg_length = arg_match_array.group()
            arg_length = arg_length.strip()
            copy_input_arg = input_arg
            copy_input_arg = copy_input_arg.replace(arg_length, '')
            copy_input_arg_split = copy_input_arg.split()
            arg_name = copy_input_arg_split[-1]
            arg_name = arg_name.strip()
            arg_type = " ".join(copy_input_arg_split[0:-1])
            arg_type = arg_type.strip()
            arg_length = arg_length[1:-1]
            default_length = arg_length
        else:
            default_length = None
            input_argument = input_arg
            if '*' in input_arg:
                default_length = 'DEFAULT_LENGTH'
                input_argument = re.sub('\*', '', input_argument)
            input_arg_split = input_argument.split()
            arg_type = " ".join(input_arg_split[0:-1])
            arg_type = arg_type.strip()
            arg_name = input_arg_split[-1]
            arg_name = arg_name.strip()
        target_all_types_of_input.append(arg_type)
        target_input_names.append(arg_name)
        target_args_type_name_length.append((arg_type, arg_name, default_length))
        target_args_length.append(default_length)
        arg_declaration = f'{input_arg};'
        target_input_initialization.append(arg_declaration)
    output = (target_return_type, target_basename,
              target_all_types_of_input, target_input_names,
              target_input_initialization, target_args_length)
    return output


# Get crypto_sign_keypair and crypto_sign functions declarations given the path to the header file (api.h/sign.h)
def find_target_by_basename2(target_basename: str, path_to_target_header_file: str) -> str:
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
                if '' in matching_string_lines:
                    index_empty_str = matching_string_lines.index('')
                    matching_string_lines = matching_string_lines[index_empty_str+1:]
                find_target_index = 0
                for line in matching_string_lines:
                    if target_basename in line:
                        find_target_index = matching_string_lines.index(line)
                # if 'ndef' in matching_string_lines:
                #     index_empty_str = matching_string_lines.index('')
                #     matching_string_lines = matching_string_lines[index_empty_str+1:]
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
                # matching_string_lines = matching_string_lines[find_target_index:]
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


def find_target_by_basename_from_source_file(target_basename: str, path_to_target_src_file: str) -> str:
    target = ''
    try:
        with open(path_to_target_src_file, 'r') as file:
            file_content = file.read()
            find_target_object = re.search(rf"[\w\s]*\W{target_basename}\W[\s*\(]*[\w\s*,\[\+\]\(\)-]*", file_content)
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
                Could not find {target_basename} into the file {path_to_target_src_file}
                '''
                print(print(textwrap.dedent(error_message)))
    except:
        print("Could not open file '{}' .".format(path_to_target_src_file))

    return target


def find_sign_and_keypair_definition_from_api_or_sign(api_sign_header_file):
    keypair = 'crypto_sign_keypair'
    sign = 'crypto_sign'
    keypair_def = find_target_by_basename(keypair, api_sign_header_file)
    sign_def = find_target_by_basename(sign, api_sign_header_file)
    keypair_sign_def = [keypair_def, sign_def]
    return keypair_sign_def


def find_verification_definition_from_api_or_sign(api_sign_header_file):
    verification = 'crypto_sign_open'
    verify_def = find_target_by_basename(verification, api_sign_header_file)
    return verify_def


# sign_find_args_types_and_names: gets 'crypto_sign_keypair' arguments types/names and its return type
def sign_find_args_types_and_names(abs_path_to_api_or_sign):
    keypair_sign_def = find_sign_and_keypair_definition_from_api_or_sign(abs_path_to_api_or_sign)
    sign_candidate = keypair_sign_def[1]
    cand_obj = Target(sign_candidate)
    args_names = cand_obj.candidate_args_names
    args_types = cand_obj.candidate_types
    cand_basename = cand_obj.get_candidate_basename()
    cand_return_type = cand_obj.candidate_return_type
    return cand_return_type, cand_basename, args_types, args_names


# sign_find_args_types_and_names: get 'crypto_sign' arguments types/names and its return type
def keypair_find_args_types_and_names(abs_path_to_api_or_sign):
    keypair_sign_def = find_sign_and_keypair_definition_from_api_or_sign(abs_path_to_api_or_sign)
    keypair_candidate = keypair_sign_def[0]
    cand_obj = Target(keypair_candidate)
    args_names = cand_obj.candidate_args_names
    args_types = cand_obj.candidate_types
    cand_basename = cand_obj.get_candidate_basename()
    cand_return_type = cand_obj.candidate_return_type
    return cand_return_type, cand_basename, args_types, args_names


def verify_find_args_types_and_names(abs_path_to_api_or_sign):
    verify_sign_def = find_verification_definition_from_api_or_sign(abs_path_to_api_or_sign)
    verify_candidate = verify_sign_def[1]
    cand_obj = Target(verify_candidate)
    args_names = cand_obj.candidate_args_names
    args_types = cand_obj.candidate_types
    cand_basename = cand_obj.get_candidate_basename()
    cand_return_type = cand_obj.candidate_return_type
    return cand_return_type, cand_basename, args_types, args_names


# ======================CREATE folders ==================================
# =======================================================================

# Create same sub-folders in each folder of a given list of folders
def generic_create_tests_folders(list_of_path_to_folders):
    for t_folder in list_of_path_to_folders:
        if not os.path.isdir(t_folder):
            cmd = ["mkdir", "-p", t_folder]
            subprocess.call(cmd, stdin=sys.stdin)


def compile_with_makefile(path_to_makefile, default=None, *args, **kwargs):
    print(":::::::compile_with_makefile:::::::")
    print(".....path_to_makefile: ", path_to_makefile)
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    # Set the tool's flags in the Makefile
    makefile = 'Makefile'
    set_tool_flags = [f"sed -i 's/^TOOLS_FLAGS := .*$/TOOLS_FLAGS := /g' {makefile}"]
    subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
    # For now for benchmark. But this should be generic
    set_tool_flags = [f"sed -i 's/^TOOL_LINK_LIBS := .*$/TOOL_LINK_LIBS := /g' {makefile}"]
    subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
    # Run make clean first in case objects files have already been obtained with the flags of a different tool.
    cmd_clean = ["make", "clean"]
    subprocess.call(cmd_clean, stdin=sys.stdin)
    additional_options = list(args)
    for key, val in kwargs.items():
        additional_options.append(f'{key}={val}')
    cmd = ["make"]
    if not additional_options:
        cmd.append('all')
    cmd.extend(additional_options)
    if default:
        cmd.append(default)
    print("++++++++++++cmd++++++++++++: ", cmd)
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)


def compile_with_cmake_14(build_folder_full_path, optional_flags=None, *args, **kwargs):
    if optional_flags is None:
        optional_flags = []
    cwd = os.getcwd()
    create_directory(build_folder_full_path)
    # Set the tool's flags in the CMakeLists.txt
    cmakelist = '../CMakeLists.txt'
    set_tool_flags = [f"sed -i -E 's/(TOOLS_FLAGS .+)/TOOLS_FLAGS "")/g'" + f" {cmakelist}"]
    subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
    set_tool_name = [f"sed -i -E 's/(TOOL_NAME .+)/TOOL_NAME "")/g'" + f" {cmakelist}"]
    subprocess.call(set_tool_name, stdin=sys.stdin, shell=True)
    os.chdir(build_folder_full_path)

    additional_options = list(args)
    for key, val in kwargs.items():
        additional_options.append(f'-D{key}={val}')
    cmd = ["cmake"]
    cmd.extend(additional_options)
    if not optional_flags == []:
        cmd.extend(optional_flags)
    cmd_ext = ["../"]
    cmd.extend(cmd_ext)
    print("+++++++++cmd++++++++: ", cmd)
    subprocess.call(cmd, stdin=sys.stdin)
    cmd = ["make", "-j"]
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)


def compile_with_cmake(build_folder_full_path, optional_flags=None, *args, **kwargs):
    if optional_flags is None:
        optional_flags = []
    cwd = os.getcwd()
    create_directory(build_folder_full_path)
    os.chdir(build_folder_full_path)
    # Set the tool's flags in the CMakeLists.txt
    cmakelist = '../CMakeLists.txt'
    set_tool_flags = [f"sed -i -E 's/(TOOLS_FLAGS .+)/TOOLS_FLAGS "")/g'" + f" {cmakelist}"]
    subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
    set_tool_name = [f"sed -i -E 's/(TOOL_NAME .+)/TOOL_NAME "")/g'" + f" {cmakelist}"]
    subprocess.call(set_tool_name, stdin=sys.stdin, shell=True)
    # For now for benchmark. But this should be generic
    set_tool_flags = [f"sed -i 's/^TOOL_LINK_LIBS := .*$/TOOL_LINK_LIBS := /g' {cmakelist}"]
    subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
    additional_options = list(args)
    for key, val in kwargs.items():
        additional_options.append(f'-D{key}={val}')
    cmd = ["cmake"]
    cmd.extend(additional_options)
    if not optional_flags == []:
        cmd.extend(optional_flags)
    cmd_ext = ["../"]
    cmd.extend(cmd_ext)
    print("+++++++++cmd++++++++: ", cmd)
    subprocess.call(cmd, stdin=sys.stdin)
    cmd = ["make", "-j"]
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)

def compile_target_candidate(path_to_candidate_makefile_cmake: str,
                             build_with_make: bool = True, additional_options=None, *args, **kwargs):
    print(":::::::compile_target_candidate::::::::")
    print("..........path_to_candidate_makefile_cmake: ", path_to_candidate_makefile_cmake)
    if build_with_make:
        compile_with_makefile(path_to_candidate_makefile_cmake, additional_options, *args, **kwargs)
    if not build_with_make:
        path_to_build_folder = f'{path_to_candidate_makefile_cmake}/build'
        compile_with_cmake(path_to_build_folder, additional_options, *args, **kwargs)


def generic_compilation(path_to_target_wrapper: str, path_to_target_binary: str,
                        path_to_test_library_directory: str, libraries_names: [Union[str, list]],
                        path_to_include_directories: Union[str, list], cflags: list, compiler: str = 'gcc'):
    target_include_dir = path_to_include_directories
    target_link_libraries = []
    if isinstance(libraries_names, str):
        target_link_libraries.extend(libraries_names.split())
    elif isinstance(libraries_names, list):
        target_link_libraries.extend(libraries_names.copy())
    target_link_libraries = list(set(target_link_libraries))
    target_link_libraries = list(map(lambda incs: f'{incs}' if '-l' in incs else f'-l{incs}', target_link_libraries))
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
    print("----------cmd: ")
    print(cmd)
    subprocess.call(cmd, stdin=sys.stdin, shell=True)



def generic_target_compilation_1(path_candidate: str, path_to_test_library_directory: str,
                               libraries_names: [Union[str, list]], path_to_include_directories: Union[str, list],
                               cflags: list, default_instance: str, instances: Optional[Union[str, list]] = None, compiler: str = 'gcc',
                               binary_patterns: Optional[Union[str, list]] = None):

    test_keypair_basename, test_sign_basename = '', '' # tool_type.get_tool_test_file_name() to be fixed
    keypair_sign = []
    path_to_tool_folder = f'{path_candidate}' # to be fixed
    path_to_instances = [path_to_tool_folder]
    candidate = path_candidate.split('/')[-1]
    instances_list = []
    if instances:
        instances_list = []
        if isinstance(instances, str):
            instances_list = instances.split()
        elif isinstance(instances, list):
            instances_list = instances.copy()
    else:
        instances_list = ["."]
    for instance in instances_list:
        if instance == ".":
            path_to_instance = f'{path_to_tool_folder}'
        else:
            path_to_instance = f'{path_to_tool_folder}/{instance}'
            path_to_include_directories_split = path_to_include_directories.split(default_instance)
            path_to_include_directories_split.insert(1, instance)
            path_to_include_directories = "".join(path_to_include_directories_split)
            if default_instance in path_to_test_library_directory:
                path_to_test_library_directory_split = path_to_test_library_directory.split(default_instance)
                path_to_test_library_directory_split.insert(1, instance)
                path_to_test_library_directory = "".join(path_to_test_library_directory_split)

        if binary_patterns is not None:
            if isinstance(binary_patterns, str):
                keypair_sign.append(binary_patterns.split())
            else:
                keypair_sign = binary_patterns.copy()
        else:
            binary_patterns = ['keypair', 'sign']
        for bin_pattern in binary_patterns:
            target_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_target_wrapper = f'{path_to_instance}/{target_folder_basename}/{test_sign_basename}'
            if bin_pattern.strip() == 'keypair':
                path_to_target_wrapper = f'{path_to_instance}/{target_folder_basename}/{test_keypair_basename}'
            path_to_target_binary = path_to_target_wrapper.split('.c')[0]
            generic_compilation(path_to_target_wrapper, path_to_target_binary, path_to_test_library_directory,
                                libraries_names, path_to_include_directories, cflags, compiler)


def parse_candidates_json_file(candidates_dict: dict, candidate: str):
    candidates = candidates_dict.keys()
    if candidate not in candidates:
        # We should raise an error
        print("There is no candidate named {}".format(candidate))
        return None
    else:
        return candidates_dict[candidate]

# ====================== ADD CLI OPTIONS ==================================
# =======================================================================


# add_generic_cli_templates_arguments: for generic tests, create a subparser for a given target
def add_generic_cli_templates_arguments(subparser,
                                        generate_template_run,
                                        tools_list=None,
                                        target_basename=None,
                                        path_to_header_file=None,
                                        path_to_target_test_file=None,
                                        target_secret_inputs=None,
                                        target_dependent_src_files=None,
                                        target_dependent_header_files=None,
                                        target_include_directory=None,
                                        target_cflags=None,
                                        target_libraries=None,
                                        target_build_directory=None,
                                        runtime_output_directory=None,
                                        template_only=None,
                                        compile_and_run_only=None,
                                        redirect_test_output_to_file=None,
                                        security_level=None,
                                        number_of_measurements='1e4',
                                        timeout='86400'):

    # if candidate_default_list_of_folders is None:
    #     candidate_default_list_of_folders = []
    generic_parser = subparser.add_parser(f'{generate_template_run}',
                                            help=f'{generate_template_run}:...',
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Default tools list
    default_tools_list = ["binsec", "ctgrind", "dudect", "flowtracker"]
    arguments = f"'--tools', '-tools', dest='tools', nargs='+', default={default_tools_list}, help = '{tools_list}'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--target_header', '-type',dest='header',type=str,default=f'{path_to_header_file}', \
    help=' {path_to_header_file}'"
    add_args_commdand = f"generic_parser.add_argument(f{arguments})"
    exec(add_args_commdand)
    arguments = f"'--target_basename', '-target',dest='target',type=str,default=f'{target_basename}', \
    help ='target basename'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--test_harness', '-test_harness',dest='test_harness', type=str, \
    default=f'{path_to_target_test_file}',"
                 f"help = 'path to the test harness file'")
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--secret_inputs', nargs='+', default={target_secret_inputs}"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--required_sources_files', nargs='+', default={target_dependent_src_files}, \
    help = 'required source files'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--required_include_files', nargs='+', default={target_dependent_header_files}, \
    help = 'required header files'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--include_directories', nargs='+', default={target_include_directory}, help = 'include directories'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--cflags', nargs='+', default={target_cflags}, help = 'target cflags for compilation'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--libraries', nargs='+', default={target_libraries}, help = 'target link libraries'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--build', '-build', dest='build',default=f'{target_build_directory}'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--runtime_output_directory', '-runtime_output_directory', dest='runtime', \
    default=f'{runtime_output_directory}'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--template_only','-template_only',dest='template_only', default=f'{template_only}',help = 'no'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--compile_run','-compile_run',dest='compile_run', default=f'{compile_and_run_only}', help='no'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--redirect_output','-redirect_output',dest='redirect_output', \
    default=f'{redirect_test_output_to_file}', help='no'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--security_level','-security_level', dest='security_level', default={security_level},\
    help = 'Instance security level'")
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--number_measurements','-number_measurements', dest='number_measurements',\
     default={number_of_measurements}, help = 'Number of measurements (Dudect)'")
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = (f"'--timeout','-timeout', dest='timeout',\
     default={timeout}, help = 'timeout (Dudect)'")
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)


# run_given_tool_on_all_candidates: Run a given tool on all integrated candidates
def run_given_tool_on_all_candidates(tools_list: list, list_all_candidates: list, list_of_options):
    ref_opt_add_impl_folder = ""
    timeout = ""
    depth = ""
    number_of_measurements = ""
    algorithms_patterns = ""
    for element in list_of_options:
        if 'ref_opt_add_implementation' in element:
            ref_opt_add_impl_folder = element.split('=')[-1]
        if 'timeout' in element:
            timeout = element.split('=')[-1]
        if 'number_measurements' in element:
            number_of_measurements = element.split('=')[-1]
        if 'depth' in element:
            depth = element.split('=')[-1]
        if 'algorithms_patterns' in element:
            algorithms_patterns = element.split('=')[-1]
    for tool in tools_list:
        for candidate in list_all_candidates:
            command_str = f'''python3 toolchain-scripts/toolchain_script.py {candidate} --tools {tool} '''
            if ref_opt_add_impl_folder:
                command_str += f'--ref_opt_add_implementation {ref_opt_add_impl_folder} '
            if timeout:
                command_str += f'--timeout {timeout} '
            if number_of_measurements:
                command_str += f'--number_measurements {number_of_measurements} '
            if depth:
                command_str += f'--depth {depth} '
            if algorithms_patterns:
                command_str += f'--algorithms_patterns {algorithms_patterns} '

            command = command_str.split()
            subprocess.call(command, stdin=sys.stdin)
