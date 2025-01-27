#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""

import os
import sys
import json
import subprocess
import shutil

from typing import Optional, Union, List

import tools
import generics as gen


def from_json_to_python_dict(path_to_json_file: str):
    with open(path_to_json_file) as json_file:
        data = json.load(json_file)
        candidates_list = data['candidates']
        chosen_tools = data['tools']
        libraries = data['libraries']
        benchmark_libraries = data['benchmark_libraries']
        return candidates_list, chosen_tools, libraries, benchmark_libraries


# ======================== COMPILATION ====================================
# =========================================================================
def compile_with_cmake(build_folder_full_path, optional_flags=None, tool_flags: Optional[Union[str, list]] = None,
                       *args, **kwargs):
    if optional_flags is None:
        optional_flags = []
    cwd = os.getcwd()
    print("-------cwd: ", cwd)
    gen.create_directory(build_folder_full_path)
    os.chdir(build_folder_full_path)
    print("-------build_folder_full_path: ", build_folder_full_path)
    print("-------os.getcwd(): ", os.getcwd())
    # Set the tool's flags in the CMakeLists.txt
    tool_name = tool_flags[0]
    tool_cflags = tool_flags[1]
    tool_link_libs = tool_flags[2]
    tool_link_libs = tool_link_libs.replace('-l', '')
    print("-------tool_link_libs: ", tool_link_libs)
    tool_template_pattern = tool_flags[-1]
    print("::::::::tool_template_pattern: ", tool_template_pattern)
    if tool_flags is not None:
        cmakelist = '../CMakeLists.txt'
        set_tool_flags = [f"sed -i -E 's/(TOOLS_FLAGS .+)/TOOLS_FLAGS "f'"{tool_cflags}"'")/g'" + f" {cmakelist}"]
        subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
        set_tool_name = [f"sed -i -E 's/(TOOL_NAME .+)/TOOL_NAME "f'"{tool_name}"'")/g'" + f" {cmakelist}"]
        subprocess.call(set_tool_name, stdin=sys.stdin, shell=True)
        set_tool_flags = [f"sed -i -E 's/(TOOL_TEMPLATE_PATTERN .+)/TOOL_TEMPLATE_PATTERN "f'"{tool_template_pattern}"'")/g'" + f" {cmakelist}"]
        subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
        set_tool_flags = [f"sed -i -E 's/(TOOL_LINK_LIBS .+)/TOOL_LINK_LIBS "f'"{tool_link_libs}"'")/g'" + f" {cmakelist}"]
        subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
    # os.chdir(build_folder_full_path) # 14-Dec

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



def compile_with_makefile(path_to_makefile, default=None,
                          tool_flags: Optional[Union[str, list]] = None, *args, **kwargs):
    cwd = os.getcwd()
    os.chdir(path_to_makefile)
    # Set the tool's flags in the Makefile
    if tool_flags is not None:
        # tool_cflags = tool_flags[-1]
        tool_cflags = tool_flags[1]
        tool_link_libs = tool_flags[2]
        makefile = 'Makefile'
        set_tool_flags = [f"sed -i 's/^TOOLS_FLAGS := .*$/TOOLS_FLAGS := {tool_cflags}/g' {makefile}"]
        subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
        # set_tool_flags = [f"sed -i -E 's/(TOOL_LINK_LIBS .+)/TOOL_LINK_LIBS "f'"{tool_link_libs}"'")/g'" + f" {makefile}"]
        set_tool_flags = [f"sed -i 's/^TOOL_LINK_LIBS := .*$/TOOL_LINK_LIBS := {tool_cflags}/g' {makefile}"]
        subprocess.call(set_tool_flags, stdin=sys.stdin, shell=True)
    # Run make clean first in case objects files have already been obtained with the flags of a different tool.
    cmd_clean = ["make", "clean"]
    subprocess.call(cmd_clean, stdin=sys.stdin)
    additional_options = list(args)
    for key, val in kwargs.items():
        additional_options.append(f'{key}={val}')
    # cmd = ["make"]
    cmd = ["make", "all"]
    if not additional_options:
        cmd.append('all')
    cmd.extend(additional_options)
    if default:
        cmd.append(default)
    print("++++++++++++cmd++++++++++++: ", cmd)
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)


def generic_compilation(path_to_target_wrapper: str, path_to_target_binary: str,
                        path_to_test_library_directory: str, libraries_names: [Union[str, list]],
                        path_to_include_directories: Union[str, list], tool_name: str, compiler: str = 'gcc'):
    tool = tools.Tools(tool_name)
    tool_cflags, tool_libs = tool.get_tool_flags_and_libs()
    target_include_dir = path_to_include_directories
    all_flags = []
    target_link_libraries = tool_libs.split()
    if isinstance(tool_cflags, str):
        all_flags = tool_cflags.split()
    elif isinstance(tool_cflags, list):
        all_flags.extend(tool_cflags.copy())
    if isinstance(libraries_names, str):
        target_link_libraries.extend(libraries_names.split())
    elif isinstance(libraries_names, list):
        target_link_libraries.extend(libraries_names.copy())
    target_link_libraries = list(set(target_link_libraries))
    target_link_libraries = list(map(lambda incs: f'{incs}' if '-l' in incs else f'-l{incs}', target_link_libraries))
    target_link_libraries_str = " ".join(target_link_libraries)
    all_flags_str = " ".join(all_flags)
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
    print("!!!!!!!!!cmd============: ")
    print(cmd)
    subprocess.call(cmd, stdin=sys.stdin, shell=True)



def generic_target_compilation(path_candidate: str, path_to_test_library_directory: str,
                               libraries_names: [Union[str, list]], path_to_include_directories: Union[str, list],
                               tool_name: str, default_instance: str, instances: Optional[Union[str, list]] = None, compiler: str = 'gcc',
                               binary_patterns: Optional[Union[str, list]] = None):
    tool_type = tools.Tools(tool_name)
    test_keypair_basename, test_sign_basename = tool_type.get_tool_test_file_name()
    keypair_sign = []
    path_to_tool_folder = f'{path_candidate}/{tool_name}'
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
                                libraries_names, path_to_include_directories, tool_name, compiler)



def compile_target_candidate(path_to_candidate_makefile_cmake: str,
                             build_with_make: bool = True, additional_options=None,
                             tool_name: Optional[str] = None, *args, **kwargs):
    tool_cflags = ''
    tool_libs = ''
    # tool_template_pattern = ()
    tool_template_pattern = ''
    tool_flags = []
    print("--------++++++++path_to_candidate_makefile_cmake: ", path_to_candidate_makefile_cmake)
    if tool_name is not None:
        tool_type = tools.Tools(tool_name)
        tool_cflags, tool_libs = tool_type.get_tool_flags_and_libs()
        tool_type.get_tool_test_file_name()
        tool_template_pattern = tool_type.tool_test_file_name
        print("--------tool_template_pattern: ", tool_template_pattern)
        tool_flags.extend([tool_name, tool_cflags, tool_libs, tool_template_pattern])
    if build_with_make:
        compile_with_makefile(path_to_candidate_makefile_cmake, additional_options, tool_flags, *args, **kwargs)
    if not build_with_make:
        path_to_build_folder = f'{path_to_candidate_makefile_cmake}/build'
        compile_with_cmake(path_to_build_folder, additional_options, tool_flags, *args, **kwargs)



# tool_initialize_candidate: given  tool, instances, keypair and sign folders and also api.h - sign.h - rng.h paths,
# consists in creating:
# 1. a directory named accordingly the tool name
# 2. two subdirectories of the previous one, named accordingly to the instance of the candidate
# and the keypair/sign algorithms
# 3. the required files for the given tool (test harness, taint, etc.) into the previous folders.
def tool_initialize_candidate(abs_path_to_api_or_sign,
                              abs_path_to_rng,
                              path_to_tool_folder,
                              path_to_tool_keypair_folder,
                              path_to_tool_sign_folder,
                              add_includes,
                              with_core_dump="yes",
                              number_of_measurements='1e4'):
    list_of_path_to_folders = [path_to_tool_folder,
                               path_to_tool_keypair_folder,
                               path_to_tool_sign_folder]
    gen.generic_create_tests_folders(list_of_path_to_folders)
    tool_name = os.path.basename(path_to_tool_folder)
    tool_type = tools.Tools(tool_name)
    tes_keypair_basename, tes_sign_basename = tool_type.get_tool_test_file_name()
    api_or_sign = os.path.basename(abs_path_to_api_or_sign)
    api_or_sign = f'"{api_or_sign}"'
    rng = os.path.basename(abs_path_to_rng)
    rng = f'"{rng}"'
    if tool_name == 'flowtracker':
        test_keypair_basename = f'{tes_keypair_basename}.xml'
        test_sign_basename = f'{tes_sign_basename}.xml'
    else:
        test_keypair_basename = f'{tes_keypair_basename}.c'
        test_sign_basename = f'{tes_sign_basename}.c'
    test_keypair = f'{path_to_tool_keypair_folder}/{test_keypair_basename}'
    ret_kp = gen.keypair_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type_kp, f_basename_kp, args_types_kp, args_names_kp = ret_kp
    test_sign = f'{path_to_tool_sign_folder}/{test_sign_basename}'
    ret_sign = gen.sign_find_args_types_and_names(abs_path_to_api_or_sign)
    return_type_s, f_basename_s, args_types_s, args_names_s = ret_sign
    print(":::::tool_initialize_candidate")
    print("-----return_type_s: ", return_type_s)
    print("-----f_basename_s: ", f_basename_s)
    if tool_name == 'ctgrind':
        tools.ctgrind_keypair_taint_content(test_keypair, api_or_sign,
                                          add_includes, return_type_kp,
                                          f_basename_kp, args_types_kp, args_names_kp)
        tools.ctgrind_sign_taint_content(test_sign, api_or_sign, rng,
                                       add_includes, return_type_s,
                                       f_basename_s, args_types_s, args_names_s)
    if tool_name == 'timecop':
        tools.timecop_keypair_taint_content(test_keypair, api_or_sign,
                                            add_includes, return_type_kp,
                                            f_basename_kp, args_types_kp, args_names_kp)
        tools.timecop_sign_taint_content(test_sign, api_or_sign, rng,
                                         add_includes, return_type_s,
                                         f_basename_s, args_types_s, args_names_s)

    if tool_name == 'binsec':
        cfg_file_kp, cfg_file_sign = tool_type.binsec_configuration_files()
        cfg_file_keypair = f'{path_to_tool_keypair_folder}/{cfg_file_kp}.cfg'
        if 'yes' in with_core_dump.lower():
            cfg_file_keypair = f'{path_to_tool_keypair_folder}/{cfg_file_kp}.ini'
        tools.cfg_content_keypair(cfg_file_keypair, with_core_dump)
        tools.test_harness_content_keypair(test_keypair, api_or_sign, add_includes, return_type_kp,
                                         f_basename_kp)
        crypto_sign_args_names = args_names_s

        if 'yes' in with_core_dump.lower():
            cfg_file_sign = f'{path_to_tool_sign_folder}/{cfg_file_sign}.ini'
        else:
            cfg_file_sign = f'{path_to_tool_sign_folder}/{cfg_file_sign}.cfg'
        tools.sign_configuration_file_content(cfg_file_sign, crypto_sign_args_names, with_core_dump)
        tools.sign_test_harness_content(test_sign, api_or_sign, add_includes, return_type_s, f_basename_s,
                                      args_types_s, args_names_s)

    if tool_name == 'dudect':
        tools.dudect_keypair_dude_content(test_keypair, api_or_sign,
                                        add_includes, return_type_kp,
                                        f_basename_kp, args_types_kp, args_names_kp)
        tools.dudect_sign_dude_content(test_sign, api_or_sign,
                                     add_includes, return_type_s,
                                     f_basename_s, args_types_s,
                                     args_names_s, number_of_measurements)
    if tool_name == 'flowtracker':
        sign_function = [f_basename_s, args_names_s]
        tools.flowtracker_keypair_xml_content(test_keypair, api_or_sign,
                                            add_includes, return_type_kp,
                                            f_basename_kp, args_types_kp, args_names_kp, sign_function)
        tools.flowtracker_sign_xml_content(test_sign, api_or_sign,
                                         add_includes, return_type_s,
                                         f_basename_s, args_types_s, args_names_s)


# initialization: given a candidate and its details (signature type, etc.), creates required arguments (folders)
# for the function 'tool_initialize_candidate'.
# It takes into account a multiple of tools  and instances (folders) for a given candidate
def initialization(tools_list, abs_path_to_api_or_sign,
                   abs_path_to_rng,
                   candidate, optimized_imp_folder,
                   instance_folder,
                   add_includes, with_core_dump="yes",
                   number_of_measurements='1e4'):
    signature_type = abs_path_to_api_or_sign.split('/')[1]
    path_candidate = f'{abs_path_to_api_or_sign.split(candidate)[0]}/{candidate}'
    tools_list_lowercase = [tool_name.lower() for tool_name in tools_list]
    for tool_name in tools_list_lowercase:
        tool_folder = tool_name
        path_to_tool_folder = f'{path_candidate}/{tool_folder}'
        tool_keypair_folder_basename = f'{candidate}_keypair'
        tool_sign_folder_basename = f'{candidate}_sign'
        path_to_instance = path_to_tool_folder
        if not instance_folder == "":
            path_to_instance = f'{path_to_instance}/{instance_folder}'
        path_to_tool_keypair_folder = f'{path_to_instance}/{tool_keypair_folder_basename}'
        path_to_tool_sign_folder = f'{path_to_instance}/{tool_sign_folder_basename}'
        tool_initialize_candidate(abs_path_to_api_or_sign,
                                  abs_path_to_rng,
                                  path_to_tool_folder,
                                  path_to_tool_keypair_folder,
                                  path_to_tool_sign_folder,
                                  add_includes,
                                  with_core_dump, number_of_measurements)


# generic_initialize_nist_candidate: generalisation of the function 'initialization', taking into account the fact
# that some candidates have only 'one' instance
def generic_initialize_nist_candidate(tools_list, candidate, abs_path_to_api_or_sign, abs_path_to_rng,
                                      optimized_imp_folder, instances_list, add_includes,
                                      with_core_dump="yes", number_of_measurements='1e4'):
    if candidate == 'qruov':
        print("------PROCESSING: qruov")
    list_of_instances = []
    if not instances_list:
        list_of_instances = [""]
    else:
        for instance_folder in instances_list:
            list_of_instances.append(instance_folder)
    for instance in list_of_instances:
        initialization(tools_list, abs_path_to_api_or_sign, abs_path_to_rng,
                       candidate, optimized_imp_folder, instance, add_includes,
                       with_core_dump, number_of_measurements)


def compile_target_from_library(path_to_candidate_makefile_cmake,
                                libraries_names: Union[str, list] = 'lcttest',
                                path_to_include_directories: Union[str, list] = '',
                                path_to_target_wrapper: str = '', path_to_target_binary: str = '',
                                tool_name: str = '', compiler: str = 'gcc', build_with_make: bool = True,
                                additional_optional=None, *args, **kwargs):

    path_to_test_library_directory = f'{path_to_candidate_makefile_cmake}/build'
    # Compile candidate and generate the library 'libcttest.a' for the tests
    compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
                             additional_optional, *args, **kwargs)
    # Compile target function
    generic_compilation(path_to_target_wrapper, path_to_target_binary, path_to_test_library_directory,
                        libraries_names, path_to_include_directories, tool_name, compiler)


# generic_init_compile: in addition to initializing a given candidate for desired tools and instances
def generic_init_compile(tools, candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                         default_instance: str, instances, additional_includes, path_to_candidate_makefile_cmake,
                         direct_link_or_compile_target: bool = True, libraries_names: Union[str, list] = 'lcttest',
                         path_to_include_directories: Union[str, list] = '', build_with_make: bool = True,
                         additional_cmake_definitions=None, number_of_measurements='1e4', compiler: str = 'gcc',
                         compile_test_harness: str = 'yes', binary_patterns: Optional[Union[str, list]] = None,
                         *args, **kwargs):
    if candidate == 'qruov':
        cwd = os.getcwd()
        os.chdir(path_to_candidate_makefile_cmake)
        platform = 'portable64'
        if args:
            platform = args[0]
        makefile = 'Makefile'
        chosen_platform = [f"sed -i 's/^platform := .*$/platform :=  {platform}/g' {makefile}"]
        subprocess.call(chosen_platform, stdin=sys.stdin, shell=True)
        instances_str = ''
        if isinstance(instances, str):
            instances_str = instances.split()
        elif isinstance(instances, list):
            instances_str = " ".join(instances)
        cmd_str = f'make {instances_str}'
        subprocess.call(cmd_str.split(), stdin=sys.stdin)
        os.chdir(cwd)

        for instance in instances:
            abs_path_to_api_or_sign_split = abs_path_to_api_or_sign.split(default_instance)
            abs_path_to_api_or_sign_split.insert(1, instance)
            abs_path_to_api_or_sign_split[-1] = f'/{platform}/api.h'
            abs_path_to_api_or_sign = "".join(abs_path_to_api_or_sign_split)
            generic_initialize_nist_candidate(tools, candidate, abs_path_to_api_or_sign, abs_path_to_rng,
                                              optimized_imp_folder, instances, additional_includes, 'yes',
                                              number_of_measurements)
    else:
        generic_initialize_nist_candidate(tools, candidate, abs_path_to_api_or_sign, abs_path_to_rng,
                                          optimized_imp_folder, instances, additional_includes, 'yes',
                                          number_of_measurements)
    path_candidate = abs_path_to_api_or_sign.split(candidate)[0]
    if path_candidate.endswith('/'):
        path_candidate += candidate
    else:
        path_candidate += f'/{candidate}'
    if 'yes' in compile_test_harness.lower():
        path_to_test_library_directory = f'{path_to_candidate_makefile_cmake}/build'
        for tool in tools:
            if not direct_link_or_compile_target:
                if not instances:
                    compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
                                             additional_cmake_definitions, tool, *args, **kwargs)
                else:
                    if candidate == 'qruov':
                        for instance in instances:
                            platform = 'portable64'
                            if args:
                                platform = args[0]
                            instance_updated = f'{instance}/{platform}'
                            path_to_include_directories_split = path_to_include_directories.split(default_instance)
                            path_to_include_directories_split.insert(1, instance_updated)
                            path_to_include_directories = "".join(path_to_include_directories_split[:-1])
                    else:
                        if build_with_make:
                            for instance in instances:
                                path_to_candidate_makefile_cmake_split = path_to_candidate_makefile_cmake.split(default_instance)
                                path_to_candidate_makefile_cmake_split.insert(1, instance)
                                path_to_candidate_makefile_cmake = "".join(path_to_candidate_makefile_cmake_split)
                        compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
                                                 additional_cmake_definitions, tool, *args, **kwargs)
            if build_with_make:
                generic_target_compilation(path_candidate, path_to_test_library_directory, libraries_names,
                                           path_to_include_directories, tool, default_instance, instances,
                                           compiler, binary_patterns)


# instance/scr folder of the given candidate with respect to optimized_imp_folder
# binary_patterns: sign/keypair, referring to crypto_sign_keypair and crypto_sign algorithms respectively
def binsec_generic_run(path_to_candidate, instances, depth, binary_patterns):
    path_to_binsec_folder = f'{path_to_candidate}/binsec'
    candidate = os.path.basename(path_to_candidate)
    cfg_pattern = ".ini"
    list_of_instances = []
    if binary_patterns is None:
        binary_patterns = ['keypair', 'sign']
    if not instances:
        path_to_instance = path_to_binsec_folder
        list_of_instances.append(path_to_instance)
    else:
        for instance in instances:
            path_to_instance = f'{path_to_binsec_folder}/{instance}'
            list_of_instances.append(path_to_instance)
    for p_instance in list_of_instances:
        for bin_pattern in binary_patterns:
            target_function = f'crypto_sign'
            if bin_pattern == 'keypair':
                target_function = f'{target_function}_keypair'
            path_to_instance_target_folder = f'{p_instance}/{candidate}_{bin_pattern}'
            bin_files = os.listdir(path_to_instance_target_folder)
            bin_files = [exe for exe in bin_files if not '.' in exe]
            for executable in bin_files:
                binary = os.path.basename(executable)
                abs_path_to_executable = f'{path_to_instance_target_folder}/{binary}.snapshot'
                path_to_gdb_script = f'{path_to_instance_target_folder}/{binary}.gdb'
                if not os.path.isfile(path_to_gdb_script):
                    tools.binsec_generate_gdb_script(path_to_gdb_script, abs_path_to_executable, target_function)
                path_to_executable_file = f'{path_to_instance_target_folder}/{binary}'
                tools.binsec_generate_core_dump(path_to_executable_file, path_to_gdb_script)
                bin_basename = binary.split('test_harness_')[-1]
                output_file = f'{path_to_instance_target_folder}/{bin_basename}_output.txt'
                stats_file = f'{path_to_instance_target_folder}/{bin_pattern}.toml'
                cfg_file = gen.find_ending_pattern(path_to_instance_target_folder, cfg_pattern)
                print("::::Running:", abs_path_to_executable)
                tools.run_binsec(abs_path_to_executable, cfg_file, stats_file, output_file, depth)


# instance/scr folder of the given candidate with respect to optimized_imp_folder
# binary_patterns: sign/keypair, referring to crypto_sign_keypair and crypto_sign algorithms respectively
def timecop_generic_run(path_to_candidate, instances, binary_patterns):
    path_to_binsec_folder = f'{path_to_candidate}/timecop'
    candidate = os.path.basename(path_to_candidate)
    list_of_instances = []
    if binary_patterns is None:
        binary_patterns = ['keypair', 'sign']
    if not instances:
        path_to_instance = path_to_binsec_folder
        list_of_instances.append(path_to_instance)
    else:
        for instance in instances:
            path_to_instance = f'{path_to_binsec_folder}/{instance}'
            list_of_instances.append(path_to_instance)
    for p_instance in list_of_instances:
        for bin_pattern in binary_patterns:
            target_function = f'crypto_sign'
            if bin_pattern == 'keypair':
                target_function = f'{target_function}_keypair'
            path_to_instance_target_folder = f'{p_instance}/{candidate}_{bin_pattern}'
            bin_files = os.listdir(path_to_instance_target_folder)
            bin_files = [exe for exe in bin_files if not '.' in exe]
            for executable in bin_files:
                binary = os.path.basename(executable)
                path_to_executable_file = f'{path_to_instance_target_folder}/{binary}'
                bin_basename = binary.split('taint_')[-1]
                output_file = f'{path_to_instance_target_folder}/{bin_basename}_output.txt'
                print("::::Running:", path_to_executable_file)
                tools.run_timecop(path_to_executable_file, output_file)


# instance/scr folder of the given candidate with respect to optimized_imp_folder
# binary_patterns: sign/keypair, referring to crypto_sign_keypair and crypto_sign algorithms respectively
def dudect_generic_run(path_to_candidate, instances, binary_patterns, timeout='2h'):
    path_to_binsec_folder = f'{path_to_candidate}/dudect'
    candidate = os.path.basename(path_to_candidate)
    list_of_instances = []
    if binary_patterns is None:
        binary_patterns = ['keypair', 'sign']
    if not instances:
        path_to_instance = path_to_binsec_folder
        list_of_instances.append(path_to_instance)
    else:
        for instance in instances:
            path_to_instance = f'{path_to_binsec_folder}/{instance}'
            list_of_instances.append(path_to_instance)
    for p_instance in list_of_instances:
        for bin_pattern in binary_patterns:
            path_to_instance_target_folder = f'{p_instance}/{candidate}_{bin_pattern}'
            bin_files = os.listdir(path_to_instance_target_folder)
            bin_files = [exe for exe in bin_files if not '.' in exe]
            for executable in bin_files:
                binary = os.path.basename(executable)
                path_to_executable_file = f'{path_to_instance_target_folder}/{binary}'
                bin_basename = binary.split('dude_')[-1]
                bin_basename = bin_basename.split('.o')[0]
                output_file = f'{path_to_instance_target_folder}/{bin_basename}_output.txt'
                print("::::Running:", path_to_executable_file)
                tools.run_dudect(path_to_executable_file,output_file,timeout)


def generic_execution(tools, path_to_candidate, instances, depth, binary_patterns, timeout='86400'):
    for tool_name in tools:
        path_to_binsec_folder = f'{path_to_candidate}/{tool_name}'
        candidate = os.path.basename(path_to_candidate)
        cfg_pattern = ".ini"
        list_of_instances = []
        if binary_patterns is None:
            binary_patterns = ['keypair', 'sign']
        if not instances:
            path_to_instance = path_to_binsec_folder
            list_of_instances.append(path_to_instance)
        else:
            for instance in instances:
                path_to_instance = f'{path_to_binsec_folder}/{instance}'
                list_of_instances.append(path_to_instance)
        for p_instance in list_of_instances:
            for bin_pattern in binary_patterns:
                target_function = f'crypto_sign'
                if bin_pattern == 'keypair':
                    target_function = f'{target_function}_keypair'
                path_to_instance_target_folder = f'{p_instance}/{candidate}_{bin_pattern}'
                bin_files = os.listdir(path_to_instance_target_folder)
                bin_files = [exe for exe in bin_files if not '.' in exe]
                for executable in bin_files:
                    binary = os.path.basename(executable)

        if 'binsec' in tool_name.lower():
            binsec_generic_run(path_to_candidate, instances, depth, binary_patterns)
        if tool_name.lower() == 'timecop':
            timecop_generic_run(path_to_candidate, instances, binary_patterns)


def generic_run(tools, path_to_candidate, instances, depth, binary_patterns, timeout='86400'):
    for tool_name in tools:
        if tool_name.lower() == 'binsec':
            binsec_generic_run(path_to_candidate, instances, depth, binary_patterns)
        if tool_name.lower() == 'timecop':
            timecop_generic_run(path_to_candidate, instances, binary_patterns)
        if tool_name.lower() == 'dudect':
            dudect_generic_run(path_to_candidate, instances, binary_patterns, timeout)


# generic_compile_run_candidate: initializes, compiles and runs given tools for the given instances
# of a given candidate.
def generic_compile_run_candidate(tools, candidate, abs_path_to_api_or_sign, abs_path_to_rng,
                                  optimized_imp_folder, default_instance: str, instances, additional_includes,
                                  path_to_candidate_makefile_cmake, direct_link_or_compile_target: bool = True,
                                  libraries_names: Union[str, list] = 'lcttest',
                                  path_to_include_directories: Union[str, list] = '', build_with_make: bool = True,
                                  additional_cmake_definitions=None, number_of_measurements='1e4', compiler: str = 'gcc',
                                  compile: str = 'yes', run: str = 'yes', binary_patterns: Optional[Union[str, list]] = None,
                                  depth: str = '1000000', timeout='86400', implementation_type='opt', security_level=None,
                                  *args, **kwargs):

    path_to_candidate = abs_path_to_api_or_sign.split(candidate)[0]
    if path_to_candidate.endswith('/'):
        path_to_candidate += candidate
    else:
        path_to_candidate += f'/{candidate}'
    if 'yes' in compile.lower() and 'yes' in run.lower():
        generic_init_compile(tools, candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                             default_instance, instances, additional_includes, path_to_candidate_makefile_cmake,
                             direct_link_or_compile_target, libraries_names,
                             path_to_include_directories, build_with_make, additional_cmake_definitions,
                             number_of_measurements, compiler, compile, binary_patterns, *args, **kwargs)
        generic_run(tools, path_to_candidate, instances, depth, binary_patterns, timeout)
    elif 'yes' in compile.lower() and 'no' in run.lower():
        generic_init_compile(tools, candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
                             default_instance, instances, additional_includes, path_to_candidate_makefile_cmake,
                             direct_link_or_compile_target, libraries_names,
                             path_to_include_directories, build_with_make, additional_cmake_definitions,
                             number_of_measurements, compiler, compile, binary_patterns, *args, **kwargs)

    if 'no' in compile.lower() and 'yes' in run.lower():
        generic_run(tools, path_to_candidate, instances, depth, binary_patterns, timeout)


def parse_candidates_json_file(candidates_dict: dict, candidate: str):
    candidates = candidates_dict.keys()
    if candidate not in candidates:
        # We should raise an error
        print("There is no candidate named {}".format(candidate))
        return None
    else:
        return candidates_dict[candidate]


def run_tests(user_entry_point: str, tools: Union[str, list], candidate: str, instances, candidates_dict,
              direct_link_or_compile_target: bool = True,
              number_of_measurements='1e4', compile: str = 'yes', run: str = 'yes',
              binary_patterns: Optional[Union[str, list]] = None, depth: str = '1000000',
              timeout='86400', implementation_type='opt', security_level=None,
              additional_cmake_definitions: Optional[Union[list, str]] = None, *args, **kwargs):
    candidates_dict = parse_candidates_json_file(candidates_dict, candidate)
    abs_path_to_api_or_sign = candidates_dict['path_to_api']
    abs_path_to_rng = candidates_dict['path_to_rng']
    optimized_imp_folder = candidates_dict['optimized_implementation']
    additional_imp_folder = candidates_dict['additional_implementation']
    additional_includes = ''
    path_to_candidate_makefile_cmake = candidates_dict['path_to_makefile_folder']
    libraries_names_all = candidates_dict['link_libraries']
    libraries_names = libraries_names_all["ct_tests"]
    path_to_include_directories = "/".join(abs_path_to_api_or_sign.split('/')[:-1])
    build_with_make = candidates_dict['build_with_makefile']
    compiler = candidates_dict['compiler']
    default_instance = candidates_dict['default_instance']
    if implementation_type == 'add':
        abs_path_to_api_or_sign_split = abs_path_to_api_or_sign.split(optimized_imp_folder)
        abs_path_to_api_or_sign_split.insert(1, additional_imp_folder)
        abs_path_to_api_or_sign = "".join(abs_path_to_api_or_sign_split)
        abs_path_to_rng_split = abs_path_to_rng.split(optimized_imp_folder)
        abs_path_to_rng_split.insert(1, additional_imp_folder)
        abs_path_to_rng = "".join(abs_path_to_rng_split)
        path_to_include_directories_split = path_to_include_directories.split(optimized_imp_folder)
        path_to_include_directories_split.insert(1, additional_imp_folder)
        path_to_include_directories = "".join(path_to_include_directories_split)

        path_to_candidate_makefile_cmake_split = path_to_candidate_makefile_cmake.split(optimized_imp_folder)
        path_to_candidate_makefile_cmake_split.insert(1, additional_imp_folder)
        path_to_candidate_makefile_cmake = "".join(path_to_candidate_makefile_cmake_split)

        optimized_imp_folder = additional_imp_folder
    generic_compile_run_candidate(tools, candidate, abs_path_to_api_or_sign, abs_path_to_rng,
                                  optimized_imp_folder, default_instance, instances, additional_includes,
                                  path_to_candidate_makefile_cmake, direct_link_or_compile_target, libraries_names,
                                  path_to_include_directories, build_with_make,
                                  additional_cmake_definitions, number_of_measurements, compiler,
                                  compile, run, binary_patterns, depth, timeout, implementation_type, security_level,
                                  *args, **kwargs)

# def generic_compile_target_candidate(candidate, abs_path_to_api_or_sign, abs_path_to_rng, optimized_imp_folder,
#                                      default_instance: str, instances, additional_includes,
#                                      path_to_candidate_makefile_cmake, direct_link_or_compile_target: bool = True,
#                                      libraries_names: Union[str, list] = 'lcttest',
#                                      path_to_include_directories: Union[str, list] = '', build_with_make: bool = True,
#                                      additional_cmake_definitions=None,
#                                      compiler: str = 'gcc', compile_test_harness: str = 'yes',
#                                      binary_patterns: Optional[Union[str, list]] = None, *args, **kwargs):
#
#     path_candidate = abs_path_to_api_or_sign.split(candidate)[0]
#     if path_candidate.endswith('/'):
#         path_candidate += candidate
#     else:
#         path_candidate += f'/{candidate}'
#     if 'yes' in compile_test_harness.lower():
#         path_to_test_library_directory = f'{path_to_candidate_makefile_cmake}/build'
#         if not direct_link_or_compile_target:
#             if not instances:
#                 compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
#                                          additional_cmake_definitions, None, *args, **kwargs)
#             else:
#                 for instance in instances:
#                     path_to_candidate_makefile_cmake_split = path_to_candidate_makefile_cmake.split(default_instance)
#                     path_to_candidate_makefile_cmake_split.insert(1, instance)
#                     path_to_candidate_makefile_cmake = "".join(path_to_candidate_makefile_cmake_split)
#                     compile_target_candidate(path_to_candidate_makefile_cmake, build_with_make,
#                                              additional_cmake_definitions, None, *args, **kwargs)
#
#




    # generic_compile_run_candidate(tools, candidate, abs_path_to_api_or_sign, abs_path_to_rng,
    #                               optimized_imp_folder, default_instance, instances, additional_includes,
    #                               path_to_candidate_makefile_cmake, direct_link_or_compile_target, libraries_names,
    #                               path_to_include_directories, build_with_make,
    #                               additional_cmake_definitions, number_of_measurements, compiler,
    #                               compile, run, binary_patterns, depth, timeout, implementation_type, security_level,
    #                               *args, **kwargs)


