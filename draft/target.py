#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import textwrap
import re


# Get crypto_sign_keypair and crypto_sign functions declarations given the path to the header file (api.h/sign.h)
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
                if '' in matching_string_lines:
                    index_empty_str = matching_string_lines.index('')
                    matching_string_lines = matching_string_lines[index_empty_str+1:]
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



# target_basename = "sign_phase1_round"
# path_to_target_src_file = "candidates/mpc-in-the-head/mirith/Optimized_Implementation/mirith_avx2_Ia_fast/sign.c"
#
# target = find_target_by_basename_from_source_file(target_basename, path_to_target_src_file)
# print("+++++target found")
# print(target)

# Take into account the case in which one have a pointer input
# that points to just one value (not really as an array)
def tokenize_target(target: str) -> tuple:
    target_declaration_split = target.split('(', 1)
    target_args = target_declaration_split[-1]
    target_return_type_and_basename = target_declaration_split[0]
    target_return_type_and_basename_split = target_return_type_and_basename.split()
    target_return_type = target_return_type_and_basename_split[0].strip()
    target_basename = target_return_type_and_basename_split[-1].strip()
    target_args = re.sub('\)\s*;', '', target_args)
    if target_args.strip() == '':
        print("The function {} has no arguments", target_basename)
        return ()
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


# A target is a string. It refers to as the declaration of a function.
# An object of type target has many attributes like the base name of a given target,
# its list of arguments in the (type name) format, the list of its names of arguments, etc.
# Such type of object also incorporate many methods used to set some attributes. For example,
# the arguments names are given by the method get_target_arguments_names().
class Target(object):
    """class: Target"""
    def __init__(self, target: str = None, target_basename: str = None, target_header_or_src_file: str = None):
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
        self.path_to_target_header_or_src_file = target_header_or_src_file
        self.target_arguments_with_types = {}
        self.target_has_arguments = True
        # Set the attributes of the target
        self.get_target_attributes()

    def find_by_basename(self, basename, path_to_target_header_or_src_file: str) -> str:
        if path_to_target_header_or_src_file.endswith('.h'):
            self.target = find_target_by_basename(basename, path_to_target_header_or_src_file)
        else:
            self.target = find_target_by_basename_from_source_file(basename, path_to_target_header_or_src_file)
        return self.target

    def is_valid_target(self):
        if '(' not in self.target or ')' not in self.target:
            if self.path_to_target_header_or_src_file is None or self.path_to_target_header_or_src_file.strip() == '':
                invalid_target_error_message = f'''
                '{self.target.upper()}' is not a valid target.
                Please give the target basename name and the path to its header file.
                Alternatively, give the full target declaration '''
                print(textwrap.dedent(invalid_target_error_message))
            else:
                self.target = self.find_by_basename(self.target_basename, self.path_to_target_header_or_src_file)
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
            token = tokenize_target(self.target)
            self.target_return_type = token[0]
            self.target_basename = token[1]
            self.target_types = token[2]
            self.target_args_names = token[3]
            self.target_args_declaration = token[4]
            self.target_args_length = token[5]
        return self.target_has_arguments
