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


# The candidates with the "[TODO]" are those with vulnerabilities (broken). We haven't tested them.

# ============================== MPC-IN-THE-HEAD ================
# ===============================================================

# ================================ MIRITH ========================
def makefile_mirith(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c ,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/sign.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        CFLAGS=-std=c11 -Wall -Wextra -pedantic -mavx2 -g 
        
        BASE_DIR = ../../{subfolder}
        
        
        DEPS=$(wildcard $(BASE_DIR)/*.h)
        OBJ=$(patsubst $(BASE_DIR)/%.c,$(BASE_DIR)/%.o,$(wildcard $(BASE_DIR)/*.c)) 
        OBJ+=$(patsubst $(BASE_DIR)/%.s,$(BASE_DIR)/%.o,$(wildcard $(BASE_DIR)/*.s))
        
        UNAME_S := $(shell uname -s)
        ifeq ($(UNAME_S),Linux)
        \tASMFLAGS := ${{CFLAGS}}
        endif
        ifeq ($(UNAME_S),Darwin)
        \tASMFLAGS := ${{CFLAGS}} -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
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
def makefile_perk(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}/src
        
        CRYPTOCODE_INCS = ../../{subfolder}/lib/cryptocode
        RANDOMBYTES_INCS = ../../{subfolder}/lib/randombytes
        XKCP_INCS = ../../{subfolder}/lib/XKCP
        
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c ,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/sign.c
        
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
        \t$(CC) -emit-llvm -I $(CRYPTOCODE_INCS) -I $(RANDOMBYTES_INCS) -I $(XKCP_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        \t-Wundef -Wshadow  -mavx2 -mpclmul -msse4.2 -maes
            #-Wno-newline-eof
        ASMFLAGS := -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
        LDFLAGS:= -lcrypto
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
        \t@echo -e "### Compiling perk-128-fast-3 file $@"
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
def makefile_mqom(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        ALL_FLAGS?= -DPARAM_HYPERCUBE_7R -DPARAM_GF31 -DPARAM_L1 -DPARAM_RND_EXPANSION_X4\
         -DHASHX4 -DXOFX4 -DPRGX4 -DNDEBUG -mavx
         
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c  $(SRC_DIR)/keygen.c,$(wildcard $(SRC_DIR)/*.c))
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
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(KEYGEN) $(SRC) $(INCS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm $(ALL_FLAGS) -I $(HASH_PATH)/avx2 -c -g $(KEYGEN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        \t-DPARAM_HYPERCUBE_7R -DPARAM_GF31 -DPARAM_L1 -DPARAM_RND_EXPANSION_X4 -DHASHX4 -DXOFX4  -DPRGX4 -DNDEBUG -mavx
        
        ALL_FLAGS+=$(EXTRA_ALL_FLAGS) -g 
        
        BASE_DIR = ../../{subfolder}
        
        SYM_OBJ= $(BASE_DIR)/rnd.o $(BASE_DIR)/hash.o $(BASE_DIR)/xof.o
        ARITH_OBJ= $(BASE_DIR)/gf31-matrix.o $(BASE_DIR)/gf31.o
        MPC_OBJ= $(BASE_DIR)/mpc.o $(BASE_DIR)/witness.o $(BASE_DIR)/serialization-specific.o $(BASE_DIR)/precomputed.o
        CORE_OBJ= $(BASE_DIR)/keygen.o $(BASE_DIR)/sign.o $(BASE_DIR)/views.o $(BASE_DIR)/commit.o \
        \t$(BASE_DIR)/sign-mpcith-hypercube.o $(BASE_DIR)/tree.o
        
        HASH_PATH=$(BASE_DIR)/sha3
        HASH_MAKE_OPTIONS=PLATFORM=avx2 
        HASH_INCLUDE=-I$(BASE_DIR)/sha3 -I. -I$(BASE_DIR)/sha3/avx2
        
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
def makefile_ryde(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}/src
        
        
        RANDOMBYTES_INCS = ../../{subfolder}/lib/randombytes
        XKCP_INCS = ../../{subfolder}/lib/XKCP
        RBC_INCS = $(BASE_DIR)/rbc-31
        RBC_SRC = $(wildcard $(BASE_DIR)/rbc-31/*.c))
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c ,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/sign.c
        
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
        \t$(CC) -emit-llvm -I $(RANDOMBYTES_INCS) -I $(XKCP_INCS) -I $(RBC_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4
        C_FLAGS_VERBOSE:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -DVERBOSE
        
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
        
        RBC_SRC:=$(BASE_DIR)/src/rbc-31
        RBC_INCLUDE:=-I $(RBC_SRC)
        
        SRC:=$(BASE_DIR)/src
        INCLUDE:=-I $(BASE_DIR)/src $(RBC_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) $(RANDOMBYTES_INCLUDE)
        
        RYDE_OBJS:=rbc_31_elt.o rbc_31_vec.o rbc_31_qpoly.o rbc_31_vspace.o rbc_31_mat.o keypair.o signature.o \
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


# =============================== MIRA =================================
def makefile_mira(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = ''
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}/src
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/nist_sign.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -g 
        
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


# =================================== SDITH ====================================
def makefile_sdith(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}/src
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/nist_sign.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -g 
        
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
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
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
        \t$(CC) $(TOOL_FLAGs) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^)\
         $(INCLUDE) $(XKCP_LINKER) $(TOOL_LIBS) -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files
        \t@echo -e "### Compiling MIRA-128F (test harness sign)"
        \t$(CC) $(TOOL_FLAGs) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^) \
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


# =============================== CROSS =========================================
# [TODO: Modify and remove if condition ]
def cmake_cross1(path_to_cmake_lists, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    cmake_file_content_src_block1 = f'''
    cmake_minimum_required(VERSION 3.7)
    project(CROSS C)
    set(CMAKE_C_STANDARD 11)
    
    set(CC gcc)
    
    set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -march=haswell -O3 -g") 
    
    set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} ${{SANITIZE}}")
    message("Compilation flags:" ${{CMAKE_C_FLAGS}})
    
    # default compilation picks reference codebase
    if(NOT DEFINED REFERENCE)
       set(REFERENCE 0)
    endif()
    
    set(CSPRNG_ALGO SHAKE_CSPRNG)
    set(HASH_ALGO SHA3_HASH)
    
    find_library(KECCAK_LIB keccak)
    if(NOT KECCAK_LIB)
     set(STANDALONE_KECCAK 1)
    endif()
    '''
    cmake_file_content_find_ctgrind_lib = ""
    if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
        cmake_file_content_find_ctgrind_lib = f'''
        find_library(CT_GRIND_LIB ctgrind)
        if(NOT CT_GRIND_LIB)
        \tmessage("${{CT_GRIND_LIB}} library not found")
        endif()
        '''
    cmake_file_content_src_block2 = f'''
    # selection of specialized compilation units differing between ref and opt
    # implementations.
    set(REFERENCE_CODE_DIR ../../Reference_Implementation) 
    set(OPTIMIZED_CODE_DIR ../../Optimized_Implementation) 
    
    message("Compiling optimized code")
    set(SPEC_HEADERS )
    set(SPEC_SOURCES
            ${{OPTIMIZED_CODE_DIR}}/lib/aes256.c
    )
    # endif()
    
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
    '''
    cmake_file_content_block_loop = f'''
    foreach(category RANGE 1 5 2)
        set(RSDP_VARIANTS RSDP RSDPG)
        foreach(RSDP_VARIANT ${{RSDP_VARIANTS}})
            set(PARAM_TARGETS SIG_SIZE SPEED)
            foreach(optimiz_target ${{PARAM_TARGETS}})
            '''
    cmake_file_content_loop_content_block_keypair = ""
    if tool_name.lower() == 'binsec':
        cmake_file_content_loop_content_block_keypair = f'''
                 #crypto_sign_keypair test harness binary
                 set(TARGET_BINARY_NAME {test_keypair}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./{candidate}_keypair/{test_keypair}.c)
                target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static) 
                target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                '''
    if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
        cmake_file_content_loop_content_block_keypair = f'''
                 #crypto_sign_keypair taint binary
                 set(TARGET_BINARY_NAME {test_keypair}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./{candidate}_keypair/{test_keypair}.c)
                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''
    cmake_file_content_loop_content_block2 = f'''
                 set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
                 set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                     COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 -D${{CSPRNG_ALGO}}=1 \
                      -D${{HASH_ALGO}}=1 -D${{RSDP_VARIANT}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
                '''
    cmake_file_content_loop_content_block_sign = ""
    if tool_name.lower() == 'binsec':
        cmake_file_content_loop_content_block_sign = f'''            
                 #crypto_sign test harness binary
                 set(TARGET_BINARY_NAME {test_sign}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./{candidate}_sign/{test_sign}.c)
                 target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
        cmake_file_content_loop_content_block_sign = f'''
                 #crypto_sign test harness binary
                 set(TARGET_BINARY_NAME {test_sign}_${{category}}_${{RSDP_VARIANT}}_${{optimiz_target}}) 
                 
                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                                    ./{candidate}_sign/{test_sign}.c)
                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                                            ${{BASE_DIR}}/include
                                            ./include) 
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
                 target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
        '''
    cmake_file_content_loop_content_block3 = f'''
                 set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}})   
                 set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                     COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 -D${{CSPRNG_ALGO}}=1 \
                     -D${{HASH_ALGO}}=1 -D${{RSDP_VARIANT}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
                '''
    cmake_file_content_block_loop_end = f'''             
            endforeach(optimiz_target) 
        endforeach(RSDP_VARIANT)
    endforeach(category)
    '''
    with open(path_to_cmake_lists, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block1))
        if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
            cmake_file.write(textwrap.dedent(cmake_file_content_find_ctgrind_lib))
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_keypair))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_sign))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block3))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop_end))


# path_to_makefile_folder, subfolder, tool_name, candidate


def cmake_cross(path_to_cmakelists_folder, subfolder, tool_name, candidate):
    loop_block_test = f'''
    MKDIR_P = mkdir -p
    .PHONY: directories
    
    all: directories test
    
    directories: folders
    
    folders:
        mkdir -p $(BUILD_FOLDERS)
    
    
    test: $(SIGN) $(SRC) $(INCS)
        for CATEGORY in 1 3 5; do \
            for RSDP_VARIANT in RSDP RSDPG; do \
                for PARAM_TARGET in SIG_SIZE SPEED; do \
                    COMPILE_FLAGS  := -DCATEGORY_${{CATEGORY}}=1 -D${{PARAM_TARGET}}=1 -D${{CSPRNG_ALGO}}=1 -D$(HASH_ALGO)=1 -D$(RSDP_VARIANT)=1 ; \
                    EXEC_BC := $(KEYPAIR)_$(CATEGORY)_$(RSDP_VARIANT)_$(PARAM_TARGET).bc ; \
                    $(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/${{EXEC_BC}} ; \
                done ; \
            done ; \
        done
    '''
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_cmakelists = f'{path_to_cmakelists_folder}/CMakeLists.txt'
    cmake_file_content = ''
    target_link_opt_block = ''
    link_flag = ''
    if tool_flags:
        if '-static' in tool_flags:
            link_flag = '-static'
    libs_str = ""
    # tool_libs = tool_libs.replace("-lm", "")
    # tool_libs = tool_libs.strip()
    libs_list = []
    if tool_libs:
        libs_str = tool_libs.replace("-l", "")
        libs_list = libs_str.split()
    if tool_name == 'flowtracker':
        print(":::: flowtracker wit cross")
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
        
        
        INCS = $(wildcard $(BASE_DIR)/include/*.h)
        SRC  = $(filter-out  $(BASE_DIR)/lib/sign.c, $(wildcard $(BASE_DIR)/lib/*.c))
        SRC  += $(OPTIMIZED_CODE_DIR)/lib/aes256.c
        
        
        SIGN = $(BASE_DIR)/lib/sign.c
        
        
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
        cmake_minimum_required(VERSION 3.7)
        project(CROSS C)
        set(CMAKE_C_STANDARD 11)
        
        set(CC gcc)
        
        set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -march=haswell -O3 -g") 
        
        set(CMAKE_C_FLAGS  "${{CMAKE_C_FLAGS}} ${{SANITIZE}}")
        message("Compilation flags:" ${{CMAKE_C_FLAGS}})
        
        # default compilation picks reference codebase
        if(NOT DEFINED REFERENCE)
           set(REFERENCE 0)
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
        
        message("Compiling optimized code")
        set(SPEC_HEADERS )
        set(SPEC_SOURCES
                ${{OPTIMIZED_CODE_DIR}}/lib/aes256.c
        )
        # endif()
        
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
                                                ${{BASE_DIR}}/include
                                                ./include) 
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
                                                ${{BASE_DIR}}/include
                                                ./include) 
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
def makefile_pqsigrm(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    subfolder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../{subfolder}/src
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
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
         
        
        
        $(EXECUTABLE_KEYPAIR_BC): $(KEY_PAIR) $(SRC) $(INCS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) -emit-llvm -c -g $(KEY_PAIR) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
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
# [TODO: Modify and remove if condition]
def cmake_less1(path_to_cmakelist, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    subfolder = ""
    path_to_cmakelist = path_to_cmakelist+'/CMakeLists.txt'
    cmake_file_content_src_block1 = f'''
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
    
    set(CMAKE_C_STANDARD 11)
    
    find_library(KECCAK_LIB keccak)
    if(NOT KECCAK_LIB)
        set(STANDALONE_KECCAK 1)
    endif()
    
    # selection of specialized compilation units differing between ref and opt implementations.
    option(AVX2_OPTIMIZED "Use the AVX2 Optimized Implementation. Else the Reference Implementation will be used." OFF)
    
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
    
    '''
    cmake_file_content_find_ctgrind_lib = ""
    if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
        cmake_file_content_find_ctgrind_lib = f'''
        find_library(CT_GRIND_LIB ctgrind)
        if(NOT CT_GRIND_LIB)
        \tmessage("${{CT_GRIND_LIB}} library not found")
        endif()
        find_library(CT_GRIND_SHARED_LIB ctgrind.so)
        if(NOT CT_GRIND_SHARED_LIB)
        \tmessage("${{CT_GRIND_SHARED_LIB}} library not found")
        \tset(CT_GRIND_SHARED_LIB /usr/lib/libctgrind.so)
        endif()
        '''
    cmake_file_content_src_block2 = f'''
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
    set(BUILD build)
    set(BUILD_KEYPAIR {candidate}_keypair)
    set(BUILD_SIGN {candidate}_sign)
    '''
    cmake_file_content_block_loop = f'''
    foreach(category RANGE 1 5 2)
        if(category EQUAL 1)
            set(PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE)
        else()
            set(PARAM_TARGETS SIG_SIZE PK_SIZE)
        endif()
        foreach(optimiz_target ${{PARAM_TARGETS}})
        '''
    cmake_file_content_loop_content_block_keypair = ""
    if tool_name.lower() == 'binsec':
        cmake_file_content_loop_content_block_keypair = f'''
            set(TEST_HARNESS ./{tool_type}/{candidate}_keypair/{test_keypair}.c \
            ./{tool_name}/{candidate}_sign/{test_sign}.c)
            set(TARGET_BINARY_NAME {test_keypair}_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_keypair/{test_keypair}.c)
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
        cmake_file_content_loop_content_block_keypair = f'''
        set(TARGET_BINARY_NAME {test_keypair}_${{category}}_${{optimiz_target}})  
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_keypair/{test_keypair}.c)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''

    cmake_file_content_loop_content_block2 = f'''
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
            '''
    cmake_file_content_loop_content_block_sign = ""
    if tool_name.lower() == 'binsec':
        cmake_file_content_loop_content_block_sign = f'''
            #Test harness for crypto_sign
            set(TARGET_BINARY_NAME {test_sign}_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_sign/{test_sign}.c)   
            target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            '''
    if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
        cmake_file_content_loop_content_block_sign = f'''    
        #Test harness for crypto_sign
            set(TARGET_BINARY_NAME {test_sign}_sign_${{category}}_${{optimiz_target}})
            add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
                    ./{candidate}_sign/{test_sign}.c)   
            target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
                    ${{BASE_DIR}}/include
                    ./include)
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
            target_link_libraries(${{TARGET_BINARY_NAME}} m ${{CT_GRIND_LIB}} ${{CT_GRIND_SHARED_LIB}})
            '''
    cmake_file_content_loop_content_block3 = f'''
            set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}}) 
            set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}}")
            '''
    cmake_file_content_block_loop_end = f'''
            #endforeach(t_harness)
        endforeach(optimiz_target)
    endforeach(category)
    '''
    with open(path_to_cmakelist, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block1))
        if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
            cmake_file.write(textwrap.dedent(cmake_file_content_find_ctgrind_lib))
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_keypair))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block2))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_sign))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block3))
        cmake_file.write(textwrap.dedent(cmake_file_content_block_loop_end))



def cmake_less(path_to_cmakelists_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_cmakelists = f'{path_to_cmakelists_folder}/CMakeLists.txt'
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
        
        
        
        INCS = $(wildcard $(BASE_DIR)/include/*.h)
        SRC  = $(filter-out  $(BASE_DIR)/lib/sign.c, $(wildcard $(BASE_DIR)/lib/*.c))
        
        
        SIGN = $(BASE_DIR)/lib/sign.c
        
        
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
        option(AVX2_OPTIMIZED "Use the AVX2 Optimized Implementation. Else the Reference Implementation will be used." OFF)
        
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
def makefile_fuleeca(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
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
    
    
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(TOOL_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(TOOL_LIBS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(TOOL_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(TOOL_LIBS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    
    
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ============================= MEDS =====================================
# [TODO]
def makefile_meds(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    
    TOOL_LIBS = {tool_libs}
    TOOL_FLAGS = {tool_flags}
    
    EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
    EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
    
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(TOOL_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(TOOL_LIBS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(TOOL_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(TOOL_LIBS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =================================== WAVE ======================================
def makefile_wave(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/api.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/api.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        CFLAGS=-I. -O3 -Wall -march=native
        LDFLAGS=-lcrypto
        
        BASE_DIR = ../../{subfolder}
        
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


def makefile_squirrels(path_to_makefile_folder, subfolder, tool_name, candidate):
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
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/nist.c, $(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/nist.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        
        OBJ1 = $(BASE_DIR)/build/codec.o $(BASE_DIR)/build/common.o $(BASE_DIR)/build/keygen_lll.o \
        $(BASE_DIR)/build/keygen.o  $(BASE_DIR)/build/minors.o $(BASE_DIR)/build/nist.o $(BASE_DIR)/build/normaldist.o \
        $(BASE_DIR)/build/param.o $(BASE_DIR)/build/sampler.o $(BASE_DIR)/build/shake.o $(BASE_DIR)/build/sign.o \
        $(BASE_DIR)/build/vector.o
        
        
        HEAD1 = $(BASE_DIR)/api.h $(BASE_DIR)/fpr.h $(BASE_DIR)/inner.h $(BASE_DIR)/param.h
        
        BUILD					= build
        BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
        BUILD_SIGN			= $(BUILD)/{candidate}_sign 
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_keypair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_sign}
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        all: $(BASE_DIR)/lib $(BASE_DIR)/build $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        
        $(BASE_DIR)/lib:
        \tmake -C ../../../lib 
        
        $(BASE_DIR)/build:
        \t-mkdir $(BASE_DIR)/build
        
        clean:
        \t-rm -f  $(OBJ1)  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        
        
       
        $(BASE_DIR)/build/codec.o: $(BASE_DIR)/codec.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/codec.o $(BASE_DIR)/codec.c
        
        $(BASE_DIR)/build/common.o: $(BASE_DIR)/common.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/common.o $(BASE_DIR)/common.c
        
        $(BASE_DIR)/build/keygen_lll.o: $(BASE_DIR)/keygen_lll.cpp $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/keygen_lll.o $(BASE_DIR)/keygen_lll.cpp
        
        $(BASE_DIR)/build/keygen.o: $(BASE_DIR)/keygen.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/keygen.o $(BASE_DIR)/keygen.c
        
        $(BASE_DIR)/build/minors.o: $(BASE_DIR)/minors.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/minors.o $(BASE_DIR)/minors.c
        
        
        $(BASE_DIR)/build/normaldist.o: $(BASE_DIR)/normaldist.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/normaldist.o $(BASE_DIR)/normaldist.c
        
        $(BASE_DIR)/build/param.o: $(BASE_DIR)/param.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/param.o $(BASE_DIR)/param.c
        
        $(BASE_DIR)/build/sampler.o: $(BASE_DIR)/sampler.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/sampler.o $(BASE_DIR)/sampler.c
        
        $(BASE_DIR)/build/shake.o: $(BASE_DIR)/shake.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/shake.o $(BASE_DIR)/shake.c
        
        $(BASE_DIR)/build/sign.o: $(BASE_DIR)/sign.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c
        
        $(BASE_DIR)/build/vector.o: $(BASE_DIR)/vector.c $(HEAD1)
        \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/vector.o $(BASE_DIR)/vector.c
        
    
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(HEAD1) $(BASE_DIR)/api.h 
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) $(TOOL_LIBS) -I . -c -o $(BUILD)/$$(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_KEYPAIR).c 
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(HEAD1) $(BASE_DIR)/api.h 
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS)  $(TOOL_LIBS) -I . -c -o $(BUILD)/$$(EXECUTABLE_SIGN)  $(EXECUTABLE_SIGN).c 
        
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# =============================== HAETAE ===================================
# [TODO: Modify and remove if condition]

def cmake_haetae(path_to_cmakelist, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_cmakelist = path_to_cmakelist+'/CMakeLists.txt'
    cmake_file_content_src_block = f'''
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
      ${{BASE_DIR}}/src/consts.c
      ${{BASE_DIR}}/src/poly.c
      ${{BASE_DIR}}/src/ntt.S
      ${{BASE_DIR}}/src/invntt.S
      ${{BASE_DIR}}/src/pointwise.S
      ${{BASE_DIR}}/src/shuffle.S
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
    set(FIPS202_SRCS ${{BASE_DIR}}/src/fips202.c ${{BASE_DIR}}/src/fips202x4.c ${{BASE_DIR}}/src/f1600x4.S)
    
    if(MSVC)
      set(C_FLAGS /nologo /O2 /W4 /wd4146 /wd4244)
    else()
      set(C_FLAGS -O3 -fomit-frame-pointer -mavx2 -Wall -Wextra -Wpedantic)
    endif()
    
    find_package(OpenSSL REQUIRED)
    
    include_directories(${{BASE_DIR}}/include)
    include_directories(${{BASE_DIR}}/api)
    link_directories(${{BASE_DIR}}/libs)
    
    add_library(fips202 SHARED ${{FIPS202_SRCS}})
    target_compile_options(fips202 PRIVATE -O3 -mavx2 -fomit-frame-pointer -fPIC)
    add_library(RNG SHARED ${{PROJECT_SOURCE_DIR}}/${{BASE_DIR}}//src/randombytes.c)
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
    cmake_file_content_loop_content_block_executables = ""
    if tool_name.lower() == 'binsec':
        cmake_file_content_loop_content_block_executables = f'''
        foreach(category RANGE 2 3 5)
            \t\tset(TARGET_KEYPAIR_BINARY_NAME {test_keypair}_${{category}})
            \t\tadd_executable(${{TARGET_KEYPAIR_BINARY_NAME}} ./{candidate}_keypair/{test_keypair}.c)
            \t\ttarget_link_libraries(${{TARGET_KEYPAIR_BINARY_NAME}}  ${{LIB_NAME${{category}}}} OpenSSL::Crypto)
            \t\ttarget_include_directories(${{TARGET_KEYPAIR_BINARY_NAME}} PUBLIC ../include)
            \t\ttarget_compile_definitions(${{TARGET_KEYPAIR_BINARY_NAME}} PUBLIC HAETAE_MODE=${{category}})
            \t\tset_target_properties(${{TARGET_KEYPAIR_BINARY_NAME}} PROPERTIES \
            RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
            
            \t\tset(TARGET_SIGN_BINARY_NAME {test_sign}_${{category}})
            \t\tadd_executable(${{TARGET_SIGN_BINARY_NAME}} ./{candidate}_sign/{test_sign}.c)
            \t\ttarget_include_directories(${{TARGET_SIGN_BINARY_NAME}} PUBLIC ../include)
            \t\ttarget_compile_definitions(${{TARGET_SIGN_BINARY_NAME}} PUBLIC HAETAE_MODE=${{category}})
            \t\ttarget_link_libraries(${{TARGET_SIGN_BINARY_NAME}}  ${{LIB_NAME${{category}}}} OpenSSL::Crypto)
        endforeach(category) 
        '''
    if 'ctgrind' in tool_name.lower() or 'ct_grind' in tool_name.lower():
        cmake_file_content_loop_content_block_executables = f'''
        find_library(CT_GRIND_LIB ctgrind)
        foreach(category RANGE 2 3 5)
        \t\tset(TARGET_KEYPAIR_BINARY_NAME {test_sign}_${{category}})
        \t\tadd_executable(${{TARGET_KEYPAIR_BINARY_NAME}} ./{candidate}_keypair/{test_sign}.c)
        \t\ttarget_link_libraries(${{TARGET_KEYPAIR_BINARY_NAME}}  ${{LIB_NAME${{category}}}}\
         ${{CT_GRIND_LIB}} OpenSSL::Crypto)
        \t\ttarget_include_directories(${{TARGET_KEYPAIR_BINARY_NAME}} PUBLIC ../include)
        \t\ttarget_compile_definitions(${{TARGET_KEYPAIR_BINARY_NAME}} PUBLIC HAETAE_MODE=${{category}})
        \t\tset_target_properties(${{TARGET_KEYPAIR_BINARY_NAME}} PROPERTIES\
         RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
        
        \t\tset(TARGET_SIGN_BINARY_NAME {test_sign}_${{category}}_1)
        \t\tadd_executable(${{TARGET_SIGN_BINARY_NAME}} ./{candidate}_sign/{test_sign}.c)
        \t\ttarget_include_directories(${{TARGET_SIGN_BINARY_NAME}} PUBLIC ../include)
        \t\ttarget_compile_definitions(${{TARGET_SIGN_BINARY_NAME}} PUBLIC HAETAE_MODE=${{category}})
        \t\ttarget_link_libraries(${{TARGET_SIGN_BINARY_NAME}}  ${{LIB_NAME${{category}}}}\
         ${{CT_GRIND_LIB}} OpenSSL::Crypto)
        \t\tset_target_properties(${{TARGET_SIGN_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}})
        endforeach(category)
        '''
    with open(path_to_cmakelist, "w") as cmake_file:
        cmake_file.write(textwrap.dedent(cmake_file_content_src_block))
        cmake_file.write(textwrap.dedent(cmake_file_content_loop_content_block_executables))


# =========================== EAGLESIGN =========================================
# [TODO]
def makefile_eaglesign(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign = gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) -lctgrind
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) -lctgrind
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# ========================== ehtv3v4 ================================
# [TODO]
def makefile_ehtv3v4(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign =gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) -lctgrind
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) -lctgrind
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# =========================== HAWK ============================================
def makefile_hawk(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/api.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/api.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
# [TODO]
def makefile_hufu(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    subfolder = ""
    src_folder = 'pqsigrm613'
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags = f'''
    CC = gcc
    LDFLAGS =  -L/usr/local/lib
    CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
    LIBFLAGS = -lcrypto -lssl -lm
    
    BASE_DIR = ../{src_folder}
     
    
    CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')
    
    OBJS = ${{CFILES}}
    
    BUILD					= build
    BUILD_KEYPAIR			= $(BUILD)/{candidate}_keypair
    BUILD_SIGN			= $(BUILD)/{candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign = gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        
        BINSEC_STATIC_FLAG  = -static
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN		    = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        CT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        
        EXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        EXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_object_files = f'''
    ifeq ($(DEBUG), 1)
    \tDBG_FLAGS = -g -O0 -DDEBUG
    else
    \tDBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
    endif
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    %.o : %.c
    \t$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
    $(EXECUTABLE_KEYPAIR): ${{OBJS}} {candidate}_keypair/$(EXECUTABLE_KEYPAIR).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    $(EXECUTABLE_SIGN): ${{OBJS}} {candidate}_sign/$(EXECUTABLE_SIGN).c
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_SIGN)
    \t$(CC) $(LDFLAGS) $(CFLAGS) $(BINSEC_STATIC_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS)
    
    matrix.o : matrix.h
    rng.o : rng.h
    api.o : api.h
    '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): ${{OBJS}} $(EXECUTABLE_KEYPAIR).c
        \tmkdir -p $(BUILD)  
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(CT_GRIND_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) -lctgrind
    
        $(EXECUTABLE_SIGN): ${{OBJS}} $(EXECUTABLE_SIGN).c
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(LDFLAGS)  $(CFLAGS) $(CT_GRIND_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) -lctgrind
    
        matrix.o : matrix.h
        rng.o : rng.h
        api.o : api.h
        '''
    makefile_content_block_clean = f'''
    clean:
    \tcd  $(BASE_DIR)/src; rm -f *.o; cd ..
    \trm -f *.o
    \t cd ../../{candidate}
    \trm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# =========================== RACCOON =============================
def sh_build_raccoon(path_to_sh_script_folder, sh_script, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
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
    gcc -o {build}/{executable_keypair} -Wall -O2 {tool_flags} {executable_keypair}.c\
    $SRC -lcrypto {tool_libs}
    
    mkdir -p {build}
    mkdir -p {build_sign}
    gcc -o {build}/{executable_sign} -Wall -O2 {tool_flags} {executable_sign}.c \
    $SRC -lcrypto {tool_libs}
    '''
    with open(path_to_sh_script, "w") as mfile:
        mfile.write(textwrap.dedent(block_binary_files))


def makefile_raccoon(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = f'''
    CC = clang
    
    BASE_DIR = ../../{subfolder}
    
    INCS = $(wildcard $(BASE_DIR)/*.h)
    #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
    SRC  = $(filter-out  $(SRC_DIR)/racc_api.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
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
     
    
    
    $(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
    \tmkdir -p $(BUILD)
    \tmkdir -p $(BUILD_KEYPAIR)
    \t$(CC) -emit-llvm -I $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
    
    $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
    \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
    
    $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
                                 rng_outside_instance_folder="no"):
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
                sh_build_raccoon(path_to_build_folder, sh_script, instance, tool_type, candidate)

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
                    sh_build_raccoon(path_to_build_folder, sh_script, instance, tool_type, candidate)
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

# ================================== QR-UOV ==========================================
# [TODO:Rename functions if needed/if not working with new script keep old script ...]

def qr_uov_main_makefile(path_to_tool_folder, subfolder):
    path_to_makefile = path_to_tool_folder+'/Makefile'
    makefile_content = f'''
    platform := portable64
    
    BASE_DIR = ..
    subdirs :={subfolder}
    
    .PHONY: all clean $(subdirs)
    
    all: $(subdirs)
    
    $(subdirs): $(BASE_DIR)/qruov_config.src
    #\tsh -c "cd .. || true"
    \tmkdir -p $(BASE_DIR)/$@/$(platform)
    \tgrep $@ $(BASE_DIR)/qruov_config.src > $(BASE_DIR)/$@/$(platform)/qruov_config.txt
    \tsh -c "cd $(BASE_DIR)/$@/$(platform) ; ln -s ../$(BASE_DIR)/$(platform)/* . || true"
    \t$(MAKE) -C $(BASE_DIR)/$@/$(platform)
    
    clean:
    \trm -rf $(subdirs)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


def makefile_qr_uov(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content = ''
    target_link_opt_block = ''
    link_flag = ''
    if tool_flags:
        if '-static ' in tool_flags:
            link_flag = '-static'
    libs_str = ""
    # tool_libs = tool_libs.replace("-lm", "")
    # tool_libs = tool_libs.strip()
    if tool_libs:
        libs_str = tool_libs.replace("-l", "")
        libs_list = libs_str.split()
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}/portable64
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        SRC  = $(filter-out  $(BASE_DIR)/sign.c $(BASE_DIR)/PQCgenKAT_sign.c, $(wildcard $(BASE_DIR)/*.c))
        
        
        
        SIGN = $(BASE_DIR)/sign.c
        
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        CFLAGS=-O3 -fomit-frame-pointer -Wno-unused-result -Wno-aggressive-loop-optimizations \
        -I. -fopenmp # -DQRUOV_HASH_LEGACY # -ggdb3 
        LDFLAGS=-lcrypto -Wl,-Bstatic -lcrypto -Wl,-Bdynamic -lm
        
        BASE_DIR = ../../{subfolder}/portable64
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


def custom_init_compile_qr_uov(custom_makefile_folder, instance_folders_list):
    path_to_tool_folder = f'multivariate/qr_uov/QR_UOV/Optimized_Implementation/{custom_makefile_folder}'
    if not os.path.isdir(path_to_tool_folder):
        cmd = ["mkdir", "-p", path_to_tool_folder]
        subprocess.call(cmd, stdin=sys.stdin)
    subfolders = " ".join(instance_folders_list)
    qr_uov_main_makefile(path_to_tool_folder, subfolders)
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
                       with_core_dump="no"):
    add_includes = []
    compile_with_cmake = 'no'
    custom_folder = "custom_makefile"
    for tool in tools_list:
        custom_init_compile_qr_uov(custom_folder, instance_folders_list)
    gen_funct.generic_compile_run_candidate(tools_list, signature_type, candidate, optimized_imp_folder,
                                            instance_folders_list, rel_path_to_api, rel_path_to_sign,
                                            rel_path_to_rng, compile_with_cmake, add_includes, to_compile,
                                            to_run, depth, build_folder,
                                            binary_patterns,rng_outside_instance_folder, with_core_dump)


# ===============================  snova ==========================================
def makefile_snova(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/sign.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        SNOVA_V = 24
        SNOVA_O = 5
        SNOVA_L = 4
        SK_IS_SEED = 0 # 0: sk = ssk; 1: sk = esk 
        TURBO = 1
        CRYPTO_ALGNAME = "SNOVA_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L)"
        SNOVA_PARAMS = -D v_SNOVA=$(SNOVA_V) -D o_SNOVA=$(SNOVA_O) -D l_SNOVA=$(SNOVA_L) -D sk_is_seed=$(SK_IS_SEED) \
        -D CRYPTO_ALGNAME=$(CRYPTO_ALGNAME) -D TURBO=$(TURBO)
        
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        # $(BASE_DIR)/build/rng.o:
        # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
        # 
        # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
        # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
        # 
        # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
        # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
        
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


# ================================  BISCUIT ==============================================
# [TODO]
def makefile_biscuit(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    path_to_makefile = path_to_makefile_folder+'/Makefile'

    # tool_type = gen_funct.Tools(tool_name)
    # test_keypair, test_sign = tool_type.get_tool_test_file_name()
    # tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    # path_to_makefile = path_to_makefile_folder+'/Makefile'

    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla \
    -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign = gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
    OLIST = $(BUILD_OUT_PATH)rng.o $(BUILD_OUT_PATH)snova.o
    
    # snova params
    SNOVA_V = 24
    SNOVA_O = 5
    SNOVA_L = 4
    SK_IS_SEED = 0 # 0: sk = ssk; 1: sk = esk 
    TURBO = 1
    CRYPTO_ALGNAME = "SNOVA_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L)"
    SNOVA_PARAMS = -D v_SNOVA=$(SNOVA_V) -D o_SNOVA=$(SNOVA_O) -D l_SNOVA=$(SNOVA_L) -D sk_is_seed=$(SK_IS_SEED)\
     -D CRYPTO_ALGNAME=$(CRYPTO_ALGNAME) -D TURBO=$(TURBO)
    
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    # $(BASE_DIR)/build/rng.o:
    # \t$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
    # 
    # $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
    # 
    # $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
    # \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o \
        $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o \
        $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c\
         -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c\
         -o $(BUILD)/$@ -lcrypto $(CT_GRIND_SHAREDLIB_PATH)libctgrind.so -lctgrind -lssl
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# =================================  dme_sign ========================================
# [TODO]
def makefile_dme_sign(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla\
     -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign = gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
    OLIST = $(BUILD_OUT_PATH)rng.o $(BUILD_OUT_PATH)snova.o
    
    # snova params
    SNOVA_V = 24
    SNOVA_O = 5
    SNOVA_L = 4
    SK_IS_SEED = 0 # 0: sk = ssk; 1: sk = esk 
    TURBO = 1
    CRYPTO_ALGNAME = "SNOVA_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L)"
    SNOVA_PARAMS = -D v_SNOVA=$(SNOVA_V) -D o_SNOVA=$(SNOVA_O) -D l_SNOVA=$(SNOVA_L) -D sk_is_seed=$(SK_IS_SEED)\
     -D CRYPTO_ALGNAME=$(CRYPTO_ALGNAME) -D TURBO=$(TURBO)
    
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o \
        $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o \
        $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c\
         -o $(BUILD)/$@ -lcrypto -lctgrind
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c\
         -o $(BUILD)/$@ -lcrypto -lctgrind
        
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# =============================== hppc ==========================================
# [TODO]
def makefile_hppc(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_cflags_obj_files = f'''
    CC = gcc
    
    CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla\
     -Wpointer-arith -O3 -march=native -mtune=native

    BASE_DIR = ../../{subfolder}
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign 
    
    KEYPAIR_FOLDER 	= {candidate}_keypair
    SIGN_FOLDER 	= {candidate}_sign
    '''
    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign = gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        BINSEC_STATIC_FLAG  = -static
        DEBUG_G_FLAG = -g
        
        # EXECUTABLE_KEYPAIR	    = {test_harness_kpair}
        # EXECUTABLE_SIGN		    = {test_harness_sign}
    
        EXECUTABLE_KEYPAIR      = {candidate}_keypair/{test_harness_kpair}
        EXECUTABLE_SIGN         = {candidate}_sign/{test_harness_sign}
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/

        \tEXECUTABLE_KEYPAIR	    = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		    = {candidate}_sign/{taint}
        '''
    makefile_content_block_creating_object_files = f'''
    #BUILD_OUT_PATH = $(BASE_DIR)/build/
    BUILD_OUT_PATH = $(BUILD)/
    
    OLIST = $(BUILD_OUT_PATH)rng.o $(BUILD_OUT_PATH)snova.o
    
    # snova params
    SNOVA_V = 24
    SNOVA_O = 5
    SNOVA_L = 4
    SK_IS_SEED = 0 # 0: sk = ssk; 1: sk = esk 
    TURBO = 1
    CRYPTO_ALGNAME = "SNOVA_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L)"
    SNOVA_PARAMS = -D v_SNOVA=$(SNOVA_V) -D o_SNOVA=$(SNOVA_O) -D l_SNOVA=$(SNOVA_L) -D sk_is_seed=$(SK_IS_SEED)\
     -D CRYPTO_ALGNAME=$(CRYPTO_ALGNAME) -D TURBO=$(TURBO)
    
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    $(BUILD)/rng.o:
    \t$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto
    
    $(BUILD)/snova.o: $(BUILD)/rng.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto
    
    $(BUILD)/sign.o: $(BUILD)/snova.o
    \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS)  $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o\
         $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) $(OLIST) $(BUILD)/sign.o \
        $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''    
        $(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) $(CFLAGS)  $(CT_GRIND_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_KEYPAIR).c \
        -o $(BUILD)/$@ -lcrypto -lctgrind
        
        $(EXECUTABLE_SIGN): $(BUILD)/sign.o
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(CT_GRIND_FLAGS) $(OLIST) $(BUILD)/sign.o $(EXECUTABLE_SIGN).c\
         -o $(BUILD)/$@ -lcrypto -lctgrind
        '''
    makefile_content_block_clean = f'''
    clean:
    \trm -f $(BASE_DIR)/build/*.o *.a
    \trm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_cflags_obj_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_creating_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# ==================================  MAYO ===============================


def cmake_mayo(path_to_cmakelists_folder, subfolder, tool_name, candidate):
    mayo_instance_subfolder = subfolder.split('/')[-1]
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_cmakelists = f'{path_to_cmakelists_folder}/CMakeLists.txt'
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
        
        SOURCE_FILES_COMMON_SYS  = ${{BASE_DIR}}/src/common/randombytes_system.c ${{BASE_DIR}}/src/common/aes_c.c \
        ${{BASE_DIR}}/src/common/aes128ctr.c ${{BASE_DIR}}/src/common/fips202.c ${{BASE_DIR}}/src/common/mem.c
        
        SOURCE_FILES_MAYO = ${{BASE_DIR}}/src/mayo.c ${{BASE_DIR}}/src/params.c ${{BASE_DIR}}/src/bitsliced_arithmetic.c
        
        COMPILE_FLAGS = -Werror -Wextra -Wno-unused-parameter -fno-strict-aliasing -std=c99  -DENABLE_AESNI=ON
        
        INC_PLATFORM = ${{BASE_DIR}}/src/generic
        
        
        
        SRC = $(SOURCE_FILES_MAYO) $(SOURCE_FILES_COMMON_SYS)
        MVARIANT_LOWER = ${{BASE_DIR}}/{subfolder}
        SIGN = ${{MVARIANT_LOWER}}/api.c
        
        COMPILE_FLAGS += -DMAYO_VARIANT={mayo_instance_subfolder}
        
        INCS_DIR = -I $(BASE_DIR)/include -I $(INC_PLATFORM) -I $(BASE_DIR)/src/common -I $(MVARIANT_LOWER)
        INCS = $(wildcard $(BASE_DIR)/include/*.h) $(wildcard $(INC_PLATFORM)/*.h) $(MVARIANT_LOWER)/api.h \
         $(wildcard $(BASE_DIR)/src/common/*.h) $(wildcard $(BASE_DIR)/src/*.h)
        
        
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
        \t$(CC) -emit-llvm $(COMPILE_FLAGS) $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        
        
        if (${{MAYO_BUILD_TYPE}} MATCHES "avx2")
            set(INC_PLATFORM ${{PROJECT_SOURCE_DIR}}/src/AVX2)
            add_definitions(-DMAYO_AVX)
        else()
            set(INC_PLATFORM ${{BASE_DIR}}/src/generic)
            # set(INC_PLATFORM ${{PROJECT_SOURCE_DIR}}/src/generic)
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
def makefile_prov(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/api.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/api.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
def makefile_tuov(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        ifndef opt
        opt = avx2
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
        INCS = $(wildcard $(BASE_DIR)/*.h)
        
        SRC  = $(filter-out  $(SRC_DIR)/sign.c ,$(wildcard $(SRC_DIR)/*.c))
        RNG	 = $(BASE_DIR)/nistkat/rng.c
        SRC  += $(RNG)
        SIGN = $(SRC_DIR)/sign.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        opt = avx2
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
        
        CFLAGS	 := -O3 -std=c11 -Wall -Wextra -Wpedantic -fno-omit-frame-pointer
        INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
        LDFLAGS  := $(LDFLAGS)
        LIBPATH  = -L/usr/local/lib -L/opt/local/lib -L/usr/lib
        LIBS     = -lcrypto
        
        CFLAGS += -mavx2 -maes
        
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


def makefile_uov(path_to_makefile_folder, subfolder, tool_name, candidate):
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
        
        SRCS           :=  $(wildcard $(SRC_DIR)/*.c)
        RNG				=$(BASE_DIR)/{architecture}/nistkat/rng.c
        SRCS    += $(RNG)
        SIGN = $(SRC_DIR)/sign.c
        
        INCPATH      += -I$(BASE_DIR)/{architecture}/nistkat
        INCS = $(wildcard $(BASE_DIR)/*.h)
        
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        
        CFLAGS   := -O3 $(CFLAGS) -std=c99 -Wall -Wextra -Wpedantic -Werror -fno-omit-frame-pointer
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
def makefile_vox(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        PARAM ?= VOX256
        
        VOX_PARAMS = -DPARAM_SET_$(PARAM)
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h) $(BASE_DIR)/fips202/fips202.h $(BASE_DIR)/rng/rng.h
        SRC = $(filter-out  $(BASE_DIR)/api.c, $(wildcard $(BASE_DIR)/*.c)) $(BASE_DIR)/fips202/fips202.c $(BASE_DIR)/rng/rng.c
        
        SIGN = $(BASE_DIR)/api.c
        
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
        \t$(CC) -emit-llvm $(VOX_PARAMS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(VOX_PARAMS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
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
        PARAM ?= VOX256
        
        CC=gcc
        CFLAGS = -std=c99 -pedantic -Wall -Wextra -O3 -funroll-loops -march=native -DPARAM_SET_$(PARAM)
        LIBS = -lcrypto
        
        BUILD           = build
        BUILD_DIR = $(BUILD)
        
        BASE_DIR = ../../../{subfolder}
        
        # Sources
        ###########
        HDR = $(wildcard $(BASE_DIR)/*.h) $(BASE_DIR)/fips202/fips202.h $(BASE_DIR)/rng/rng.h
        SRC = $(wildcard $(BASE_DIR)/*.c) $(BASE_DIR)/fips202/fips202.c $(BASE_DIR)/rng/rng.c
        #BUILD_DIRS_ALL = $(BASE_DIR)/$(BUILD_DIR) $(BASE_DIR)/$(BUILD_DIR)/fips202 $(BASE_DIR)/$(BUILD_DIR)/rng
        BUILD_DIRS_ALL = $(BUILD_DIR) $(BUILD_DIR)/fips202 $(BUILD_DIR)/rng
        
        BUILD_DIRS_ALL += $(BUILD_DIR)/fips202/keccak4x
        
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
def makefile_aimer(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/api.c $(SRC_DIR)/PQCgenKAT_sign.c ,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/api.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        # SPDX-License-Identifier: MIT
        
        CC = gcc
        CFLAGS += -I. -O3 -g -Wall -Wextra -march=native -fomit-frame-pointer
        NISTFLAGS = -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter -Wno-unused-result
        AVX2FLAGS = -mavx2 -mpclmul
        
        BASE_DIR = ../../{subfolder}
        
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
        
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.c $(BASE_DIR)/field/field128.c\
        $(BASE_DIR)/aim128.c $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c \
        $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
        \tmkdir -p $(BUILD_KEYPAIR) 
        \t$(CC) -D_BSD_SOURCE -D_DEFAULT_SOURCE $(CFLAGS) $(TOOL_FLAGS) $(AVX2FLAGS)  -D_AIMER_L=1 \
         $^ $(LDFLAGS) $(TOOL_LIBS) -lcrypto -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.c $(BASE_DIR)/field/field128.c $(BASE_DIR)/aim128.c \
        $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c \
        $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) -D_BSD_SOURCE -D_DEFAULT_SOURCE $(CFLAGS) $(TOOL_FLAGS) $(AVX2FLAGS)  -D_AIMER_L=1  \
        $^ $(LDFLAGS) $(TOOL_LIBS) -lcrypto -o $(BUILD)/$@
        
    
        clean:
        \trm -f $(wildcard *.o) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
        \t$(MAKE) -C $(SHAKE_PATH) clean   
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ================================ ascon_sign ===================================

def makefile_ascon_sign(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c ,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/sign.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        THASH = robust
    
        CC=/usr/bin/gcc
        CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
        
        BASE_DIR = ../../../{subfolder}
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
         
          
        SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c \
        $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c $(BASE_DIR)/sign.c
        
        SOURCES += $(BASE_DIR)/hash_ascon.c $(BASE_DIR)/ascon_opt64/ascon.c $(BASE_DIR)/ascon_opt64/permutations.c  \
        $(BASE_DIR)/thash_ascon_$(THASH).c
        
        
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

def makefile_faest(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        SRC  = $(filter-out  $(SRC_DIR)/crypto_sign.c, $(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/crypto_sign.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        CC?=gcc
        CXX?=g++
        CFLAGS+=-g -O3 -std=gnu11 -march=native
        
        SRC_DIR = ../../{subfolder}
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        CPPFLAGS+=-I$(SRC_DIR)/sha3
        
        SOURCES=$(filter-out $(SRC_DIR)/randomness.c,$(wildcard $(SRC_DIR)/*.c)) $(wildcard $(SRC_DIR)/sha3/*.c) $(wildcard $(SRC_DIR)/sha3/*.s)
        SOURCES +=$(SRC_DIR)/NIST-KATs/rng.c
        
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
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c.o $(LIBFAEST) $(SRC_DIR)/randomness.c.o
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CPPFLAGS) $(TOOL_FLAGS) $(LDFLAGS) $^ -lcrypto $(TOOL_LIBS) -o $(BUILD)/$@
        
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c.o $(LIBFAEST) $(SRC_DIR)/randomness.c.o
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

def makefile_sphincs_alpha(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        BASE_DIR = ../../{subfolder}
        
        
        PARAMETERS = {subfolder}
        THASH = simple
        
        CFLAGS = $(EXTRA_CFLAGS) -DPARAMS=$(PARAMETERS)
        PARAMS_INCS = $(BASE_DIR)/params
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/sign.c
        
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
        \t$(CC) -emit-llvm $(CFLAGS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(CFLAGS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
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
        THASH = simple
        
        CC=/usr/bin/gcc
        CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
        
        BASE_DIR = ../../{subfolder}
        
        SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c \
                    $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c \
                    $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c
        HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h $(BASE_DIR)/merkle.h \
                    $(BASE_DIR)/wots.h $(BASE_DIR)/wotsx1.h $(BASE_DIR)/utils.h $(BASE_DIR)/utilsx1.h \
                    $(BASE_DIR)/fors.h $(BASE_DIR)/api.h  $(BASE_DIR)/hash.h $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h
        
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
# ============================== PREON ==================================
def preon_subfolder_parser(subfolder):
    subfold_basename = os.path.basename(subfolder)
    subfold_basename_split = subfold_basename.split('Preon')
    security_level_labeled = subfold_basename_split[-1]
    security_level = security_level_labeled[:3]
    return security_level, security_level_labeled


def makefile_preon(path_to_makefile_folder, subfolder, tool_name, candidate):
    security_level, security_level_labeled = preon_subfolder_parser(subfolder)
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../../{subfolder}
        
        CFLAGS := ${{CFLAGS}} -DUSE_PREON{security_level_labeled} -DAES{security_level}=1 -DUSE_PRNG -O3
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/api.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/api.c
        
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
        \t$(CC) -emit-llvm $(CFLAGS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) -emit-llvm $(CFLAGS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)
        
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
        CFLAGS := ${{CFLAGS}} -DUSE_PREON{security_level_labeled} -DAES{security_level}=1 -DUSE_PRNG -O3
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


# ============================== ALTEQ ==========================================
# [TODO]
def makefile_alteq(path_to_makefile_folder, subfolder, tool_name, candidate):
    tool_type = gen_funct.Tools(tool_name)
    test_keypair, test_sign = tool_type.get_tool_test_file_name()
    tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    if tool_name == 'flowtracker':
        makefile_content = f'''
        CC = clang
        
        BASE_DIR = ../../{subfolder}
        
        INCS = $(wildcard $(BASE_DIR)/*.h)
        #SRC  = $(wildcard $(BASE_DIR)/*.c)) 
        SRC  = $(filter-out  $(SRC_DIR)/sign.c, $(wildcard $(SRC_DIR)/*.c))
        SIGN = $(BASE_DIR)/sign.c
        
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
        \t$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)
        
        $(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
        \topt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)
        
        $(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
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
        PARAMS = {subfolder}
        #PARAMS = sphincs-a-sha2-128f
        THASH = simple
        
        CC=/usr/bin/gcc
        CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
        
        BASE_DIR = ../../{subfolder}
        
        SOURCES =    $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c \
                    $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c \
                    $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c
        HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h $(BASE_DIR)/merkle.h \
                    $(BASE_DIR)/wots.h $(BASE_DIR)/wotsx1.h $(BASE_DIR)/utils.h $(BASE_DIR)/utilsx1.h $(BASE_DIR)/fors.h \
                    $(BASE_DIR)/api.h  $(BASE_DIR)/hash.h $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h
        
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
        
        DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
        DET_HEADERS = $(HEADERS:randombytes.%=rng.%)
        
        TOOL_LIBS = {tool_libs}
        TOOL_FLAGS = {tool_flags}
        
        BUILD           = build
        BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
        BUILD_SIGN		= $(BUILD)/{candidate}_sign
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_keypair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_sign} 
        
        .PHONY: clean 
        
        default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
        
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< $(TOOL_LIBS)
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< $(TOOL_LIBS)
        
        clean:
        \t-$(RM) $(EXECUTABLE_KEYPAIR)
        \t-$(RM) $(EXECUTABLE_SIGN)
        '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content))


# ============================ EMLE2_0 =======================================
# [TODO]
def makefile_emle2_0(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcck
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../{subfolder}
    '''
    makefile_content_block_object_files = f'''
    SOURCES = $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c\
                $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c \
                $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c
    HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h $(BASE_DIR)/merkle.h\
                $(BASE_DIR)/wots.h $(BASE_DIR)/wotsx1.h $(BASE_DIR)/utils.h $(BASE_DIR)/utilsx1.h \
                $(BASE_DIR)/fors.h $(BASE_DIR)/api.h  $(BASE_DIR)/hash.h $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h
    
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
    
    DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
    DET_HEADERS = $(HEADERS:randombytes.%=rng.%)
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign = gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        
        '''
    makefile_content_block_all_target = f''' 
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. -lctgrind
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. -lctgrind
        '''
    makefile_content_block_clean = f''' 
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# ============================== kaz_sign ================================
# [TODO]
def makefile_kaz_sign(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../{subfolder}
    '''
    makefile_content_block_object_files = f'''
    SOURCES = $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c \
                $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c \
                $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c
    HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h $(BASE_DIR)/merkle.h \
                $(BASE_DIR)/wots.h $(BASE_DIR)/wotsx1.h $(BASE_DIR)/utils.h $(BASE_DIR)/utilsx1.h \
                $(BASE_DIR)/fors.h $(BASE_DIR)/api.h  $(BASE_DIR)/hash.h $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h
    
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
    
    DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
    DET_HEADERS = $(HEADERS:randombytes.%=rng.%)
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign = gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        
        '''
    makefile_content_block_all_target = f''' 
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. -lctgrind
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. -lctgrind
        '''
    makefile_content_block_clean = f''' 
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# ================================ xifrat ===================================
# [TODO]
def makefile_xifrat(path_to_makefile_folder, subfolder, tool_type, candidate):
    tool = gen_funct.GenericPatterns(tool_type)
    path_to_makefile = path_to_makefile_folder+'/Makefile'
    makefile_content_block_header = f'''
    PARAMS = {subfolder}
    #PARAMS = sphincs-a-sha2-128f
    THASH = simple
    
    CC=/usr/bin/gcc
    CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)
    
    BASE_DIR = ../../{subfolder}
    '''
    makefile_content_block_object_files = f'''
    SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c \
                $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c \
                $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c
    HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h $(BASE_DIR)/merkle.h \
                $(BASE_DIR)/wots.h $(BASE_DIR)/wotsx1.h $(BASE_DIR)/utils.h $(BASE_DIR)/utilsx1.h \
                $(BASE_DIR)/fors.h $(BASE_DIR)/api.h  $(BASE_DIR)/hash.h $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h
    
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
    
    DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
    DET_HEADERS = $(HEADERS:randombytes.%=rng.%)
    
    BUILD           = build
    BUILD_KEYPAIR	= $(BUILD)/{candidate}_keypair
    BUILD_SIGN		= $(BUILD)/{candidate}_sign
    '''

    makefile_content_block_tool_flags_binary_files = ""
    if tool_type.lower() == 'binsec':
        test_harness_kpair = gen_funct.binsec_test_harness_keypair
        test_harness_sign = gen_funct.binsec_test_harness_sign
        makefile_content_block_tool_flags_binary_files = f'''
        \tBINSEC_STATIC_FLAG  = -static
        \tDEBUG_G_FLAG = -g
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{test_harness_kpair}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{test_harness_sign} 
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        taint = gen_funct.ctgrind_taint
        makefile_content_block_tool_flags_binary_files = f'''
        \tCT_GRIND_FLAGS = -g -Wall -ggdb  -std=c99  -Wextra -lm
        \tCT_GRIND_SHAREDLIB_PATH = /usr/lib/
        
        \tEXECUTABLE_KEYPAIR	 = {candidate}_keypair/{taint}
        \tEXECUTABLE_SIGN		 = {candidate}_sign/{taint}
        
        '''
    makefile_content_block_all_target = f''' 
    .PHONY: clean 
    
    default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    
    all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
    '''
    makefile_content_block_binary_files = ""
    if tool_type.lower() == 'binsec':
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN)
        \t$(CC) $(CFLAGS) $(DEBUG_G_FLAG) $(BINSEC_STATIC_FLAG) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto
        '''
    if 'ctgrind' in tool_type.lower() or 'ct_grind' in tool_type.lower():
        makefile_content_block_binary_files = f'''
        $(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_KEYPAIR)
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. -lctgrind
            
        $(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
        \tmkdir -p $(BUILD)
        \tmkdir -p $(BUILD_SIGN) 
        \t$(CC) $(CFLAGS) $(CT_GRIND_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto -L. -lctgrind
        '''
    makefile_content_block_clean = f''' 
    clean:
    \t-$(RM) $(EXECUTABLE_KEYPAIR)
    \t-$(RM) $(EXECUTABLE_SIGN)
    '''
    with open(path_to_makefile, "w") as mfile:
        mfile.write(textwrap.dedent(makefile_content_block_header))
        mfile.write(textwrap.dedent(makefile_content_block_object_files))
        mfile.write(textwrap.dedent(makefile_content_block_tool_flags_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_all_target))
        mfile.write(textwrap.dedent(makefile_content_block_binary_files))
        mfile.write(textwrap.dedent(makefile_content_block_clean))


# ==========================  ISOGENY ========================================
# ============================================================================
# =========================== sqisign ========================================

# def cmake_sqisign(path_to_cmakelists_folder, subfolder, tool_name, candidate):
#     tool_type = gen_funct.Tools(tool_name)
#     test_keypair, test_sign = tool_type.get_tool_test_file_name()
#     tool_flags, tool_libs = tool_type.get_tool_flags_and_libs()
#     path_to_cmakelists = f'{path_to_cmakelists_folder}/CMakeLists.txt'
#     cmake_file_content = ''
#     target_link_opt_block = ''
#     link_flag = ''
#     libs_list = []
#     if tool_flags:
#         if '-static ' in tool_flags:
#             link_flag = '-static'
#     libs_str = ""
#     tool_libs = tool_libs.replace("-lm", "")
#     tool_libs = tool_libs.strip()
#     if tool_libs:
#         libs_str = tool_libs.replace("-l", "")
#         libs_list = libs_str.split()
#     if tool_name == 'flowtracker':
#         print(":::: flowtracker wit cross")
#         path_to_cmakelists = f'{path_to_cmakelists_folder}/Makefile'
#         cmake_file_content = f'''
#         CC = clang
#
#         # selection of specialized compilation units differing between ref and opt
#         # implementations.
#         REFERENCE_CODE_DIR = ../../Reference_Implementation
#         OPTIMIZED_CODE_DIR = ../../Optimized_Implementation
#
#         BASE_DIR = $(REFERENCE_CODE_DIR)
#
#
#         INCS = $(wildcard $(BASE_DIR)/include/*.h)
#         SRC  = $(filter-out  $(BASE_DIR)/lib/sign.c, $(wildcard $(BASE_DIR)/lib/*.c))
#         SRC  += $(OPTIMIZED_CODE_DIR)/lib/aes256.c
#
#
#         SIGN = $(BASE_DIR)/lib/sign.c
#
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
#
#         cmake_file_content = f'''
#
#         cmake_minimum_required(VERSION 3.5)
#         project(SQIsign VERSION 1.0 LANGUAGES C ASM)
#
#         set(SQISIGN_SO_VERSION "0")
#         set(CMAKE_C_STANDARD 99)
#
#         include(CTest)
#
#
#         option(ENABLE_CT_TESTING  "Enable compilation for constant time testing." OFF)
#
#
#         if (NOT DEFINED SQISIGN_BUILD_TYPE)
#             SET(SQISIGN_BUILD_TYPE "broadwell")
#         endif()
#
#         if(SQISIGN_BUILD_TYPE STREQUAL "broadwell")
#             SET(SVARIANT_S "lvl1")
#         else()
#             SET(SVARIANT_S "lvl1;lvl3;lvl5")
#         endif()
#         '''
#         find_libs_block = ''
#         for lib in libs_list:
#             lib_variable = lib.upper()
#             lib_variable = f'{lib_variable}_LIB'
#             find_libs_block += f'''
#         find_library({lib_variable} {lib})
#         if(NOT {lib_variable})
#         \tmessage("{lib} library not found")
#         endif()
#         '''
#         if libs_list:
#             cmake_file_content += f'{find_libs_block}'
#         cmake_file_content += f'''
#         set(BASE_DIR  "../{subfolder}")
#         include(${{BASE_DIR}}/.cmake/flags.cmake)
#         include(${{BASE_DIR}}/.cmake/sanitizers.cmake)
#         include(${{BASE_DIR}}/.cmake/target.cmake)
#         if(ENABLE_DOC_TARGET)
#             include(${{BASE_DIR}}/.cmake/target_docs.cmake)
#         endif()
#         include(${{BASE_DIR}}/.cmake/gmpconfig.cmake)
#
#         set()
#
#         # set(SELECT_IMPL_TYPE ${{PROJECT_SOURCE_DIR}}/.cmake/impl_type.cmake)
#         # set(SELECT_SQISIGN_VARIANT ${{PROJECT_SOURCE_DIR}}/.cmake/sqisign_variant.cmake)
#
#         set(SELECT_IMPL_TYPE ${{BASE_DIR}}/.cmake/impl_type.cmake)
#         set(SELECT_SQISIGN_VARIANT ${{BASE_DIR}}/.cmake/sqisign_variant.cmake)
#
#         set(INC_PUBLIC ${{BASE_DIR}}/include)
#
#         add_subdirectory(${{BASE_DIR}}/src)
#         add_subdirectory(${{BASE_DIR}}/apps)
#
#
#
#         FOREACH(SVARIANT ${{SVARIANT_S}})
#             string(TOLOWER ${{SVARIANT}} SVARIANT_LOWER)
#             string(TOUPPER ${{SVARIANT}} SVARIANT_UPPER)
#             add_executable(sqisign_test_kat_${{SVARIANT}} test_kat.c)
#             target_link_libraries(sqisign_test_kat_${{SVARIANT}} sqisign_${{SVARIANT_LOWER}}_test)
#             target_include_directories(sqisign_test_kat_${{SVARIANT}} PRIVATE ${{PROJECT_SOURCE_DIR}}/src/nistapi/${{SVARIANT_LOWER}} ${{INC_PUBLIC}} ${{INC_INTBIG}} ${{INC_PRECOMP_${{SVARIANT_UPPER}}}} ${{INC_QUATERNION}} ${{INC_KLPT}} ${{INC_GF_${{SVARIANT_UPPER}}}} ${{INC_EC}} ${{INC_COMMON}} ${{INC_ID2ISO}} ${{INC_PROTOCOLS}})
#
#             add_executable(sqisign_bench_${SVARIANT} bench.c)
#             target_link_libraries(sqisign_bench_${SVARIANT} sqisign_${SVARIANT_LOWER})
#             target_include_directories(sqisign_bench_${SVARIANT} PUBLIC ${PROJECT_SOURCE_DIR}/src/common ${INC_PUBLIC} ${PROJECT_SOURCE_DIR}/src/nistapi/${SVARIANT_LOWER})
#
#             add_executable(sqisign_test_scheme_${SVARIANT} test_sqisign.c)
#             target_link_libraries(sqisign_test_scheme_${SVARIANT} sqisign_${SVARIANT_LOWER})
#             target_include_directories(sqisign_test_scheme_${SVARIANT} PUBLIC ${PROJECT_SOURCE_DIR}/src/common ${INC_PUBLIC} ${PROJECT_SOURCE_DIR}/src/nistapi/${SVARIANT_LOWER})
#
#             add_executable(sqisign_test_prof_${SVARIANT} test_sqisign_prof.c)
#             target_link_libraries(sqisign_test_prof_${SVARIANT} sqisign_${SVARIANT_LOWER})
#             target_include_directories(sqisign_test_prof_${SVARIANT} PUBLIC ${PROJECT_SOURCE_DIR}/src/common ${INC_PUBLIC} ${PROJECT_SOURCE_DIR}/src/nistapi/${SVARIANT_LOWER})
#
#             add_test(sqisign_${SVARIANT}_KAT sqisign_test_kat_${SVARIANT})
#             add_test(sqisign_${SVARIANT}_SELFTEST sqisign_test_scheme_${SVARIANT})
#         ENDFOREACH()
#
#
#         cmake_minimum_required(VERSION 3.9.4)
#         project(LESS C)
#
#         # build type can be case-sensitive!
#         string(TOUPPER "${{CMAKE_BUILD_TYPE}}" UPPER_CMAKE_BUILD_TYPE)
#
#         set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -Wall -pedantic -Wuninitialized -Wsign-conversion -Wno-strict-prototypes")
#
#         include(CheckCCompilerFlag)
#         unset(COMPILER_SUPPORTS_MARCH_NATIVE CACHE)
#         check_c_compiler_flag(-march=native COMPILER_SUPPORTS_MARCH_NATIVE)
#
#         include(CheckIPOSupported)
#         check_ipo_supported(RESULT lto_supported OUTPUT error)
#
#         if(UPPER_CMAKE_BUILD_TYPE MATCHES DEBUG)
#             message(STATUS "Building in Debug mode!")
#         else() # Release, RELEASE, MINSIZEREL, etc
#             set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -mtune=native -O3 -g")
#             if(COMPILER_SUPPORTS_MARCH_NATIVE)
#                 set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -march=native")
#             endif()
#             if(lto_supported)
#                 message(STATUS "IPO / LTO enabled")
#                 set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
#             endif()
#         endif()
#
#         option(COMPRESS_CMT_COLUMNS "Enable COMPRESS_CMT_COLUMNS to compress commitment in SG and VY before hashing" OFF)
#         if(COMPRESS_CMT_COLUMNS)
#             message(STATUS "COMPRESS_CMT_COLUMNS is enabled")
#             add_definitions(-DCOMPRESS_CMT_COLUMNS)
#         else()
#             message(STATUS "COMPRESS_CMT_COLUMNS is disabled")
#         endif()
#         unset(COMPRESS_CMT_COLUMNS CACHE)
#
#         set(SANITIZE "")
#         message(STATUS "Compilation flags:" ${{CMAKE_C_FLAGS}})
#
#         set(CMAKE_C_STANDARD 11)
#
#         find_library(KECCAK_LIB keccak)
#         if(NOT KECCAK_LIB)
#             set(STANDALONE_KECCAK 1)
#         endif()
#
#         # selection of specialized compilation units differing between ref and opt implementations.
#         option(AVX2_OPTIMIZED "Use the AVX2 Optimized Implementation. Else the Reference Implementation will be used." OFF)
#
#         #set(BASE_DIR  ../Optimized_Implementation)
#         set(BASE_DIR  ../)
#         set(HEADERS
#                 ${{BASE_DIR}}/include/api.h
#                 ${{BASE_DIR}}/include/codes.h
#                 ${{BASE_DIR}}/include/fips202.h
#                 ${{BASE_DIR}}/include/fq_arith.h
#                 ${{BASE_DIR}}/include/keccakf1600.h
#                 ${{BASE_DIR}}/include/LESS.h
#                 ${{BASE_DIR}}/include/monomial_mat.h
#                 ${{BASE_DIR}}/include/parameters.h
#                 ${{BASE_DIR}}/include/rng.h
#                 ${{BASE_DIR}}/include/seedtree.h
#                 ${{BASE_DIR}}/include/sha3.h
#                 ${{BASE_DIR}}/include/utils.h
#                 )
#
#         if(STANDALONE_KECCAK)
#             message(STATUS "Employing standalone SHA-3")
#             set(KECCAK_EXTERNAL_LIB "")
#             set(KECCAK_EXTERNAL_ENABLE "")
#             list(APPEND COMMON_SOURCES ${{BASE_DIR}}/lib/keccakf1600.c)
#             list(APPEND COMMON_SOURCES ${{BASE_DIR}}/lib/fips202.c)
#         else()
#             message(STATUS "Employing libkeccak")
#             set(KECCAK_EXTERNAL_LIB keccak)
#             set(KECCAK_EXTERNAL_ENABLE "-DSHA_3_LIBKECCAK")
#         endif()
#
#         '''
#         find_libs_block = ''
#         for lib in libs_list:
#             find_libs_block += f'''
#         find_library({lib})
#         if(NOT {lib})
#         \tmessage("{lib} library not found")
#         endif()
#         '''
#         if libs_list:
#             cmake_file_content += f'{find_libs_block}'
#         cmake_file_content += f'''
#         set(SOURCES
#                 ${{COMMON_SOURCES}}
#                 ${{BASE_DIR}}/lib/codes.c
#                 ${{BASE_DIR}}/lib/LESS.c
#                 ${{BASE_DIR}}/lib/monomial.c
#                 ${{BASE_DIR}}/lib/rng.c
#                 ${{BASE_DIR}}/lib/seedtree.c
#                 ${{BASE_DIR}}/lib/utils.c
#                 ${{BASE_DIR}}/lib/sign.c
#                 )
#         set(BUILD build)
#         set(BUILD_KEYPAIR {candidate}_keypair)
#         set(BUILD_SIGN {candidate}_sign)
#
#         foreach(category RANGE 1 5 2)
#             if(category EQUAL 1)
#                 set(PARAM_TARGETS SIG_SIZE BALANCED PK_SIZE)
#             else()
#                 set(PARAM_TARGETS SIG_SIZE PK_SIZE)
#             endif()
#             foreach(optimiz_target ${{PARAM_TARGETS}})
#
#                 set(TEST_HARNESS ./{tool_name}/{candidate}_keypair/{test_keypair}.c \
#                 ./{tool_name}/{candidate}_sign/{test_sign}.c)
#                 set(TARGET_BINARY_NAME {test_keypair}_${{category}}_${{optimiz_target}})
#                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
#                         ./{candidate}_keypair/{test_keypair}.c)
#         '''
#         if link_flag:
#             cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)'
#         cmake_file_content += f'''
#                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
#                         ${{BASE_DIR}}/include
#                         ./include)
#                 target_link_libraries(${{TARGET_BINARY_NAME}} m {libs_str} ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
#                 set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_KEYPAIR}})
#                 set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
#                         COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}} ")
#
#                 #Test harness for crypto_sign
#                 set(TARGET_BINARY_NAME {test_sign}_${{category}}_${{optimiz_target}})
#                 add_executable(${{TARGET_BINARY_NAME}} ${{HEADERS}} ${{SOURCES}}
#                         ./{candidate}_sign/{test_sign}.c)
#                 '''
#         if link_flag:
#             cmake_file_content += f'target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)'
#         cmake_file_content += f'''
#                 target_link_options(${{TARGET_BINARY_NAME}} PRIVATE -static)
#                 target_include_directories(${{TARGET_BINARY_NAME}} PRIVATE
#                         ${{BASE_DIR}}/include
#                         ./include)
#                 target_link_libraries(${{TARGET_BINARY_NAME}} m {libs_str} ${{SANITIZE}} ${{KECCAK_EXTERNAL_LIB}})
#                 set_target_properties(${{TARGET_BINARY_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${{BUILD_SIGN}})
#                 set_property(TARGET ${{TARGET_BINARY_NAME}} APPEND PROPERTY
#                         COMPILE_FLAGS "-DCATEGORY_${{category}}=1 -D${{optimiz_target}}=1 ${{KECCAK_EXTERNAL_ENABLE}}")
#
#                 #endforeach(t_harness)
#             endforeach(optimiz_target)
#         endforeach(category)
#         '''
#     with open(path_to_cmakelists, "w") as cmake_file:
#         cmake_file.write(textwrap.dedent(cmake_file_content))


def makefile_candidate(path_to_makefile_folder, subfolder, tool_type, candidate):
    if candidate == "mirith":
        makefile_mirith(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "mira":
        makefile_mira(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "mqom":
        makefile_mqom(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "perk":
        makefile_perk(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "ryde":
        makefile_ryde(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "pqsigrm":
        makefile_pqsigrm(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "wave":
        makefile_wave(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "prov":
        makefile_prov(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "qr_uov":
        makefile_qr_uov(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "snova":
        makefile_snova(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "tuov":
        makefile_tuov(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "uov":
        makefile_uov(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "vox":
        makefile_vox(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "aimer":
        makefile_aimer(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "ascon_sign":
        makefile_ascon_sign(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "faest":
        makefile_faest(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "sphincs_alpha":
        makefile_sphincs_alpha(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "preon":
        makefile_preon(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "squirrels":
        makefile_squirrels(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "raccoon":
        makefile_raccoon(path_to_makefile_folder, subfolder, tool_type, candidate)
    # =======================================================================================
    # The following candidates are supposed to be compiled with cmake. But if the chosen tool is flowtraker,
    # then these candidates are compiled with Makefile. Indeed, the function 'cmake_cross', etc., will generate
    # a Makefile instead of a CMakeLists.txt
    # ========================= LESS ==============================================
    # The function makefile_less is meant for the use of the tool flowtracker only
    if candidate == "cross":
        cmake_cross(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "less":
        cmake_less(path_to_makefile_folder, subfolder, tool_type, candidate)
    if candidate == "mayo":
        cmake_mayo(path_to_makefile_folder, subfolder, tool_type, candidate)


def cmake_candidate(path_to_cmake_lists, subfolder, tool_type, candidate):
    if candidate == "cross":
        cmake_cross(path_to_cmake_lists, subfolder, tool_type, candidate)
    if candidate == "mayo":
        cmake_mayo(path_to_cmake_lists, subfolder, tool_type, candidate)
    if candidate == "less":
        cmake_less(path_to_cmake_lists, subfolder, tool_type, candidate)
    if candidate == "sqisign":
        #cmake_sqisign(path_to_cmake_lists, subfolder, tool_type, candidate)
        pass


# Candidates that are compiled with a sh script
def sh_candidate(path_to_sh_file, subfolder, tool_type, candidate):
    if candidate == "raccoon":
        sh_script = 'compile_raccoon'
        sh_build_raccoon(path_to_sh_file, sh_script, subfolder,tool_type,candidate)