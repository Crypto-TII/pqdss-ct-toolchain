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



global_errors_dict = {}


def find_target_by_basename(target_basename: str, path_to_target_header_file: str) -> str:
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
            token = tokenize_target(self.target)
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


def binsec_test_harness_template(target_basename: str, target_header_file: str,
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


def ctverif_target_wrapper_block(path_to_target_header_file, target_basename):
    find_target_keypair = find_target_by_basename(target_basename, path_to_target_header_file)
    targ_obj = Target(find_target_keypair)
    args_names = targ_obj.target_args_names
    args_types = targ_obj.target_types
    targ_return_type = targ_obj.target_return_type
    function_signature = str(tuple(args_names))
    function_signature = re.sub("'",'', function_signature)
    target_call = ''
    ret_type_custom = targ_return_type
    if targ_return_type.strip() == 'void' or targ_return_type.strip() == 'extern':
        target_call = f'\t{target_basename}{function_signature};'
        ret_type_custom = 'void'
    else:
        target_call = f'''
    \t{ret_type_custom} result = {target_basename}{function_signature};
    \treturn result;'''
    public_in_block = ""
    for arg in args_names:
        public_in_block += f'''
    \tpublic_in(__SMACK_value({arg}));\n
    '''
    wrapper_block = f'''
    //{target_basename}_wrapper
    {ret_type_custom} {target_basename}_wrapper{function_signature}{{
    {public_in_block}
    \t//__disjoint_regions(arg_i, arg_i_len, arg_j, arg_j_len);
    \t//public_in(__SMACK_values(arg_k, arg_k_len));
    
    {target_call}
    }}
    '''
    return wrapper_block


def ctverif_create_test_source_file(path_to_target_src_file, add_includes):
    ctverif_include = f'#include "ctverif.h"\n'
    keypair_ctverif_name = ''
    sign_ctverif_name = ''
    path_to_target_src_file_split = path_to_target_src_file.split('/')
    target_c_file_basename = path_to_target_src_file_split[-1]
    path_to_target_c_file_folder = "/".join(path_to_target_src_file_split[0:-1])
    target_ctverif = f'{path_to_target_c_file_folder}/ctverif_{target_c_file_basename}'
    if not os.path.isfile(target_ctverif):
        with open(path_to_target_src_file, "r") as f:
            contents = f.readlines()
        with open(target_ctverif, "w") as f:
            contents.insert(0, ctverif_include)
            if add_includes:
                i = 1
                for incs in add_includes:
                    contents.insert(1+i, f'#include {incs}\n')
                    i += 1
            contents = "".join(contents)
            f.write(contents)
    return target_ctverif


def ctverif_create_target_wrappers(path_to_target_src_file, target_basename,
                                   path_to_target_header_file, add_includes):
    target_ctverif = ctverif_create_test_source_file(path_to_target_src_file, add_includes)
    target_wrapper_block = ctverif_target_wrapper_block(path_to_target_header_file, target_basename)
    with open(target_ctverif, "a+") as f:
        contents = f.readlines()
        if f'//{target_basename}_wrapper' not in contents:
            f.write(textwrap.dedent(target_wrapper_block))



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


def generic_template(tools_list: list, target_basename: str, target_header_file,
                     secret_arguments, path_to_test_harness, includes):
    path_to_test_harness_split = path_to_test_harness.split('/')
    if path_to_test_harness is None or path_to_test_harness == 'None':
        path_to_test_harness_split = []
        path_to_test_harness = ''
    test_harness_basename = os.path.basename(path_to_test_harness)
    test_file_basename = test_harness_basename
    if not test_file_basename.endswith('.c'):
        test_file_basename = f'test_{target_basename}.c'
    for tool_name in tools_list:
        tool_obj = Tools(tool_name)
        full_path_to_test_harness = ''
        path_to_test_harness_split_extend = path_to_test_harness_split.copy()
        if not path_to_test_harness_split_extend:
            full_path_to_test_harness = f'{tool_name}/{test_file_basename}'
        else:
            if tool_name.strip() not in path_to_test_harness_split:
                if len(path_to_test_harness_split) == 1:
                    if test_harness_basename.endswith('.c'):
                        path_to_test_harness_split_extend.insert(0, tool_name)
                    else:
                        path_to_test_harness_split_extend.append(tool_name)
                        path_to_test_harness_split_extend.append(test_file_basename)
                else:
                    if test_harness_basename.endswith('.c'):
                        path_to_test_harness_split_extend.insert(len(path_to_test_harness_split_extend)-1, tool_name)
                    else:
                        path_to_test_harness_split_extend.append(tool_name)
                        path_to_test_harness_split_extend.append(test_file_basename)
            full_path_to_test_harness = "/".join(path_to_test_harness_split_extend)
        tool_obj.tool_template(target_basename, target_header_file, secret_arguments, full_path_to_test_harness, includes)


# tools_list = ["ctgrind"]
# target_header = "kem/kyber/ref/poly.h"
# target_basename = "poly_tomsg"
# secret_inputs = ["msg"]
# test_harness = "kem/kyber/ref/ctgrind/poly_tomsg.c"
# incs = []
# generic_template(tools_list, target_basename, target_header, secret_inputs, test_harness, incs)