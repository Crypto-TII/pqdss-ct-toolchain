
CC = gcc
CFLAGS:= -std=c99 -pedantic -Wall -Wextra -O3 -funroll-all-loops -march=native         	-Wimplicit-function-declaration -Wredundant-decls         	-Wundef -Wshadow  -mavx2 -mpclmul -msse4.2 -maes
    #-Wno-newline-eof
ASMFLAGS := -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
LDFLAGS:= -lcrypto
ADDITIONAL_CFLAGS:= -Wno-missing-prototypes -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter

BASE_DIR = ../../perk-128-fast-3
# Directories
BUILD_DIR:=build
BIN_DIR:=$(BUILD_DIR)/bin
LIB_DIR:=$(BASE_DIR)/lib
SRC_DIR:=$(BASE_DIR)/src

EXECUTABLE_KEYPAIR	    = perk_keypair/test_harness_crypto_sign_keypair
EXECUTABLE_SIGN		    = perk_sign/test_harness_crypto_sign

BUILD					= $(BUILD_DIR)
BUILD_KEYPAIR			= $(BUILD)/perk_keypair
BUILD_SIGN			= $(BUILD)/perk_sign

TOOL_LIBS = 
TOOL_FLAGS = -g

# Exclude main.c and PQCgenKAT_sign.c 
MAIN_PERK_SRC:=$(SRC_DIR)/main.c
MAIN_KAT_SRC:=$(SRC_DIR)/PQCgenKAT_sign.c

# exclude sources from "find"
EXCL_SRC:=! -name $(notdir $(MAIN_PERK_SRC))                   ! -name $(notdir $(MAIN_KAT_SRC))

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
	@echo -e "### Compiling external library file $@"
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(ADDITIONAL_CFLAGS) -c $< $(LIB_INCLUDE) -o $@

$(SORT_COBJS): $(BUILD_DIR)/%.o: %.c
	@echo -e "### Compiling external library file $@"
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -fwrapv $(ADDITIONAL_CFLAGS) -c $< $(LIB_INCLUDE) -o $@

$(LIB_SOBJS): $(BUILD_DIR)/%.o: %.s
	@echo -e "### Assembling external library file $@"
	@mkdir -p $(dir $@)
	$(CC) $(ASMFLAGS) -c $< -o $@

$(PERK_OBJS): $(BUILD_DIR)/%$(EXT).o: %.c
	@echo -e "### Compiling perk-128-fast-3 file $@"
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< $(PERK_INCLUDE) -o $@

# main targets
$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c  $(PERK_OBJS) $(LIB_OBJS)
	@echo -e "### Compiling PERK Test harness keypair"
	@mkdir -p $(dir $@)
	mkdir -p $(BUILD_KEYPAIR) 
	$(CC) $(CFLAGS) $(TOOL_FLAGS) -Wno-strict-prototypes -Wno-unused-result              $(PERK_INCLUDE) -o $(BUILD)/$@ $^ $(LDFLAGS) $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c  $(PERK_OBJS) $(LIB_OBJS)
	@echo -e "### Compiling PERK Test harness sign"
	@mkdir -p $(dir $@) 
	mkdir -p $(BUILD_SIGN) 
	$(CC) $(CFLAGS) $(TOOL_FLAGS) -Wno-strict-prototypes -Wno-unused-result              $(PERK_INCLUDE) -o $(BUILD)/$@ $^ $(LDFLAGS) $(TOOL_LIBS)

clean:
	rm -rf $(BUILD_DIR) 
