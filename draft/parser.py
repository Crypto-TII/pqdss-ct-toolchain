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
from typing import Union, List


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









file_to_parse = "candidates/other/preon/Optimized_Implementation/binsec/Preon128/Preon128A/build/preon_keypair/dec_crypto.txt"
set_of_opcode = parser_from_pattern(file_to_parse, 'aesenc')
get_opcode_block(set_of_opcode, "aesenc", 'output_aesenc.txt')


# gf31_random_elements
#
#
# Keccak_HashSqueeze --> KeccakWidth1600_SpongeSqueeze --> <KeccakWidth1600_SpongeSqueeze
# --													 --> KeccakP1600_ExtractBytes
# --													 --> <KeccakP1600_Permute_24rounds -->  <__KeccakF1600>
