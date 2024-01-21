
# select parameter set (one of: VOX128 VOX192 VOX256)
PARAM ?= VOX256

CC=gcc
CFLAGS = -std=c99 -pedantic -Wall -Wextra -O3 -funroll-loops -march=native -DPARAM_SET_$(PARAM)
LIBS = -lcrypto

BUILD           = build
BUILD_DIR = $(BUILD)

BASE_DIR = ../../../vox_sign

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


BUILD_KEYPAIR	= $(BUILD)/vox_keypair
BUILD_SIGN		= $(BUILD)/vox_sign 

KEYPAIR_FOLDER 	= vox_keypair
SIGN_FOLDER 	= vox_sign


EXECUTABLE_KEYPAIR      = vox_keypair/test_harness_crypto_sign_keypair
EXECUTABLE_SIGN         = vox_sign/test_harness_crypto_sign

TOOL_LIBS = 
TOOL_FLAGS = -g

all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

.PHONY: all

$(BUILD_DIR)/%.o:$(BASE_DIR)/%.c $(HDR) | $(BUILD_DIRS_ALL)
	$(CC) -o $@ $< $(CFLAGS) -c

$(BUILD_DIRS_ALL): %:
	mkdir -p $@

.SECONDARY: $(OBJ)

$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(OBJ)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -o $(BUILD)/$@ $^ $(CFLAGS) -static $(TOOL_FLAGS) -I. -Irng/ $(LIBS) $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(OBJ)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -o $(BUILD)/$@ $^ $(CFLAGS) -static $(TOOL_FLAGS) -I. -Irng/ $(LIBS) $(TOOL_LIBS)

clean:
	-rm -rf $(BASE_DIR)/$(BUILD_DIR)
	rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
