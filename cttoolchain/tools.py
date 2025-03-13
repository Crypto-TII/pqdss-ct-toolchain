#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""
import os
import stat
import textwrap
import re
import shutil
import sys
import subprocess
from subprocess import Popen

from typing import Optional, Union, List

import generics as gen


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
        if self.tool_name.lower() == 'timecop':
            self.tool_flags = "-Wall -g -Wextra"
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
        if self.tool_name.lower() == 'timecop':
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

# ======================TEST HARNESS =================================
# ====================================================================

# BINSEC: Test harness for crypto_sign_keypair
def test_harness_content_keypair(test_harness_file,
                                 api_or_sign, add_includes,
                                 function_return_type,
                                 function_name):
    test_harness_file_content_block1 = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h>
    '''
    test_harness_file_content_block2 = f'''
    uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;
    uint8_t sk[CRYPTO_SECRETKEYBYTES] ;
    
    int main(){{
    \t{function_name}(pk, sk);
    \t{function_return_type} result =  {function_name}(pk, sk);
    \texit(result);
    }} 
    '''
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block1))
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        t_harness_file.write(f'#include {api_or_sign}\n')
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block2))


# BINSEC: Test harness for crypto_sign
def sign_test_harness_content(test_harness_file, api_or_sign, add_includes,
                              function_return_type,
                              function_name, args_types,
                              args_names):
    if 'const' in args_types[2]:
        args_types[2] = re.sub("const ", "", args_types[2])
        args_types[4] = re.sub("const ", "", args_types[4])
    test_harness_file_content_block1 = f'''
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <ctype.h> 
    '''
    arguments = f'{args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {args_names[4]}'
    test_harness_file_content_block2 = f'''
    #define msg_length  3300
    {args_types[0]} {args_names[0]}[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len
    {args_types[1]} {args_names[1]} ;
    volatile {args_types[3]} {args_names[3]} = msg_length ;
    {args_types[2]} {args_names[2]}[msg_length] ;
    {args_types[4]} {args_names[4]}[CRYPTO_SECRETKEYBYTES] ;
    
    int main(){{
    \t{function_name}({arguments});
    \t{function_return_type} result =  {function_name}({arguments});
    \texit(result);
    }}
    '''
    with open(test_harness_file, "w") as t_harness_file:
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block1))
        if not add_includes == []:
            for include in add_includes:
                t_harness_file.write(f'#include {include}\n')
        t_harness_file.write(f'#include {api_or_sign}\n')
        t_harness_file.write(textwrap.dedent(test_harness_file_content_block2))


# CTGRIND: taint for crypto_sign_keypair
def ctgrind_keypair_taint_content(taint_file, api_or_sign, add_includes,
                                  function_return_type,
                                  function_name,
                                  args_types,
                                  args_names):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    #include <ctgrind.h>
    #include <openssl/rand.h>
    
    '''
    taint_file_content_block_main = f'''
    #define CTGRIND_SAMPLE_SIZE 100
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} *{args_names[1]};
    
    int main() {{
    \t{args_names[0]} = calloc(CRYPTO_PUBLICKEYBYTES, sizeof({args_types[0]})); 
    \t{args_names[1]} = calloc(CRYPTO_SECRETKEYBYTES, sizeof({args_types[1]}));

    \t{function_return_type} result = 2 ;
    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\tct_poison({args_names[1]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[1]}));
    \t\tresult = {function_name}({args_names[0]},{args_names[1]}); 
    \t\tct_unpoison({args_names[1]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[1]})); 
    \t}}

    \tfree({args_names[0]});
    \tfree({args_names[1]});
    \treturn result; 
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        t_file.write(f'#include {api_or_sign}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


# CTGRIND: taint for crypto_sign
def ctgrind_sign_taint_content(taint_file, api_or_sign,
                               rng, add_includes,
                               function_return_type,
                               function_name, args_types,
                               args_names):
    args_types[2] = re.sub("const ", "", args_types[2])
    args_types[4] = re.sub("const ", "", args_types[4])
    type_sk_with_no_const = args_types[4]
    secret_key = args_names[4]

    if rng == '""' or rng == '':
        rng = '"../toolchain_randombytes.h"'
    taint_file_folder_split = taint_file.split('/')[0:-2]
    taint_file_folder = "/".join(taint_file_folder_split)
    toolchain_rand = 'candidates/toolchain_randombytes.h'
    toolchain_rand_cpy = f'{taint_file_folder}/toolchain_randombytes.h'
    shutil.copyfile(toolchain_rand, toolchain_rand_cpy)
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    #include <ctgrind.h>
    '''
    taint_file_content_block_main = f'''
    #define CTGRIND_SAMPLE_SIZE 100
    #define max_message_length 3300
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} {args_names[1]} = 0;
    //{args_types[1]} *{args_names[1]};
    {args_types[2]} *{args_names[2]};
    {args_types[3]} {args_names[3]} = 0;
    {args_types[4]} {secret_key}[CRYPTO_SECRETKEYBYTES] = {{0}};
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \trandombytes({args_names[2]}, {args_names[3]});
    \t//randombytes({args_names[4]}, CRYPTO_SECRETKEYBYTES);
    \t{type_sk_with_no_const} public_key[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t(void)crypto_sign_keypair(public_key, {secret_key});
    }} 
    
    int main() {{
    \t{function_return_type} result = 2 ; 
    \tfor (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {{
    \t\t{args_names[3]} = 33*(i+1);
    \t\t{args_names[2]} = ({args_types[2]} *)calloc({args_names[3]}, sizeof({args_types[2]}));
    \t\t{args_names[0]} = ({args_types[0]} *)calloc({args_names[3]}+CRYPTO_BYTES, sizeof({args_types[0]}));
    
    \t\tgenerate_test_vectors(); 
    \t\tct_poison({secret_key}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tresult = {function_name}({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {secret_key}); 
    \t\tct_unpoison({secret_key}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tfree({args_names[0]});
    \t\tfree({args_names[2]});
    \t}}
    \treturn result;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        t_file.write(f'#include {api_or_sign}\n')
        t_file.write(f'#include {rng}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


# TIMECOP: taint for crypto_sign_keypair
def timecop_keypair_taint_content(taint_file, api_or_sign, add_includes, function_return_type,
                                  function_name, args_types, args_names):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #include "poison.h"
    '''
    taint_file_content_block_main = f'''
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} *{args_names[1]};
    
    int main() {{
    \t{args_names[0]} = calloc(CRYPTO_PUBLICKEYBYTES, sizeof({args_types[0]})); 
    \t{args_names[1]} = calloc(CRYPTO_SECRETKEYBYTES, sizeof({args_types[1]}));

    \t{function_return_type} result = 2 ;
    \tpoison({args_names[1]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[1]}));
    \tresult = {function_name}({args_names[0]},{args_names[1]}); 
    \tunpoison({args_names[1]}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[1]})); 
    \tfree({args_names[0]});
    \tfree({args_names[1]});
    \treturn result; 
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        t_file.write(f'#include {api_or_sign}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


# TIMECOP: taint for crypto_sign
def timecop_sign_taint_content1(taint_file, api_or_sign, rng, add_includes,
                               function_return_type, function_name, args_types, args_names):
    args_types[2] = re.sub("const ", "", args_types[2])
    args_types[4] = re.sub("const ", "", args_types[4])
    type_sk_with_no_const = args_types[4]
    secret_key = args_names[4]
    rng = '"toolchain_randombytes.h"'
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #include "poison.h"
    '''
    taint_file_content_block_main = f'''
    #define TIMECOP_NUMBER_OF_EXECUTION 100
    #define max_message_length 3300
    
    {args_types[0]} *{args_names[0]};
    {args_types[1]} {args_names[1]} = 0;
    //{args_types[1]} *{args_names[1]};
    {args_types[2]} *{args_names[2]};
    {args_types[3]} {args_names[3]} = 0;
    {args_types[4]} {secret_key}[CRYPTO_SECRETKEYBYTES] = {{0}};
    
    void generate_test_vectors() {{
    \t//Fill randombytes
    \tct_randombytes({args_names[2]}, {args_names[3]});
    \t//ct_randombytes({args_names[4]}, CRYPTO_SECRETKEYBYTES);
    \t{type_sk_with_no_const} public_key[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t(void)crypto_sign_keypair(public_key, {secret_key});
    }} 
    
    int main() {{
    \t{function_return_type} result = 2 ; 
    \tfor (int i = 0; i < TIMECOP_NUMBER_OF_EXECUTION; i++) {{
    \t\t{args_names[3]} = 33*(i+1);
    \t\t{args_names[2]} = ({args_types[2]} *)calloc({args_names[3]}, sizeof({args_types[2]}));
    \t\t{args_names[0]} = ({args_types[0]} *)calloc({args_names[3]}+CRYPTO_BYTES, sizeof({args_types[0]}));
    
    \t\tgenerate_test_vectors(); 
    \t\t
    \t\tpoison({secret_key}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tresult = {function_name}({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {secret_key}); 
    \t\tunpoison({secret_key}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tfree({args_names[0]});
    \t\tfree({args_names[2]});
    \t}}
    \treturn result;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        t_file.write(f'#include {api_or_sign}\n')
        t_file.write(f'#include {rng}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


# TIMECOP: taint for crypto_sign
def timecop_sign_taint_content(taint_file, api_or_sign, rng, add_includes,
                               function_return_type, function_name, args_types, args_names):
    args_types[2] = re.sub("const ", "", args_types[2])
    args_types[4] = re.sub("const ", "", args_types[4])
    type_sk_with_no_const = args_types[4]
    secret_key = args_names[4]
    rng = '"toolchain_randombytes.h"'
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #include "poison.h"
    '''
    taint_file_content_block_main = f'''
    #define TIMECOP_NUMBER_OF_EXECUTION 1
    #define max_message_length 3300
    
    int main() {{
    \t{args_types[0]} *{args_names[0]};
    \t{args_types[1]} {args_names[1]} = 0;
    \t//{args_types[1]} *{args_names[1]};
    \t{args_types[2]} *{args_names[2]};
    \t{args_types[3]} {args_names[3]} = 0;
    \t{args_types[4]} {secret_key}[CRYPTO_SECRETKEYBYTES] = {{0}};
    \t{function_return_type} result = 2 ; 
    \tfor (int i = 0; i < TIMECOP_NUMBER_OF_EXECUTION; i++) {{
    \t\t{args_names[3]} = 33*(i+1);
    \t\t{args_names[2]} = ({args_types[2]} *)calloc({args_names[3]}, sizeof({args_types[2]}));
    \t\t{args_names[0]} = ({args_types[0]} *)calloc({args_names[3]}+CRYPTO_BYTES, sizeof({args_types[0]}));
    
    \t\tct_randombytes({args_names[2]}, {args_names[3]});
    \t\t{type_sk_with_no_const} public_key[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t\t(void)crypto_sign_keypair(public_key, {secret_key});
    
    \t\tpoison({secret_key}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tresult = {function_name}({args_names[0]}, &{args_names[1]}, {args_names[2]}, {args_names[3]}, {secret_key}); 
    \t\tunpoison({secret_key}, CRYPTO_SECRETKEYBYTES * sizeof({args_types[4]}));
    \t\tfree({args_names[0]});
    \t\tfree({args_names[2]});
    \t}}
    \treturn result;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        t_file.write(f'#include {api_or_sign}\n')
        t_file.write(f'#include {rng}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


# DUDECT: for crypto_sign_keypair
def dudect_keypair_dude_content(taint_file, api_or_sign, add_includes,
                                function_return_type,
                                function_name,
                                args_types,
                                args_names, number_of_measurements='1e4'):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #define DUDECT_IMPLEMENTATION
    #include <dudect.h>
    
    '''
    taint_file_content_block_main = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    \t{args_types[0]} {args_names[0]}[CRYPTO_PUBLICKEYBYTES] = {{0}};;
    \t{args_types[1]} {args_names[1]}[CRYPTO_SECRETKEYBYTES] = {{0}};;
    
    \t{function_return_type} result = {function_name}({args_names[0]},{args_names[1]});
    \treturn result;
    }}
    
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
    
    int main(int argc, char **argv)
    {{
    \t(void)argc;
    \t(void)argv;

    \tdudect_config_t config = {{
    \t\t.chunk_size = 32,
    \t\t.number_measurements = {number_of_measurements},
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
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        t_file.write(f'#include {api_or_sign}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


# DUDECT: for crypto_sign
def dudect_sign_dude_content_18_fev(taint_file, api_or_sign, add_includes,
                             function_return_type,
                             function_name,
                             args_types,
                             args_names, number_of_measurements='1e4'):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #define DUDECT_IMPLEMENTATION
    #include <dudect.h>
    
    #define MESSAGE_LENGTH 3300
    
    #define SECRET_KEY_BYTE_LENGTH CRYPTO_SECRETKEYBYTES
    #define SIGNATURE_MESSAGE_BYTE_LENGTH (MESSAGE_LENGTH + CRYPTO_BYTES)
    
    '''
    type_msg = args_types[2]
    type_sk = args_types[4]

    type_sk_with_no_const = type_sk.replace('const', '')
    type_sk_with_no_const = type_sk_with_no_const.strip()

    sig_msg = args_names[0]
    sig_msg_len = args_names[1]
    msg = args_names[2]
    msg_len = args_names[3]
    sk = args_names[4]
    ret_type = function_return_type

    taint_file_split = taint_file.split('/')
    taint_file_folder = "/".join(taint_file_split[0:-1])
    static_class_execution_times = f'{taint_file_folder}/static.txt'
    random_class_execution_times = f'{taint_file_folder}/random.txt'

    taint_file_content_block_main = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    
    \t{args_types[1]} {sig_msg_len} = SIGNATURE_MESSAGE_BYTE_LENGTH; //the signature length could be initialized to 0.
    \t{args_types[0]} {sig_msg}[SIGNATURE_MESSAGE_BYTE_LENGTH] = {{0}};
    \t{args_types[3]} {msg_len} = MESSAGE_LENGTH; //  the message length could be also randomly generated.
    \t{type_msg} *{msg} = ({type_msg}*)data + 0; 
    \t{type_sk} *{sk} = ({type_sk}*)data + MESSAGE_LENGTH*sizeof({type_msg}) ; 
    
    \tuint8_t ret_val = 0;
    \tconst {ret_type} result = {function_name}({sig_msg}, &{sig_msg_len}, {msg}, {msg_len}, {sk});
    \tret_val ^= (uint8_t) result ^ {sig_msg}[0] ^ {sig_msg}[SIGNATURE_MESSAGE_BYTE_LENGTH - 1];
    \treturn ret_val;
    }}
    
    void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {{
    \trandombytes_dudect(input_data, c->number_measurements * c->chunk_size);
    \t{type_sk_with_no_const} public_key[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t{type_sk_with_no_const} fixed_secret_key[CRYPTO_SECRETKEYBYTES] = {{0}};
    \t(void)crypto_sign_keypair(public_key, fixed_secret_key);
    \tfor (size_t i = 0; i < c->number_measurements; i++) {{
    \t\tclasses[i] = randombit();
    \t\t\tif (classes[i] == 0) {{
     \t\t\t\t//Uncomment this line if you want to have a fixed message in this class.
    \t\t\t\t//memset(input_data + (size_t)i * c->chunk_size, 0x01, MESSAGE_LENGTH*sizeof({type_msg}));
    \t\t\t\tmemcpy(input_data + (size_t)i * c->chunk_size+MESSAGE_LENGTH*sizeof({type_msg}), 
    \t\t\t\t        fixed_secret_key, SECRET_KEY_BYTE_LENGTH*sizeof({type_sk}));
    \t\t\t}} else {{
    \t\t\t\t//Uncomment this line if you want to have a fixed message in this class.
    \t\t\t\t//memset(input_data + (size_t)i * c->chunk_size, 0x01, MESSAGE_LENGTH*sizeof({type_msg}));
    \t\t\t\tconst size_t offset = (size_t)i * c->chunk_size;
    \t\t\t\t{type_sk_with_no_const} pk[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t\t\t\t{type_sk_with_no_const} *sk = ({type_sk_with_no_const} *)input_data + offset + MESSAGE_LENGTH*sizeof({type_msg});
    \t\t\t\t(void)crypto_sign_keypair(pk, sk);
    \t\t\t}}
    \t\t}}
    \t}}
    
    int main(int argc, char **argv)
    {{
    \t(void)argc;
    \t(void)argv;
    
    \tconst size_t chunk_size = sizeof({type_msg})*MESSAGE_LENGTH + SECRET_KEY_BYTE_LENGTH*sizeof({type_sk}); 

    \tdudect_config_t config = {{
    \t\t.chunk_size = chunk_size,
    \t\t.number_measurements = {number_of_measurements},
    \t}};
    \tdudect_ctx_t ctx;

    \tdudect_init(&ctx, &config);
    
    FILE *static_distribution, *random_distribution;
    static_distribution = fopen("{static_class_execution_times}", "w");
    random_distribution = fopen("{random_class_execution_times}", "w");
    fprintf(static_distribution, "%s", "Static distribution measurements\\n");
    fprintf(random_distribution, "%s", "Random distribution measurements\\n");

    \tdudect_state_t state = DUDECT_NO_LEAKAGE_EVIDENCE_YET;
    \twhile (state == DUDECT_NO_LEAKAGE_EVIDENCE_YET) {{
    \t\tstate = dudect_main(&ctx);
    \t\tfor(int i=0;i<{number_of_measurements};i++){{
    \t\t\tif (ctx.classes[i] == 0){{
    \t\t\t\tfprintf(static_distribution, "%ld\\n", ctx.exec_times[i]);
    \t\t\t}}
    \t\t\telse{{
    \t\t\t\tfprintf(random_distribution, "%ld\\n", ctx.exec_times[i]);
    \t\t\t}}
    \t\t}}
    \t}}
    \tfclose(static_distribution);
    \tfclose(random_distribution);
    \tdudect_free(&ctx);
    \treturn (int)state;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        t_file.write(f'#include {api_or_sign}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


def dudect_sign_dude_content(taint_file, api_or_sign, add_includes,
                             function_return_type,
                             function_name,
                             args_types,
                             args_names, number_of_measurements='1e4', **kwargs):
    taint_file_content_block_include = f'''
    #include <stdio.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdlib.h>
    
    #define DUDECT_IMPLEMENTATION
    #include <dudect.h>
    
    #define MESSAGE_LENGTH 3300
    
    #define SECRET_KEY_BYTE_LENGTH CRYPTO_SECRETKEYBYTES
    #define SIGNATURE_MESSAGE_BYTE_LENGTH (MESSAGE_LENGTH + CRYPTO_BYTES)
    
    '''
    type_msg = args_types[2]
    type_sk = args_types[4]

    type_sk_with_no_const = type_sk.replace('const', '')
    type_sk_with_no_const = type_sk_with_no_const.strip()

    sig_msg = args_names[0]
    sig_msg_len = args_names[1]
    msg = args_names[2]
    msg_len = args_names[3]
    sk = args_names[4]
    ret_type = function_return_type

    taint_file_split = taint_file.split('/')
    taint_file_folder = "/".join(taint_file_split[0:-1])
    execution_times = f'{taint_file_folder}/measurements.txt'
    # random_class_execution_times = f'{taint_file_folder}/random.txt'

    taint_file_content_block_main = f'''
    uint8_t do_one_computation(uint8_t *data) {{
    
    \t{args_types[1]} {sig_msg_len} = SIGNATURE_MESSAGE_BYTE_LENGTH; //the signature length could be initialized to 0.
    \t{args_types[0]} {sig_msg}[SIGNATURE_MESSAGE_BYTE_LENGTH] = {{0}};
    \t{args_types[3]} {msg_len} = MESSAGE_LENGTH; //  the message length could be also randomly generated.
    \t{type_msg} *{msg} = ({type_msg}*)data + 0; 
    \t{type_sk} *{sk} = ({type_sk}*)data + MESSAGE_LENGTH*sizeof({type_msg}) ; 
    
    \tuint8_t ret_val = 0;
    \tconst {ret_type} result = {function_name}({sig_msg}, &{sig_msg_len}, {msg}, {msg_len}, {sk});
    \tret_val ^= (uint8_t) result ^ {sig_msg}[0] ^ {sig_msg}[SIGNATURE_MESSAGE_BYTE_LENGTH - 1];
    \treturn ret_val;
    }}
    
    void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {{
    \trandombytes_dudect(input_data, c->number_measurements * c->chunk_size);
    \t{type_sk_with_no_const} public_key[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t{type_sk_with_no_const} fixed_secret_key[CRYPTO_SECRETKEYBYTES] = {{0}};
    \t(void)crypto_sign_keypair(public_key, fixed_secret_key);
    \tfor (size_t i = 0; i < c->number_measurements; i++) {{
    \t\tclasses[i] = randombit();
    \t\t\tif (classes[i] == 0) {{
     \t\t\t\t//Uncomment this line if you want to have a fixed message in this class.
    \t\t\t\t//memset(input_data + (size_t)i * c->chunk_size, 0x01, MESSAGE_LENGTH*sizeof({type_msg}));
    \t\t\t\tmemcpy(input_data + (size_t)i * c->chunk_size+MESSAGE_LENGTH*sizeof({type_msg}), 
    \t\t\t\t        fixed_secret_key, SECRET_KEY_BYTE_LENGTH*sizeof({type_sk}));
    \t\t\t}} else {{
    \t\t\t\t//Uncomment this line if you want to have a fixed message in this class.
    \t\t\t\t//memset(input_data + (size_t)i * c->chunk_size, 0x01, MESSAGE_LENGTH*sizeof({type_msg}));
    \t\t\t\tconst size_t offset = (size_t)i * c->chunk_size;
    \t\t\t\t{type_sk_with_no_const} pk[CRYPTO_PUBLICKEYBYTES] = {{0}};
    \t\t\t\t{type_sk_with_no_const} *sk = ({type_sk_with_no_const} *)input_data + offset + MESSAGE_LENGTH*sizeof({type_msg});
    \t\t\t\t(void)crypto_sign_keypair(pk, sk);
    \t\t\t}}
    \t\t}}
    \t}}
    
    int main(int argc, char **argv)
    {{
    \t(void)argc;
    \t(void)argv;
    
    \tconst size_t chunk_size = sizeof({type_msg})*MESSAGE_LENGTH + SECRET_KEY_BYTE_LENGTH*sizeof({type_sk}); 

    \tdudect_config_t config = {{
    \t\t.chunk_size = chunk_size,
    \t\t.number_measurements = {number_of_measurements},
    \t}};
    \tdudect_ctx_t ctx;

    \tdudect_init(&ctx, &config);
    
    FILE *distributions;
    distributions = fopen("{execution_times}", "w");
    fprintf(distributions, "%s", "Static and Random distribution measurements\\n");
    
    
    \tdudect_state_t state = DUDECT_NO_LEAKAGE_EVIDENCE_YET;
    \twhile (state == DUDECT_NO_LEAKAGE_EVIDENCE_YET) {{
    \t\tstate = dudect_main(&ctx);
    \t\tfor(int i=0;i<{number_of_measurements};i++){{
    \t\t\tif (ctx.classes[i] == 0){{
    \t\t\t\tfprintf(distributions, "static;%ld\\n", ctx.exec_times[i]);
    \t\t\t}}
    \t\t\telse{{
    \t\t\t\tfprintf(distributions, "random;%ld\\n", ctx.exec_times[i]);
    \t\t\t}}
    \t\t}}
    \t}}
    \tfclose(distributions);
    \tdudect_free(&ctx);
    \treturn (int)state;
    }}
    '''
    with open(taint_file, "w") as t_file:
        t_file.write(textwrap.dedent(taint_file_content_block_include))
        if not add_includes == []:
            for include in add_includes:
                t_file.write(f'#include {include}\n')
        t_file.write(f'#include {api_or_sign}\n')
        t_file.write(textwrap.dedent(taint_file_content_block_main))


# FLOWTRACKER: xml file for crypto_sign_keypair
def flowtracker_keypair_xml_content(xml_file, api_or_sign, add_includes,
                                    function_return_type,
                                    function_name,
                                    args_types,
                                    args_names, crypto_sign_function=None):

    sign_function_name, sign_args_names = crypto_sign_function
    sig_msg = sign_args_names[0]
    sig_msg_len = sign_args_names[1]
    msg = sign_args_names[2]
    msg_len = sign_args_names[3]

    pk = args_names[0]
    sk = args_names[1]
    crypto_keypair = function_name
    xml_file_content = f'''
    <functions>
        <sources>
            <function>
                <name>{crypto_keypair}</name>
                <return>false</return>
                <public>
                    <parameter>{pk}</parameter>
                </public>
                <secret>
                    <parameter>{sk}</parameter>       <!--Secret key-->
                </secret>
            </function>
            <function>
                <name>crypto_sign</name>
                <return>false</return>
                <public>
                    <parameter>{sig_msg}</parameter>
                    <parameter>{sig_msg_len}</parameter>
                    <parameter>{msg}</parameter>
                    <parameter>{msg_len}</parameter>
                    <parameter>{sk}</parameter> 
                </public>
                <secret>
                </secret>
            </function>
        </sources>
    </functions>
    '''
    with open(xml_file, "w") as t_file:
        t_file.write(textwrap.dedent(xml_file_content))


# FLOWTRACKER: xml file for crypto_sign
def flowtracker_sign_xml_content(xml_file, api_or_sign, add_includes,
                                 function_return_type,
                                 function_name,
                                 args_types,
                                 args_names):

    sig_msg = args_names[0]
    sig_msg_len = args_names[1]
    msg = args_names[2]
    msg_len = args_names[3]
    sk = args_names[4]
    ret_type = function_return_type
    crypto_sign = function_name
    xml_file_content = f'''
    <functions>
        <sources>
            <function>
                <name>{crypto_sign}</name>
                <return>false</return>
                <public>
                    <parameter>{sig_msg}</parameter>
                    <parameter>{sig_msg_len}</parameter>
                    <parameter>{msg}</parameter>
                    <parameter>{msg_len}</parameter>
                </public>
                <secret>
                    <parameter>{sk}</parameter>   <!--Secret key-->
                </secret>
            </function>
            <function>
                <name>{crypto_sign}</name>
                <return>false</return>
                <public>
                    <parameter>{sk}</parameter>
                    <parameter>pk</parameter>
                </public>
                <secret>
                </secret>
            </function>
        </sources>
    </functions>
    '''
    with open(xml_file, "w") as t_file:
        t_file.write(textwrap.dedent(xml_file_content))


def flowtracker_test_harness_template(target_basename: str, target_src_file: str,
                                      secret_arguments: list, path_to_xml_file: str) -> None:
    """flowtracker_template_test_harness:  Generate a test harness template (default) for flowtracker"""

    test_harness_directory_split = path_to_xml_file.split('/')
    test_harness_directory = "/".join(test_harness_directory_split[:-1])
    if not os.path.isdir(test_harness_directory):
        print("Remark: {} is not a directory".format(test_harness_directory))
        print("--- creating {} directory".format(test_harness_directory))
        cmd = ["mkdir", "-p", test_harness_directory]
        subprocess.call(cmd, stdin=sys.stdin)

    find_target = gen.find_target_by_basename_from_source_file(target_basename, target_src_file)
    targ_obj = gen.Target(find_target)
    args_names = targ_obj.candidate_args_names
    args_types = targ_obj.candidate_types
    targ_return_type = targ_obj.candidate_return_type
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
    with open(path_to_xml_file, "w+") as t_harness_file:
        t_harness_file.write(textwrap.dedent(xml_file_block))


# ======================CONFIGURATION FILES =================================
# ===========================================================================


# BINSEC: script for crypto_sign_keypair
def sign_configuration_file_content(cfg_file_sign, crypto_sign_args_names, with_core_dump="yes"):
    sig_msg = crypto_sign_args_names[0]
    sig_msg_len = crypto_sign_args_names[1]
    msg = crypto_sign_args_names[2]
    msg_len = crypto_sign_args_names[3]
    sk = crypto_sign_args_names[4]
    script_file = cfg_file_sign
    if 'no' in with_core_dump.lower():
        print("Binsec: only test with core dump is taken into account.")
    if not cfg_file_sign.endswith('.ini'):
        cfg_file_sign_split = cfg_file_sign.split('.')
        if len(cfg_file_sign_split) == 1:
            script_file = f'{cfg_file_sign}.ini'
        else:
            script_file = f'{cfg_file_sign_split[0:-1]}.ini'
    cfg_file_content = f'''
    starting from core
    replace <getrandom> (buf, buffen, _) by
        for i<64> in 0 to buffen -1 do
            @[buf + i] := nondet as urandom
        end
        return buffen
    end
    
    import <brk>, <__curbrk> from libc.so.6
    replace <brk> (addr) by
        @[<__curbrk>, 8] := addr
        return 0
    end

    '''
    exploration_goal = f'''
    explore all'''
    cfg_file_content += f''' 
    secret global {sk}
    public global {sig_msg}, {sig_msg_len}, {msg}, {msg_len}
    halt at <exit>
    {exploration_goal}
    '''
    with open(script_file, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))


# BINSEC: script for crypto_sign
def cfg_content_keypair(cfg_file_keypair, with_core_dump="yes"):
    if 'no' in with_core_dump.lower():
        print("Binsec: only test with core dump is taken into account.")
    script_file = cfg_file_keypair
    if not cfg_file_keypair.endswith('.ini'):
        cfg_file_sign_split = cfg_file_keypair.split('.')
        if len(cfg_file_sign_split) == 1:
            script_file = f'{cfg_file_keypair}.ini'
        else:
            script_file = f'{cfg_file_keypair[0:-1]}.ini'
    cfg_file_content = f'''
    starting from core
    replace <getrandom> (buf, buffen, _) by
        for i<64> in 0 to buffen -1 do
            @[buf + i] := nondet as urandom
        end
        return buffen
    end
    import <brk>, <__curbrk> from libc.so.6
    replace <brk> (addr) by
        @[<__curbrk>, 8] := addr
        return 0
    end
    '''
    exploration_goal = f'''
    explore all'''
    cfg_file_content += f'''
    secret global sk
    public global pk
    halt at <exit>
    {exploration_goal}
    '''
    with open(script_file, "w") as cfg_file:
        cfg_file.write(textwrap.dedent(cfg_file_content))



# ======================CREATE folders ==================================
# =======================================================================

# Create same sub-folders in each folder of a given list of folders
def generic_create_tests_folders(list_of_path_to_folders):
    for t_folder in list_of_path_to_folders:
        if not os.path.isdir(t_folder):
            cmd = ["mkdir", "-p", t_folder]
            subprocess.call(cmd, stdin=sys.stdin)


# ==================== EXECUTION =====================================
# ====================================================================

# Run Binsec
def run_binsec_v_0_9_1(executable_file, cfg_file, stats_files, output_file, depth):
    command = f'''binsec -sse -checkct -sse-script {cfg_file} -sse-depth  {depth} -sse-self-written-enum 1
          '''
    command += f'{executable_file}'
    cmd_args_lst = command.split()
    with open(output_file, "w") as file:
        execution = Popen(cmd_args_lst, universal_newlines=True, stdout=file, stderr=file)
        execution.communicate()

    with open(output_file, "r") as file:
        output_lines = file.readlines()
        if output_lines:
            program_status_filter = list(filter(lambda line: 'Program status is' in line, output_lines))
            prog_status_search = re.search(r'Program status is : \w*', program_status_filter[0])
            program_status = prog_status_search.group(0)
            program_need_for_stubs_filter = list(filter(lambda line: 'Cut path ' in line, output_lines))
            required_stubs = []
            if program_need_for_stubs_filter:
                for sse_error in program_need_for_stubs_filter:
                    prog_stub_search = re.search(r'Cut path \w*', sse_error)
                    if prog_stub_search:
                        address = re.search(r'@\s \w*', sse_error)
                        print("++++++address: ", address)
                    program_stub = prog_stub_search.group()
                    print("++++++sse_error: ", sse_error)
                    print("++++++program_stub: ", program_stub)
            program_exploration_filter = list(filter(lambda line: 'Exploration is incomplete' in line, output_lines))
            if program_exploration_filter:
                print("---Exploration is incomplete")
            if program_status.strip() == 'insecure':
                print("---The target program is insecure. Please refer to the README.md to check the insecure instructions")
            if program_status.strip() == 'secure':
                print("---The target program is secure.")
            else:
                print("---Binsec cannot prove that the target program is secure or insecure.")


def run_binsec(executable_file, cfg_file, stats_files, output_file, depth, **kwargs):
    command = f'''binsec -sse -checkct -checkct-features memory-access,control-flow,divisor,dividend,multiplication
     -sse-script {cfg_file} -sse-depth  {depth} -sse-self-written-enum 1 -checkct-stats-file {stats_files}'''
    if kwargs:
        for k, value in kwargs.items():
            if 'sse_timeout' in k:
                command += f' -sse-timeout {value}'
            elif 'solver_timeout' in k:
                command += f' -fml-solver-timeout {value}'
    command += f' {executable_file}'
    cmd_args_lst = command.split()
    with open(output_file, "w") as file:
        execution = Popen(cmd_args_lst, universal_newlines=True, stdout=file, stderr=file)
        execution.communicate()


# Generate gdb script
def binsec_generate_gdb_script1(path_to_gdb_script: str, path_to_snapshot_file: str, function_name='crypto_sign'):
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
    break main
    run
    finish
    generate-core-file {snapshot_file}
    kill
    quit
    '''
    with open(gdb_script, "w+") as gdb_file:
        gdb_file.write(textwrap.dedent(snapshot))


# Generate gdb script
def binsec_generate_gdb_script(path_to_gdb_script: str, path_to_snapshot_file: str, function_name='crypto_sign'):
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
    break main
    start
    generate-core-file {snapshot_file}
    kill
    quit
    '''
    with open(gdb_script, "w+") as gdb_file:
        gdb_file.write(textwrap.dedent(snapshot))


# Given an executable, generate a core file (.snapshot) with a given gdb script
def binsec_generate_core_dump1(path_to_executable_file: str, path_to_gdb_script: str):
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
    print("-------cmd: ")
    print(cmd)
    cmd_list = cmd.split()
    subprocess.call(cmd_list, stdin=sys.stdin)
    os.chdir(cwd)


# Given an executable, generate a core file (.snapshot) with a given gdb script
def binsec_generate_core_dump(path_to_executable_file: str, path_to_gdb_script: str):
    cmd = f'gdb -x {path_to_gdb_script} ./{path_to_executable_file}'
    cmd_list = cmd.split()
    subprocess.call(cmd_list, stdin=sys.stdin)


# Run CTGRIND
def run_ctgrind(binary_file, output_file):
    command = f'''valgrind -s --track-origins=yes --leak-check=full 
                --show-leak-kinds=all --verbose --log-file={output_file} ./{binary_file}'''
    cmd_args_lst = command.split()
    subprocess.call(cmd_args_lst, stdin=sys.stdin)


# Run TIMECOP
def run_timecop(binary_file, output_file):
    command = f'''valgrind -s --track-origins=yes --leak-check=full 
                --show-leak-kinds=all --verbose --log-file={output_file} ./{binary_file}'''
    cmd_args_lst = command.split()
    subprocess.call(cmd_args_lst, stdin=sys.stdin)


# Run DUDECT
def run_dudect_18_fev(executable_file: str, output_file: str, timeout='86400'):
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


def run_dudect(executable_file: str, output_file: str, timeout: Optional[Union[str, int]] = None):
    command = ""
    if timeout is None:
        command = f'timeout 86400 ./{executable_file}'
    else:
        if isinstance(timeout, str) and timeout.lower() == 'no':
            command += f'./{executable_file}'
        elif isinstance(timeout, str) and timeout.lower() != 'no':
            command = f'timeout {timeout} ./{executable_file}'
        elif isinstance(timeout, int):
            command = f'timeout {timeout} ./{executable_file}'
    cmd_args_lst = command.split()
    execution = subprocess.Popen(cmd_args_lst, stdout=subprocess.PIPE)
    output, error = execution.communicate()
    output_decode = output.decode('utf-8')
    with open(output_file, "w") as file:
        for line in output_decode.split('\n'):
            file.write(line + '\n')

# Run FLOWTRACKER
def run_flowtracker_12_march(rbc_file, xml_file, output_file, sh_file_folder):
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


def run_flowtracker(rbc_file, xml_file, output_file):
    cwd = os.getcwd()
    rbc_file_folder = os.path.dirname(rbc_file)
    xml_file_basename = os.path.basename(xml_file)
    output_file_basename = os.path.basename(output_file)
    rbc_file_basename = os.path.basename(rbc_file)
    os.chdir(rbc_file_folder)
    sh_command = f'''
    #!/bin/sh
    opt -basicaa -load AliasSets.so -load DepGraph.so -load bSSA2.so -bssa2\
    -xmlfile {xml_file_basename} {rbc_file_basename} 2>{output_file_basename}
    '''
    shell_file = 'run_candidate.sh'
    with open(shell_file, 'w') as sh_file:
        sh_file.write(textwrap.dedent(sh_command))
    st = os.stat('run_candidate.sh')
    os.chmod('run_candidate.sh', st.st_mode | stat.S_IEXEC)
    cmd = ["./run_candidate.sh"]
    subprocess.call(cmd, stdin=sys.stdin, shell=True)
    os.chdir(cwd)


def flowtracker_compile_target_src_file(target_src_file, target_include_directory, xml_file):
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



def ctgrind_generic_run(ctgrind_folder, signature_type,
                        candidate, optimized_imp_folder,
                        opt_src_folder_list_dir,
                        build_folder, binary_patterns):
    optimized_imp_folder_full_path = f'{signature_type}/{candidate}/{optimized_imp_folder}'
    ctgrind_folder_full_path = f'{optimized_imp_folder_full_path}/{ctgrind_folder}'
    list_of_instances = []
    if not opt_src_folder_list_dir:
        path_to_subfolder = ctgrind_folder_full_path
        list_of_instances.append(path_to_subfolder)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = f'{ctgrind_folder_full_path}/{subfold}'
            list_of_instances.append(path_to_subfolder)
    for instance in list_of_instances:
        path_to_build_folder = f'{instance}/{build_folder}'
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            ctgrind_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{ctgrind_folder_basename}'
            path_to_pattern_subfolder = f'{instance}/{ctgrind_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                bin_basename = executable.split('taint_')[-1]
                bin_basename = bin_basename.split('.o')[0]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                print("::::Running:", abs_path_to_executable)
                run_ctgrind(abs_path_to_executable, output_file)


def dudect_generic_run(dudect_folder, signature_type,
                       candidate, optimized_imp_folder,
                       opt_src_folder_list_dir,
                       build_folder, binary_patterns, timeout='86400'):
    optimized_imp_folder_full_path = f'{signature_type}/{candidate}/{optimized_imp_folder}'
    dudect_folder_full_path = f'{optimized_imp_folder_full_path}/{dudect_folder}'
    list_of_instances = []
    if not opt_src_folder_list_dir:
        path_to_subfolder = dudect_folder_full_path
        list_of_instances.append(path_to_subfolder)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = f'{dudect_folder_full_path}/{subfold}'
            list_of_instances.append(path_to_subfolder)
    for instance in list_of_instances:
        path_to_build_folder = f'{instance}/{build_folder}'
        for bin_pattern in binary_patterns:
            dudect_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_build_folder}/{dudect_folder_basename}'
            path_to_pattern_subfolder = f'{instance}/{dudect_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            for executable in bin_files:
                bin_basename = executable.split('dude_')[-1]
                bin_basename = bin_basename.split('.o')[0]
                output_file = f'{path_to_pattern_subfolder}/{bin_basename}_output.txt'
                abs_path_to_executable = f'{path_to_binary_pattern_subfolder}/{executable}'
                print("::::Running:", abs_path_to_executable)
                run_dudect(abs_path_to_executable, output_file, timeout)


def flowtracker_generic_run(flowtracker_folder, signature_type,
                            candidate, optimized_imp_folder,
                            opt_src_folder_list_dir,
                            build_folder, binary_patterns):
    cwd = os.getcwd()
    xml_pattern = '.xml'
    rbc_pattern = '.rbc'
    optimized_imp_folder_full_path = f'{signature_type}/{candidate}/{optimized_imp_folder}'
    flowtracker_folder_full_path = optimized_imp_folder_full_path + '/' + flowtracker_folder
    list_of_instances = []
    if not opt_src_folder_list_dir:
        path_to_subfolder = flowtracker_folder_full_path
        list_of_instances.append(path_to_subfolder)
    else:
        for subfold in opt_src_folder_list_dir:
            path_to_subfolder = f'{flowtracker_folder_full_path}/{subfold}'
            list_of_instances.append(path_to_subfolder)
    for instance in list_of_instances:
        path_to_build_folder = f'{instance}/{build_folder}'
        path_to_binary_files = path_to_build_folder
        for bin_pattern in binary_patterns:
            flowtracker_folder_basename = f'{candidate}_{bin_pattern}'
            path_to_binary_pattern_subfolder = f'{path_to_binary_files}/{flowtracker_folder_basename}'
            path_to_pattern_subfolder = f'{instance}/{flowtracker_folder_basename}'
            bin_files = os.listdir(path_to_binary_pattern_subfolder)
            bin_files = [file for file in bin_files if file.endswith('.rbc')]
            for executable in bin_files:
                bin_basename = executable.split('rbc_')[-1]
                bin_basename = bin_basename.split('.rbc')[0]
                output_file = f'{bin_basename}_output.out'
                xml_file = gen.find_ending_pattern(path_to_pattern_subfolder, xml_pattern)
                xml_file = os.path.basename(xml_file)

                rbc_file_folder = f'../{build_folder}/{flowtracker_folder_basename}'
                rbc_file = f'{rbc_file_folder}/{executable}'
                os.chdir(path_to_pattern_subfolder)
                sh_file_folder = flowtracker_folder_basename
                print("::::Running: ", rbc_file)
                run_flowtracker(rbc_file, xml_file, output_file, sh_file_folder)
            os.chdir(cwd)


