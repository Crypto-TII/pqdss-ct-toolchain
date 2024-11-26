#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from subprocess import Popen
import sys

import os
import re

# def test_sed(path_to_file: str, expression):
#     file_directory = "/".join(path_to_file.split("/")[:-1])
#     print("---file_directory: ", file_directory)
#     os.chdir(file_directory)
#     makefile = f"Makefile"
#     # sed -i "s/^projdir .*$/projdir PacMan/" .ignore
#     cmd = [f"sed -i "s/^TOOLS_FLAGS := .*$/TOOLS_FLAGS := {expression}/g" {makefile}"]
#     subprocess.call(cmd, stdin=sys.stdin, shell=True)
#
#
# path_to_file = "candidates/mpc-in-the-head/perk/Optimized_Implementation/perk-128-fast-3/Makefile"
# exp = "-g -Wall"
# test_sed(path_to_file, exp)

# path_to_benchmark_folder = "candidates/mpc-in-the-head/mqom/Optimized_Implementation/mqom_cat1_gf31_fast"
#
# list_file = os.listdir(path_to_benchmark_folder)
# print("===list_file")
# print(list_file)
# list_file = [file for file in list_file if os.path.isfile(f"{path_to_benchmark_folder}/{file}")]
# print("===list_file")
# print(list_file)


# sys.stdout.write("Hello")
# print("PRINT", file=sys.stderr)


#print("1\t2\t3".expandtabs(4))

#
# p_to_bench = "candidates/mpc-in-the-head/perk/benchmarks/perk_bench.txt"
#
# f_b = open(p_to_bench, "r")
# f_b_content = f_b.read()
# # print(f_b_content)
#
# instance = "perk-128-fast-5"
# instance_match1 = re.search(rf"[\w\s]*\W{instance}\s(.)*", f_b_content, flags=re.DOTALL)
# catch all except
# Candidate: perk
# Security Level: 128
# Instance:


# match1_found = ""
#
# instance_match1 = re.search(rf"Instance: {instance}\s(.)*", f_b_content, flags=re.DOTALL)
# print("instance_match: ", instance_match1)
# if instance_match1:
#     match1_found = instance_match1.group()
#     # print("match1_found: ")
#     # print(match1_found)
#
# index_line1 = f_b_content.index(match1_found[0])
# print(":::::::index_line1: ", index_line1)
# missing_lines = f"""
# {f_b_content.splitlines()[index_line1]}
# {f_b_content.splitlines()[index_line1+1]}
# """
#
# print("++++++++++++missing_lines")
# print(missing_lines)
# print("++++++++++++match1_found")
# print(match1_found)




# f_decl = "int test_function(uint8_t *key, int length, uint16_t msg_len, unsigned char message[LENGTH]);"
# f_decl_search = re.search(rf"\W\s*(...)", f_decl)
# print("f_decl_search: ", f_decl_search)
# if f_decl_search:
#     f_decl_search_found = f_decl_search.group()
#     print("search_found: ", f_decl_search_found)



print("==============================================")
# print("match1_found")
# print(match1_found)
# match1_found1 = f"""
# {missing_lines}{match1_found}
# """

# print("match1_found1")
# print(match1_found1)

# f_b_content_new1 = re.sub(match1_found,"", f_b_content)
# # f_b_content_new = f_b_content.replace(missing_lines,"-----")
# # f_b_content_new = f_b_content.replace(match1_found,"Love")
# f_b_content_new = f_b_content.replace(match1_found,"Love")
# # f_b_content_new = f_b_content.replace(f_b_content_new,"Love")
# print("f_b_content_new")
# print(f_b_content_new)
# f_b_content_new = f_b_content.replace(f_b_content_new,"Love")





# Good patterns
# instance_match1 = re.search(rf"Instance: {instance}\s(.)*", f_b_content, flags=re.DOTALL)
# if instance_match1:
#     match1_found = instance_match1.group()
# index_line1 = f_b_content.index(match1_found[0])
# print(":::::::index_line1: ", index_line1)
# missing_lines = f"""
# {f_b_content.splitlines()[index_line1]}
# {f_b_content.splitlines()[index_line1+1]}
# """

# import pqc_signature as psig
# path_to_user_entry_point = "cttool-draft/candidates.json"
# ret = psig.from_json_to_python_dict(path_to_user_entry_point)
# candidates_dict, chosen_tools, libraries, benchmark_libraries = ret
#
# candidates = candidates_dict.keys()
#
# print("candidates")
# print(list(candidates))
# print(type(candidates))

def get_candidates_instances(path_to_instances_folder):
    instances = os.listdir(path_to_instances_folder)
    instances = [instance for instance in instances if os.path.isdir(f"{path_to_instances_folder}/{instance}")]
    # print(instances)
    return instances

p_ins = "candidates/lattice/hawk/NIST/Optimized_Implementation/avx2"



instances_t = get_candidates_instances(p_ins)

#instances_t = [inst for inst in instances_t if "neon" not in inst]

print(instances_t)




