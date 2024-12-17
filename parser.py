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
from typing import Union, List, Optional
import argparse


def parser_from_pattern(file_to_parse: str, pattern: str = ""):
    with open(file_to_parse, "r") as file:
        output_lines = file.readlines()
        # find lines that contain 'pattern'
        filter_list = list(filter(lambda line: f'\t{pattern}' in line, output_lines))
        # Remove \n
        list_of_opcode = list(map(str.strip, filter_list))
        # Remove \t
        list_of_opcode = list(map(lambda line: line.replace('\t', ''), list_of_opcode))
        # Split accordingly to ':'
        list_of_opcode = list(map(lambda line: line.split(':')[-1], list_of_opcode))

    set_of_opcode = set(list_of_opcode)
    return set_of_opcode


def get_opcode_block(list_of_opcode: Union[list, set], pattern: str = "", path_to_output: str = ""):
    opcode_block = f'''
    # opcode for {pattern}
    '''
    for line in list_of_opcode:
        # print("----line: ", line)
        # opcode_match = re.match(r'[\w+]*', line)
        # opcode_match = re.search('[\w+\s]*(?=[\s]*aesenclast)', line)
        opcode_match = re.search(f'[\w+\s]*(?=[\s\w+]*{pattern})', line)
        opcode = opcode_match.group(0)
        mnemonic_and_operands_match = re.search(f'{pattern}[\w+\s,%]*', line)
        mnemonic_and_operands = mnemonic_and_operands_match.group(0)
        # print("opcode: ", opcode)
        # print("mnemonic_and_operands: ", mnemonic_and_operands)
        dest_register = line.split(',')[-1]
        dest_register = dest_register.replace('%', '')
        # print("dest_register: ", dest_register)
        opcode_block += f'''
        # {mnemonic_and_operands}
        replace opcode {opcode} by
            {dest_register} := secret # nondet
        end
        '''
    with open(path_to_output, "w") as file:
        file.write(textwrap.dedent(opcode_block))


def get_opcode_command_name(binary: str, address: str):
    cwd = os.getcwd()
    binary_folder = os.path.dirname(binary)
    binary_basename = os.path.basename(binary)
    os.chdir(binary_folder)
    print("---binary_folder: ", binary_folder)
    # cmd_str = f'gdb ./{binary}.snapshot {binary}'
    cmd_str = f'gdb ./{binary_basename} {binary_basename}.snapshot'
    print("cmd_str: ", cmd_str)
    subprocess.call(cmd_str.split(), stdin=sys.stdin, shell=True)
    os.chdir(cwd)
    # cmd_str = f'x/i {address}'
    # print("cmd_str: ", cmd_str)
    # subprocess.call(cmd_str.split(), stdin=sys.stdin, shell=True)


def get_stubs(path_to_asm_file: str, command_name: str):
    set_of_opcode = parser_from_pattern(path_to_asm_file, command_name)
    stubs_output = f'stubs_{command_name}.txt'
    get_opcode_block(set_of_opcode, command_name, stubs_output)


def cli_stubs(subparser):

    generic_parser = subparser.add_parser('stubs', help='stubs:...',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arguments = f"'--command', '-command', dest='command', type=str, help = 'command'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--binary', '-binary', dest='binary', type=str, help = 'binary'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--path_asm_code', '-asm_file', dest='asm', type=str, help = 'path to asm code file'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)
    arguments = f"'--address', '-address', dest='address', type=str, help = 'Address of the required stub'"
    add_args_commdand = f"generic_parser.add_argument({arguments})"
    exec(add_args_commdand)


def get_required_stubs(args_parse):
    command = args_parse.command
    binary = args_parse.binary
    path_asm_code = args_parse.asm
    address = args_parse.address
    if address:
        get_opcode_command_name(binary, address)
    get_stubs(path_asm_code, command)


parser = argparse.ArgumentParser(prog="tii-constant-time-toolchain",
                                 description="Constant time check with Binsec, Timecop, Dudect",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)


subparser = parser.add_subparsers(help="", dest='tii_ct_toolchain')

cli_stubs(subparser)

# set all the command-line arguments into the object args
args = parser.parse_args()


def main():
    """ Function: main"""
    get_required_stubs(args)


if __name__ == "__main__":
    main()




# file_to_parse = "candidates/mpc-in-the-head/perk/binsec/perk-128-fast-3/perk_keypair/crypto.txt"
# file_to_parse = "candidates/mpc-in-the-head/mirith/binsec/mirith_avx2_Ia_fast/mirith_sign/obj_lib.txt"
# set_of_opcode = parser_from_pattern(file_to_parse, 'vpblendvb')
# get_opcode_block(set_of_opcode, "vpblendvb", 'output_vpblendvb.txt')


# gf31_random_elements
#
#
# Keccak_HashSqueeze --> KeccakWidth1600_SpongeSqueeze --> <KeccakWidth1600_SpongeSqueeze
# --													 --> KeccakP1600_ExtractBytes
# --													 --> <KeccakP1600_Permute_24rounds -->  <__KeccakF1600>
