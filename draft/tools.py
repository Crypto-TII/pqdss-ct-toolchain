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
from typing import Optional, Union, List
from subprocess import Popen

import target as target


# Patterns of test files (.c files) for binsec - ctgrind - dudect - flowtracker - ctverif;
# and also for binsec script file (configuration file).
class GenericPatterns(object):
    def __init__(self, tool_name: str):
        self.tool_test_file_pattern = ''
        self.tool_name = tool_name
        self.binsec_configuration_file = "ini"

    def get_tool_test_file_pattern(self) -> str:
        if self.tool_name == 'binsec':
            self.tool_test_file_pattern = 'test_harness'
        elif self.tool_name == 'ctgrind':
            self.tool_test_file_pattern = 'taint'
        elif self.tool_name == 'dudect':
            self.tool_test_file_pattern = 'test'
        elif self.tool_name == 'ctverif':
            self.tool_test_file_pattern = 'wrapper'
        elif self.tool_name == 'flowtracker':
            self.tool_test_file_pattern = 'xml'
        return self.tool_test_file_pattern


# ==================== EXECUTION =====================================
# ====================================================================
# Run binsec
def binsec_generic_execution(executable_file: str, cfg_file: str,
                             output_file: Optional[str] = None,
                             depth: Optional[Union[int, str]] = 1000000,
                             additional_options: Optional[list] = None) -> None:
    command = f'''binsec -sse -checkct -sse-script {cfg_file} -sse-depth  {depth} -sse-self-written-enum 1 '''
    if additional_options:
        for add_opt in additional_options:
            command += f'-{add_opt} '
    command += f' {executable_file}'
    cmd_args_lst = command.split()
    if output_file:
        with open(output_file, "w") as file:
            execution = Popen(cmd_args_lst, universal_newlines=True, stdout=file, stderr=file)
            execution.communicate()
    else:
        subprocess.call(cmd_args_lst, stdin=sys.stdin)


# Generate gdb script
def generic_gdb_script(path_to_gdb_script: str, path_to_snapshot_file: str) -> None:
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
def binsec_generate_core_dump(path_to_executable_file: str, path_to_gdb_script: str) -> None:
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
    subprocess.call(cmd, stdin=sys.stdin, shell=True)
    os.chdir(cwd)


# Run ctgrind
def ctgrind_generic_execution(binary_file: str, output_file: Optional[str] = None) -> None:
    command = f'valgrind -s --track-origins=yes --leak-check=full --show-leak-kinds=all --verbose '
    if output_file:
        command += f' --log-file={output_file}'
    command += f' ./{binary_file}'
    cmd_args_lst = command.split()
    subprocess.call(cmd_args_lst, stdin=sys.stdin)


# Run dudect
def dudect_generic_execution(executable_file: str, output_file: Optional[str] = None,
                             timeout: Union[str, int] = '5h') -> None:
    command = ""
    if timeout and timeout.lower() == 'no':
        command += f'./{executable_file}'
    else:
        command = f'timeout {timeout} ./{executable_file}'
    cmd_args_lst = command.split()
    if output_file:
        with open(output_file, "w") as file:
            execution = Popen(cmd_args_lst, universal_newlines=True, stdout=file, stderr=file)
            execution.communicate()
    else:
        subprocess.call(cmd_args_lst, stdin=sys.stdin)


# Run flowtracker
def flowtracker_generic_execution(target_src_file: str, xml_file: str,
                                  target_include_directory: Optional[list] = None) -> None:
    output_rbc_file = xml_file
    rbc_file_directory_split = output_rbc_file.split('/')
    rbc_file_directory = "/".join(rbc_file_directory_split[:-1])
    if not os.path.isdir(rbc_file_directory):
        print("Remark: {} is not a directory".format(rbc_file_directory))
        print("--- creating {} directory".format(rbc_file_directory))
        cmd = ["mkdir", "-p", rbc_file_directory]
        subprocess.call(cmd, stdin=sys.stdin)

    rbc_file_basename = os.path.basename(output_rbc_file)
    file_basename_without_format = rbc_file_basename.split(".")[0]
    path_to_rbc_file_without_format = output_rbc_file.split('.')[0]
    path_to_bc_file = f'{path_to_rbc_file_without_format}.bc'
    cmd_str = f'clang -emit-llvm '
    if target_include_directory:
        for incs_dir in target_include_directory:
            cmd_str += f'-I {incs_dir} '
    cmd_str += f' -c -g {target_src_file} -o {path_to_bc_file}'
    subprocess.call(cmd_str, stdin=sys.stdin, shell=True)
    path_to_rbc_file = f'{path_to_rbc_file_without_format}.rbc'
    cmd_str = f'opt -instnamer -mem2reg {path_to_bc_file} > {path_to_rbc_file}'
    subprocess.call(cmd_str, stdin=sys.stdin, shell=True)
    # Change directory, so that the files .dot can be generated in the same
    # directory as the target .xml  and .rbc files
    cwd = os.getcwd()
    os.chdir(rbc_file_directory)
    xml_file_basename = f'{file_basename_without_format}.xml'
    rbc_file_basename = f'{file_basename_without_format}.rbc'
    output_file = f'{file_basename_without_format}_output.out'
    cmd_str = (f'opt -basicaa -load AliasSets.so -load DepGraph.so -load bSSA2.so -bssa2 -xmlfile'
               f' {xml_file_basename} {rbc_file_basename} 2> {output_file}')
    subprocess.call(cmd_str, stdin=sys.stdin, shell=True)
    os.chdir(cwd)


# Run ctverif
def ctverif_generic_execution(target_wrapper: str, target_src_file: str, output_file=None, unroll=1, time_limit=None):
    command = f"ctverif --entry-points {target_wrapper} "
    if unroll:
        command += f'--unroll {unroll} '
    if time_limit:
        command += f'--time-limit {time_limit} '
    command += f'{target_src_file}'
    cmd_args_lst = command.split()

    if output_file:
        with open(output_file, "w") as file:
            execution = Popen(cmd_args_lst, universal_newlines=True, stdout=file, stderr=file)
            execution.communicate()
    else:
        subprocess.call(cmd_args_lst, stdin=sys.stdin)


# ==================== TEMPLATES =====================================
# ====================================================================
# binsec: generic script
def generic_configuration_file(cfg_file_sign: str, secret_arguments: list, public_arguments: list) -> None:
    script_file = cfg_file_sign
    if not cfg_file_sign.endswith('.ini'):
        cfg_file_sign_split = cfg_file_sign.split('.')
        if len(cfg_file_sign_split) == 1:
            script_file = f'{cfg_file_sign}.ini'
        else:
            script_file = f'{cfg_file_sign_split[0:-1]}.ini'
    secret_args_block = 'secret global'
    public_args_block = 'public global'
    for sec_arg in secret_arguments:
        secret_args_block += f' {sec_arg}'
    for pub_arg in public_arguments:
        public_args_block += f' {pub_arg}'
    cfg_file_content = f''' 
    starting from core
    {secret_args_block}
    {public_args_block}
    halt at <exit>
    explore all
    '''
    with open(script_file, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))


# binsec: generic template (test harness)
def binsec_test_harness_generic_template(target_basename: str, target_header_or_src_file: str,
                                         secret_arguments: list, path_to_test_harness: Optional[str] = None,
                                         includes: Optional[list] = None) -> None:
    """binsec_test_harness_generic_template:  Generate a test harness template (default) for binsec"""
    if path_to_test_harness:
        test_harness_directory_split = path_to_test_harness.split('/')
        test_harness_directory = "/".join(test_harness_directory_split[:-1])
        if not os.path.isdir(test_harness_directory):
            print("Remark: {} is not a directory".format(test_harness_directory))
            print("--- creating {} directory".format(test_harness_directory))
            cmd = ["mkdir", "-p", test_harness_directory]
            subprocess.call(cmd, stdin=sys.stdin)
    else:
        test_file_obj = GenericPatterns('binsec')
        test_file_pattern = test_file_obj.get_tool_test_file_pattern()
        target_header_or_src_file_split = target_header_or_src_file.split('/')
        test_harness_directory = "/".join(target_header_or_src_file_split[:-1])
        if test_harness_directory:
            path_to_test_harness = f'{test_harness_directory}/{test_file_pattern}_{target_basename}.c'
        else:
            path_to_test_harness = f'{test_file_pattern}_{target_basename}.c'

    target_obj = target.Target('', target_basename, target_header_or_src_file)
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
    path_to_config_file = f'{test_harness_directory}/{target_basename}.ini'
    target_public_inputs = [arg for arg in args_names if arg not in secret_arguments]
    generic_configuration_file(path_to_config_file, secret_arguments, target_public_inputs)


# ctgrind: generic template
def ctgrind_test_harness_generic_template(target_basename: str, target_header_or_src_file: str,
                                          secret_arguments: list, path_to_test_harness: Optional[str] = None,
                                          includes: Optional[list] = None) -> None:
    """ctgrind_test_harness_generic_template:  Generate a test harness template (default) for ctgrind"""

    if path_to_test_harness:
        test_harness_directory_split = path_to_test_harness.split('/')
        test_harness_directory = "/".join(test_harness_directory_split[:-1])
        if not os.path.isdir(test_harness_directory):
            print("Remark: {} is not a directory".format(test_harness_directory))
            print("--- creating {} directory".format(test_harness_directory))
            cmd = ["mkdir", "-p", test_harness_directory]
            subprocess.call(cmd, stdin=sys.stdin)
    else:
        test_file_obj = GenericPatterns('ctgrind')
        test_file_pattern = test_file_obj.get_tool_test_file_pattern()
        target_header_or_src_file_split = target_header_or_src_file.split('/')
        test_harness_directory = "/".join(target_header_or_src_file_split[:-1])
        if test_harness_directory:
            path_to_test_harness = f'{test_harness_directory}/{test_file_pattern}_{target_basename}.c'
        else:
            path_to_test_harness = f'{test_file_pattern}_{target_basename}.c'
    target_obj = target.Target('', target_basename, target_header_or_src_file)
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
        \t//ct_poison({sec_arg}, DEFAULT_LENGTH * sizeof({sec_args_type}));
        '''
        ct_unpoison_block += f'''
        \t//ct_unpoison({sec_arg}, DEFAULT_LENGTH * sizeof({sec_args_type}));
        '''
        generate_random_inputs_block += f'''
        //randombytes_ct_toolchain({sec_arg}, DEFAULT_LENGTH * sizeof({sec_args_type}));'''
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
    //Make sure that the file 'toolchain_rng.h' is copied in /usr/include
    //#include <toolchain_rng.h> 
    
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
    \t//{args_names[0]} = ({args_types[0]} *)calloc(DEFAULT_LENGTH, sizeof({args_types[0]}));
    
    \t{targ_return_type} result ; 
    \tfor (int i = 0; i < DEFAULT_CTGRIND_SAMPLE_SIZE; i++) {{
    \t\tgenerate_test_vectors(); 
    \t\t{ct_poison_block}
    \t\tresult = {target_basename}({args_names_string}); 
    \t\t{ct_unpoison_block}
    \t}}
    
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


# dudect: generic template
def dudect_test_harness_generic_template(target_basename: str, target_header_or_src_file: str,
                                         path_to_test_harness: Optional[str] = None,
                                         includes: Optional[list] = None) -> None:
    """dudect_test_harness_generic_template:  Generate a test harness template (default) for dudect"""

    if path_to_test_harness:
        test_harness_directory_split = path_to_test_harness.split('/')
        test_harness_directory = "/".join(test_harness_directory_split[:-1])
        if not os.path.isdir(test_harness_directory):
            print("Remark: {} is not a directory".format(test_harness_directory))
            print("--- creating {} directory".format(test_harness_directory))
            cmd = ["mkdir", "-p", test_harness_directory]
            subprocess.call(cmd, stdin=sys.stdin)
    else:
        test_file_obj = GenericPatterns('dudect')
        test_file_pattern = test_file_obj.get_tool_test_file_pattern()
        target_header_or_src_file_split = target_header_or_src_file.split('/')
        test_harness_directory = "/".join(target_header_or_src_file_split[:-1])
        if test_harness_directory:
            path_to_test_harness = f'{test_harness_directory}/{test_file_pattern}_{target_basename}.c'
        else:
            path_to_test_harness = f'{test_file_pattern}_{target_basename}.c'

    target_obj = target.Target('', target_basename, target_header_or_src_file)
    arguments_declaration = target_obj.target_args_declaration
    args_names = target_obj.target_args_names
    args_types = target_obj.target_types
    targ_return_type = target_obj.target_return_type
    target_inputs = ", ".join(args_names)
    declaration_initialization_block = ""
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
    do_one_computation_block = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    {declaration_initialization_block}
    \t//Do the needed process on the input <<data>>
    \t//{args_names[0]} = ({args_types[0]} *) data;
    \t{targ_return_type} result = {target_basename}({target_inputs});
    \treturn result;
    }}
    '''
    prepare_inputs_block = f'''
    void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {{
    \t//Do the needed process on the input <<data>>
    \trandombytes_dudect(input_data, c->number_measurements * c->chunk_size);
    \tfor (size_t i = 0; i < c->number_measurements; i++) {{
    \t\tclasses[i] = randombit();
    \t\t\tif (classes[i] == 0) {{
    \t\t\t\tDo the needed process
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
    with open(path_to_test_harness, "w+") as t_harness_file:
        t_harness_file.write(textwrap.dedent(headers_block))
        t_harness_file.write(textwrap.dedent(additional_includes))
        t_harness_file.write(textwrap.dedent(do_one_computation_block))
        t_harness_file.write(textwrap.dedent(prepare_inputs_block))
        t_harness_file.write(textwrap.dedent(main_function_block))


# flowtracker: generic template
def flowtracker_test_harness_generic_template(target_basename: str, target_header_or_src_file: str,
                                              secret_arguments: list,
                                              path_to_xml_file: Optional[str] = None) -> None:
    """flowtracker_test_harness_generic_template:  Generate a test harness template (default) for flowtracker"""

    if path_to_xml_file:
        xml_file_directory_split = path_to_xml_file.split('/')
        xml_file_directory = "/".join(xml_file_directory_split[:-1])
        if not os.path.isdir(xml_file_directory):
            print("Remark: {} is not a directory".format(xml_file_directory))
            print("--- creating {} directory".format(xml_file_directory))
            cmd = ["mkdir", "-p", xml_file_directory]
            subprocess.call(cmd, stdin=sys.stdin)
    else:
        test_file_obj = GenericPatterns('flowtracker')
        test_file_pattern = test_file_obj.get_tool_test_file_pattern()
        target_header_or_src_file_split = target_header_or_src_file.split('/')
        xml_file_directory = "/".join(target_header_or_src_file_split[:-1])
        if xml_file_directory:
            path_to_xml_file = f'{xml_file_directory}/{test_file_pattern}_{target_basename}.c'
        else:
            path_to_xml_file = f'{test_file_pattern}_{target_basename}.c'

    target_obj = target.Target('', target_basename, target_header_or_src_file)
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
    with open(path_to_xml_file, "w+") as xml_file:
        xml_file.write(textwrap.dedent(xml_file_block))


# ctverif: generic wrapper
def ctverif_target_generic_wrapper(target_basename: str, target_src_file: str) -> str:
    """ctverif_target_generic_wrapper:  Generate a wrapper template (default) for ctverif"""
    if not target_src_file.endswith('.c'):
        print("---ERROR: Please provide a .c file, {} is not one.".format(target_src_file))
        return ''
    target_src_file_directory_split = target_src_file.split('/')
    src_file_directory = "/".join(target_src_file_directory_split[:-1])
    test_file_obj = GenericPatterns('ctverif')
    test_file_pattern = test_file_obj.get_tool_test_file_pattern()
    src_file_basename = os.path.basename(target_src_file)
    src_file_basename_format = src_file_basename.split('.')[0]
    if src_file_directory:
        path_to_wrapper = f'{src_file_directory}/{src_file_basename_format}_{test_file_pattern}.c'
    else:
        path_to_wrapper = f'{src_file_basename_format}_{test_file_pattern}.c'

    target_obj = target.Target('', target_basename, target_src_file)
    args_names = target_obj.target_args_names
    targ_return_type = target_obj.target_return_type
    find_target_custom = target.find_target_by_basename_from_source_file(target_basename, target_src_file)
    find_target_custom = find_target_custom.replace('(', '!', 1)
    find_target_custom = find_target_custom.split('!')[-1]
    find_target_custom = find_target_custom.split(';')[0]
    function_signature = f'({find_target_custom}'
    function_inputs_tuple = str(tuple(args_names))
    function_inputs_tuple = re.sub("'", '', function_inputs_tuple)
    target_call = ''
    ret_type_custom = targ_return_type
    if targ_return_type.strip() == 'void' or targ_return_type.strip() == 'extern':
        target_call = f'\t{target_basename}{function_inputs_tuple};'
        ret_type_custom = 'void'
    else:
        target_call = f'''
    \t{ret_type_custom} result = {target_basename}{function_inputs_tuple};
    \treturn result;'''
    public_in_block = '''
    \t//__disjoint_regions(arg_i, arg_i_len, arg_j, arg_j_len);
    
    \t//Boilerplate
    '''
    for arg in args_names:
        public_in_block += f'''
    \tpublic_in(__SMACK_value({arg}));'''
    wrapper_block = ''
    if not os.path.isfile(path_to_wrapper):
        wrapper_block += f'''
    #include <stdio.h>
    #include <stdint.h>
    
    #include "ctverif.h"
    
    #include "{src_file_basename}"
        '''
    wrapper_block += f'''
    //{target_basename}_wrapper
    {ret_type_custom} {target_basename}_wrapper{function_signature}{{
    {public_in_block}
    
    \t/* arg_k is a public input data */
    \t//public_in(__SMACK_values(arg_k, arg_k_len));
    
    \t/* arg_n is an input and output */
    \t//declassified_in(__SMACK_values(arg_n,arg_n_len));
    \t//declassified_out(__SMACK_values(arg_n,arg_n_len));
    
    \t/* the return value is not considered as sensitive*/
    \t//public_out_value(__SMACK_return_value());

    {target_call}
    }}
    '''
    with open(path_to_wrapper, "a+") as f:
        contents = f.readlines()
        if f'//{target_basename}_wrapper' not in contents:
            f.write(textwrap.dedent(wrapper_block))
    target_wrapper_file_name = f'{path_to_wrapper}'
    return target_wrapper_file_name


# Tools:
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
            self.tool_flags = "-g"  # -static
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

    def tool_template(self, target_basename: str, target_header_or_src_file: str,
                      secret_arguments: list, path_to_test_harness: str, includes: list):
        if self.tool_name.lower() == 'binsec':
            binsec_test_harness_generic_template(target_basename, target_header_or_src_file,
                                                 secret_arguments, path_to_test_harness, includes)
        if self.tool_name.lower() == 'ctgrind':
            ctgrind_test_harness_generic_template(target_basename, target_header_or_src_file,
                                                  secret_arguments, path_to_test_harness, includes)
        if self.tool_name.lower() == 'dudect':
            dudect_test_harness_generic_template(target_basename, target_header_or_src_file,
                                                 path_to_test_harness, includes)
        if self.tool_name.lower() == 'flowtracker':
            flowtracker_test_harness_generic_template(target_basename, target_header_or_src_file,
                                                      secret_arguments, path_to_test_harness)
        if self.tool_name.lower() == 'ctverif':
            ctverif_target_generic_wrapper(target_basename, target_header_or_src_file)

    def tool_execution(self, executable_file: str, config_file: str = None,
                       output_file: str = None, sse_depth: int = 1000000,
                       target_include_directory: Optional[list] = None,
                       timeout: Optional[str] = None, additional_options: Optional[list] = None) -> None:

        if self.tool_name.lower() == 'binsec':
            binsec_generic_execution(executable_file, config_file, output_file, sse_depth, additional_options)
        if self.tool_name.lower() == 'ctgrind':
            ctgrind_generic_execution(executable_file, output_file)
        if self.tool_name.lower() == 'dudect':
            dudect_generic_execution(executable_file, output_file, timeout)
        if self.tool_name.lower() == 'flowtracker':
            flowtracker_generic_execution(executable_file, config_file, target_include_directory)
        if self.tool_name.lower() == 'ctverif':
            sse_depth = 1  # sse_depth = unroll
            timeout = 1  # time_limit = timeout
            ctverif_generic_execution(config_file, executable_file, output_file, sse_depth, timeout)


# generic_template: generic a template corresponding to a given tool for the given target
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
        tool_obj.tool_template(target_basename, target_header_file, secret_arguments,
                               full_path_to_test_harness, includes)


tools_list = ["binsec"]
target_header = "candidates/lattice/eaglesign/Specifications_and_Supporting_Documentation/Optimized_Implementation/EagleSign3/sign.c"
target_basename = "crypto_sign"
secret_inputs = ["sk"]
test_harness = "crypto_sign_bin.c"
# #test_harness = ''
incs = []
generic_template(tools_list, target_basename, target_header, secret_inputs, test_harness, incs)
