#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Technical Validation Team
"""
import os
import sys
import subprocess
import textwrap
import generic_functions as gen_funct


# ============================== MPC-IN-THE-HEAD ================
# ===============================================================

def implementation_required_flags(ref_impl: str=None, opt_impl: str=None,
                                  add_avx2_impl: str=None, add_neon_impl: str=None,
                                  impl_flags: list=None, special_src_files: list=None):

    ref_flags = []
    opt_flags = []
    add_avx2_flags = []
    add_neon_flags = []
    special_additional_src_files = special_src_files
    if ref_impl:
        ref_flags = impl_flags
    if opt_impl:
        opt_flags = impl_flags
    if add_avx2_impl:
        add_avx2_flags = impl_flags
    if add_neon_impl:
        add_neon_flags = impl_flags
    return ref_flags, opt_flags, add_avx2_flags, add_neon_flags, special_additional_src_files


# ================================ MIRITH ========================
def makefile_mirith(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    add_cflags = ""
    asm_flags = ""
    if implementation_type == 'opt':
        add_cflags = f'-mavx2'
        asm_flags = f'ASMFLAGS := ${{CFLAGS}} -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1'
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:

        makefile_content = f'''
        CC=gcc
        CFLAGS=-std=c11 -Wall -Wextra -pedantic {add_cflags}
        
        BASE_DIR = ../../{subfolder}
        
        
        DEPS=$(wildcard $(BASE_DIR)/*.h)
        OBJ=$(patsubst $(BASE_DIR)/%.c,$(BASE_DIR)/%.o,$(wildcard $(BASE_DIR)/*.c)) 
        OBJ+=$(patsubst $(BASE_DIR)/%.s,$(BASE_DIR)/%.o,$(wildcard $(BASE_DIR)/*.s))
        
        UNAME_S := $(shell uname -s)
        ifeq ($(UNAME_S),Linux)
        \tCFLAGS := ${{CFLAGS}} -lcrypto
        endif
        ifeq ($(UNAME_S),Darwin)
        \tCFLAGS := ${{CFLAGS}} -I/usr/local/opt/openssl/include
        \tLIBS :=-L/usr/local/opt/openssl/lib -lcrypto
        \t{asm_flags}
        endif
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_FLAGS = {tool_flags}
        TOOL_LIBS = {tool_libs}
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        %.o: %.s
        \t$(CC) -c $(ASMFLAGS) -o $@ $<
        
        %.o: %.c $(DEPS)
        \t$(CC) -c $(CFLAGS) -o $@ $<
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).o $(OBJ)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LIBDIR) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) $(TOOL_LIBS) $(TOOL_FLAGS)
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).o $(OBJ)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LIBDIR) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) $(TOOL_LIBS) $(TOOL_FLAGS)
        
        .PHONY: clean
          
        clean:
        \trm -f $(BASE_DIR)/*.o $(BASE_DIR)/*.su
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ========================================== PERK ============================
def makefile_perk(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    add_cflags = ""
    asm_flags = ""
    if implementation_type == 'opt':
        add_cflags = f'-mavx2 -mpclmul -msse4.2 -maes'
        asm_flags = f'ASMFLAGS := -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1'
    #
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}/src
        
        CRYPTOCODE_INCS = ../../{subfolder}/lib/cryptocode
        RANDOMBYTES_INCS = ../../{subfolder}/lib/randombytes
        XKCP_INCS = ../../{subfolder}/lib/XKCP
        
        
        
        SIGN = $(BASE_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(CRYPTOCODE_INCS) -I $(RANDOMBYTES_INCS) -I $(XKCP_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(CRYPTOCODE_INCS) -I $(RANDOMBYTES_INCS) -I $(XKCP_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''   
        CC = gcc
        CFLAGS:= -std=c99 -pedantic -Wall -Wextra -O3 -funroll-all-loops -march=native \
        \t-Wimplicit-function-declaration -Wredundant-decls \
        \t-Wundef -Wshadow  {add_cflags}
            #-Wno-newline-eof
        # ASMFLAGS := -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
        LDFLAGS:= -lcrypto
        {asm_flags}
        ADDITIONAL_CFLAGS:= -Wno-missing-prototypes -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter
        
        BASE_DIR = ../../{subfolder}
        # Directories
        BUILD_DIR:=build
        BIN_DIR:=$(BUILD_DIR)/bin
        LIB_DIR:=$(BASE_DIR)/lib
        SRC_DIR:=$(BASE_DIR)/src
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        BUILD					= $(BUILD_DIR)
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        # Exclude main.c and PQCgenKAT_sign.c 
        MAIN_PERK_SRC:=$(SRC_DIR)/main.c
        MAIN_KAT_SRC:=$(SRC_DIR)/PQCgenKAT_sign.c
        
        # exclude sources from "find"
        EXCL_SRC:=! -name $(notdir $(MAIN_PERK_SRC)) \
                  ! -name $(notdir $(MAIN_KAT_SRC))
        
        # PERK sources
        PERK_SRC:= $(shell find $(SRC_DIR) -name "*.c" $(EXCL_SRC))
        # Lib sources
        LIB_CSRC := $(shell find $(LIB_DIR) -name "*.c" ! -path  "lib/djbsort/*")
        SORT_CSRC := $(shell find $(LIB_DIR)/djbsort -name "*.c")
        LIB_SSRC := $(shell find $(LIB_DIR) -name "*.s")
        
        
        # PERK objects
        PERK_OBJS:=$(PERK_SRC:%.c=$(BUILD_DIR)/%$(EXT).o)
        # Lib objects
        LIB_COBJS:=$(LIB_CSRC:%.c=$(BUILD_DIR)/%.o)
        SORT_COBJS:=$(SORT_CSRC:%.c=$(BUILD_DIR)/%.o)
        LIB_SOBJS:=$(LIB_SSRC:%.s=$(BUILD_DIR)/%.o)
        LIB_OBJS:=$(LIB_COBJS) $(LIB_SOBJS) $(SORT_COBJS)
        
        
        # include directories
        LIB_INCLUDE:=-I $(LIB_DIR)/cryptocode -I $(LIB_DIR)/XKCP -I $(LIB_DIR)/randombytes -I $(LIB_DIR)/djbsort
        PERK_INCLUDE:=-I $(SRC_DIR) $(LIB_INCLUDE)
        
        .PHONY: all
        default: $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN)
        all: $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN)   
        
        # build rules
        $(LIB_COBJS): $(BUILD_DIR)/%.o: %.c
        \t@echo -e "### Compiling external library file $@"
        \t@mkdir -p $(dir $@)
        \t$(CC) $(CFLAGS) $(ADDITIONAL_CFLAGS) -c $< $(LIB_INCLUDE) -o $@
        
        $(SORT_COBJS): $(BUILD_DIR)/%.o: %.c
        \t@echo -e "### Compiling external library file $@"
        \t@mkdir -p $(dir $@)
        \t$(CC) $(CFLAGS) -fwrapv $(ADDITIONAL_CFLAGS) -c $< $(LIB_INCLUDE) -o $@
        
        $(LIB_SOBJS): $(BUILD_DIR)/%.o: %.s
        \t@echo -e "### Assembling external library file $@"
        \t@mkdir -p $(dir $@)
        \t$(CC) $(ASMFLAGS) -c $< -o $@
        
        $(PERK_OBJS): $(BUILD_DIR)/%$(EXT).o: %.c
        \t@echo -e "### Compiling {subfolder} file $@"
        \t@mkdir -p $(dir $@)
        \t$(CC) $(CFLAGS) -c $< $(PERK_INCLUDE) -o $@
        
        # main targets
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c  $(PERK_OBJS) $(LIB_OBJS)
        \t@echo -e "### Compiling PERK Test harness keypair"
        \t@mkdir -p $(dir $@)
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -Wno-strict-prototypes -Wno-unused-result \
             $(PERK_INCLUDE) -o $(BUILD)/$@ $^ $(LDFLAGS) $(TOOL_LIBS)
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c  $(PERK_OBJS) $(LIB_OBJS)
        \t@echo -e "### Compiling PERK Test harness sign"
        \t@mkdir -p $(dir $@) 
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -Wno-strict-prototypes -Wno-unused-result \
             $(PERK_INCLUDE) -o $(BUILD)/$@ $^ $(LDFLAGS) $(TOOL_LIBS)
        
        clean:
        \trm -rf $(BUILD_DIR) 
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ============================== MQOM ================================
def get_mqom_params_index(subfolder):
    subfolder_split = subfolder.split("_")
    cat_index = subfolder_split[1][-1]
    gf_index = subfolder_split[2][2:]
    return cat_index, gf_index


def makefile_mqom(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    add_cflags = ""
    asm_flags = ""
    cat_index, gf_index = get_mqom_params_index(subfolder)
    implementation_type = implementation_type.strip()
    implementation_type = implementation_type.lower()
    arch = ""
    if implementation_type == 'ref':
        arch = 'opt64'
    if implementation_type == 'opt':
        arch = 'avx2'
        add_cflags = '-DPARAM_RND_EXPANSION_X4 -DHASHX4 -DXOFX4 -DPRGX4 -mavx '
        asm_flags = ''

    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        ALL_FLAGS?= -DPARAM_HYPERCUBE_7R -DPARAM_GF{gf_index} -DPARAM_L{cat_index} -DPARAM_RND_EXPANSION_X4\
         -DHASHX4 -DXOFX4 -DPRGX4 -DNDEBUG -mavx
         
        
        SIGN = $(BASE_DIR)/sign.c
        KEYGEN = $(BASE_DIR)/keygen.c
        
        HASH_PATH=$(BASE_DIR)/sha3
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(KEYGEN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(ALL_FLAGS) -I $(HASH_PATH)/avx2 -c -g $(KEYGEN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(ALL_FLAGS) -I $(HASH_PATH)/avx2 -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''    
        CC?=gcc
        ALL_FLAGS?=-O3 -flto -fPIC -std=c11 -march=native -Wall -Wextra -Wpedantic -Wshadow \
        \t-DPARAM_HYPERCUBE_7R -DPARAM_GF{gf_index} -DPARAM_L{cat_index} -DNDEBUG
        
        ALL_FLAGS+=$(EXTRA_ALL_FLAGS) {add_cflags}
        
        BASE_DIR = ../../{subfolder}
        
        SYM_OBJ= $(BASE_DIR)/rnd.o $(BASE_DIR)/hash.o $(BASE_DIR)/xof.o
        ARITH_OBJ= $(BASE_DIR)/gf{gf_index}-matrix.o $(BASE_DIR)/gf{gf_index}.o
        MPC_OBJ= $(BASE_DIR)/mpc.o $(BASE_DIR)/witness.o $(BASE_DIR)/serialization-specific.o $(BASE_DIR)/precomputed.o
        CORE_OBJ= $(BASE_DIR)/keygen.o $(BASE_DIR)/sign.o $(BASE_DIR)/views.o $(BASE_DIR)/commit.o \
        \t$(BASE_DIR)/sign-mpcith-hypercube.o $(BASE_DIR)/tree.o
        
        HASH_PATH=$(BASE_DIR)/sha3
        HASH_MAKE_OPTIONS=PLATFORM={arch}
        HASH_INCLUDE=-I$(BASE_DIR)/sha3 -I. -I$(BASE_DIR)/sha3/{arch}
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_OBJ	    = {candidate}_keypair/{test_keypair}.o $(BASE_DIR)/generator/rng.o
        EXECUTABLE_SIGN_OBJ		    = {candidate}_sign/{test_sign}.o $(BASE_DIR)/generator/rng.o
        
        EXECUTABLE_KEYPAIR  = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN     = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        
        %.o : %.c
        \t$(CC) -c $(ALL_FLAGS) $(HASH_INCLUDE) -I. $< -o $@
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        
        libhash:
        \t$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH)
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
        \tmkdir -p $(BUILD) 
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) \
        \t$(TOOL_FLAGS) $(ALL_FLAGS) -L$(HASH_PATH) -L. $(TOOL_LIBS) -lhash -lcrypto -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(TOOL_FLAGS) \
        \t$(ALL_FLAGS) -L$(HASH_PATH) -L. $(TOOL_LIBS) -lhash -lcrypto -o $(BUILD)/$@
    
        clean:
        \trm -f $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ)
        \trm -f $(EXECUTABLE_KEYPAIR_OBJ) $(EXECUTABLE_SIGN_OBJ)  
        \trm -rf unit-*
        \t$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH) clean
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ============================= RYDE ===========================================
def get_ryde_secret_level(subfolder):
    subfolder_split = subfolder.split("ryde")
    level = subfolder_split[-1][0:-1]
    if level == '128':
        rbc_level = '31'
    elif level == '192':
        rbc_level = '37'
    else:
        rbc_level = '43'
    return rbc_level


def makefile_ryde(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    add_cflags = ""
    if implementation_type == 'opt':
        add_cflags = '-mavx2 -mpclmul -msse4.2 -maes'

    makefile_content = ''
    rbc_level = get_ryde_secret_level(subfolder)
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}/src
        
        
        RANDOMBYTES_INCS = ../../{subfolder}/lib/randombytes
        XKCP_INCS = ../../{subfolder}/lib/XKCP
        RBC_INCS = $(BASE_DIR)/rbc-31
        
        SIGN = $(BASE_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(RANDOMBYTES_INCS) -I $(XKCP_INCS) -I $(RBC_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(RANDOMBYTES_INCS) -I $(XKCP_INCS) -I $(RBC_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f''' 
        SCRIPT_VERSION=v1.0
        SCRIPT_AUTHOR=RYDE team
        
        CC=gcc
        C_FLAGS:=-O3 -flto {add_cflags} -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4
        C_FLAGS_VERBOSE:=-O3 -flto {add_cflags} -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -DVERBOSE
        
        BASE_DIR = ../../{subfolder}
        
        RANDOMBYTES_SRC:=$(BASE_DIR)/lib/randombytes/randombytes.c
        RANDOMBYTES_INCLUDE:=-I $(BASE_DIR)/lib/randombytes -lcrypto
        
        XKCP_SRC:=$(BASE_DIR)/lib/XKCP
        XKCP_SRC_SIMPLE:=$(XKCP_SRC)/SimpleFIPS202.c
        XKCP_INCLUDE:=-I$(XKCP_SRC) -I$(XKCP_SRC)/avx2
        XKCP_INCLUDE_SIMPLE:=-I $(XKCP_SRC)
        XKCP_LINKER:=-L$(XKCP_SRC) -lshake
        
        WRAPPER_SRC:=$(BASE_DIR)/src/wrapper
        WRAPPER_INCLUDE:=-I $(WRAPPER_SRC)
        
        RBC_SRC:=$(BASE_DIR)/src/rbc-{rbc_level}
        RBC_INCLUDE:=-I $(RBC_SRC)
        
        SRC:=$(BASE_DIR)/src
        INCLUDE:=-I $(BASE_DIR)/src $(RBC_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) $(RANDOMBYTES_INCLUDE)
        
        RYDE_OBJS:=rbc_{rbc_level}_elt.o rbc_{rbc_level}_vec.o rbc_{rbc_level}_qpoly.o rbc_{rbc_level}_vspace.o rbc_{rbc_level}_mat.o keypair.o signature.o \
                    verification.o mpc.o parsing.o tree.o sign.o
        LIB_OBJS:=SimpleFIPS202.o randombytes.o
        
        #BUILD:=bin/build
        #BIN:=bin
        BUILD:=build
        BIN:=build/bin
        
        
        \tEXECUTABLE_KEYPAIR	    = {test_keypair}
        \tEXECUTABLE_SIGN		    = {test_sign}
        
        \tBUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        \tBUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        \tSRC_KEYPAIR	    	= {candidate}_keypair/{test_keypair}.c
        \tSRC_SIGN		    	= {candidate}_sign/{test_sign}.c
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
            
        folders:
        \t@echo -e "### Creating build folders"
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BIN)
        
        randombytes.o: folders
        \t@echo -e "### Compiling $@"
        \t$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BIN)/$@
        
        SimpleFIPS202.o: folders
        \t@echo -e "### Compiling $@"
        \t$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER)\
            -o $(BIN)/SimpleFIPS202.o
        
        xkcp: folders
        \t@echo -e "### Compiling XKCP"
        \tmake -C $(XKCP_SRC)
        
        rbc_%.o: $(RBC_SRC)/rbc_%.c | folders
        \t@echo -e "### Compiling $@"
        \t$(CC) $(C_FLAGS) -c $< $(RBC_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BIN)/$@
        
        %.o: $(SRC)/%.c | folders
        \t@echo -e "### Compiling $@"
        \t$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BIN)/$@ 
    
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        
    
        $(EXECUTABLE_KEYPAIR): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build {test_keypair}
        \t@echo -e "### Compiling test harness keypair"
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(TOOL_FLAGS) $(C_FLAGS) $(SRC_KEYPAIR) $(addprefix $(BIN)/, $^) \
        $(INCLUDE) $(XKCP_LINKER) -o $(BUILD_KEYPAIR)/$@ $(TOOL_LIBS)
    
        $(EXECUTABLE_SIGN): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build {test_sign}
        \t@echo -e "### Compiling test harness sign"
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(TOOL_FLAGS) $(C_FLAGS) $(SRC_SIGN) $(addprefix $(BIN)/, $^) \
        $(INCLUDE) $(XKCP_LINKER) -o $(BUILD_SIGN)/$@ $(TOOL_LIBS)
        
        .PHONY: clean
        clean: ##@Miscellaneous Clean data
        \tmake -C $(XKCP_SRC) clean
        \trm -f $(EXECUTABLE_KEYPAIR)
        \trm -f $(EXECUTABLE_SIGN)
        \trm -rf $(BIN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== SDITH ======================================
def get_sdith_level_and_field(subfolder):
    instance_basename = os.path.basename(subfolder)
    instance_split = instance_basename.split('_')
    sdith_field = instance_split[-1]
    sdith_level = instance_split[2][-1]
    return sdith_level, sdith_field


def makefile_sdith(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    sdith_level, sdith_field = get_sdith_level_and_field(subfolder)
    sdith_field = sdith_field.upper()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    ref_opt = 'avx2'
    if implementation_type == 'ref':
        ref_opt = 'ref'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC=gcc
        BASE_DIR = ../../../{subfolder}
        
        .POSIX:
        
        VARIANT = {ref_opt}
        FIELD = {sdith_field}
        SEC_LEVEL = CAT_{sdith_level}
        
        HASH_PATH=$(BASE_DIR)/sha3
        HASH_INCLUDE=-I$(BASE_DIR)/sha3/avx2
        
        ifeq ($(VARIANT), avx2)
        \tAVXFLAGS = -DAVX2 -mavx2 -mpclmul -mgfni -mavx -maes
        \tHASH_MAKE_OPTIONS = PLATFORM=avx2
        else
        \tAVXFLAGS =
        \tHASH_MAKE_OPTIONS = PLATFORM=opt64
        endif
        
        CFLAGS = -W -Wall -O3 -fPIC -DNDEBUG -D${{SEC_LEVEL}} -std=c11
        
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        ifeq ($(VARIANT), avx2)
            GF256_SRC = $(BASE_DIR)/gf256.c $(BASE_DIR)/gf2p32.c $(BASE_DIR)/gf256-avx2-polytable-ct.c \
             $(BASE_DIR)/gf256-avx2.c $(BASE_DIR)/gf256-avx2-gfni.c $(BASE_DIR)/gf256-avx-pclmul.c
            P251_SRC = $(BASE_DIR)/p251.c $(BASE_DIR)/p251p4.c $(BASE_DIR)/p251-avx2-ct.c
        else
            GF256_SRC = $(BASE_DIR)/gf2p32.c $(BASE_DIR)/gf256.c
            P251_SRC = $(BASE_DIR)/p251.c $(BASE_DIR)/p251p4.c
        endif
        
        ifeq ($(FIELD), GF256)
            FIELD_SRC = ${{GF256_SRC}}
        else
            FIELD_SRC = ${{P251_SRC}}
        endif
        
        CRYPTO_SRC = $(BASE_DIR)/hash-sha3.c $(BASE_DIR)/rng.c $(BASE_DIR)/treeprg.c
        SDITH_SRC = $(BASE_DIR)/sdith.c $(BASE_DIR)/precomputed.c $(BASE_DIR)/sign.c
        
        
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
          
        .PHONY: all
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        libhash:
        \t$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH)
        
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c ${{SRC}} ${{FIELD_SRC}} ${{CRYPTO_SRC}} ${{SDITH_SRC}} \
        $(BASE_DIR)/generator/rng.c  libhash
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t-${{CC}} ${{CFLAGS}} ${{AVXFLAGS}} $(TOOL_FLAGS) -o $(BUILD)/$@ ${{SRC}} ${{FIELD_SRC}} ${{CRYPTO_SRC}}\
         ${{SDITH_SRC}} $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/generator/rng.c -I. ${{HASH_INCLUDE}} -L${{HASH_PATH}} -lcrypto -lhash $(TOOL_LIBS)
         
         
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c ${{SRC}} ${{FIELD_SRC}} ${{CRYPTO_SRC}} ${{SDITH_SRC}} \
        $(BASE_DIR)/generator/rng.c  libhash
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t-${{CC}} ${{CFLAGS}} ${{AVXFLAGS}} $(TOOL_FLAGS) -o $(BUILD)/$@ ${{SRC}} ${{FIELD_SRC}} ${{CRYPTO_SRC}}\
         ${{SDITH_SRC}} $(EXECUTABLE_SIGN).c $(BASE_DIR)/generator/rng.c -I. ${{HASH_INCLUDE}} -L${{HASH_PATH}} -lcrypto -lhash $(TOOL_LIBS)
         
        
        clean:
        \t-rm $(OBJS) $(BASE_DIR)/prng/prng.o $(BASE_DIR)/prng/prng-nist.o $(BASE_DIR)/NIST-kat/rng.o    
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =============================== MIRA =================================
def makefile_mira(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    add_clfags = ''
    if implementation_type == 'opt':
        add_clfags = '-mavx2 -mpclmul -msse4.2 -maes'
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}/src
        
        SIGN = $(BASE_DIR)/nist_sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        SCRIPT_VERSION=v1.0
        SCRIPT_AUTHOR=MIRA team
        
        CC=gcc
        C_FLAGS:=-O3 -flto {add_clfags} -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4
        
        BASE_DIR = ../../{subfolder}
        
        RANDOMBYTES_SRC:=$(BASE_DIR)/lib/randombytes/randombytes.c
        RANDOMBYTES_INCLUDE:=-I $(BASE_DIR)/lib/randombytes -lcrypto
        
        XKCP_SRC:=$(BASE_DIR)/lib/XKCP
        XKCP_SRC_SIMPLE:=$(XKCP_SRC)/SimpleFIPS202.c
        XKCP_INCLUDE:=-I$(XKCP_SRC) -I$(XKCP_SRC)/avx2
        XKCP_INCLUDE_SIMPLE:=-I $(XKCP_SRC)
        XKCP_LINKER:=-L$(XKCP_SRC) -lshake
        
        WRAPPER_SRC:=$(BASE_DIR)/src/wrapper
        WRAPPER_INCLUDE:=-I $(WRAPPER_SRC)
        
        FFI_SRC:=$(BASE_DIR)/src/finite_fields
        FFI_INCLUDE:=-I $(FFI_SRC)
        
        SRC:=$(BASE_DIR)/src
        INCLUDE:=-I $(BASE_DIR)/src $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) $(RANDOMBYTES_INCLUDE)
        
        
        MIRA_OBJS:=finite_fields.o keygen.o sign.o verify.o nist_sign.o mpc.o parsing.o tree.o
        LIB_OBJS:=SimpleFIPS202.o randombytes.o
        
        BUILD:=build
        BIN:=build/bin
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
    
        BINSEC_STATIC_FLAG      = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_FLAGS = {tool_flags}
        TOOL_LIBS = {tool_libs}
        
        C_FLAGS +=  $(TOOL_FLAGS)
        
        folders:
        \t@echo -e "### Creating build/bin folders"
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BIN)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN) 
        
        
        randombytes.o: folders
        \t@echo -e "### Compiling $@"
        \t$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BIN)/$@
        
        SimpleFIPS202.o: folders
        \t@echo -e "### Compiling $@"
        \t$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER)\
         -o $(BIN)/SimpleFIPS202.o
        
        xkcp: folders
        \t@echo -e "### Compiling XKCP"
        \tmake -C $(XKCP_SRC)
        
        
        finite_fields.o: $(FFI_SRC)/finite_fields.c | folders
        \t@echo -e "### Compiling finite_fields"
        \t$(CC) $(C_FLAGS) -c $< $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BIN)/$@
        
        %.o: $(SRC)/%.c | folders
        \t@echo -e "### Compiling $@"
        \t$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BIN)/$@
        
        
        all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)  ##@Build Build all the project
        
        $(EXECUTABLE_KEYPAIR): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files
        \t@echo -e "### Compiling MIRA-128F (test harness keypair)"
        \t$(CC) $(TOOL_FLAGS) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^)\
         $(INCLUDE) $(XKCP_LINKER) $(TOOL_LIBS) -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files
        \t@echo -e "### Compiling MIRA-128F (test harness sign)"
        \t$(CC) $(TOOL_FLAGS) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^)\
         $(INCLUDE) $(XKCP_LINKER) $(TOOL_LIBS) -o $(BUILD)/$@
         
         
        .PHONY: clean
        clean:
        \tmake -C $(XKCP_SRC) clean
        \trm -f $(EXECUTABLE_KEYPAIR)
        \trm -f $(EXECUTABLE_SIGN)
        \trm -rf $(BUILD)/bin
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# # =================================== SDITH ====================================
# def makefile_sdith(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
#     tool_type = gen_funct.Tools(tool_name)
#     test_keypair, test_sign = tool_type.get_tool_test_file_name()
#     tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
#     path_to_makefile = path_to_makefile_folder+'/Makefile'
#     if tool_name == 'flowtracker':
#         makefile_content = f'''
#         CC = clang
#
#         BASE_DIR = ../../{subfolder}/src
#
#         INCS = $(wildcard $(BASE_DIR)/*.h)
#         #SRC  = $(wildcard $(BASE_DIR)/*.c))
#         SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
#         SIGN = $(BASE_DIR)/nist_sign.c
#
#         BUILD			= build
#         BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
#         BUILD_SIGN		= $(BUILD)/{candidate}_sign
#
#         EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
#         EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
#         EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
#         EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
#
#         all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
#
#
#
#         $(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
#         \tmkdir -p $(BUILD)
#         \tmkdir -p $(BUILD_KEYPAIR)
#         \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
#
#         $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
#         \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
#
#         $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
#         \tmkdir -p $(BUILD)
#         \tmkdir -p $(BUILD_SIGN)
#         \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
#
#         $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
#         \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
#
#         .PHONY: clean
#
#         clean:
#         \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
#         \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
#         '''
#     else:
#         makefile_content = f'''
#         SCRIPT_VERSION=v1.0
#         SCRIPT_AUTHOR=MIRA team
#
#         CC=gcc
#         C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -g
#
#         BASE_DIR = ../../{subfolder}
#
#         RANDOMBYTES_SRC:=$(BASE_DIR)/lib/randombytes/randombytes.c
#         RANDOMBYTES_INCLUDE:=-I $(BASE_DIR)/lib/randombytes -lcrypto
#
#         XKCP_SRC:=$(BASE_DIR)/lib/XKCP
#         XKCP_SRC_SIMPLE:=$(XKCP_SRC)/SimpleFIPS202.c
#         XKCP_INCLUDE:=-I$(XKCP_SRC) -I$(XKCP_SRC)/avx2
#         XKCP_INCLUDE_SIMPLE:=-I $(XKCP_SRC)
#         XKCP_LINKER:=-L$(XKCP_SRC) -lshake
#
#         WRAPPER_SRC:=$(BASE_DIR)/src/wrapper
#         WRAPPER_INCLUDE:=-I $(WRAPPER_SRC)
#
#         FFI_SRC:=$(BASE_DIR)/src/finite_fields
#         FFI_INCLUDE:=-I $(FFI_SRC)
#
#         SRC:=$(BASE_DIR)/src
#         INCLUDE:=-I $(BASE_DIR)/src $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) $(RANDOMBYTES_INCLUDE)
#
#
#         MIRA_OBJS:=finite_fields.o keygen.o sign.o verify.o nist_sign.o mpc.o parsing.o tree.o
#         LIB_OBJS:=SimpleFIPS202.o randombytes.o
#
#         BUILD:=build
#         BIN:=build/bin
#         BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
#         BUILD_SIGN			= $(BUILD)/{candidate}_sign
#
#         BINSEC_STATIC_FLAG      = -static
#         EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
#         EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
#
#         TOOL_LIBS = {tool_libs}
#         TOOL_FLAGS = {tool_flags}
#
#         folders:
#         \t@echo -e "### Creating build/bin folders"
#         \tmkdir -p $(BUILD)
#         \tmkdir -p $(BIN)
#         \tmkdir -p $(BUILD_KEYPAIR)
#         \tmkdir -p $(BUILD_SIGN)
#
#
#         randombytes.o: folders
#         \t@echo -e "### Compiling $@"
#         \t$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BIN)/$@
#
#         SimpleFIPS202.o: folders
#         \t@echo -e "### Compiling $@"
#         \t$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER)\
#          -o $(BIN)/SimpleFIPS202.o
#
#         xkcp: folders
#         \t@echo -e "### Compiling XKCP"
#         \tmake -C $(XKCP_SRC)
#
#
#         finite_fields.o: $(FFI_SRC)/finite_fields.c | folders
#         \t@echo -e "### Compiling finite_fields"
#         \t$(CC) $(C_FLAGS) -c $< $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BIN)/$@
#
#         %.o: $(SRC)/%.c | folders
#         \t@echo -e "### Compiling $@"
#         \t$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BIN)/$@
#
#
#         all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)  ##@Build Build all the project
#
#         $(EXECUTABLE_KEYPAIR): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files
#         \t@echo -e "### Compiling MIRA-128F (test harness keypair)"
#         \t$(CC) $(TOOL_FLAGs) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^)\
#          $(INCLUDE) $(XKCP_LINKER) $(TOOL_LIBS) -o $(BUILD)/$@
#
#         $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files
#         \t@echo -e "### Compiling MIRA-128F (test harness sign)"
#         \t$(CC) $(TOOL_FLAGs) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^) \
#         $(INCLUDE) $(XKCP_LINKER) $(TOOL_LIBS) -o $(BUILD)/$@
#
#         .PHONY: clean
#         clean:
#         \tmake -C $(XKCP_SRC) clean
#         \trm -f $(EXECUTABLE_KEYPAIR)
#         \trm -f $(EXECUTABLE_SIGN)
#         \trm -rf $(BUILD)/bin
#         '''
#     with open(path_to_makefile, "w") as mfile:
#         mfile.write(textwrap.dedent(makefile_content))


# =============================== CROSS =========================================
def cmake_cross(path_to_cmakelists_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_cmakelists = f'{path_to_cmakelists_folder}/CMakeLists.txt'
    ref_option = 0
    if implementation_type == 'ref':
        ref_option = 1

    cmake_file_content = ''
    target_link_opt_block = ''
    link_flag = ''
    if tool_flags:
        if '-static' in tool_flags:
            link_flag = '-static'
    libs_str = ""
    libs_list = []
    if tool_libs:
        libs_str = tool_libs.replace("-l", "")
        libs_list = libs_str.split()
    if tool_name == 'flowtracker':
        path_to_cmakelists = f'{path_to_cmakelists_folder}/Makefile'
        cmake_file_content = f'''
        CC = clang
        
        # selection of specialized compilation units differing between ref and opt
        # implementations.
        REFERENCE_CODE_DIR = ../../Reference_Implementation
        OPTIMIZED_CODE_DIR = ../../Optimized_Implementation
        
        BASE_DIR = $(REFERENCE_CODE_DIR)
        
        INCS_DIR = $(BASE_DIR)/include
        CATEGORY = 1
        RSDP_VARIANT =  RSDP
        PARAM_TARGETS =  SIG_SIZE
        CSPRNG_ALGO = SHAKE_CSPRNG
        HASH_ALGO = SHA3_HASH
        COMPILE_FLAGS  = -DCATEGORY_$(CATEGORY)=1 -D$(PARAM_TARGETS)=1 -D$(CSPRNG_ALGO)=1 \
        -D$(HASH_ALGO)=1 -D$(RSDP_VARIANT)=1 #${{KECCAK_EXTERNAL_ENABLE}}
        
        
        SIGN = $(BASE_DIR)/lib/sign.c
        
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        cmake_file_content = f'''
        cmake_minimum_required(VERSION 3.7)
        project(CROSS C)
        set(CMAKE_C_STANDARD 11)
        
        set(CC gcc)
        
        set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -march=native -O3 -g {tool_flags}") 
        
        set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} ${{SANITIZE}}")
        message("Compilation flags:" ${{CMAKE_C_FLAGS}})
        
        # default compilation picks reference codebase
        if(NOT DEFINED REFERENCE)
           set(REFERENCE {ref_option})
        endif()
        
        set(CSPRNG_ALGO SHAKE_CSPRNG)
        set(HASH_ALGO SHA3_HASH)
        
        find_library(KECCAK_LIB keccak)
        if(NOT KECCAK_LIB)
         set(STANDALONE_KECCAK 1)
        endif()
        '''
        find_libs_block = ''
        for lib in libs_list:
            lib_variable = lib.upper()
            lib_variable = f'{lib_variable}_LIB'
            find_libs_block += f'''
        find_library({lib_variable} {lib})
        if(NOT {lib_variable})
        \tmessage("{lib} library not found")
        endif()
        '''
        if libs_list:
            cmake_file_content += f'{find_libs_block}'
        cmake_file_content += f''' 
        # selection of specialized compilation units differing between ref and opt
        # implementations.
        set(REFERENCE_CODE_DIR ../../Reference_Implementation) 
        set(OPTIMIZED_CODE_DIR ../../Optimized_Implementation) 
        
        if(REFERENCE)
            message("Compiling portable reference code")
            set(SPEC_HEADERS  )
            set(SPEC_SOURCES
                    ${{REFERENCE_CODE_DIR}}/lib/aes256.c
            )
            else()
            message("Compiling optimized code")
            set(SPEC_HEADERS )
            set(SPEC_SOURCES
                    ${{OPTIMIZED_CODE_DIR}}/lib/aes256.c
            )
        endif()
        
        
        set(BASE_DIR ${{REFERENCE_CODE_DIR}})
        set(HEADERS
            ${{SPEC_HEADERS}}
            ${{BASE_DIR}}/include/api.h
            ${{BASE_DIR}}/include/aes256.h
            ${{BASE_DIR}}/include/aes256_ctr_drbg.h
            ${{BASE_DIR}}/include/CROSS.h
            ${{BASE_DIR}}/include/csprng_hash.h
            ${{BASE_DIR}}/include/pack_unpack.h
            ${{BASE_DIR}}/include/fips202.h
            ${{BASE_DIR}}/include/fq_arith.h
            ${{BASE_DIR}}/include/keccakf1600.h
            ${{BASE_DIR}}/include/parameters.h
            ${{BASE_DIR}}/include/seedtree.h
            ${{BASE_DIR}}/include/sha2.h
            ${{BASE_DIR}}/include/sha3.h
            ${{BASE_DIR}}/include/merkle_tree.h
            ${{BASE_DIR}}/include/merkle.h
        )
        
        if(STANDALONE_KECCAK)
          message("Employing standalone SHA-3")
          set(KECCAK_EXTERNAL_LIB "")
          set(KECCAK_EXTERNAL_ENABLE "")
          list(APPEND FALLBACK_SOURCES ${{BASE_DIR}}/lib/keccakf1600.c)
          list(APPEND FALLBACK_SOURCES ${{BASE_DIR}}/lib/fips202.c)
        else()
          message("Employing libkeccak")
          set(KECCAK_EXTERNAL_LIB keccak)
          set(KECCAK_EXTERNAL_ENABLE "-DSHA_3_LIBKECCAK")
        endif()
        
        
        set(SOURCES
            ${{SPEC_SOURCES}}
            ${{FALLBACK_SOURCES}}
            ${{BASE_DIR}}/lib/aes256_ctr_drbg.c
            ${{BASE_DIR}}/lib/CROSS.c
            ${{BASE_DIR}}/lib/csprng_hash.c
            ${{BASE_DIR}}/lib/pack_unpack.c
            ${{BASE_DIR}}/lib/keccakf1600.c
            ${{BASE_DIR}}/lib/fips202.c
            ${{BASE_DIR}}/lib/seedtree.c
            ${{BASE_DIR}}/lib/merkle.c
            ${{BASE_DIR}}/lib/sha2.c
            ${{BASE_DIR}}/lib/sign.c 
        )
        
        set(BUILD build)
        set(BUILD_KEYPAIR {candidate}_keypair)
        set(BUILD_SIGN {candidate}_sign)
        
        foreach(category RANGE 1 5 2)
            set(RSDP_VARIANTS RSDP RSDPG)
            foreach(RSDP_VARIANT ${{RSDP_VARIANTS}})
                set(PARAM_TARGETS SIG_SIZE SPEED)
                foreach(optimiz_target ${{PARAM_TARGETS}})
                     #crypto_sign_keypair test harness binary
                     set(TARGET_BINARY_NAME {test_keypair}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                     add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                        ./{candidate}_keypair/{test_keypair}.c)
                    '''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)'
        cmake_file_content += f''' 
                    target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                                ${{BASE_DIR}}/include) 
                     target_link_libraries(${{TARGET_BINARY_NAME}} m {libs_str} ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                     set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
                     set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                         COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 -D${{CSPRNG_ALGO}}=1 \
                          -D${{HASH_ALGO}}=1 -D${{RSDP_VARIANT}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")     
                                
                     #crypto_sign test harness binary
                     set(TARGET_BINARY_NAME {test_sign}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                     
                     add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                        ./{candidate}_sign/{test_sign}.c)
                    '''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)'
        cmake_file_content += f''' 
               target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                                ${{BASE_DIR}}/include) 
                     target_link_libraries(${{TARGET_BINARY_NAME}} {libs_str} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                     set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}})   
                     set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                         COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 -D${{CSPRNG_ALGO}}=1 \
                         -D${{HASH_ALGO}}=1 -D${{RSDP_VARIANT}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")           
                endforeach(optimiz_target) 
            endforeach(RSDP_VARIANT)
        endforeach(category)
        '''
    with open(path_to_cmakelists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content))


# ===============================  CODE =====================================
# ===========================================================================

# ===============================  PQSIGRM ==================================
def makefile_pqsigrm(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    add_cflags = ''
    if implementation_type == 'opt':
        add_cflags = '-mavx2'
    subfolder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../{subfolder}/src
        
        
        SIGN = $(BASE_DIR)/sign.c
        KEY_PAIR = $(BASE_DIR)/keypair.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(KEY_PAIR)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -c -g $(KEY_PAIR) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC = gcc
        LDFLAGS =  -L/usr/local/lib
        CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function {add_cflags}
        LIBFLAGS = -lcrypto -lssl -lm
        
        BASE_DIR = ../{subfolder}
        
        CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
        
        
        OBJS = $(CFILES)
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        ifeq ($(DEBUG), 1)
        \tDBG_FLAGS = -g -O0 -DDEBUG
        else
        \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
        endif
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        %.o : %.c
        \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
        
        
        $(EXECUTABLE_KEYPAIR): $(OBJS) $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(OBJS) $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(TOOL_LIBS)
        
        matrix.o : $(BASE_DIR)/matrix.h
        rng.o : $(BASE_DIR)/rng.h
        api.o : $(BASE_DIR)/api.h
        
        clean:
        \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
        \trm -f *.o
        \t cd ../../{candidate}
        \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =========================== LESS ==============================================
def cmake_less(path_to_cmakelists_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_cmakelists = f'{path_to_cmakelists_folder}/CMakeLists.txt'
    add_cflags = ""
    asm_flags = ""
    avx2_optimized_option = "OFF"
    if implementation_type == 'opt':
        add_cflags = f''
        asm_flags = f''
    if implementation_type == 'add':
        avx2_optimized_option = "ON"

    cmake_file_content = ''
    target_link_opt_block = ''
    link_flag = ''
    if tool_flags:
        if '-static ' in tool_flags or ' -static' in tool_flags:
            link_flag = '-static'
    libs_str = ""
    # tool_libs = tool_libs.replace("-lm", "")
    # tool_libs = tool_libs.strip()
    libs_list = []
    if tool_libs:
        libs_str = tool_libs.replace("-l", "")
        libs_list = libs_str.split()
    if tool_name == 'flowtracker':
        path_to_cmakelists = f'{path_to_cmakelists_folder}/Makefile'
        cmake_file_content = f'''
        CC = clang
        
        BASE_DIR = ../
        
        
        INCS_DIR = $(BASE_DIR)/include
        
        
        # CATEGORY RANGE 1 5 2
        # PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE
        # if CATEGORY = 1   PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE
        # else PARAM_TARGETS SIG_SIZE PK_SIZE
        
        KECCAK_EXTERNAL_ENABLE = 
        CATEGORY = 1
        RSDP_VARIANT =  RSDP
        PARAM_TARGETS =  SIG_SIZE
        COMPILE_FLAGS = -DCATEGORY_${{CATEGORY}}=1 -D${{PARAM_TARGETS}}=1 ${{KECCAK_EXTERNAL_ENABLE}}
        
        
        
        SIGN = $(BASE_DIR)/lib/sign.c
        
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        cmake_file_content = f'''
        cmake_minimum_required(VERSION 3.9.4)
        project(LESS C)
    
        # build type can be case-sensitive!
        string(TOUPPER "${{CMAKE_BUILD_TYPE}}" UPPER_CMAKE_BUILD_TYPE)
        
        set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -Wsign-conversion -Wno-strict-prototypes")
        
        include(CheckCCompilerFlag)
        unset(COMPILER_SUPPORTS_MARCH_NATIVE CACHE)
        check_c_compiler_flag(-march=native COMPILER_SUPPORTS_MARCH_NATIVE)
        
        include(CheckIPOSupported)
        check_ipo_supported(RESULT lto_supported OUTPUT error)
        
        if(UPPER_CMAKE_BUILD_TYPE MATCHES DEBUG)
            message(STATUS "Building in Debug mode!")
        else() # Release, RELEASE, MINSIZEREL, etc
            set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -mtune=native -O3 -g")   
            if(COMPILER_SUPPORTS_MARCH_NATIVE)
                set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -march=native")
            endif()
            if(lto_supported)
                message(STATUS "IPO / LTO enabled")
                set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
            endif()
        endif()
        
        option(COMPRESS_CMT_COLUMNS "Enable COMPRESS_CMT_COLUMNS to compress commitment in SG and VY before hashing" OFF)
        if(COMPRESS_CMT_COLUMNS)
            message(STATUS "COMPRESS_CMT_COLUMNS is enabled")
            add_definitions(-DCOMPRESS_CMT_COLUMNS)
        else()
            message(STATUS "COMPRESS_CMT_COLUMNS is disabled")
        endif()
        unset(COMPRESS_CMT_COLUMNS CACHE)
        
        set(SANITIZE "")
        message(STATUS "Compilation flags:" ${{CMAKE_C_FLAGS}})
        
        set(CMAKE_C_STANDARD 11)'''
        find_libs_block = ''
        libs_variables = ''
        for lib in libs_list:
            lib_variable = lib.upper()
            lib_variable = f'{lib_variable}_LIB'
            l_var = f'{lib_variable}'
            l_var = f'{{{l_var}}}'
            libs_variables += f' ${l_var}'
            find_libs_block += f'''
        find_library({lib_variable} {lib})
        if(NOT {lib_variable})
        \tmessage("{lib} library not found")
        endif()
        '''
        if libs_list:
            cmake_file_content += f'{find_libs_block}'
        cmake_file_content += f'''
        
        find_library(KECCAK_LIB keccak)
        if(NOT KECCAK_LIB)
            set(STANDALONE_KECCAK 1)
        endif()
        
        # selection of specialized compilation units differing between ref and opt implementations.
        option(AVX2_OPTIMIZED "Use the AVX2 Optimized Implementation. 
        Else the Reference Implementation will be used." {avx2_optimized_option})
        
        message(".....Checking AVX2_OPTIMIZED:  " ${{AVX2_OPTIMIZED}})
        
        #set(BASE_DIR  ../Optimized_Implementation) 
        set(BASE_DIR  ../)  
        set(HEADERS
                ${{BASE_DIR}}/include/api.h
                ${{BASE_DIR}}/include/codes.h
                ${{BASE_DIR}}/include/fips202.h
                ${{BASE_DIR}}/include/fq_arith.h
                ${{BASE_DIR}}/include/keccakf1600.h
                ${{BASE_DIR}}/include/LESS.h
                ${{BASE_DIR}}/include/monomial_mat.h
                ${{BASE_DIR}}/include/parameters.h
                ${{BASE_DIR}}/include/rng.h
                ${{BASE_DIR}}/include/seedtree.h
                ${{BASE_DIR}}/include/sha3.h
                ${{BASE_DIR}}/include/utils.h
                )
        
        if(STANDALONE_KECCAK)
            message(STATUS "Employing standalone SHA-3")
            set(KECCAK_EXTERNAL_LIB "")
            set(KECCAK_EXTERNAL_ENABLE "")
            list(APPEND COMMON_SOURCES ${{BASE_DIR}}/lib/keccakf1600.c)
            list(APPEND COMMON_SOURCES ${{BASE_DIR}}/lib/fips202.c)
        else()
            message(STATUS "Employing libkeccak")
            set(KECCAK_EXTERNAL_LIB keccak)
            set(KECCAK_EXTERNAL_ENABLE "-DSHA_3_LIBKECCAK")
        endif()
        
        set(SOURCES
                ${{COMMON_SOURCES}}
                ${{BASE_DIR}}/lib/codes.c
                ${{BASE_DIR}}/lib/LESS.c
                ${{BASE_DIR}}/lib/monomial.c
                ${{BASE_DIR}}/lib/rng.c
                ${{BASE_DIR}}/lib/seedtree.c
                ${{BASE_DIR}}/lib/utils.c
                ${{BASE_DIR}}/lib/sign.c
                )
        if(AVX2_OPTIMIZED)
                set(SOURCES ${{SOURCES}} ${{BASE_DIR}}/lib/avx2_table.c)
                set(HEADERS ${{HEADERS}} ${{BASE_DIR}}/include/avx2_macro.h)
                message("------------AVX2 OPT is ON")
        endif()
        
        set(BUILD build)
        set(BUILD_KEYPAIR {candidate}_keypair)
        set(BUILD_SIGN {candidate}_sign)
        
        foreach(category RANGE 1 5 2)
            if(category EQUAL 1)
                set(PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE)
            else()
                set(PARAM_TARGETS SIG_SIZE PK_SIZE)
            endif()
            foreach(optimiz_target ${{PARAM_TARGETS}})
            
                set(TARGET_BINARY_NAME {test_keypair}_${{category}}_${{optimiz_target}})  
                add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                        ./{candidate}_keypair/{test_keypair}.c)
                target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                        ${{BASE_DIR}}/include
                        ./include)'''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
                target_link_libraries(${{TARGET_BINARY_NAME}} {libs_variables} ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                
                set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
                set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                        COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
                
                
                #Test harness for crypto_sign
                set(TARGET_BINARY_NAME {test_sign}_${{category}}_${{optimiz_target}})
                add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                        ./{candidate}_sign/{test_sign}.c)   
                target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                        ${{BASE_DIR}}/include
                        ./include)'''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
                target_link_libraries(${{TARGET_BINARY_NAME}} {libs_variables} ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                
                set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}}) 
                set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                        COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}}")
                
                #endforeach(t_harness)
            endforeach(optimiz_target)
        endforeach(category)
        '''
    with open(path_to_cmakelists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content))


# ========================== FULEECA ========================================
# [TODO]
def makefile_fuleeca(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    fuleeca_level = subfolder[-1]
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    message = ''
    if implementation_type == 'ref':
        message = '# Same as Optimized implementation'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        {message}
        CC ?= /usr/bin/cc
        BASE_DIR = ../../{subfolder}
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        CFLAGS += -std=c11 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
          -Wshadow -Wpointer-arith -Wreturn-local-addr -O3 -mtune=native -march=native
        NISTFLAGS += -Wno-unused-result -O3
        
        SOURCES = $(BASE_DIR)/sign.c $(BASE_DIR)/poly.c $(BASE_DIR)/coeff.c $(BASE_DIR)/utils.c $(BASE_DIR)/encode.c
        HEADERS = $(BASE_DIR)/config.h $(BASE_DIR)/params.h $(BASE_DIR)/api.h $(BASE_DIR)/sign.h $(BASE_DIR)/poly.h\
        $(BASE_DIR)/coeff.h $(BASE_DIR)/utils.h $(BASE_DIR)/encode.h
        KECCAK_SOURCES = $(SOURCES) $(BASE_DIR)/fips202.c
        KECCAK_HEADERS = $(HEADERS) $(BASE_DIR)/fips202.h
        
        
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        CFLAGS += $(TOOL_FLAGS)
          
        .PHONY: all shared
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        shared: \
        fuleeca{fuleeca_level}_ref.so \
        fuleeca_fips202_ref.so \
        
        fuleeca_fips202_ref.so: fips202.c fips202.h
        \t$(CC) -shared -fPIC $(CFLAGS) -o $@ $<

        fuleeca{fuleeca_level}_ref.so: $(SOURCES) $(HEADERS)
        \t$(CC) -shared -fPIC $(CFLAGS) -DLEESIGN_MODE={fuleeca_level} -o $@ $(SOURCES)
        
        
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/rng.c $(BASE_DIR)/rng.h $(KECCAK_SOURCES) \
         $(KECCAK_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(TOOL_FLAGS) $(NISTFLAGS) -o $(BUILD)/$@  $< $(BASE_DIR)/rng.c $(KECCAK_SOURCES) $(LDFLAGS) -lcrypto  $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(BASE_DIR)/rng.c $(BASE_DIR)/rng.h $(KECCAK_SOURCES) \
         $(KECCAK_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(TOOL_FLAGS) $(NISTFLAGS) -o $(BUILD)/$@  $< $(BASE_DIR)/rng.c $(KECCAK_SOURCES) $(LDFLAGS) -lcrypto  $(TOOL_LIBS)
        
        
        clean:
        \trm -f $(BASE_DIR)/*.o $(BASE_DIR)/*.i  $(BASE_DIR)/*.s
        \trm -f $(BASE_DIR)/fuleeca{fuleeca_level}_ref.so
        \trm -f $(BASE_DIR)/fuleeca_fips202_ref.so
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ============================= MEDS =====================================
def makefile_meds(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    message = ''
    if implementation_type == 'ref':
        message = '# Same as Optimized implementation'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/meds.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        
        SHELL := /bin/bash
        {message}
        LIBS = -lssl -lcrypto
        CC := gcc
        
        BASE_DIR = ../../{subfolder}
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_FLAGS = {tool_flags}
        TOOL_LIBS = {tool_libs}
        
        ifdef DEBUG
        CFLAGS := -g -Wall -DDEBUG
        OBJDIR := debug
        else
        CFLAGS := -O3 -Wall
        OBJDIR := $(BUILD)
        endif
        
        ifdef LOG
        CFLAGS += -DDEBUG
        endif
        
        CFLAGS += -I$(OBJDIR) -INIST
        
        SOURCES  = $(filter-out  $(BASE_DIR)/PQCgenKAT_sign.c $(BASE_DIR)/test.c $(BASE_DIR)/bench.c ,$(wildcard $(BASE_DIR)/*.c))
        HEADERS = $(wildcard *.h)
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        %.o: %.c
        \t$(CC) $(CFLAGS) -c -o $@ $<
        
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(SOURCES)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) -o $(BUILD)/$@ $(EXECUTABLE_KEYPAIR).c $(SOURCES) $(LIBS)  $(TOOL_LIBS) $(TOOL_FLAGS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(SOURCES)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) -o $(BUILD)/$@ $(EXECUTABLE_SIGN).c $(SOURCES) $(LIBS)  $(TOOL_LIBS) $(TOOL_FLAGS)
        
        
        .PHONY: clean
        
        clean:
        \trm -f $(BASE_DIR)/*.o
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== WAVE ======================================
def makefile_wave(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    message = ''
    if implementation_type == 'ref':
        message = '# Same as Optimized implementation'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        {message}
        CC=gcc
        BASE_DIR = ../../{subfolder}
        CFLAGS=-I. -O3 -Wall -march=native -I$(BASE_DIR)
        LDFLAGS=-lcrypto
        
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        OBJS=$(BASE_DIR)/api.o $(BASE_DIR)/fq_arithmetic/mf3.o $(BASE_DIR)/fq_arithmetic/vf2.o\
        $(BASE_DIR)/fq_arithmetic/vf3.o $(BASE_DIR)/keygen.o $(BASE_DIR)/prng/fips202.o\
        $(BASE_DIR)/sign.o $(BASE_DIR)/util/bitstream.o $(BASE_DIR)/util/compress.o\
        $(BASE_DIR)/util/djbsort_portable.o $(BASE_DIR)/util/gauss.o $(BASE_DIR)/util/hash.o\
        $(BASE_DIR)/util/mf3permut.o $(BASE_DIR)/util/tritstream.o $(BASE_DIR)/verify.o\
        $(BASE_DIR)/wave/decode.o $(BASE_DIR)/wave/randperm.o $(BASE_DIR)/wave/reject.o $(BASE_DIR)/wave/sample.o
        
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
          
        .PHONY: all
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
        $(BASE_DIR)/prng/prng-nist.o:
        \t$(CC) $(CFLAGS) -DNIST_KAT -c -o $(BASE_DIR)/prng/prng-nist.o $(BASE_DIR)/prng/prng.c
        
        $(EXECUTABLE_KEYPAIR): $(OBJS) $(BASE_DIR)/prng/prng-nist.o $(BASE_DIR)/NIST-kat/rng.o $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) $^ -o $(BUILD)/$@ $(LDFLAGS) $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(OBJS) $(BASE_DIR)/prng/prng-nist.o $(BASE_DIR)/NIST-kat/rng.o $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) $^ -o $(BUILD)/$@ $(LDFLAGS) $(TOOL_LIBS)
        
        clean:
        \t-rm $(OBJS) $(BASE_DIR)/prng/prng.o $(BASE_DIR)/prng/prng-nist.o $(BASE_DIR)/NIST-kat/rng.o    
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =============================== LATTICE ======================================
# ==============================================================================
# ========================== EAGLESIGN ========================================
def makefile_eaglesign(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    eagle_sign_level = subfolder[-1]
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    avx2_flag = ''
    if implementation_type == 'opt':
        avx2_flag = '-mavx2'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC ?= /usr/bin/cc
        BASE_DIR = ../../{subfolder}
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        CFLAGS += {avx2_flag}
        NISTFLAGS += {avx2_flag}
        
        
        SOURCES = $(BASE_DIR)/sign.c $(BASE_DIR)/packing.c $(BASE_DIR)/polyvec.c $(BASE_DIR)/poly.c $(BASE_DIR)/ntt.c \
         $(BASE_DIR)/reduce.c $(BASE_DIR)/polymatrix.c
        HEADERS = $(BASE_DIR)/config.h $(BASE_DIR)/params.h $(BASE_DIR)/api.h $(BASE_DIR)/sign.h $(BASE_DIR)/packing.h \
         $(BASE_DIR)/polymatrix.h $(BASE_DIR)/polyvec.h $(BASE_DIR)/poly.h $(BASE_DIR)/ntt.h \
          $(BASE_DIR)/reduce.h $(BASE_DIR)/symmetric.h $(BASE_DIR)/randombytes.h
        KECCAK_SOURCES = $(SOURCES) $(BASE_DIR)/fips202.c $(BASE_DIR)/symmetric-shake.c
        KECCAK_HEADERS = $(HEADERS) $(BASE_DIR)/fips202.h
            
        
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
          
        .PHONY: all shared
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        shared: \
        \tlibpq_eaglesign{eagle_sign_level}_ref.so \
        \tlibpq_fips202_ref.so \
        \tlibpq_aes256ctr_ref.so \
        
        
        libpq_fips202_ref.so: $(BASE_DIR)/fips202.c $(BASE_DIR)/fips202.h
        \t$(CC) -shared -fPIC $(CFLAGS) -o $@ $<

        libpq_aes256ctr_ref.so: $(BASE_DIR)/aes256ctr.c $(BASE_DIR)/aes256ctr.h
        \t$(CC) -shared -fPIC $(CFLAGS) -o $@ $<
        
        libpq_eaglesign{eagle_sign_level}_ref.so: $(SOURCES) $(HEADERS) $(BASE_DIR)/symmetric-shake.c
        \t$(CC) -shared -fPIC $(CFLAGS) -DEAGLESIGN_MODE={eagle_sign_level} \
        \t -o $@ $(SOURCES) $(BASE_DIR)/symmetric-shake.c
        
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/rng.c $(KECCAK_SOURCES) $(KECCAK_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(TOOL_FLAGS) $(NISTFLAGS) -DEAGLESIGN_MODE={eagle_sign_level} -o $(BUILD)/$@  $< $(BASE_DIR)/rng.c \
         $(KECCAK_SOURCES) -lcrypto  $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(BASE_DIR)/rng.c $(KECCAK_SOURCES) $(KECCAK_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(TOOL_FLAGS) $(NISTFLAGS) -DEAGLESIGN_MODE={eagle_sign_level} -o $(BUILD)/$@  $< $(BASE_DIR)/rng.c \
         $(KECCAK_SOURCES) -lcrypto  $(TOOL_LIBS)
        
        
        clean:
        \trm -f $(BASE_DIR)/*.o
        \trm -f $(BASE_DIR)/libpq_eaglesign{eagle_sign_level}_ref.so
        \trm -f $(BASE_DIR)/libpq_fips202_ref.so
        \trm -f $(BASE_DIR)/libpq_aes256ctr_ref.so
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ========================== EHTV3V4 ========================================
def makefile_ehtv3v4(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC ?= /usr/bin/cc
        BASE_DIR = ../../{subfolder}
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        
        CFLAGS = -g -O3 -std=c99
        LDFLAGS = -static-libgcc -lssl -lcrypto -lm

        HEADERS = $(wildcard $(BASE_DIR)/*.h)
        SOURCES = $(filter-out  $(BASE_DIR)/PQCgenKAT_sign.c, $(wildcard $(BASE_DIR)/*.c))
        
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
          
        .PHONY: all
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(HEADERS) $(SOURCES) 
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(TOOL_FLAGS) $(CFLAGS) -o $(BUILD)/$@ $<  $(SOURCES) $(LDFLAGS)  $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(HEADERS) $(SOURCES) 
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(TOOL_FLAGS) $(CFLAGS) -o $(BUILD)/$@ $< $(SOURCES) $(LDFLAGS)  $(TOOL_LIBS)
        
        
        clean:
        \trm -f $(BASE_DIR)/*.o
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ===============================  SQUIRRELS ===================================
def squirrels_level(subfolder):
    subfolder_split = subfolder.split("-")
    level_roman_digest = subfolder_split[-1]
    if level_roman_digest == "I":
        level = 1
    elif level_roman_digest == "II":
        level = 2
    elif level_roman_digest == "III":
        level = 3
    elif level_roman_digest == "IV":
        level = 4
    else:
        level = 5
    return level


def makefile_squirrels(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    level = squirrels_level(subfolder)
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        .POSIX:
        NIST_LEVEL?={level}
        BASE_DIR = ../../{subfolder}
        
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/nist.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        .POSIX:
    
        NIST_LEVEL?={level}
        
        BASE_DIR = ../../{subfolder}
        CC = gcc
        CFLAGS = -W -Wall -O3 -march=native -I../../../lib/build/mpfr/include -I../../../lib/build/mpfr/include\
         -I../../../lib/build/gmp/include -I../../../lib/build/flint/include/flint \
         -I../../../lib/build/fplll/include -DSQUIRRELS_LEVEL=$(NIST_LEVEL)
        LD = gcc -v
        LDFLAGS = 
        
        LIBSRPATH = '$$ORIGIN'../../../../../lib/build
        LIBS = -lm \
        \t-L../../../lib/build/mpfr/lib -Wl,-rpath,$(LIBSRPATH)/mpfr/lib -lmpfr \
        \t-L../../../lib/build/gmp/lib -Wl,-rpath,$(LIBSRPATH)/gmp/lib -lgmp \
        \t-L../../../lib/build/flint/lib -Wl,-rpath,$(LIBSRPATH)/flint/lib -lflint \
        \t-L../../../lib/build/fplll/lib -Wl,-rpath,$(LIBSRPATH)/fplll/lib -lfplll \
        \t-lstdc++
        
        OBJ = $(BIN)/codec.o $(BIN)/common.o $(BIN)/keygen_lll.o \
        $(BIN)/keygen.o  $(BIN)/minors.o $(BIN)/nist.o $(BIN)/normaldist.o \
        $(BIN)/param.o $(BIN)/sampler.o $(BIN)/shake.o $(BIN)/sign.o \
        $(BIN)/vector.o
        
        
        HEADERS = $(BASE_DIR)/api.h $(BASE_DIR)/fpr.h $(BASE_DIR)/inner.h $(BASE_DIR)/param.h
        RNG_HEADER = ../../../KAT/generator/katrng.h
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign 
        BIN			    = $(BUILD)/bin
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        all: $(BASE_DIR)/lib build_folders $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        $(BASE_DIR)/lib:
        \tmake -C ../../../lib 
        
        build_folders:
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BIN)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN)
        
        clean:
        \t-rm -f  $(BIN) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
       
        $(BIN)/codec.o: $(BASE_DIR)/codec.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/codec.o $(BASE_DIR)/codec.c
        
        $(BIN)/common.o: $(BASE_DIR)/common.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/common.o $(BASE_DIR)/common.c
        
        $(BIN)/keygen_lll.o: $(BASE_DIR)/keygen_lll.cpp $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/keygen_lll.o $(BASE_DIR)/keygen_lll.cpp
        
        $(BIN)/keygen.o: $(BASE_DIR)/keygen.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/keygen.o $(BASE_DIR)/keygen.c
        
        $(BIN)/minors.o: $(BASE_DIR)/minors.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/minors.o $(BASE_DIR)/minors.c
        
        $(BIN)/normaldist.o: $(BASE_DIR)/normaldist.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/normaldist.o $(BASE_DIR)/normaldist.c
        
        $(BIN)/param.o: $(BASE_DIR)/param.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/param.o $(BASE_DIR)/param.c
        
        $(BIN)/sampler.o: $(BASE_DIR)/sampler.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/sampler.o $(BASE_DIR)/sampler.c
        
        $(BIN)/shake.o: $(BASE_DIR)/shake.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/shake.o $(BASE_DIR)/shake.c
        
        $(BIN)/sign.o: $(BASE_DIR)/sign.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/sign.o $(BASE_DIR)/sign.c
        
        $(BIN)/vector.o: $(BASE_DIR)/vector.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/vector.o $(BASE_DIR)/vector.c
        
        $(BIN)/nist.o: $(BASE_DIR)/nist.c $(HEADERS)
        \t$(CC) $(CFLAGS) -c -o $(BIN)/nist.o $(BASE_DIR)/nist.c
        
        $(BIN)/katrng.o: ../../../KAT/generator/katrng.c $(BASE_DIR)/api.h $(RNG_HEADER)
        \t$(CC) $(CFLAGS) -I . -c -o $(BIN)/katrng.o ../../../KAT/generator/katrng.c
        
        
        $(BIN)/{test_keypair}.o: $(EXECUTABLE_KEYPAIR).c $(HEADERS) $(RNG_HEADER)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -I .  -c -o $@ $(EXECUTABLE_KEYPAIR).c
        
        $(BIN)/{test_sign}.o: $(EXECUTABLE_SIGN).c $(HEADERS) $(RNG_HEADER)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -I .  -c -o $@ $(EXECUTABLE_SIGN).c

        $(EXECUTABLE_KEYPAIR): $(BIN)/{test_keypair}.o $(BIN)/katrng.o  $(OBJ)
        \t$(CC) $(LDFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_KEYPAIR) $(BIN)/{test_keypair}.o $(BIN)/katrng.o $(OBJ)  $(LIBS) $(TOOL_LIBS)

        $(EXECUTABLE_SIGN): $(BIN)/{test_sign}.o $(BIN)/katrng.o  $(OBJ)
        \t$(CC) $(LDFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_SIGN) $(BIN)/{test_sign}.o $(BIN)/katrng.o $(OBJ)  $(LIBS) $(TOOL_LIBS)
        
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =============================== HAETAE ===================================
def cmake_haetae(path_to_cmakelist, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    cmakelists = f'{path_to_cmakelist}/CMakeLists.txt'
    add_src_files = ''
    add_cflags = ''
    add_fips_src_files = ''
    ntt_src = '${BASE_DIR}/src/ntt.c'
    if implementation_type == 'opt':
        ntt_src = '${BASE_DIR}/src/ntt.S'
        add_src_files = f'''
        ${{BASE_DIR}}/src/consts.c
        ${{BASE_DIR}}/src/invntt.S
        ${{BASE_DIR}}/src/pointwise.S
        ${{BASE_DIR}}/src/shuffle.S
        '''
        add_cflags = '-mavx2'
        add_fips_src_files = '${BASE_DIR}/src/fips202x4.c ${BASE_DIR}/src/f1600x4.S'

    cmake_file_content = ''
    target_link_opt_block = ''
    link_flag = ''
    if tool_flags:
        if '-static ' in tool_flags or ' -static' in tool_flags:
            link_flag = '-static'
    libs_str = ""
    # tool_libs = tool_libs.replace("-lm", "")
    # tool_libs = tool_libs.strip()
    libs_list = []
    if tool_libs:
        libs_str = tool_libs.replace("-l", "")
        libs_list = libs_str.split()
    if tool_name == 'flowtracker':
        cmakelists = f'{path_to_cmakelist}/Makefile'
        cmake_file_content = f'''
        CC = clang
        
        BASE_DIR = ..
        
        
        INCS_DIR = $(BASE_DIR)/include
        
        
        KECCAK_EXTERNAL_ENABLE = 
        CATEGORY = 2
        
        
        INCS = $(wildcard $(BASE_DIR)/include/*.h)
        SRC  = $(filter-out  $(BASE_DIR)/src/sign.c, $(wildcard $(BASE_DIR)/src/*.c))
        SRC += $(wildcard $(BASE_DIR)/include/*.S)
        
        SIGN = $(BASE_DIR)/src/sign.c
        
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        cmake_file_content = f'''
        cmake_minimum_required(VERSION 3.16)
        project({subfolder} LANGUAGES ASM C CXX) # CXX for the google test
        
        enable_testing() # Enables running `ctest`
        
        set(BASE_DIR ..)
        
        set(CMAKE_C_STANDARD 11)
        set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/libs/)
        set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/libs/)
        set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/bin/)
        set(EXECUTABLE_OUTPUT_PATH ${{CMAKE_BINARY_DIR}}/bin/)
        set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
        
        set(HAETAE_SRCS
          {add_src_files}
          {ntt_src}
          ${{BASE_DIR}}/src/poly.c
          ${{BASE_DIR}}/src/fft.c
          ${{BASE_DIR}}/src/reduce.c
          ${{BASE_DIR}}/src/polyvec.c
          ${{BASE_DIR}}/src/polymat.c
          ${{BASE_DIR}}/src/polyfix.c
          ${{BASE_DIR}}/src/decompose.c
          ${{BASE_DIR}}/src/sampler.c
          ${{BASE_DIR}}/src/packing.c
          ${{BASE_DIR}}/src/sign.c
          ${{BASE_DIR}}/src/fixpoint.c
          ${{BASE_DIR}}/src/encoding.c
        )
        
        set(HAETAE_FIPS202_SRCS
          ${{HAETAE_SRCS}}
          ${{BASE_DIR}}/src/symmetric-shake.c
        )
        set(FIPS202_SRCS ${{BASE_DIR}}/src/fips202.c {add_fips_src_files})
        
        if(MSVC)
          set(C_FLAGS /nologo /O2 /W4 /wd4146 /wd4244)
        else()
          set(C_FLAGS -O3 -fomit-frame-pointer {add_cflags} -Wall -Wextra -Wpedantic)
        endif()
        
        find_package(OpenSSL REQUIRED)
        '''
        find_libs_block = ''
        libs_variables = ''
        for lib in libs_list:
            lib_variable = lib.upper()
            lib_variable = f'{lib_variable}_LIB'
            l_var = f'{lib_variable}'
            l_var = f'{{{l_var}}}'
            libs_variables += f' ${l_var}'
            find_libs_block += f'''
            find_library({lib_variable} {lib})
            if(NOT {lib_variable})
            \tmessage("{lib} library not found")
            endif()
            '''
        if libs_list:
            cmake_file_content += f'{find_libs_block}'
        cmake_file_content += f'''
        include_directories(${{BASE_DIR}}/include)
        include_directories(${{BASE_DIR}}/api)
        link_directories(${{BASE_DIR}}/libs)
        
        add_library(fips202 SHARED ${{FIPS202_SRCS}})
        target_compile_options(fips202 PRIVATE -O3 {add_cflags} -fomit-frame-pointer -fPIC)
        add_library(RNG SHARED ${{PROJECT_SOURCE_DIR}}/${{BASE_DIR}}/src/randombytes.c)
        target_compile_options(RNG PRIVATE -O3 -fomit-frame-pointer -fPIC)
        target_link_libraries(RNG PUBLIC OpenSSL::Crypto)
        
        
        # HAETAE 2 SHAKE ONLY
        set(LIB_NAME2 ${{PROJECT_NAME}}2)
        add_library(${{LIB_NAME2}} SHARED ${{HAETAE_FIPS202_SRCS}})
        target_compile_definitions(${{LIB_NAME2}} PUBLIC HAETAE_MODE=2)
        target_compile_options(${{LIB_NAME2}} PRIVATE ${{C_FLAGS}})
        target_link_libraries(${{LIB_NAME2}} INTERFACE fips202 m)
        target_link_libraries(${{LIB_NAME2}} PUBLIC RNG)
        
        # HAETAE 3 SHAKE ONLY
        set(LIB_NAME3 ${{PROJECT_NAME}}3)
        add_library(${{LIB_NAME3}} SHARED ${{HAETAE_FIPS202_SRCS}})
        target_compile_definitions(${{LIB_NAME3}} PUBLIC HAETAE_MODE=3)
        target_compile_options(${{LIB_NAME3}} PRIVATE ${{C_FLAGS}})
        target_link_libraries(${{LIB_NAME3}} INTERFACE fips202 m)
        target_link_libraries(${{LIB_NAME3}} PUBLIC RNG)
        
        # HAETAE 5 SHAKE ONLY
        set(LIB_NAME5 ${{PROJECT_NAME}}5)
        add_library(${{LIB_NAME5}} SHARED ${{HAETAE_FIPS202_SRCS}})
        target_compile_definitions(${{LIB_NAME5}} PUBLIC HAETAE_MODE=5)
        target_compile_options(${{LIB_NAME5}} PRIVATE ${{C_FLAGS}})
        target_link_libraries(${{LIB_NAME5}} INTERFACE fips202 m)
        target_link_libraries(${{LIB_NAME5}} PUBLIC RNG)
        
        
        set(BUILD build)
        set(BUILD_KEYPAIR {candidate}_keypair)
        set(BUILD_SIGN {candidate}_sign)
        '''
        cmake_file_content += f'''
        set(CATEGORIES 2 3 5)
        foreach(category IN LISTS CATEGORIES)
            \tset(TARGET_KEYPAIR_BINARY_NAME {test_keypair}_${{category}})
            \tadd_executable(${{TARGET_KEYPAIR_BINARY_NAME}} ./{candidate}_keypair/{test_keypair}.c)
            \ttarget_link_libraries(${{TARGET_KEYPAIR_BINARY_NAME}} {libs_variables}  ${{LIB_NAME${{category}}}} OpenSSL::Crypto)
            \tset_target_properties(${{TARGET_KEYPAIR_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
        '''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
            \tset(TARGET_SIGN_BINARY_NAME {test_sign}_${{category}})
            \tadd_executable(${{TARGET_SIGN_BINARY_NAME}} ./{candidate}_sign/{test_sign}.c)
            \ttarget_link_libraries(${{TARGET_SIGN_BINARY_NAME}} {libs_variables} ${{LIB_NAME${{category}}}} OpenSSL::Crypto)
            \tset_target_properties(${{TARGET_SIGN_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}})
            '''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
        endforeach()
        '''
    with open(cmakelists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content))


# =========================== HAWK ============================================
def makefile_hawk(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/api.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC = c99
        CFLAGS = -Wall -Wextra -Wshadow -Wundef -O2
        LD = $(CC)
        LDFLAGS =
        LIBS =
        
        
        CC = c99
        CFLAGS = -Wall -Wextra -Wshadow -Wundef -O2
        LD = $(CC)
        LDFLAGS =
        LIBS =
        
        
        BASE_DIR = ../../{subfolder}
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        CFLAGS += $(TOOL_FLAGS) 
        
        OBJCORE = $(BASE_DIR)/hawk_kgen.o $(BASE_DIR)/hawk_sign.o $(BASE_DIR)/hawk_vrfy.o $(BASE_DIR)/ng_fxp.o\
         $(BASE_DIR)/ng_hawk.o $(BASE_DIR)/ng_mp31.o $(BASE_DIR)/ng_ntru.o $(BASE_DIR)/ng_poly.o \
         $(BASE_DIR)/ng_zint31.o $(BASE_DIR)/sha3.o
        HEAD = $(BASE_DIR)/hawk.h $(BASE_DIR)/hawk_inner.h $(BASE_DIR)/hawk_config.h $(BASE_DIR)/sha3.h
        NG_HEAD = $(BASE_DIR)/ng_config.h $(BASE_DIR)/ng_inner.h $(BASE_DIR)/sha3.h
        OBJAPI = $(BASE_DIR)/api.o
        OBJEXTRA_KEYPAIR = $(BASE_DIR)/rng.o $(EXECUTABLE_KEYPAIR).o
        OBJEXTRA_SIGN = $(BASE_DIR)/rng.o $(EXECUTABLE_SIGN).o
       
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        $(BASE_DIR)/hawk_kgen.o: $(BASE_DIR)/hawk_kgen.c $(HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/hawk_kgen.o $(BASE_DIR)/hawk_kgen.c
    
        $(BASE_DIR)/hawk_sign.o: $(BASE_DIR)/hawk_sign.c $(HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/hawk_sign.o $(BASE_DIR)/hawk_sign.c
        
        $(BASE_DIR)/hawk_vrfy.o: $(BASE_DIR)/hawk_vrfy.c $(HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/hawk_vrfy.o $(BASE_DIR)/hawk_vrfy.c
        
        $(BASE_DIR)/ng_fxp.o: $(BASE_DIR)/ng_fxp.c $(NG_HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_fxp.o $(BASE_DIR)/ng_fxp.c
        
        $(BASE_DIR)/ng_hawk.o: $(BASE_DIR)/ng_hawk.c $(NG_HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_hawk.o $(BASE_DIR)/ng_hawk.c
        
        $(BASE_DIR)/ng_mp31.o: $(BASE_DIR)/ng_mp31.c $(NG_HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_mp31.o $(BASE_DIR)/ng_mp31.c
        
        $(BASE_DIR)/ng_ntru.o: $(BASE_DIR)/ng_ntru.c $(NG_HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_ntru.o $(BASE_DIR)/ng_ntru.c
        
        $(BASE_DIR)/ng_poly.o: $(BASE_DIR)/ng_poly.c $(NG_HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_poly.o $(BASE_DIR)/ng_poly.c
        
        $(BASE_DIR)/ng_zint31.o: $(BASE_DIR)/ng_zint31.c $(NG_HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_zint31.o $(BASE_DIR)/ng_zint31.c
        
        $(BASE_DIR)/sha3.o: $(BASE_DIR)/sha3.c $(NG_HEAD)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/sha3.o $(BASE_DIR)/sha3.c
        
        $(BASE_DIR)/api.o: $(BASE_DIR)/api.c $(BASE_DIR)/api.h $(BASE_DIR)/hawk.h $(BASE_DIR)/sha3.h
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/api.o $(BASE_DIR)/api.c
    
        $(BASE_DIR)/rng.o: $(BASE_DIR)/rng.c $(BASE_DIR)/rng.h
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/rng.o $(BASE_DIR)/rng.c
        
        $(EXECUTABLE_KEYPAIR).o: $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
        \t$(CC) $(CFLAGS) -c -o $(EXECUTABLE_KEYPAIR).o $(EXECUTABLE_KEYPAIR).c
            
        $(EXECUTABLE_SIGN).o: $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
        \t$(CC) $(CFLAGS) -c -o $(EXECUTABLE_SIGN).o $(EXECUTABLE_SIGN).c
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
          
        $(EXECUTABLE_KEYPAIR): $(OBJCORE) $(OBJAPI) $(OBJEXTRA_KEYPAIR)
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(LD) $(LDFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_KEYPAIR) $(OBJCORE)\
         $(OBJAPI) $(OBJEXTRA_KEYPAIR) $(LIBS) $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(OBJCORE) $(OBJAPI) $(OBJEXTRA_SIGN)
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_SIGN)
        \t$(LD) $(LDFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_SIGN) $(OBJCORE)\
         $(OBJAPI) $(OBJEXTRA_SIGN) $(LIBS) $(TOOL_LIBS)
            
        clean:
        \t-rm -f $(OBJCORE) $(OBJAPI) $(OBJEXTRA_KEYPAIR) $(OBJEXTRA_SIGN) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ========================= HUFU ====================================
def makefile_hufu(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    specific_filter_out = ''
    if implementation_type == 'add':
        specific_filter_out = '$(BASE_DIR)/main.c'
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:

        makefile_content = f'''
        
        CC=clang
        ifeq "$(CC)" "gcc"
            COMPILER=gcc
        else ifeq "$(CC)" "clang"
            COMPILER=clang
        endif
        
        ARCHITECTURE=_AMD64_
        
        CC=/usr/bin/gcc
        CFLAGS= -mavx2 -mbmi2 -mpopcnt -O3 -std=gnu11 -march=native -Wextra -DNIX -mfpmath=sse -msse2 -ffp-contract=off
        LDFLAGS= -lm -lssl -lcrypto
        
        BASE_DIR = ../../{subfolder}
        
        SOURCES  = $(filter-out {specific_filter_out} $(BASE_DIR)/PQCgenKAT_sign.c ,$(wildcard $(BASE_DIR)/*.c))
        SOURCES += $(wildcard $(BASE_DIR)/aes/*.c) $(BASE_DIR)/random/random.c\
        $(wildcard $(BASE_DIR)/sha3/*.c) $(BASE_DIR)/rANS/compress.c\
        $(wildcard $(BASE_DIR)/normaldist/*.c) $(wildcard $(BASE_DIR)/sampling/*.c)
        
        HEADERS = $(wildcard $(BASE_DIR)/*.h) $(wildcard $(BASE_DIR)/aes/*.h) \
            $(BASE_DIR)/random/random.h $(wildcard $(BASE_DIR)/sha3/*.h) \
            $(BASE_DIR)/rANS/compress.h \
            $(wildcard $(BASE_DIR)/normaldist/*.h) $(wildcard $(BASE_DIR)/sampling/*.h)
        
                
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_FLAGS = {tool_flags}
        TOOL_LIBS = {tool_libs}
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        %.o: %.c
        \t$(CC) $(CFLAGS) -c -o $@ $<
            
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(SOURCES)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) -o $(BUILD)/$@ $(EXECUTABLE_KEYPAIR).c $(SOURCES) $(LDFLAGS)  $(TOOL_LIBS) $(TOOL_FLAGS)
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(SOURCES)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) -o $(BUILD)/$@ $(EXECUTABLE_SIGN).c $(SOURCES) $(LDFLAGS)  $(TOOL_LIBS) $(TOOL_FLAGS)
        
        
        .PHONY: clean
          
        clean:
        \trm -f $(BASE_DIR)/*.o 
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =========================== RACCOON =============================
def sh_build_raccoon(path_to_sh_script_folder, sh_script, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    opt_level = ''
    if implementation_type == 'opt':
        opt_level = '-O2'
    if tool_name.lower() == 'ctgrind':
        tool_flags = tool_flags.replace('-std=c99', '')
    if tool_name.lower() == 'dudect':
        tool_flags = tool_flags.replace('-std=c11', '')
    executable_keypair = f'{candidate}_keypair/{test_keypair}'
    executable_sign = f'{candidate}_sign/{test_sign}'
    path_to_sh_script = f'{path_to_sh_script_folder}/{sh_script}.sh'
    base_dir = f'../../{subfolder}'
    build = f'build'
    build_keypair = f'{build}/{candidate}_keypair'
    build_sign = f'{build}/{candidate}_sign'
    block_binary_files = f'''
    #!/bin/bash
    SRC=$(find {base_dir}/* -name "*.c" ! -name  PQCgenKAT_sign.c)
    mkdir -p {build}
    mkdir -p {build_keypair}
    gcc -o {build}/{executable_keypair} -Wall {opt_level} {tool_flags} {executable_keypair}.c\
    $SRC -lcrypto {tool_libs}
    
    mkdir -p {build}
    mkdir -p {build_sign}
    gcc -o {build}/{executable_sign} -Wall {opt_level} {tool_flags} {executable_sign}.c \
    $SRC -lcrypto {tool_libs}
    '''
    with open(path_to_sh_script, "w") as mfile:
        mfile.write(textwrap.dedent(block_binary_files))


def makefile_raccoon(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC = clang
    
    BASE_DIR = ../../{subfolder}
    
    SIGN = $(BASE_DIR)/racc_api.c
    
    INCS_DIR = $(BASE_DIR)
    
    BUILD			= build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    
    EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
    EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
    EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
    EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
    
    all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
     
    
    
    $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
    
    $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
    \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
    
    $(EXECUTABLE_SIGN_BC): $(SIGN)
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
    
    $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
    \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
        
    .PHONY: clean
      
    clean:
    \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
    \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def generic_init_compile_with_sh(tools_list, signature_type,
                                 candidate, optimized_imp_folder,
                                 instance_folders_list, rel_path_to_api,
                                 rel_path_to_sign, rel_path_to_rng,
                                 add_includes, build_folder, sh_script,
                                 rng_outside_instance_folder="no",
                                 implementation_type='opt'):
    path_to_optimized_implementation_folder = signature_type+'/'+candidate+'/'+optimized_imp_folder
    if not instance_folders_list:
        gen_funct.generic_initialize_nist_candidate(tools_list, signature_type,
                                                    candidate, optimized_imp_folder,
                                                    instance_folders_list, rel_path_to_api,
                                                    rel_path_to_sign, rel_path_to_rng,
                                                    add_includes, rng_outside_instance_folder)
        instance = '""'
        for tool_type in tools_list:
            path_to_build_folder = f'{path_to_optimized_implementation_folder}/{tool_type}'
            if not os.path.isdir(path_to_build_folder):
                cmd = ["mkdir", "-p", path_to_build_folder]
                subprocess.call(cmd, stdin=sys.stdin)
            cwd = os.getcwd()
            if tool_type.strip() == "flowtracker":
                makefile_raccoon(path_to_build_folder, instance, tool_type, candidate)
                os.chdir(path_to_build_folder)
                cmd = ["make"]
                subprocess.call(cmd, stdin=sys.stdin)
            else:
                os.chdir(path_to_build_folder)
                sh_build_raccoon(path_to_build_folder, sh_script, instance, tool_type, candidate, implementation_type)

                cmd_str = f"sudo chmod u+x ./{sh_script}.sh"
                cmd = cmd_str.split()
                subprocess.call(cmd, stdin=sys.stdin)
                cmd_str = f"./{sh_script}.sh"
                cmd = cmd_str.split()
                subprocess.call(cmd, stdin=sys.stdin, shell=True)
            os.chdir(cwd)
    else:
        for instance in instance_folders_list:
            gen_funct.generic_initialize_nist_candidate(tools_list, signature_type,
                                                        candidate, optimized_imp_folder,
                                                        instance_folders_list, rel_path_to_api,
                                                        rel_path_to_sign, rel_path_to_rng,
                                                        add_includes, rng_outside_instance_folder)
            for tool_type in tools_list:
                path_to_build_folder = f'{path_to_optimized_implementation_folder}/{tool_type}/{instance}'
                if not os.path.isdir(path_to_build_folder):
                    cmd = ["mkdir", "-p", path_to_build_folder]
                    subprocess.call(cmd, stdin=sys.stdin)
                cwd = os.getcwd()
                if tool_type.strip() == "flowtracker":
                    makefile_raccoon(path_to_build_folder, instance, tool_type, candidate)
                    os.chdir(path_to_build_folder)
                    cmd = ["make"]
                    subprocess.call(cmd, stdin=sys.stdin)
                else:
                    sh_build_raccoon(path_to_build_folder, sh_script, instance,
                                     tool_type, candidate, implementation_type)
                    os.chdir(path_to_build_folder)
                    cmd_str = f"sudo chmod u+x ./{sh_script}.sh"
                    cmd = cmd_str.split()
                    subprocess.call(cmd, stdin=sys.stdin)
                    cmd_str = f"./{sh_script}.sh"
                    cmd = cmd_str.split()
                    subprocess.call(cmd, stdin=sys.stdin, shell=True)
                    os.chdir(cwd)


# ================================ MULTIVARIATE =====================================
# ===================================================================================
# =================================== BISCUIT =======================================
def makefile_biscuit(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    sha3_target = 'generic64'
    biscuit_file = 'biscuit.c'
    uintx_bitsize = '64'
    target_arch = ''
    if implementation_type == 'ref':
        biscuit_file = 'biscuit_mq_ref.c'
        uintx_bitsize = '8'
    if implementation_type == 'add':
        sha3_target = 'AVX2'
        uintx_bitsize = '256'
        target_arch = '-msse2'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC=gcc
        BASE_DIR = ../../{subfolder}
        
        SHA3_TARGET = {sha3_target}
        UINTX_BITSIZE = {uintx_bitsize}
        BISCUIT_FILE = {biscuit_file}
        TARGET_ARCH = {target_arch}

        SHA3_ASM = $(wildcard $(BASE_DIR)/sha3/*.s) $(wildcard $(BASE_DIR)/sha3/$(SHA3_TARGET)/*.s)
        SHA3_SRC = $(wildcard $(BASE_DIR)/sha3/*.c) $(wildcard $(BASE_DIR)/sha3/$(SHA3_TARGET)/*.c)
        
        
        CFLAGS = -Wall -pedantic -Wextra -O3
        CPPFLAGS = -I$(BASE_DIR)/sha3/$(SHA3_TARGET) -DUINTX_BITSIZE=$(UINTX_BITSIZE)
        
        HDR = $(BASE_DIR)/biscuit.h $(BASE_DIR)/utils.h $(BASE_DIR)/batch_tools.h $(wildcard $(BASE_DIR)/params*.h)
        SRC = $(BASE_DIR)/$(BISCUIT_FILE) $(BASE_DIR)/utils.c $(BASE_DIR)/batch_tools.c
        OBJ = $(SRC:.c=.o) $(SHA3_SRC:.c=.o) $(SHA3_ASM:.s=.o)
        
        API_OBJ = $(BASE_DIR)/rng.o $(BASE_DIR)/api.o
        
        OBJ_KEYPAIR =  $(EXECUTABLE_KEYPAIR).o
        OBJ_SIGN =  $(EXECUTABLE_SIGN).o
        
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
            
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
          
        # EXE: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        # EXE_KP = $(BUILD)/$(EXECUTABLE_KEYPAIR)
        # EXE_SIGN = $(BUILD)/$(EXECUTABLE_SIGN)
        # EXE = $(EXE_KP) #$(EXE_SIGN)
        
        CFLAGS += $(TOOL_FLAGS)
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        # folders:
        # \tmkdir -p $(BUILD)
        # \tmkdir -p $(BUILD_KEYPAIR)
        # \tmkdir -p $(BUILD_SIGN)
        # 
        # $(EXE_KP): LDLIBS = -lcrypto $(TOOL_LIBS)
        # $(EXE_KP): folders $(EXECUTABLE_KEYPAIR).c $(API_OBJ) $(OBJ)
        
        # $(EXE_SIGN): LDLIBS = -lcrypto $(TOOL_LIBS)
        # $(EXE_sign): folders $(EXECUTABLE_SIGN).c $(API_OBJ) $(OBJ)
        
        
        $(EXECUTABLE_KEYPAIR).o: $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
        \t$(CC) $(CFLAGS) -c -o $(EXECUTABLE_KEYPAIR).o $(EXECUTABLE_KEYPAIR).c
        
        $(EXECUTABLE_SIGN).o: $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
        \t$(CC) $(CFLAGS) -c -o $(EXECUTABLE_SIGN).o $(EXECUTABLE_SIGN).c
        
         $(EXECUTABLE_KEYPAIR): $(OBJ_KEYPAIR) $(API_OBJ) $(OBJ)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(OBJ_KEYPAIR) $(API_OBJ) $(OBJ)  -lcrypto  $(TOOL_LIBS)
            
        $(EXECUTABLE_SIGN): $(OBJ_SIGN) $(API_OBJ) $(OBJ)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(OBJ_SIGN) $(API_OBJ) $(OBJ) -lcrypto  $(TOOL_LIBS)
 
                
        clean:
        \t-rm $(API_OBJ) $(OBJ) $(EXE)    
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== DME-SIGN =======================================
def makefile_dme_sign(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        BASE_DIR = ../../../{subfolder}
        
        
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
            
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
          
        .PHONY: all clean
        
        all:  build_folders $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        OBJ = $(BIN)/rng.o $(BIN)/sign.o $(BIN)/sha3.o $(BIN)/dme.o
        
        BIN = bin
        
        build_folders:
        \tmkdir -p $(BIN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN)
        
        $(BIN)/rng.o: $(BASE_DIR)/rng.c $(BASE_DIR)/rng.h
        \tgcc -c -o $@ $(BASE_DIR)/rng.c -O3
        
        $(BIN)/sign.o: $(BASE_DIR)/sign.c $(BASE_DIR)/api.h $(BASE_DIR)/sha3.h $(BASE_DIR)/dme.h $(BASE_DIR)/rng.h
        \tgcc -c -o $@ $(BASE_DIR)/sign.c -Wall -Wextra -Werror -pedantic -std=gnu99 -O3
        
        $(BIN)/sha3.o: $(BASE_DIR)/sha3.c $(BASE_DIR)/sha3.h
        \tgcc -c -o $@ $(BASE_DIR)/sha3.c -Wall -Wextra -Werror -pedantic -std=gnu99 -O3
        
        $(BIN)/dme.o: $(BASE_DIR)/dme.c $(BASE_DIR)/dme.h $(BASE_DIR)/rng.h
        \tgcc -o $(BIN)/dme.o -c $(BASE_DIR)/dme.c -Wall -Wextra -Werror -pedantic -std=gnu99 -O3
        
        
        
        $(BIN)/{test_keypair}.o: $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
        \tgcc -c -o $@ $(EXECUTABLE_KEYPAIR).c
        
        $(BIN)/{test_sign}.o: $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
        \tgcc -c -o $@ $(EXECUTABLE_SIGN).c
        
        $(EXECUTABLE_KEYPAIR): $(BIN)/{test_keypair}.o $(OBJ)
        \tgcc -o $(BUILD)/$(EXECUTABLE_KEYPAIR) $(BIN)/{test_keypair}.o $(OBJ) -Wall -Wextra -O3 -lcrypto $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(BIN)/{test_sign}.o $(OBJ)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \tgcc -o $(BUILD)/$(EXECUTABLE_SIGN) $(BIN)/{test_sign}.o $(OBJ) -Wall -Wextra -O3 -lcrypto $(TOOL_LIBS)
            
                
        clean:
        \t-rm $(OBJ) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== HPPC =======================================
def makefile_hppc(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        BASE_DIR = ../../{subfolder}
        
        LDFLAGS=-lm4ri -lflint -lgmp -lm -lstdc++ -lntl -ldl -lcrypto -pthread -lpthread -lgf2x
        THREADED=-pthread -lpthread
        OPTIMIZED=-Ofast -march=native
        DFLAGS=-DMULT_STRASSEN


        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        BIN             = bin
            
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        SOURCES=$(BASE_DIR)/rng.c $(BASE_DIR)/sign.c $(BASE_DIR)/serializer.c $(BASE_DIR)/gen.c
        HEADERS=$(BASE_DIR)/rng.h $(BASE_DIR)/serializer.h $(BASE_DIR)/gen.h $(BASE_DIR)/ntl_utils.h $(BASE_DIR)/api.h
          
        .PHONY: all clean
        
        all:  build_folders $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        build_folders:
        \tmkdir -p $(BIN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN)
        
        
        $(EXECUTABLE_KEYPAIR):
        \tg++ -c -o $(BIN)/ntl_utils.o $(BASE_DIR)/ntl_utils.cpp $(THREADED) 
        \tgcc $@.c $(HEADERS) $(SOURCES) $(BIN)/ntl_utils.o -o $(BUILD)/$@ $(LDFLAGS) $(OPTIMIZED)\
         $(THREADED) $(TOOL_FLAGS) -std=c99 $(TOOL_LIBS)
         
        $(EXECUTABLE_SIGN):
        \tg++ -c -o $(BIN)/ntl_utils.o $(BASE_DIR)/ntl_utils.cpp $(THREADED) 
        \tgcc $@.c $(HEADERS) $(SOURCES) $(BIN)/ntl_utils.o -o $(BUILD)/$@ $(LDFLAGS) $(OPTIMIZED)\
         $(THREADED) $(TOOL_FLAGS) -std=c99 $(TOOL_LIBS)
                
        clean:
        \trm -f $(BIN)/*.o >/dev/null
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== wise =======================================
def makefile_wise(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        LDFLAGS=-lflint -lgmp -lcrypto
        
        
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -I. $(LDFLAGS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -I. $(LDFLAGS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        BASE_DIR = ../../{subfolder}
        
        LDFLAGS=-lflint -lgmp -lcrypto
        OPTIMIZED=-Ofast -march=native
        DFLAGS=-DMULT_STRASSEN


        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        BIN             = bin
            
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        SOURCES=$(BASE_DIR)/rng.c $(BASE_DIR)/sign.c $(BASE_DIR)/serializer.c $(BASE_DIR)/gen.c
        HEADERS=$(BASE_DIR)/rng.h $(BASE_DIR)/serializer.h $(BASE_DIR)/gen.h $(BASE_DIR)/api.h
          
        .PHONY: all clean
        
        all:  build_folders $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        build_folders:
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN)
        
        
        $(EXECUTABLE_KEYPAIR):
        \tgcc $@.c $(HEADERS) $(SOURCES) -o $(BUILD)/$@ $(LDFLAGS) $(OPTIMIZED)\
        $(TOOL_FLAGS) -std=c99 $(TOOL_LIBS)
         
        $(EXECUTABLE_SIGN): 
        \tgcc $@.c $(HEADERS) $(SOURCES) -o $(BUILD)/$@ $(LDFLAGS) $(OPTIMIZED)\
        $(TOOL_FLAGS) -std=c99 $(TOOL_LIBS)
                
        clean:
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ================================== QR-UOV ==========================================
def qr_uov_main_makefile(path_to_tool_folder, subfolder, implementation_type='opt'):
    path_to_makefile = path_to_tool_folder+'/Makefile'
    platform = 'portable64'
    if implementation_type == 'ref':
        platform = 'ref'
    if implementation_type == 'add':
        platform = 'avx2'
    makefile_content = f'''
    platform := {platform}
    
    BASE_DIR = ..
    subdirs :={subfolder}
    
    .PHONY: all clean $(subdirs)
    
    all: $(subdirs)
    
    $(subdirs): $(BASE_DIR)/qruov_config.src
    \tmkdir -p $(BASE_DIR)/$@
    \tgrep $@ $(BASE_DIR)/qruov_config.src > $(BASE_DIR)/$@/qruov_config.txt
    \tsh -c "cd $(BASE_DIR)/$@ ; ln -s $(BASE_DIR)/$(platform)/* . || true"
    \t$(MAKE) -C $(BASE_DIR)/$@
    
    clean:
    \trm -rf $(subdirs)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def makefile_qr_uov(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    platform = 'ref'
    add_cflags = ''
    if implementation_type == 'opt':
        add_cflags = '-Wno-aggressive-loop-optimizations'
        platform = 'portable64'
    if implementation_type == 'add':
        add_cflags = '-Wno-aggressive-loop-optimizations -march=native'
        platform = 'avx2'

    makefile_content = ''
    target_link_opt_block = ''
    link_flag = ''
    if tool_flags:
        if '-static ' in tool_flags:
            link_flag = '-static'
    libs_str = ""
    if tool_libs:
        libs_str = tool_libs.replace("-l", "")
        libs_list = libs_str.split()
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        #BASE_DIR = ../../{subfolder}/{platform}
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        SRC  = $(filter-out  $(BASE_DIR)/sign.c $(BASE_DIR)/PQCgenKAT_sign.c, $(wildcard $(BASE_DIR)/*.c))
        
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/sign.c
        
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(BASE_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(BASE_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC=gcc
        CFLAGS=-O3 -fomit-frame-pointer -Wno-unused-result {add_cflags} -I. -fopenmp
        LDFLAGS=-lcrypto -Wl,-Bstatic -lcrypto -Wl,-Bdynamic -lm
        
        # BASE_DIR = ../../{subfolder}/{platform}
        BASE_DIR = ../../{subfolder}
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
       
        OBJS=$(BASE_DIR)/Fql.o $(BASE_DIR)/mgf.o  $(BASE_DIR)/qruov.o $(BASE_DIR)/rng.o \
        $(BASE_DIR)/sign.o $(BASE_DIR)/matrix.o
        
        .PHONY: all clean
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        $(EXECUTABLE_KEYPAIR): Makefile $(EXECUTABLE_KEYPAIR).c $(OBJS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t${{CC}} ${{OBJS}} ${{CFLAGS}} $(TOOL_FLAGS) ${{LDFLAGS}} $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ $(TOOL_LIBS)
    
        $(EXECUTABLE_SIGN): Makefile $(EXECUTABLE_SIGN).c $(OBJS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t${{CC}} ${{OBJS}} ${{CFLAGS}} $(TOOL_FLAGS) ${{LDFLAGS}} $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ $(TOOL_LIBS)
        
        
        clean:
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def custom_init_compile_qr_uov(custom_makefile_folder, instance_folders_list, implementation_type):
    implementation_folder = 'Optimized_Implementation'
    if implementation_type == 'ref':
        implementation_folder = 'Reference_Implementation'
    if implementation_type == 'add':
        implementation_folder = 'Alternative_Implementation'
    path_to_tool_folder = f'candidates/multivariate/qr_uov/QR_UOV/{implementation_folder}/{custom_makefile_folder}'
    if not os.path.isdir(path_to_tool_folder):
        cmd = ["mkdir", "-p", path_to_tool_folder]
        subprocess.call(cmd, stdin=sys.stdin)
    subfolders = " ".join(instance_folders_list)
    qr_uov_main_makefile(path_to_tool_folder, subfolders, implementation_type)
    cwd = os.getcwd()
    os.chdir(path_to_tool_folder)
    cmd = ["make"]
    subprocess.call(cmd, stdin=sys.stdin)
    os.chdir(cwd)
    cmd = ["rm", "-r", path_to_tool_folder]
    subprocess.call(cmd, stdin=sys.stdin)


def compile_run_qr_uov(tools_list, signature_type, candidate,
                       optimized_imp_folder, instance_folders_list,
                       rel_path_to_api, rel_path_to_sign, rel_path_to_rng,
                       to_compile, to_run, depth, build_folder,
                       binary_patterns, rng_outside_instance_folder="no",
                       with_core_dump="no", number_of_measurements='1e4', timeout='86400', implementation_type='opt'):
    add_includes = []
    compile_with_cmake = 'no'
    custom_folder = "custom_makefile"
    for tool in tools_list:
        custom_init_compile_qr_uov(custom_folder, instance_folders_list, implementation_type)
    gen_funct.generic_compile_run_candidate(tools_list, signature_type, candidate, optimized_imp_folder,
                                            instance_folders_list, rel_path_to_api, rel_path_to_sign,
                                            rel_path_to_rng, compile_with_cmake, add_includes, to_compile,
                                            to_run, depth, build_folder,
                                            binary_patterns,rng_outside_instance_folder, with_core_dump,
                                            None, None,number_of_measurements, timeout,
                                            implementation_type)



# ===============================  snova ==========================================
def get_snova_parameters(subfolder):
    subfolder_split = subfolder.split('-')
    snova, snova_v, snova_o, fixed_val, snova_l, key = subfolder_split
    esk_or_ssk = 0
    if key == 'ssk':
        esk_or_ssk = 1
    return snova_v, snova_o, snova_l, esk_or_ssk


def makefile_snova(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    add_snova_params = ''
    snova_turbo = ''
    if implementation_type == 'opt':
        add_snova_params = '-D TURBO=$(TURBO)'
        snova_turbo = 'TURBO = 1'
    snova_v, snova_o, snova_l, esk_or_ssk = get_snova_parameters(subfolder)
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC = gcc
        
        CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla\
         -Wpointer-arith -O3 -march=native -mtune=native
    
        BASE_DIR = ../../{subfolder}
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign 
        
        KEYPAIR_FOLDER 	= {candidate}_keypair
        SIGN_FOLDER 	= {candidate}_sign
        
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
    
        #BUILD_OUT_PATH = $(BASE_DIR)/build/
        BUILD_OUT_PATH = $(BUILD)/
        
        OLIST = $(BUILD_OUT_PATH)rng.o $(BUILD_OUT_PATH)snova.o
        
        # snova params
        SNOVA_V = {snova_v}
        SNOVA_O = {snova_o}
        SNOVA_L = {snova_l}
        SK_IS_SEED = {esk_or_ssk} # 0: sk = ssk; 1: sk = esk 
        {snova_turbo}
        CRYPTO_ALGNAME = \\"SNOVA_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L)\\"
        SNOVA_PARAMS = -D v_SNOVA=$(SNOVA_V) -D o_SNOVA=$(SNOVA_O) -D l_SNOVA=$(SNOVA_L) -D sk_is_seed=$(SK_IS_SEED) \
        -D CRYPTO_ALGNAME=$(CRYPTO_ALGNAME) {add_snova_params}
        
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        $(BUILD)/rng.o:
        \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
        
        $(BUILD)/snova.o: $(BUILD)/rng.o
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
        
        $(BUILD)/sign.o: $(BUILD)/snova.o
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
        
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o \
        $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(TOOL_FLAGS) $(OLIST) $(BUILD)/sign.o \
        $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(TOOL_LIBS)
        
        clean:
        \trm -f $(BASE_DIR)/build/*.o *.a
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ==================================  MAYO ===============================
def cmake_mayo(path_to_cmakelists_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    mayo_instance_subfolder = subfolder.split('/')[-1]
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_cmakelists = f'{path_to_cmakelists_folder}/CMakeLists.txt'
    mayo_build_type = 'avx2'
    if implementation_type == 'ref':
        mayo_build_type = 'ref'

    cmake_file_content = ''
    target_link_opt_block = ''
    link_flag = ''
    if tool_flags:
        if '-static' in tool_flags:
            link_flag = '-static'
    libs_str = ""
    libs_list = []
    if tool_libs:
        libs_str = tool_libs.replace("-l", "")
        libs_list = libs_str.split()
    if tool_name == 'flowtracker':
        path_to_cmakelists = f'{path_to_cmakelists_folder}/Makefile'
        cmake_file_content = f'''
        CC = clang
        
        BASE_DIR  = ../../..
        
        # MVARIANT_S =  MAYO_1 MAYO_2 MAYO_3 MAYO_5
        
        
        COMPILE_FLAGS = -Werror -Wextra -Wno-unused-parameter -fno-strict-aliasing -std=c99  -DENABLE_AESNI=ON
        
        INC_PLATFORM = ${{BASE_DIR}}/src/generic
        
        
        
        MVARIANT_LOWER = ${{BASE_DIR}}/{subfolder}
        SIGN = ${{MVARIANT_LOWER}}/api.c
        
        COMPILE_FLAGS += -DMAYO_VARIANT={mayo_instance_subfolder}
        
        INCS_DIR = -I $(BASE_DIR)/include -I $(INC_PLATFORM) -I $(BASE_DIR)/src/common -I $(MVARIANT_LOWER)
        
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        cmake_file_content = f'''
        cmake_minimum_required(VERSION 3.5)
        project(MAYO VERSION 1.0 LANGUAGES C CXX ASM)
        
        set(MAYO_SO_VERSION "0")
        set(CMAKE_C_STANDARD 99)
        
        option(ENABLE_STRICT "Build with strict compile options." ON)

        if(ENABLE_STRICT)
           message("Enable strict flag ON")
        endif()
        set(BASE_DIR  ../../..)
        
        
        SET(MVARIANT "{mayo_instance_subfolder}")

        include(${{BASE_DIR}}/.cmake/flags.cmake)
        include(${{BASE_DIR}}/.cmake/sanitizers.cmake)
        include(${{BASE_DIR}}/.cmake/target.cmake)
        
        set(SOURCE_FILES_COMMON_SYS 
            ${{BASE_DIR}}/src/common/randombytes_system.c 
            ${{BASE_DIR}}/src/common/aes_c.c 
            ${{BASE_DIR}}/src/common/aes128ctr.c 
            ${{BASE_DIR}}/src/common/fips202.c 
            ${{BASE_DIR}}/src/common/mem.c
        )

        add_library(mayo_common_sys ${{SOURCE_FILES_COMMON_SYS}})
        target_include_directories(mayo_common_sys PRIVATE ${{BASE_DIR}}/src/common ${{BASE_DIR}}/include)
        target_compile_options(mayo_common_sys PUBLIC ${{C_OPT_FLAGS}})
        
        
        if (ENABLE_AESNI)
            message("AES-NI enabled")
            target_compile_definitions(mayo_common_sys PUBLIC ENABLE_AESNI)
        endif()
        
        set(SOURCE_FILES_MAYO 
            ${{BASE_DIR}}/src/mayo.c 
            ${{BASE_DIR}}/src/params.c 
            ${{BASE_DIR}}/src/bitsliced_arithmetic.c
        )
        
        set(HEADER_FILES_MAYO
            ${{BASE_DIR}}/src/bitsliced_arithmetic.h
        )
        
        
        set(MAYO_BUILD_TYPE_REDEFINED {mayo_build_type})
        if (${{MAYO_BUILD_TYPE_REDEFINED}} MATCHES "avx2")
            message("avx2 implementation is chosen")
            set(INC_PLATFORM ${{BASE_DIR}}/src/AVX2)
            add_definitions(-DMAYO_AVX)
        else()
            set(INC_PLATFORM ${{BASE_DIR}}/src/generic)
        endif()
        '''
        find_libs_block = ''
        for lib in libs_list:
            lib_variable = lib.upper()
            lib_variable = f'{lib_variable}_LIB'
            find_libs_block += f'''
        find_library({lib_variable} {lib})
        if(NOT {lib_variable})
        \tmessage("{lib} library not found")
        endif()
        '''
        if libs_list:
            cmake_file_content += f'{find_libs_block}'
        cmake_file_content += f'''
        set(BUILD build)
        set(BUILD_KEYPAIR {candidate}_keypair)
        set(BUILD_SIGN {candidate}_sign)
        
        
        if (ENABLE_PARAMS_DYNAMIC)
            # mayo and libraries
            add_library(mayo ${{SOURCE_FILES_MAYO}})
            target_link_libraries(mayo PUBLIC mayo_common_sys)
            target_include_directories(mayo PUBLIC ${{BASE_DIR}}/include PRIVATE {{BASE_DIR}}/common ${{INC_PLATFORM}})
            target_compile_definitions(mayo PUBLIC ENABLE_PARAMS_DYNAMIC)

        '''
        cmake_file_content += f''' 
            # mayo_<x>_nistapi libraries
            set(SOURCE_FILES_VARIANT ${{BASE_DIR}}/src/${{MVARIANT}}/api.c)
            add_library(${{MVARIANT}}_nistapi ${{SOURCE_FILES_VARIANT}})
            target_link_libraries(${{MVARIANT}}_nistapi PRIVATE mayo)
            target_include_directories(${{MVARIANT}}_nistapi PUBLIC ${{MVARIANT}} ${{INC_PLATFORM}})
            
            # crypto_sign_keypair
            set(TARGET_KEYPAIR_BINARY_NAME {test_keypair}_${{MVARIANT}})
            add_executable(${{TARGET_KEYPAIR_BINARY_NAME}} {candidate}_keypair/{test_keypair}.c)
            '''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_KEYPAIR_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
            target_link_libraries(${{TARGET_KEYPAIR_BINARY_NAME}} PRIVATE {libs_str}  ${{MVARIANT}}_nistapi)
             '''
        cmake_file_content += f'''
            # crypto_sign_keypair
            set(TARGET_SIGN_BINARY_NAME {test_sign}_${{MVARIANT}})
            add_executable(${{TARGET_SIGN_BINARY_NAME}} {candidate}_sign/{test_sign}.c)
            '''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_SIGN_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
            target_link_libraries(${{TARGET_SIGN_BINARY_NAME}} PRIVATE {libs_str}  ${{MVARIANT}}_nistapi)
        '''

        cmake_file_content += f'''    
        else()
            add_library(${{MVARIANT}} ${{SOURCE_FILES_MAYO}} ${{HEADER_FILES_MAYO}})
            target_link_libraries(${{MVARIANT}} PUBLIC mayo_common_sys)
            target_include_directories(${{MVARIANT}} PUBLIC ${{BASE_DIR}}/include  PRIVATE ${{BASE_DIR}}/src/common ${{BASE_DIR}}/src ${{INC_PLATFORM}})
            string(TOUPPER ${{MVARIANT}} MVARIANT_UPPER)
            target_compile_definitions(${{MVARIANT}} PUBLIC MAYO_VARIANT=${{MVARIANT_UPPER}})
            
            
            set(SOURCE_FILES_VARIANT ${{BASE_DIR}}/src/${{MVARIANT}}/api.c ${{BASE_DIR}}/src/${{MVARIANT}}/api.h)
            add_library(${{MVARIANT}}_nistapi ${{SOURCE_FILES_VARIANT}})
            target_link_libraries(${{MVARIANT}}_nistapi PRIVATE ${{MVARIANT}})
            target_include_directories(${{MVARIANT}}_nistapi PUBLIC ${{MVARIANT}} PUBLIC ${{BASE_DIR}}/include ${{BASE_DIR}}/src/${{MVARIANT}})
            
            # crypto_sign_keypair
            set(TARGET_KEYPAIR_BINARY_NAME {test_keypair}_${{MVARIANT}})
            add_executable(${{TARGET_KEYPAIR_BINARY_NAME}} ./{candidate}_keypair/{test_keypair}.c)
                '''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_KEYPAIR_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
            target_link_libraries(${{TARGET_KEYPAIR_BINARY_NAME}} PRIVATE {libs_str}  ${{MVARIANT}}_nistapi)
            set_target_properties(${{TARGET_KEYPAIR_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
             '''
        cmake_file_content += f'''
            # crypto_sign_keypair
            set(TARGET_SIGN_BINARY_NAME {test_sign}_${{MVARIANT}})
            add_executable(${{TARGET_SIGN_BINARY_NAME}} {candidate}_sign/{test_sign}.c)
            '''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_SIGN_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
            target_link_libraries(${{TARGET_SIGN_BINARY_NAME}} PRIVATE {libs_str}  ${{MVARIANT}}_nistapi)
            set_target_properties(${{TARGET_SIGN_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}})
        endif()
        '''
    with open(path_to_cmakelists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content))


# ==================================  PROV ===================================
def makefile_prov(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    message = ''
    if implementation_type == 'ref':
        message = '# Same flags as for the optimized implementation.'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/api.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        {message}
        CC=gcc
        WARNING_FLAGS=-Wall -Wextra -Wpedantic
        
        BASE_DIR = ../../{subfolder}
        
        SHAKE_PATH= $(BASE_DIR)/SHAKE
        CFLAGS= -O2 -I./$(SHAKE_PATH)/sha3
        KATFLAGS= -I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib
        LDFLAGS= $(SHAKE_PATH)/sha3/libshake.a
        
        PROV_OBJ= $(BASE_DIR)/field.o $(BASE_DIR)/matrix.o $(BASE_DIR)/prov.o
        KAT_OBJ= $(BASE_DIR)/field.o $(BASE_DIR)/matrix.o $(BASE_DIR)/prov.o $(BASE_DIR)/api.o $(BASE_DIR)/rng.o
        SHAKE_OBJ = $(SHAKE_PATH)/hash.o
        SHAKE= $(BASE_DIR)/shake
        
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign 
            
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        
        all: $(SHAKE) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        .PHONY : clean $(BASE_DIR)/shake
        
        $(BASE_DIR)/shake:
        \t$(MAKE) -C $(SHAKE_PATH)
    
        $(BASE_DIR)/rng.o: $(BASE_DIR)/rng.c
        \t$(CC) -c -O2 -I/usr/local/opt/openssl/include $< -o $@
        
        
        $(EXECUTABLE_KEYPAIR): $(KAT_OBJ) $(BASE_DIR)/rng.o
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(@).c $(CFLAGS) $(KATFLAGS) $(KAT_OBJ) $(SHAKE_OBJ) $(TOOL_FLAGS)\
         -o $(BUILD)/$@ $(LDFLAGS) -lssl -lcrypto $(TOOL_LIBS)
                
        $(EXECUTABLE_SIGN): $(KAT_OBJ) $(BASE_DIR)/rng.o
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(@).c $(CFLAGS) $(KATFLAGS) $(KAT_OBJ) $(SHAKE_OBJ) $(TOOL_FLAGS)\
         -o $(BUILD)/$@ $(LDFLAGS) -lssl -lcrypto $(TOOL_LIBS)
         
        clean:
        \trm -f $(BASE_DIR)/*.o $(BASE_DIR)/*.a
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================  TUOV =================================
def makefile_tuov(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    platform = 'u64'
    add_cflags = ''
    if implementation_type == 'opt':
        platform = 'avx2'
        add_cflags = '-mavx2 -maes'

    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        ifndef opt
        opt = {platform}
        #opt = u64
        endif
        
        ifndef PROJ
        PROJ = Ip
        # PROJ = Is
        #PROJ = III
        #PROJ = V
        endif
        
        BASE_DIR    = ../..
        PROJ        = {subfolder}
        SRC_DIR     := $(BASE_DIR)/$(PROJ)
        
        INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
        INCPATH  += -I$(BASE_DIR)/nistkat
        
        
        SIGN = $(SRC_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC=    gcc
        LD=    gcc
        
        ifndef opt
        opt = {platform}
        #opt = u64
        endif
        
        ifndef PROJ
        PROJ = Ip
        # PROJ = Is
        #PROJ = III
        #PROJ = V
        endif
        
        BASE_DIR    = ../..
        PROJ        = {subfolder}
        SRC_DIR     := $(BASE_DIR)/$(PROJ)
        
        CFLAGS	 := -O3 -std=c11 -Wall -Wextra -Wpedantic -fno-omit-frame-pointer {add_cflags}
        INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
        LDFLAGS  := $(LDFLAGS)
        LIBPATH  = -L/usr/local/lib -L/opt/local/lib -L/usr/lib
        LIBS     = -lcrypto
        
        
        ifeq ($(opt), avx2)
            CFLAGS += -D_BLAS_AVX2_
        endif
        ifeq ($(opt), u64)
            CFLAGS += -D_BLAS_UINT64_
        endif
        
        ifeq ($(PROJ), Ip)
            CFLAGS += -D_TUOV256_112_44
        endif
        ifeq ($(PROJ), Is)
            CFLAGS += -D_TUOV16_160_64
        endif
        ifeq ($(PROJ), III)
            CFLAGS += -D_TUOV256_184_72
        endif
        ifeq ($(PROJ), V)
            CFLAGS += -D_TUOV256_244_96
        endif
        
        ifdef pkc
        CFLAGS += -D_TUOV_PKC
        endif
        
        ifdef skc
        CFLAGS += -D_TUOV_PKC_SKC
        endif
        
        SRCS           :=  $(wildcard $(SRC_DIR)/*.c)
        # SRCS_O         :=  $(SRCS:.c=.o)
        # SRCS_O_NOTDIR  :=  $(notdir $(SRCS_O))
        
        #OBJ = $(SRCS_O_NOTDIR)
        OBJ = $(patsubst $(SRC_DIR)/%.c,$(BUILD)/%.o,$(SRCS))
        
        CFLAGS       += -D_NIST_KAT_
        INCPATH      += -I$(BASE_DIR)/nistkat
        RNG				=$(BASE_DIR)/nistkat/rng.c
        OBJ          += $(BUILD)/rng.o
        
        
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign 
        
        KEYPAIR_FOLDER 	= {candidate}_keypair
        SIGN_FOLDER 	= {candidate}_sign
        
        BUILD_DIRS_ALL = $(BUILD) $(BUILD_KEYPAIR) $(BUILD_SIGN)
            
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        $(BUILD)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIRS_ALL)
        \t${{hide}}$(CC) -o $@ $< $(CFLAGS) $(INCPATH) -c
        
        $(BUILD)/rng.o: $(RNG)
        \t${{hide}}$(CC) -o $@ $< $(CFLAGS) $(INCPATH) -c
        
        $(BUILD_DIRS_ALL): %:
        \tmkdir -p $@
        
        $(EXECUTABLE_KEYPAIR): $(OBJ) $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t${{hide}}$(CC) $(CFLAGS) $(TOOL_FLAGS) $(INCPATH) $(LDFLAGS) $(LIBPATH) $^\
         -o $(BUILD)/$@ $(LIBS) $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(OBJ) $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t${{hide}}$(CC) $(CFLAGS) $(TOOL_FLAGS) $(INCPATH) $(LDFLAGS) $(LIBPATH) $^ \
        -o $(BUILD)/$@ $(LIBS) $(TOOL_LIBS)
        
        clean:
        \t ${{hide}}-rm -f build/*.o $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================  UOV =======================================
# [TODO]

def get_uov_additional_cflags_and_ld(subfolder):
    additional_cflags = ""
    ld = "$(CC)"
    subfolder_split = subfolder.split('/')
    architecture = subfolder_split[0]
    if architecture == 'avx2':
        additional_cflags = "-mavx2 -maes"
    if architecture == 'neon':
        additional_cflags = "-flax-vector-conversions"
        ld = "clang"
    return additional_cflags, ld


def makefile_uov(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    additional_cflags, loader = get_uov_additional_cflags_and_ld(subfolder)
    subfolder_split = subfolder.split('/')
    architecture = subfolder_split[0]
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        LD =    {loader}
        ifndef PROJ
        PROJ = Ip
        # PROJ = Is
        #PROJ = III
        #PROJ = V
        endif
        
        BASE_DIR    = ../../..
        PROJ        = {subfolder}
        SRC_DIR     := $(BASE_DIR)/$(PROJ)
        
        INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
        LIBPATH  = -L/usr/local/lib -L/opt/local/lib -L/usr/lib
        LIBS     = -lcrypto
        
        SIGN = $(SRC_DIR)/sign.c
        
        INCPATH      += -I$(BASE_DIR)/{architecture}/nistkat
        
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC ?=    clang
        LD =    {loader}
        
        
        ifndef PROJ
        PROJ = Ip
        # PROJ = Is
        #PROJ = III
        #PROJ = V
        endif
        
        BASE_DIR    = ../../..
        PROJ        = {subfolder}
        SRC_DIR     := $(BASE_DIR)/$(PROJ)
        
        CFLAGS   := -O3 $(CFLAGS) -std=c99 -Wall -Wextra -Wpedantic -fno-omit-frame-pointer # -Werror
        INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
        LDFLAGS  := $(LDFLAGS)
        LIBPATH  = -L/usr/local/lib -L/opt/local/lib -L/usr/lib
        LIBS     = -lcrypto
        
        CFLAGS += {additional_cflags}
        
        
        SRCS           :=  $(wildcard $(SRC_DIR)/*.c)
        
        OBJ = $(patsubst $(SRC_DIR)/%.c,$(BUILD)/%.o,$(SRCS))
        
        CFLAGS       += -D_NIST_KAT_
        INCPATH      += -I$(BASE_DIR)/{architecture}/nistkat
        RNG				=$(BASE_DIR)/{architecture}/nistkat/rng.c
        #RNG				=$(SRC_DIR)/nistkat/rng.c
        OBJ          += $(BUILD)/rng.o
        
        
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign 
        
        KEYPAIR_FOLDER 	= {candidate}_keypair
        SIGN_FOLDER 	= {candidate}_sign
        
        BUILD_DIRS_ALL = $(BUILD) $(BUILD_KEYPAIR) $(BUILD_SIGN)
        
            
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        .INTERMEDIATE:  $(OBJ)
        .PHONY: all clean
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        $(BUILD)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIRS_ALL)
        \t${{hide}}$(CC) -o $@ $< $(CFLAGS) $(INCPATH) -c
        
        $(BUILD)/rng.o: $(RNG)
        \t${{hide}}$(CC) -o $@ $< $(CFLAGS) $(INCPATH) -c
        
        $(BUILD_DIRS_ALL): %:
        \tmkdir -p $@
        
        $(EXECUTABLE_KEYPAIR): $(OBJ) $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t${{hide}}$(CC) $(CFLAGS) $(TOOL_FLAGS) $(INCPATH) $(LDFLAGS) $(LIBPATH) $^ \
        -o $(BUILD)/$@ $(LIBS) $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(OBJ) $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t${{hide}}$(CC) $(CFLAGS) $(TOOL_FLAGS) $(INCPATH) $(LDFLAGS) $(LIBPATH) $^ \
        -o $(BUILD)/$@ $(LIBS) $(TOOL_LIBS)
        
        clean:
        \t ${{hide}}-rm -f build/*.o $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ===============================  VOX =====================================
# [TODO]
def makefile_vox(path_to_makefile_folder, subfolder, tool_name, candidate, security_level, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    vox_add_src_files = ''
    vox_add_build_dir = ''

    if implementation_type == 'add':
        vox_add_src_files = 'SRC += $(BASE_DIR)/fips202/fips202x4.c $(BASE_DIR)/fips202/keccak4x/KeccakP-1600-times4-SIMD256.c'
        vox_add_build_dir = 'BUILD_DIRS_ALL += $(BUILD_DIR)/fips202/keccak4x'

    if tool_name == 'flowtracker':
        makefile_content = f'''
        PARAM ?= VOX{security_level}
        
        VOX_PARAMS = -DPARAM_SET_$(PARAM)
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/api.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(VOX_PARAMS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(VOX_PARAMS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        # select parameter set (one of: VOX128 VOX192 VOX256)
        PARAM ?= VOX{security_level}
        
        
        CC=gcc
        CFLAGS = -std=c99 -pedantic -Wall -Wextra -O3 -funroll-loops -march=native -DPARAM_SET_$(PARAM)
        LIBS = -lcrypto
        
        BUILD           = build
        BUILD_DIR = $(BUILD)
        
        BASE_DIR = ../../{subfolder}
        
        # Sources
        ###########
        HDR = $(wildcard $(BASE_DIR)/*.h) $(BASE_DIR)/fips202/fips202.h $(BASE_DIR)/rng/rng.h
        SRC = $(wildcard $(BASE_DIR)/*.c) $(BASE_DIR)/fips202/fips202.c $(BASE_DIR)/rng/rng.c
        BUILD_DIRS_ALL = $(BUILD_DIR) $(BUILD_DIR)/fips202 $(BUILD_DIR)/rng
        

        {vox_add_src_files}
        {vox_add_build_dir}
        
        OBJ = $(patsubst $(BASE_DIR)/%.c,$(BUILD_DIR)/%.o,$(SRC))
        
        # Executables
        ##############
    
        
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign 
        
        KEYPAIR_FOLDER 	= {candidate}_keypair
        SIGN_FOLDER 	= {candidate}_sign
        
        
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        .PHONY: all
        
        $(BUILD_DIR)/%.o:$(BASE_DIR)/%.c $(HDR) | $(BUILD_DIRS_ALL)
        \t$(CC) -o $@ $< $(CFLAGS) -c
    
        $(BUILD_DIRS_ALL): %:
        \tmkdir -p $@
    
        .SECONDARY: $(OBJ)
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(OBJ)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -o $(BUILD)/$@ $^ $(CFLAGS) $(TOOL_FLAGS) -I. -Irng/ $(LIBS) $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(OBJ)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -o $(BUILD)/$@ $^ $(CFLAGS) $(TOOL_FLAGS) -I. -Irng/ $(LIBS) $(TOOL_LIBS)
        
        clean:
        \t-rm -rf $(BASE_DIR)/$(BUILD_DIR)
        \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ============================ SYMMETRIC =======================================
# ==============================================================================

# =============================  AIMER =========================================
def aimer_level_parameters(subfolder):
    subfold_basename = os.path.basename(subfolder)
    subfold_basename_split = subfold_basename.split('-')
    params_level = subfold_basename_split[1][1]
    security_level = 128
    if params_level == '3':
        security_level = 192
    elif params_level == '5':
        security_level = 256
    return params_level, security_level


def makefile_aimer(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    avx2_flags = ''
    if implementation_type == 'opt':
        avx2_flags = 'AVX2FLAGS = -mavx2 -mpclmul'

    params_level, security_level = aimer_level_parameters(subfolder)
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/api.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        # SPDX-License-Identifier: MIT
        
        CC = gcc
        BASE_DIR = ../../{subfolder}
        CFLAGS += -I. -O3 -g -Wall -Wextra -march=native -fomit-frame-pointer -I$(BASE_DIR)
        NISTFLAGS = -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter -Wno-unused-result
        {avx2_flags}
        
        SHAKE_PATH = $(BASE_DIR)/shake
        SHAKE_LIB = libshake.a
        LDFLAGS = $(SHAKE_PATH)/$(SHAKE_LIB)
        
        
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_sign}
        
        
        TOOL_FLAGS = {tool_flags}
        TOOL_LIBS = {tool_libs}
        
        .PHONY: all
        
        all: $(SHAKE_LIB) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        $(BUILD)/.c.o:
        \t$(CC) -c $(CFLAGS) $< -o $@
        
        $(SHAKE_LIB):
        \t$(MAKE) -C $(SHAKE_PATH)
        
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.c $(BASE_DIR)/field/field{security_level}.c\
        $(BASE_DIR)/aim{security_level}.c $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c \
        $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) -D_BSD_SOURCE -D_DEFAULT_SOURCE $(CFLAGS) $(TOOL_FLAGS) $(AVX2FLAGS)  -D_AIMER_L={params_level} \
         $^ $(LDFLAGS) $(TOOL_LIBS) -lcrypto -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.c $(BASE_DIR)/field/field{security_level}.c $(BASE_DIR)/aim{security_level}.c \
        $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c \
        $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) -D_BSD_SOURCE -D_DEFAULT_SOURCE $(CFLAGS) $(TOOL_FLAGS) $(AVX2FLAGS)  -D_AIMER_L={params_level}  \
        $^ $(LDFLAGS) $(TOOL_LIBS) -lcrypto -o $(BUILD)/$@
        
    
        clean:
        \trm -f $(wildcard *.o) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        \t$(MAKE) -C $(SHAKE_PATH) clean   
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ================================ ascon_sign ===================================
def get_ascon_sign_robust_or_simple_type(subfolder):
    subfolder_split = subfolder.split('/')
    subfolder_split = subfolder_split[0]
    robust_or_simple = subfolder_split.split('_')[-1]
    return robust_or_simple


def makefile_ascon_sign(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    ascon_specific_src_files = '$(BASE_DIR)/ascon/ascon.c'
    if implementation_type == 'opt':
        ascon_specific_src_files = '$(BASE_DIR)/ascon_opt64/ascon.c $(BASE_DIR)/ascon_opt64/permutations.c'
    robust_or_simple = get_ascon_sign_robust_or_simple_type(subfolder)
    robust_or_simple = robust_or_simple.lower()
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        INCS_DIR = $(BASE_DIR)
        
        SIGN = $(BASE_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        THASH = {robust_or_simple}
    
        CC=/usr/bin/gcc
        CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
        
        BASE_DIR = ../../../{subfolder}
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
         
          
        SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c \
        $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c $(BASE_DIR)/sign.c
        
        SOURCES += $(BASE_DIR)/hash_ascon.c {ascon_specific_src_files} $(BASE_DIR)/thash_ascon_$(THASH).c
        
        
        DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
            
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    
        all:  $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN) 
           
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)
    
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)
        
        clean:
        \t-$(RM)  $(EXECUTABLE_SIGN)
        \t-$(RM)  $(EXECUTABLE_KEYPAIR) 
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ================================= faest ========================================

def makefile_faest(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    specific_cflags = '-O3 -std=gnu11'
    cpp_cflags = '-I. -Isha3 -DNDEBUG -DHAVE_OPENSSL'
    filter_out_src = '$(SRC_DIR)/randomness.c'
    specific_src_files = '$(wildcard $(SRC_DIR)/sha3/*.c) $(wildcard $(SRC_DIR)/sha3/*.s)'
    specific_randomness = 'randomness'
    rng = '$(SRC_DIR)/NIST-KATs/rng.c'
    if implementation_type == 'add':
        specific_cflags = '-O2 -mtune=native -std=c11'
        cpp_cflags = '-DHAVE_OPENSSL -DNDEBUG -MMD -MP -MF $*.d'
        filter_out_src = '$(SRC_DIR)/randomness_os.c $(SRC_DIR)/randomness_randombytes.c $(SRC_DIR)/rng.c'
        specific_src_files = '$(wildcard $(SRC_DIR)/*.c) $(wildcard $(SRC_DIR)/*.s)'
        specific_randomness = 'randomness_randombytes'
        rng = '$(SRC_DIR)/rng.c'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        INCS_DIR = $(BASE_DIR)
        
        
        SIGN = $(BASE_DIR)/crypto_sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        CC?=gcc
        CXX?=g++
        CFLAGS+=-g {specific_cflags} -march=native
        CPPFLAGS+={cpp_cflags}
        
        SRC_DIR = ../../{subfolder}
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        CPPFLAGS+=-I$(SRC_DIR)/sha3
        
        SOURCES=$(filter-out {filter_out_src}, $(wildcard $(SRC_DIR)/*.c)) {specific_src_files}
        #SOURCES +=$(SRC_DIR)/NIST-KATs/rng.c
        
        LIBFAEST=$(SRC_DIR)/libfaest.a
        
        EXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		 = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
          
        
        all: $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        .PHONY: all
        
        $(LIBFAEST): $(SOURCES:.c=.o) $(SOURCES:.s=.o)
        \tar rcs $@ $^

        %.c.o: %.c
        \t$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c.o $(LIBFAEST) $(SRC_DIR)/{specific_randomness}.c.o
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CPPFLAGS) $(TOOL_FLAGS) $(LDFLAGS) $^ -lcrypto $(TOOL_LIBS) -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c.o $(LIBFAEST) $(SRC_DIR)/{specific_randomness}.c.o
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CPPFLAGS) $(TOOL_FLAGS) $(LDFLAGS) $^ -lcrypto $(TOOL_LIBS) -o $(BUILD)/$@
        
        
        clean: 
        \trm -f $(SRC_DIR)/*.d $(SRC_DIR)/*.o $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        .PHONY: clean
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== Sphincs-alpha ===========================

def makefile_sphincs_alpha(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    sphincs_alpha_thash = 'simple'
    specific_content_simple = f'''
        ifneq (,$(findstring shake,$(PARAMS)))
            \tSOURCES += $(BASE_DIR)/fips202.c $(BASE_DIR)/hash_shake.c $(BASE_DIR)/thash_shake_$(THASH).c
            \tHEADERS += $(BASE_DIR)/fips202.h
        endif
        ifneq (,$(findstring haraka,$(PARAMS)))
            \tSOURCES += $(BASE_DIR)/haraka.c $(BASE_DIR)/hash_haraka.c $(BASE_DIR)/thash_haraka_$(THASH).c
            \tHEADERS += $(BASE_DIR)/haraka.h
        endif
        ifneq (,$(findstring sha2,$(PARAMS)))
            \tSOURCES += $(BASE_DIR)/sha2.c $(BASE_DIR)/hash_sha2.c $(BASE_DIR)/thash_sha2_$(THASH).c
            \tHEADERS += $(BASE_DIR)/sha2.h
        endif
        '''
    add_cflags = '-Wconversion'
    specific_src_files = '$(BASE_DIR)/wotsx1.c  $(BASE_DIR)/utilsx1.c'
    specific_header_files = '$(BASE_DIR)/wotsx1.h  $(BASE_DIR)/utilsx1.h '
    if implementation_type == 'add':
        sphincs_alpha_thash = 'robust'
        add_cflags = '-march=native -flto -fomit-frame-pointer'
        specific_src_files = f'''$(BASE_DIR)/hash_sha2.c $(BASE_DIR)/hash_sha2x8.c $(BASE_DIR)/thash_sha2_$(THASH).c\
        $(BASE_DIR)/thash_sha2_$(THASH)x8.c $(BASE_DIR)/sha2.c $(BASE_DIR)/sha256x8.c $(BASE_DIR)/sha512x4.c \
         $(BASE_DIR)/sha256avx.c  $(BASE_DIR)/utilsx8.c'''
        specific_header_files = f'''$(BASE_DIR)/hashx8.h  $(BASE_DIR)/thashx8.h  $(BASE_DIR)/sha2.h  \
        $(BASE_DIR)/sha256x8.h $(BASE_DIR)/sha512x4.h $(BASE_DIR)/sha256avx.h  $(BASE_DIR)/utilsx8.h'''
        specific_content_simple = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        BASE_DIR = ../../{subfolder}
        
        
        PARAMETERS = {subfolder}
        THASH = {sphincs_alpha_thash}
        
        CFLAGS = $(EXTRA_CFLAGS) -DPARAMS=$(PARAMETERS)
        PARAMS_INCS = $(BASE_DIR)/params
        
        INCS_DIR = $(BASE_DIR)
        SIGN = $(BASE_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(CFLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(CFLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        PARAMS = {subfolder}
        #PARAMS = sphincs-a-sha2-128f
        THASH = {sphincs_alpha_thash}
        
        CC=/usr/bin/gcc
        CFLAGS=-Wall -Wextra -Wpedantic -Wmissing-prototypes -O3 -std=c99 -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS) {add_cflags}
               
        
        BASE_DIR = ../../{subfolder}
        
        SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c \
                $(BASE_DIR)/utils.c $(BASE_DIR)/fors.c $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c {specific_src_files}
                
        HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h  $(BASE_DIR)/merkle.h \
         $(BASE_DIR)/wots.h $(BASE_DIR)/utils.h $(BASE_DIR)/fors.h $(BASE_DIR)/api.h $(BASE_DIR)/hash.h \
          $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h {specific_header_files}
        
        {specific_content_simple}
        
        DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
        DET_HEADERS = $(HEADERS:randombytes.%=rng.%)
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_keypair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_sign}
        
        .PHONY: clean 
        
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)
        
         
        clean:
        \t-$(RM) $(EXECUTABLE_KEYPAIR)
        \t-$(RM) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def makefile_sphincs_alpha1(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    sphincs_alpha_thash = 'simple'
    sphincs_alpha_thash_other = 'robust'
    specific_content_simple = f'''
        ifneq (,$(findstring shake,$(PARAMS)))
            \tSOURCES += $(BASE_DIR)/fips202.c $(BASE_DIR)/hash_shake.c $(BASE_DIR)/thash_shake_$(THASH).c
            \tHEADERS += $(BASE_DIR)/fips202.h
        endif
        ifneq (,$(findstring haraka,$(PARAMS)))
            \tSOURCES += $(BASE_DIR)/haraka.c $(BASE_DIR)/hash_haraka.c $(BASE_DIR)/thash_haraka_$(THASH).c
            \tHEADERS += $(BASE_DIR)/haraka.h
        endif
        ifneq (,$(findstring sha2,$(PARAMS)))
            \tSOURCES += $(BASE_DIR)/sha2.c $(BASE_DIR)/hash_sha2.c $(BASE_DIR)/thash_sha2_$(THASH).c
            \tHEADERS += $(BASE_DIR)/sha2.h
        endif
        '''
    add_cflags = '-Wconversion'
    specific_src_files = '$(BASE_DIR)/wotsx1.c  $(BASE_DIR)/utilsx1.c'
    specific_header_files = '$(BASE_DIR)/wotsx1.h  $(BASE_DIR)/utilsx1.h '
    if implementation_type == 'add':
        sphincs_alpha_thash = 'robust'
        sphincs_alpha_thash_other = 'simple'
        add_cflags = '-march=native -flto -fomit-frame-pointer'
        specific_src_files = f'''$(BASE_DIR)/hash_sha2.c $(BASE_DIR)/hash_sha2x8.c $(BASE_DIR)/thash_sha2_$(THASH).c\
        $(BASE_DIR)/thash_sha2_$(THASH)x8.c $(BASE_DIR)/sha2.c $(BASE_DIR)/sha256x8.c $(BASE_DIR)/sha512x4.c \
         $(BASE_DIR)/sha256avx.c  $(BASE_DIR)/utilsx8.c'''
        specific_header_files = f'''$(BASE_DIR)/hashx8.h  $(BASE_DIR)/thashx8.h  $(BASE_DIR)/sha2.h  \
        $(BASE_DIR)/sha256x8.h $(BASE_DIR)/sha512x4.h $(BASE_DIR)/sha256avx.h  $(BASE_DIR)/utilsx8.h'''
        specific_content_simple = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        BASE_DIR = ../../{subfolder}
        
        
        PARAMETERS = {subfolder}
        THASH = {sphincs_alpha_thash}
        
        CFLAGS = $(EXTRA_CFLAGS) -DPARAMS=$(PARAMETERS)
        PARAMS_INCS = $(BASE_DIR)/params
        
        INCS_DIR = $(BASE_DIR)
        SIGN = $(BASE_DIR)/sign.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(CFLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(CFLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        PARAMS = {subfolder}
        #PARAMS = sphincs-a-sha2-128f
        THASH = {sphincs_alpha_thash}
        THASH_OPP = {sphincs_alpha_thash_other}
        
        CC=/usr/bin/gcc
        CFLAGS=-Wall -Wextra -Wpedantic -Wmissing-prototypes -O3 -std=c99 -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS) {add_cflags}
            
        BASE_DIR = ../../{subfolder}
        SOURCES = $(filter-out $(BASE_DIR)/thash_sha2_$(THASH_OPP)x8.c $(BASE_DIR)/PQCgenKAT_sign.c $(BASE_DIR)/rng.c  $(BASE_DIR)/thash_sha2_$(THASH_OPP).c,$(wildcard $(BASE_DIR)/*.c))
        HEADERS = $(filter-out  $(BASE_DIR)/rng.h $(BASE_DIR)/params.h, $(wildcard $(BASE_DIR)/*.h))
        # SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c \
        #         $(BASE_DIR)/utils.c $(BASE_DIR)/fors.c $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c {specific_src_files}
                
        # HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h  $(BASE_DIR)/merkle.h \
        #  $(BASE_DIR)/wots.h $(BASE_DIR)/utils.h $(BASE_DIR)/fors.h $(BASE_DIR)/api.h $(BASE_DIR)/hash.h \
        #   $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h {specific_header_files}
        
        {specific_content_simple}
        
        DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
        DET_HEADERS = $(HEADERS:randombytes.%=rng.%)
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_keypair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_sign}
        
        .PHONY: clean 
        
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)
        
         
        clean:
        \t-$(RM) $(EXECUTABLE_KEYPAIR)
        \t-$(RM) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ==============================  OTHER =================================
# =======================================================================
# =================================== ALTEQ =======================================
def makefile_alteq(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    alteq_opt = ''
    alteq_opt2 = ''
    if implementation_type == 'opt':
        alteq_opt = '-mavx2 -mssse3 -maes'
        alteq_opt2 = '-fwhole-program -flto -funroll-loops'

    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        BASE_DIR = ..
        
        OPT = -lcrypto -O3  -Wall -pedantic {alteq_opt}
        OPT2 = {alteq_opt2}
        OPT3= -Wno-unused-function
        LDFLAGS= -lssl -lcrypto -L/usr/local/opt/openssl/lib -lm
        CFLAGS= -I/usr/local/opt/openssl/include
        
        # no need to force old standards for speed tests, this will save a lot of warnings
        # STD = -ansi
        STD =
        # only use RDPMC if you can be sure you can use it. Otherwise default to RDTSC
        # RDPMC = -D USE_RDPMC
        RDPMC =
        

        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        BIN             = bin
            
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        AES_SRC = $(wildcard $(BASE_DIR)/aes/*.c)
        KECCAK_SRC = $(wildcard $(BASE_DIR)/keccak/*.c) $(wildcard $(BASE_DIR)/keccak/*.s)
        SRC = $(BASE_DIR)/atf.c $(BASE_DIR)/compress.c $(BASE_DIR)/expand.c $(BASE_DIR)/field.c \
        $(BASE_DIR)/matrix.c $(BASE_DIR)/sign.c
        
        SOURCES = $(AES_SRC) $(KECCAK_SRC) $(SRC)
        
        all_api = $(BASE_DIR)/api/api.h.1.fe $(BASE_DIR)/api/api.h.3.fe $(BASE_DIR)/api/api.h.5.fe \
        $(BASE_DIR)/api/api.h.1.lp $(BASE_DIR)/api/api.h.3.lp $(BASE_DIR)/api/api.h.5.lp
        
        
        .PHONY: all clean $(all_api)

        all:  build_folders $(all_api)
        
        
        build_folders:
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN)
        
        
        $(all_api):
        \t@echo -e "### Processing $@"
        \tcp $@ $(BASE_DIR)/api.h
        \tgcc $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_KEYPAIR)_$(word 1, $(subst .,_,$(@F))) \
        $(EXECUTABLE_KEYPAIR).c $(SOURCES) $(LDFLAGS) $(TOOL_LIBS)  $(STD) $(OPT) $(OPT3)
        \tgcc $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_SIGN)_$(word 1, $(subst .,_,$(@F))) \
        $(EXECUTABLE_SIGN).c $(SOURCES) $(LDFLAGS) $(TOOL_LIBS)  $(STD) $(OPT) $(OPT3)
                
        clean:
        \trm -f $(BUILD)/$(EXECUTABLE_KEYPAIR)/*
        \trm -f $(BUILD)/$(EXECUTABLE_SIGN)/*
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== EMLE =======================================
def makefile_emle(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    add_cflags = ''
    if implementation_type == 'add':
        add_cflags = '-maes'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/nist.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        BASE_DIR = ../../{subfolder}
        
        CFLAGS = -O3 -Wall -Wextra -Wpedantic {add_cflags}
        LDFLAGS = -fPIC -lssl -lcrypto
        

        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        BIN             = bin
            
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        
        OBJS = $(BIN)/impl.o $(BIN)/fips202.o $(BIN)/conv.o $(BIN)/aes256ctr.o $(BIN)/randvec.o $(BIN)/rng.o \
        $(BIN)/nist.o 
        

        all:  build_folders $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        build_folders:
        \tmkdir -p $(BIN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN)
        
        
        
        $(BIN)/%.o : $(BASE_DIR)/%.c
        \tgcc $(CFLAGS) -o $@ -c $< 
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c  $(OBJS) $(BASE_DIR)/api.h
        \tgcc $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $^ $(LDFLAGS) $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c  $(OBJS) $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
        \tgcc $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $^ $(LDFLAGS) $(TOOL_LIBS)
        
        
        $(BIN)/impl.o: $(BASE_DIR)/impl.h $(BASE_DIR)/fips202.h $(BASE_DIR)/conv.h $(BASE_DIR)/aes256ctr.h \
         $(BASE_DIR)/randvec.h $(BASE_DIR)/mod.h $(BASE_DIR)/impl.c
        $(BIN)/fips202.o: $(BASE_DIR)/fips202.h $(BASE_DIR)/fips202.c
        $(BIN)/conv.o: $(BASE_DIR)/conv.h $(BASE_DIR)/mod.h $(BASE_DIR)/conv.c
        $(BIN)/aes256ctr.o: $(BASE_DIR)/aes256ctr.h $(BASE_DIR)/aes256ctr.c
        $(BIN)/randvec.o: $(BASE_DIR)/randvec.h $(BASE_DIR)/aes256ctr.h $(BASE_DIR)/mod.h $(BASE_DIR)/littleendian.h \
        $(BASE_DIR)/randvec.c
        $(BIN)/rng.o: $(BASE_DIR)/rng.h $(BASE_DIR)/rng.c
        $(BIN)/nist.o: $(BASE_DIR)/api.h $(BASE_DIR)/impl.h $(BASE_DIR)/rng.h $(BASE_DIR)/littleendian.h \
        $(BASE_DIR)/nist.c
        
        
        
        .PHONY: clean
        clean:
        \trm -f $(BIN)/*
        \trm -f $(BUILD)/$(EXECUTABLE_KEYPAIR) $(BUILD)/$(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== KAZ_SIGN =======================================
def makefile_kaz_sign(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/sign.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        BASE_DIR = ../../{subfolder}
        
        CC=gcc
        CFLAGS=
        INC=-I/usr/include/openssl
        LINK=-lcrypto -lgmp 
        

        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        BIN             = bin
            
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        
        all:  build_folders $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        build_folders:
        \tmkdir -p $(BIN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN)
        
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.h $(BASE_DIR)/gmp.h $(BIN)/sign.o \
         $(BIN)/kaz_api.o $(BIN)/rng.o $(BIN)/sha256.o
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_KEYPAIR) $(EXECUTABLE_KEYPAIR).c $(BIN)/rng.o \
         $(BIN)/sha256.o $(BIN)/kaz_api.o $(BIN)/sign.o $(INC) $(LINK) $(TOOL_LIBS)
         
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.h $(BASE_DIR)/gmp.h $(BIN)/sign.o \
         $(BIN)/kaz_api.o $(BIN)/rng.o $(BIN)/sha256.o
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_SIGN) $(EXECUTABLE_SIGN).c $(BIN)/rng.o \
         $(BIN)/sha256.o $(BIN)/kaz_api.o $(BIN)/sign.o $(INC) $(LINK) $(TOOL_LIBS)
         
        
        $(BIN)/sign.o: $(BASE_DIR)/api.h $(BASE_DIR)/gmp.h $(BASE_DIR)/kaz_api.h $(BASE_DIR)/sign.c
        \t$(CC) $(CFLAGS) -c $(BASE_DIR)/sign.c -o $(BIN)/sign.o $(INC)
        
        $(BIN)/kaz_api.o: $(BASE_DIR)/kaz_api.c $(BASE_DIR)/kaz_api.h
        \t$(CC) $(CFLAGS) -c $(BASE_DIR)/kaz_api.c -o $(BIN)/kaz_api.o $(INC)
        
        $(BIN)/rng.o: $(BASE_DIR)/rng.c $(BASE_DIR)/rng.h
        \t$(CC) $(CFLAGS) -c $(BASE_DIR)/rng.c -o $(BIN)/rng.o $(INC)
        
        $(BIN)/sha256.o: $(BASE_DIR)/sha256.c $(BASE_DIR)/sha256.h
        \t$(CC) $(CFLAGS) -c $(BASE_DIR)/sha256.c -o $(BIN)/sha256.o $(INC)
                
        
        
        .PHONY: clean
        clean:
        \trm -f $(BIN)/*
        \trm -f $(BUILD)/$(EXECUTABLE_KEYPAIR) $(BUILD)/$(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== xifrat =======================================
def makefile_xifrat(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    src_folder = '../Reference_Implementation/'
    if implementation_type == 'ref':
        src_folder = ''
    if tool_name == 'ctverif' or tool_name == 'ct-verif':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        WRAPPER_KEYPAIR  = {candidate}_keypair/{test_keypair}
        WRAPPER_SIGN     = {candidate}_keypair/{test_sign}
        EXECUTABLE_KEYPAIR_BPL	= {candidate}_keypair/{test_keypair}.bpl
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BPL		= {candidate}_sign/{test_sign}.bpl
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BPL) #$(EXECUTABLE_SIGN_BPL) 
         
        
        
        $(EXECUTABLE_KEYPAIR_BPL): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tsmack -t --verifier=boogie --entry-points {test_keypair} -bpl $(BUILD)/$(EXECUTABLE_KEYPAIR_BPL) $(WRAPPER_KEYPAIR).c
        \t#$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        
        #$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        #\truby -I$(BAMPATH)/lib $(BAMPATH)/bin/bam --shadowing $(SMACKOUT) -o $(BAMOUT)
        
        #$(EXECUTABLE_SIGN_BC): $(SIGN)
        #\tmkdir -p $(BUILD)
        #\tmkdir -p $(BUILD_SIGN)
        #\t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        #$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        #\topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    elif tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        SIGN = $(BASE_DIR)/api.c
        INCS_DIR = $(BASE_DIR)
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f'''
        BASE_DIR = ../..
        
        CFLAGS = -I.
        

        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        BIN             = bin
            
            
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        
        OBJS=\
        $(BIN)/rng.o $(BIN)/sign.o $(BIN)/rijndael.o $(BIN)/shake.o $(BIN)/sponge.o \
        $(BIN)/keccak-f-1600.o $(BASE_DIR)/endian.o $(BIN)/xifrat-sign.o $(BIN)/xifrat-funcs.o
        
        all:  build_folders $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        
        build_folders:
        \tmkdir -p $(BIN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \tmkdir -p $(BUILD_SIGN)
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(OBJ)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_KEYPAIR) $(EXECUTABLE_KEYPAIR).c $(OBJ) $(TOOL_LIBS) $(LDFLAGS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(OBJ)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$(EXECUTABLE_SIGN) $(EXECUTABLE_SIGN).c $(OBJ) $(TOOL_LIBS) $(LDFLAGS)
        
        %.o: %.c
        \t$(CC) $(CFLAGS) -o $@ -c $<
        
        common: \
        $(BASE_DIR)/common.h  $(BASE_DIR)/{src_folder}mysuitea-common.h
        
        $(BIN)/rng.o: \
        $(BASE_DIR)/{src_folder}rng.c $(BASE_DIR)/{src_folder}rng.h \
        
        $(BIN)/sign.o: \
        $(BASE_DIR)/{src_folder}sign.c $(BASE_DIR)/{src_folder}sign.h \
        
        $(BIN)/sponge.o: \
        $(BASE_DIR)/{src_folder}sponge.c $(BASE_DIR)/{src_folder}sponge.h common
        
        
        $(BIN)/endian.o: \
        $(BASE_DIR)/{src_folder}endian.c $(BASE_DIR)/{src_folder}endian.h common
        
        $(BIN)/shake.o: \
        $(BASE_DIR)/{src_folder}shake.c $(BASE_DIR)/{src_folder}shake.h \
        $(BASE_DIR)/{src_folder}keccak.h $(BASE_DIR)/{src_folder}sponge.h common
        
        $(BIN)/keccak-f-1600.o: \
        $(BASE_DIR)/{src_folder}keccak-f-1600.c $(BASE_DIR)/{src_folder}keccak.c.h \
        $(BASE_DIR)/{src_folder}keccak.h common
        
        $(BIN)/xifrat-sign.o: \
        $(BASE_DIR)/{src_folder} $(BASE_DIR)/{src_folder}
        
        $(BIN)/xifrat-funcs.o: \
        $(BASE_DIR)/xifrat-funcs.h common
            
            
        .PHONY: clean
        clean:
        \trm -f $(BIN)/*
        \trm -f $(BUILD)/$(EXECUTABLE_KEYPAIR) $(BUILD)/$(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))

# ============================== PREON ==================================
def preon_subfolder_parser(subfolder):
    subfold_basename = os.path.basename(subfolder)
    subfold_basename_split = subfold_basename.split('Preon')
    security_level_labeled = subfold_basename_split[-1]
    security_level = security_level_labeled[:3]
    return security_level, security_level_labeled


def makefile_preon(path_to_makefile_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    security_level, security_level_labeled = preon_subfolder_parser(subfolder)
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    specific_opt_flag_level = '-O3'
    if implementation_type == 'ref':
        specific_opt_flag_level = '-O0'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        INCS_DIR = $(BASE_DIR)
        
        CFLAGS := ${{CFLAGS}} -DUSE_PREON{security_level_labeled} -DAES{security_level}=1 -DUSE_PRNG {specific_opt_flag_level}
        
        SIGN = $(BASE_DIR)/api.c
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(CFLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(CFLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        makefile_content = f''' 
        CC = cc
        CFLAGS := ${{CFLAGS}} -DUSE_PREON{security_level_labeled} -DAES{security_level}=1 -DUSE_PRNG {specific_opt_flag_level}
        LFLAGS := ${{LFLAGS}} -lm -lssl -lcrypto
        
       
        BASE_DIR = ../../../{subfolder}
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
            
        SRC_FILES := $(filter-out  $(BASE_DIR)/PQCgenKAT_sign.c ,$(wildcard $(BASE_DIR)/*.c))
            
        EXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		 = {candidate}_sign/{test_sign}
        
            
        all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        %.o: %.c
        \t@$(CC) $(CFLAGS) -c $< -o $@
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(SRC_FILES)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(SRC_FILES) $< $(LFLAGS) $(TOOL_LIBS)
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(SRC_FILES)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(SRC_FILES) $< $(LFLAGS) $(TOOL_LIBS)
        
        .PHONY: clean  
        
        clean:
        \t@rm -f $(BASE_DIR)/*.o 
        \t@rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ==========================  ISOGENY ========================================
# ============================================================================
# =========================== sqisign ========================================
def cmake_sqisign(path_to_cmakelists_folder, subfolder, tool_name, candidate, implementation_type='opt'):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_cmakelists = f'{path_to_cmakelists_folder}/CMakeLists.txt'
    add_cflags = ""
    asm_flags = ""
    avx2_optimized_option = "OFF"
    if implementation_type == 'opt':
        add_cflags = f''
        asm_flags = f''
    if implementation_type == 'add':
        avx2_optimized_option = "ON"

    cmake_file_content = ''
    target_link_opt_block = ''
    link_flag = ''
    if tool_flags:
        if '-static ' in tool_flags or ' -static' in tool_flags:
            link_flag = '-static'
    libs_str = ""
    # tool_libs = tool_libs.replace("-lm", "")
    # tool_libs = tool_libs.strip()
    libs_list = []
    if tool_libs:
        libs_str = tool_libs.replace("-l", "")
        libs_list = libs_str.split()
    if tool_name == 'flowtracker':
        path_to_cmakelists = f'{path_to_cmakelists_folder}/Makefile'
        cmake_file_content = f'''
        CC = clang
        
        BASE_DIR = ../
        
        
        INCS_DIR = $(BASE_DIR)/include
        
        
        # CATEGORY RANGE 1 5 2
        # PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE
        # if CATEGORY = 1   PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE
        # else PARAM_TARGETS SIG_SIZE PK_SIZE
        
        KECCAK_EXTERNAL_ENABLE = 
        CATEGORY = 1
        RSDP_VARIANT =  RSDP
        PARAM_TARGETS =  SIG_SIZE
        COMPILE_FLAGS = -DCATEGORY_${{CATEGORY}}=1 -D${{PARAM_TARGETS}}=1 ${{KECCAK_EXTERNAL_ENABLE}}
        
        
        
        SIGN = $(BASE_DIR)/lib/sign.c
        
        
        BUILD			= build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        EXECUTABLE_KEYPAIR_BC	= {candidate}_keypair/{test_keypair}.bc
        EXECUTABLE_KEYPAIR_RBC	= {candidate}_keypair/{test_keypair}.rbc
        EXECUTABLE_SIGN_BC		= {candidate}_sign/{test_sign}.bc
        EXECUTABLE_SIGN_RBC		= {candidate}_sign/{test_sign}.rbc
        
        all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
        $(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)
            
        .PHONY: clean
          
        clean:
        \trm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
        \trm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
        '''
    else:
        cmake_file_content = f'''
        cmake_minimum_required(VERSION 3.9.4)
        project(LESS C)
    
        # build type can be case-sensitive!
        string(TOUPPER "${{CMAKE_BUILD_TYPE}}" UPPER_CMAKE_BUILD_TYPE)
        
        set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -Wsign-conversion -Wno-strict-prototypes")
        
        include(CheckCCompilerFlag)
        unset(COMPILER_SUPPORTS_MARCH_NATIVE CACHE)
        check_c_compiler_flag(-march=native COMPILER_SUPPORTS_MARCH_NATIVE)
        
        include(CheckIPOSupported)
        check_ipo_supported(RESULT lto_supported OUTPUT error)
        
        if(UPPER_CMAKE_BUILD_TYPE MATCHES DEBUG)
            message(STATUS "Building in Debug mode!")
        else() # Release, RELEASE, MINSIZEREL, etc
            set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -mtune=native -O3 -g")   
            if(COMPILER_SUPPORTS_MARCH_NATIVE)
                set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -march=native")
            endif()
            if(lto_supported)
                message(STATUS "IPO / LTO enabled")
                set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
            endif()
        endif()
        
        option(COMPRESS_CMT_COLUMNS "Enable COMPRESS_CMT_COLUMNS to compress commitment in SG and VY before hashing" OFF)
        if(COMPRESS_CMT_COLUMNS)
            message(STATUS "COMPRESS_CMT_COLUMNS is enabled")
            add_definitions(-DCOMPRESS_CMT_COLUMNS)
        else()
            message(STATUS "COMPRESS_CMT_COLUMNS is disabled")
        endif()
        unset(COMPRESS_CMT_COLUMNS CACHE)
        
        set(SANITIZE "")
        message(STATUS "Compilation flags:" ${{CMAKE_C_FLAGS}})
        
        set(CMAKE_C_STANDARD 11)'''
        find_libs_block = ''
        libs_variables = ''
        for lib in libs_list:
            lib_variable = lib.upper()
            lib_variable = f'{lib_variable}_LIB'
            l_var = f'{lib_variable}'
            l_var = f'{{{l_var}}}'
            libs_variables += f' ${l_var}'
            find_libs_block += f'''
        find_library({lib_variable} {lib})
        if(NOT {lib_variable})
        \tmessage("{lib} library not found")
        endif()
        '''
        if libs_list:
            cmake_file_content += f'{find_libs_block}'
        cmake_file_content += f'''
        
        find_library(KECCAK_LIB keccak)
        if(NOT KECCAK_LIB)
            set(STANDALONE_KECCAK 1)
        endif()
        
        # selection of specialized compilation units differing between ref and opt implementations.
        option(AVX2_OPTIMIZED "Use the AVX2 Optimized Implementation. 
        Else the Reference Implementation will be used." {avx2_optimized_option})
        
        message(".....Checking AVX2_OPTIMIZED:  " ${{AVX2_OPTIMIZED}})
        
        #set(BASE_DIR  ../Optimized_Implementation) 
        set(BASE_DIR  ../)  
        set(HEADERS
                ${{BASE_DIR}}/include/api.h
                ${{BASE_DIR}}/include/codes.h
                ${{BASE_DIR}}/include/fips202.h
                ${{BASE_DIR}}/include/fq_arith.h
                ${{BASE_DIR}}/include/keccakf1600.h
                ${{BASE_DIR}}/include/LESS.h
                ${{BASE_DIR}}/include/monomial_mat.h
                ${{BASE_DIR}}/include/parameters.h
                ${{BASE_DIR}}/include/rng.h
                ${{BASE_DIR}}/include/seedtree.h
                ${{BASE_DIR}}/include/sha3.h
                ${{BASE_DIR}}/include/utils.h
                )
        
        if(STANDALONE_KECCAK)
            message(STATUS "Employing standalone SHA-3")
            set(KECCAK_EXTERNAL_LIB "")
            set(KECCAK_EXTERNAL_ENABLE "")
            list(APPEND COMMON_SOURCES ${{BASE_DIR}}/lib/keccakf1600.c)
            list(APPEND COMMON_SOURCES ${{BASE_DIR}}/lib/fips202.c)
        else()
            message(STATUS "Employing libkeccak")
            set(KECCAK_EXTERNAL_LIB keccak)
            set(KECCAK_EXTERNAL_ENABLE "-DSHA_3_LIBKECCAK")
        endif()
        
        set(SOURCES
                ${{COMMON_SOURCES}}
                ${{BASE_DIR}}/lib/codes.c
                ${{BASE_DIR}}/lib/LESS.c
                ${{BASE_DIR}}/lib/monomial.c
                ${{BASE_DIR}}/lib/rng.c
                ${{BASE_DIR}}/lib/seedtree.c
                ${{BASE_DIR}}/lib/utils.c
                ${{BASE_DIR}}/lib/sign.c
                )
        if(AVX2_OPTIMIZED)
                set(SOURCES ${{SOURCES}} ${{BASE_DIR}}/lib/avx2_table.c)
                set(HEADERS ${{HEADERS}} ${{BASE_DIR}}/include/avx2_macro.h)
                message("------------AVX2 OPT is ON")
        endif()
        
        set(BUILD build)
        set(BUILD_KEYPAIR {candidate}_keypair)
        set(BUILD_SIGN {candidate}_sign)
        
        foreach(category RANGE 1 5 2)
            if(category EQUAL 1)
                set(PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE)
            else()
                set(PARAM_TARGETS SIG_SIZE PK_SIZE)
            endif()
            foreach(optimiz_target ${{PARAM_TARGETS}})
            
                set(TARGET_BINARY_NAME {test_keypair}_${{category}}_${{optimiz_target}})  
                add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                        ./{candidate}_keypair/{test_keypair}.c)
                target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                        ${{BASE_DIR}}/include
                        ./include)'''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
                target_link_libraries(${{TARGET_BINARY_NAME}} {libs_variables} ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                
                set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
                set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                        COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
                
                
                #Test harness for crypto_sign
                set(TARGET_BINARY_NAME {test_sign}_${{category}}_${{optimiz_target}})
                add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                        ./{candidate}_sign/{test_sign}.c)   
                target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                        ${{BASE_DIR}}/include
                        ./include)'''
        if link_flag:
            cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE {link_flag})'
        cmake_file_content += f'''
                target_link_libraries(${{TARGET_BINARY_NAME}} {libs_variables} ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                
                set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}}) 
                set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                        COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}}")
                
                #endforeach(t_harness)
            endforeach(optimiz_target)
        endforeach(category)
        '''
    with open(path_to_cmakelists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content))

def makefile_candidate(path_to_makefile_folder, subfolder, tool_type, candidate,
                       security_level=None, implementation_type='opt'):
    if candidate == "mirith":
        makefile_mirith(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "mira":
        makefile_mira(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "mqom":
        makefile_mqom(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "perk":
        makefile_perk(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "ryde":
        makefile_ryde(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "pqsigrm":
        makefile_pqsigrm(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "wave":
        makefile_wave(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "prov":
        makefile_prov(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "qr_uov":
        makefile_qr_uov(path_to_makefile_folder, subfolder, tool_type, candidate,  implementation_type)
    if candidate == "snova":
        makefile_snova(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "tuov":
        makefile_tuov(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "uov":
        makefile_uov(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "vox":
        makefile_vox(path_to_makefile_folder, subfolder, tool_type, candidate, security_level, implementation_type)
    if candidate == "aimer":
        makefile_aimer(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "ascon_sign":
        makefile_ascon_sign(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "faest":
        makefile_faest(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "sphincs_alpha":
        makefile_sphincs_alpha(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "preon":
        makefile_preon(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "squirrels":
        makefile_squirrels(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "raccoon":
        makefile_raccoon(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "hawk":
        makefile_hawk(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "meds":
        makefile_meds(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "hufu":
        makefile_hufu(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "meds":
        makefile_meds(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "fuleeca":
        makefile_fuleeca(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "eaglesign":
        makefile_eaglesign(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "ehtv3v4":
        makefile_ehtv3v4(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "sdith":
        makefile_sdith(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "biscuit":
        makefile_biscuit(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "dme_sign":
        makefile_dme_sign(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "hppc":
        makefile_hppc(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "wise":
        makefile_wise(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "alteq":
        makefile_alteq(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "emle":
        makefile_emle(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "kaz_sign":
        makefile_kaz_sign(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "xifrat":
        makefile_xifrat(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    # =======================================================================================
    # The following candidates are supposed to be compiled with cmake. But if the chosen tool is flowtracker,
    # then these candidates are compiled with Makefile. Indeed, the function 'cmake_cross', etc., will generate
    # a Makefile instead of a CMakeLists.txt
    # ========================= LESS ==============================================
    # The function makefile_less is meant for the use of the tool flowtracker only
    if candidate == "cross":
        cmake_cross(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "less":
        cmake_less(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "mayo":
        cmake_mayo(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)
    if candidate == "haetae":
        print('==========CALL: cmake_haetae')
        cmake_haetae(path_to_makefile_folder, subfolder, tool_type, candidate, implementation_type)


def cmake_candidate(path_to_cmake_lists, subfolder, tool_type, candidate, implementation_type='opt'):
    if candidate == "cross":
        cmake_cross(path_to_cmake_lists, subfolder, tool_type, candidate, implementation_type)
    if candidate == "mayo":
        cmake_mayo(path_to_cmake_lists, subfolder, tool_type, candidate, implementation_type)
    if candidate == "less":
        cmake_less(path_to_cmake_lists, subfolder, tool_type, candidate, implementation_type)
    if candidate == "haetae":
        print('------CALL: cmake_haetae')
        cmake_haetae(path_to_cmake_lists, subfolder, tool_type, candidate, implementation_type)
    if candidate == "sqisign":
        pass


# Candidates that are compiled with a sh script
def sh_candidate(path_to_sh_file, subfolder, tool_type, candidate, implementation_type='opt'):
    if candidate == "raccoon":
        sh_script = 'compile_raccoon'
        sh_build_raccoon(path_to_sh_file, sh_script, subfolder, tool_type, candidate, implementation_type)