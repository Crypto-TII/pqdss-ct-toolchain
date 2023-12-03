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


def find_ending_pattern(folder, pattern):
    test_folder = glob.glob(folder + '/*' + pattern)
    return test_folder[0]


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


def run_dudect(binary_file, output_file):
    command = f'./{binary_file}'
    print("::::::::Running current command: ", command)
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file, "w") as file:
        for line in output_decode.split('\n'):
            file.write(line + '\n')


def run_flowtracker(rbc_file, xml_file, output_file):
    command = f'''opt -basicaa -load AliasSets.so -load DepGraph.so -load bSSA2.so -bssa2 \
            -xmlfile {xml_file} {rbc_file} 2> {output_file}.out
        '''
    cmd_args_lst = command.split()
    subprocess.call(cmd_args_lst, stdin=sys.stdin)


def compile_for_flowtracker(target_src_file, output_directory=".", target_dependencies="", target_includes=""):
    target_basename = os.path.basename(target_src_file)
    target_basename = target_basename.split(".c")[0]
    target_src_file_basename = target_src_file.split(".c")[0]
    output_bc_file = ""  # compile src c file to llvm
    command = ''
    if output_directory == ".":
        output_bc_file = target_src_file_basename
    else:
        command += f'''clang -emit-llvm'''
        if target_dependencies:
            output_bc_file = f'{output_directory}/{target_src_file_basename}'
            command += f''' {target_dependencies}'''
        if target_includes:
            command += f''' -I{target_includes}'''

        output_bc_file = f'{output_directory}/rbc_{target_basename}'
    command += f''' -c -g {target_src_file} -o {output_bc_file}.bc'''
    cmd_args_lst = command.split()
    print("command split")
    print(cmd_args_lst)
    subprocess.call(cmd_args_lst, stdin=sys.stdin)
    compiled_file = ""
    command = f'''opt -instnamer -mem2reg {output_bc_file}.bc > {compiled_file}.rbc'''
    cmd_args_lst = command.split()
    subprocess.call(cmd_args_lst, stdin=sys.stdin)



# src_file = 'mpc-in-the-head/mirith/Optimized_Implementation/mirith_avx2_Ia_fast/sign.c'
# output_directory = 'mpc-in-the-head/mirith/Optimized_Implementation/flowtracker/mirith_avx2_Ia_fast/build/mirith_keypair'
# compile_for_flowtracker(src_file, output_directory)

# clang -emit-llvm -c -g sign.c -o sign.bc opt -instnamer -mem2reg sign.bc > sign.rbc opt -basicaa
# -load AliasSets.so -load DepGraph.so -load bSSA2.so -bssa2 -xmlfile xml_crypto_sign_keypair.xml sign.rbc


# def compile_flowtracker(xml_file):
#     # Compile encrypt.c with flowtracker
#     printf "Compiling with flowtracker\n"
#
#     FLOWTRACKER_BC="${COMPILED_DIR}/flowtracker.bc"
#     FLOWTRACKER_COMPILED="${COMPILED_DIR}/flowtracker.rbc"
#     clang -emit-llvm -I${COMPILED_DIR} -I$COMMON_DIR -g -c $ENCRYPT -o $FLOWTRACKER_BC
#     [ $? -ne 0 ] && error "Error compiling provided src to llvm"
#     opt -instnamer -mem2reg $FLOWTRACKER_BC > $FLOWTRACKER_COMPILED
#     [ $? -ne 0 ] && error "Error compiling provided src with flowtracker"

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


def tokenize_target(target: str):
    target_split = re.split(r"[()]\s*", target)
    ret_type_basename = target_split[0].split(" ")
    target_return_type = ret_type_basename[0]
    target_base_name = ret_type_basename[1]
    target_args = target_split[1]
    if target_args == '' or target_args == ' ':
        print("The function {} has no arguments", target_base_name)
    else:
        target_input_names = []
        target_input_initialization = []
        target_all_types_of_input = []
        for input_arg in re.split(r",", target_args):
            type_arg, name_arg, input_declaration = tokenize_argument(input_arg)
            target_all_types_of_input.append(type_arg)
            target_input_names.append(name_arg)
            target_input_initialization.append(input_declaration)
        output = (target_return_type, target_base_name,
                  target_all_types_of_input, target_input_names,
                  target_input_initialization)
        return output


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


# A target is a string. It refers to as the declaration of a function.
# An object of type target has many attributes like the base name of a given target,
# its list of arguments in the (type name) format, the list of its names of arguments, etc.
# Such type of object also incorporate many methods used to set some attributes. For example,
# the arguments names are given by the method get_target_arguments_names().


# Call it Target instead of target
class Target(object):
    def __init__(self, target):
        self.target = target
        self.target_arguments_with_types = {}
        self.target_return_type = ""
        self.target_types = ""
        self.target_args_names = ""
        self.target_args_declaration = ""
        self.target_basename = ""
        self.target_test_harness_name = ""
        self.target_source_file_name = ""
        self.target_executable = ""  # One call it "base_name-target_bin"
        self.target_configuration_file = ""
        self.target_stats_file = ""
        self.target_assumption = ""
        self.parent_header_file = ""
        self.parent_source_file = ""
        self.target_secret_data = []
        self.target_public_data = []
        self.cmd_binsec_compilation_target = []
        self.cmd_binsec_run_target = []

        self.target_has_arguments_status = True
        self.target_split = re.split(r"[()]\s*", target)
        self.target_args = self.target_split[1]
        self.get_target_has_arguments_status()

    def get_target_has_arguments_status(self):
        if self.target_args == '' or self.target_args == ' ':
            self.target_has_arguments_status = False
        else:
            self.target_has_arguments_status = True
            token = tokenize_target(self.target)
            self.target_return_type = token[0]
            self.target_basename = token[1]
            self.target_types = token[2]
            self.target_args_names = token[3]
            self.target_args_declaration = token[4]
        return self.target_has_arguments_status

    def get_target_basename(self):
        return self.target_basename

    def get_target_source_file_basename(self):
        return self.target_basename + ".c"

    def get_target_test_harness_basename(self):
        return "test_harness_" + self.target_basename + ".c"

    def get_target_memory_init_basename(self):
        return "memory_edit_" + self.target_basename + ".txt"

    def get_target_configuration_basename(self):
        return self.target_basename + ".cfg"

    def get_target_stats_file_basename(self):
        return self.target_basename + ".toml"

    def get_target_executable_basename(self):
        return self.target_basename + "_bin"

    def get_arg_names(self):
        return self.target_args_names

    def get_target_arguments_names(self):
        return self.target_args_names

    def get_target_secret_data(self):
        for el in self.target_secret_data:
            if el not in self.target_args_names:
                error_message = 'is not an argument of the function'
                print("{0} {1}  {2}".format(el, error_message, self.target_basename))
                self.target_secret_data = []
                return self.target_secret_data
        return self.target_secret_data

    def get_target_public_data(self):
        for el in self.target_public_data:
            if el not in self.target_args_names:
                error_message = 'is not an argument of the function'
                print("{0} {1} {2}".format(el, error_message, self.target_basename))
                self.target_secret_data = []
                return self.target_secret_data
        return self.target_public_data

    def target_arguments_initialization(self, file):
        pass

    def target_arguments_declaration(self):
        return self.target_args_declaration

    def binsec_run_target(self, folder):
        target_executable_file = find_ending_pattern(folder, "_exec")
        config_file = glob.glob(folder + '/*.cfg')[0]
        stats_file = glob.glob(folder + '/*.toml')[0]
        st_file = open(stats_file, 'w')
        st_file.close()
        if self.cmd_binsec_run_target:
            subprocess.call(self.cmd_binsec_run_target, stdin=sys.stdin)
        else:
            cmd_str = f'''binsec -checkc -checkct-script
                    {config_file} -checkct-stats-file {stats_file}
                    {target_executable_file}'''
            cmd = cmd_str.split()
            subprocess.call(cmd, stdin=sys.stdin)


class Tools(object):
    """Create an object, tool, encapsulating its flags
    and execution method"""

    def __init__(self, tool_name):
        self.tool_flags = ""
        self.tool_libs = ""
        self.tool_test_file_name = ""
        self.tool_name = tool_name

    def run_binsec(self, config_file, executable_file, output_file,
                   sse_depth=1000, stats_file="", additonal_flags=None):
        # cmd_str = f'''binsec -sse -checkct -sse-depth  {sse_depth} -sse-script {config_file}
        # -checkct-stats-file {stats_file} {executable_file}'''
        # more_flags = ""
        cmd_str = f'''binsec -sse -checkct -sse-depth  {sse_depth} -sse-script {config_file} 
        -checkct-stats-file {stats_file} {executable_file}'''
        more_flags = ""
        if additonal_flags is not None:
            if type(additonal_flags) is list:
                more_flags = "".join(additonal_flags)
            elif type(additonal_flags) is str:
                more_flags = additonal_flags
            cmd_str = f'{cmd_str} {more_flags}'
        command = cmd_str.split()
        execution = subprocess.Popen(command, stdout=subprocess.PIPE)
        output, error = execution.communicate()
        output_decode = output.decode('utf-8')
        with open(output_file, "w") as file:
            for line in output_decode.split('\n'):
                file.write(line + '\n')

    def run_ctgrind(self, executable_file, output_file):
        command = f'''valgrind -s --track-origins=yes --leak-check=full 
                --show-leak-kinds=all --verbose --log-file={output_file} ./{executable_file}'''
        cmd_args_lst = command.split()
        subprocess.call(cmd_args_lst, stdin=sys.stdin)

    def run_dudect(self, executable_file, output_file):
        command = f'./{executable_file}'
        # command = f'timeout 120 ./{executable_file}'
        cmd_args_lst = command.split()
        execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
        output, error = execution.communicate()
        output_decode = output.decode('utf-8')
        with open(output_file, "w") as file:
            for line in output_decode.split('\n'):
                file.write(line + '\n')

    def run_flowtracker(self, rbc_file, xml_file, output_file):
        command = f'''opt -basicaa -load AliasSets.so -load DepGraph.so -load bSSA2.so -bssa2 \
            -xmlfile {xml_file} {rbc_file} 2> {output_file}.out
        '''
        cmd_args_lst = command.split()
        subprocess.call(cmd_args_lst, stdin=sys.stdin)

    def get_tool_flags_and_libs(self):
        if self.tool_name == 'binsec':
            self.tool_flags = "-static -g"
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

    def binsec_configuration_files(self):
        kp_cfg = "cfg_keypair"
        sign_cfg = "cfg_sign"
        return kp_cfg, sign_cfg

    def run_tool(self,config_file, executable_file, output_file,
                 sse_depth=1000, stats_file="", additonal_flags=None):
        if self.tool_name == 'binsec':
            self.run_binsec(config_file, executable_file, output_file,
                            sse_depth, stats_file, additonal_flags)
        if self.tool_name == 'dudect':
            self.run_dudect(executable_file, output_file)
        if self.tool_name == 'ctgrind':
            self.run_ctgrind(executable_file, output_file)
        if self.tool_name == 'flowtracker':
            print("----Yet to be integrated")


def tool_generic_run(tool_name, signature_type, target,
                     optimized_imp_folder, opt_src_folder_list_dir,
                     depth, build_folder, binary_patterns):
    tool_folder = tool_name
    optimized_imp_folder_full_path = signature_type + '/' + target + '/' + optimized_imp_folder
    tool_folder_full_path = optimized_imp_folder_full_path + '/' + tool_folder
    tool_type = Tools(tool_name)
    test_file = tool_type.tool_test_file_name
    if not opt_src_folder_list_dir:
        path_to_subfolder = tool_folder_full_path
        path_to_build_folder = path_to_subfolder + '/' + build_folder
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            tool_folder_basename = f'{target}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{tool_folder_basename}'
            path_to_pattern_subfolder = f'{path_to_subfolder}/{tool_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                bin_basename = executable.split(f'{test_file}_')[-1]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                if tool_type == 'binsec':
                    cfg_pattern = ".cfg"
                    stats_file = f'{path_to_pattern_subfolder}/{bin_pattern}.toml'
                    cfg_file = find_ending_pattern(path_to_pattern_subfolder, cfg_pattern)
                else:
                    cfg_file = ""
                    stats_file = ""
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                tool_type.run_tool(cfg_file, abs_path_to_executable, output_file, depth, stats_file)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = tool_folder_full_path + '/' + subfold
            path_to_build_folder = path_to_subfolder + '/' + build_folder
            path_to_binary_files = path_to_build_folder
            for bin_pattern in binary_patterns:
                tool_folder_basename = f'{target}_{bin_pattern}'
                path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{tool_folder_basename}'
                path_to_pattern_subfolder = f'{path_to_subfolder}/{tool_folder_basename}'
                bin_files = os.listdir(path_to_binary_pattern_subfolder)
                for executable in bin_files:
                    bin_basename = executable.split(f'{test_file}_')[-1]
                    output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                    if tool_type == 'binsec':
                        cfg_pattern = ".cfg"
                        stats_file = f'{path_to_pattern_subfolder}/{bin_pattern}.toml'
                        cfg_file = find_ending_pattern(path_to_pattern_subfolder, cfg_pattern)
                    else:
                        stats_file = ""
                        cfg_file = ""
                    abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                    tool_type.run_tool(cfg_file, abs_path_to_executable, output_file, depth, stats_file)

