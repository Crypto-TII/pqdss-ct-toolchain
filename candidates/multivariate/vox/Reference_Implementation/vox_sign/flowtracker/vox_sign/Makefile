
PARAM ?= VOX256

VOX_PARAMS = -DPARAM_SET_$(PARAM)
CC = clang

BASE_DIR = ../../../vox_sign

INCS = $(wildcard $(BASE_DIR)/*.h) $(BASE_DIR)/fips202/fips202.h $(BASE_DIR)/rng/rng.h
SRC = $(filter-out  $(BASE_DIR)/api.c, $(wildcard $(BASE_DIR)/*.c)) $(BASE_DIR)/fips202/fips202.c $(BASE_DIR)/rng/rng.c

SIGN = $(BASE_DIR)/api.c

BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/vox_keypair
BUILD_SIGN		= $(BUILD)/vox_sign

EXECUTABLE_KEYPAIR_BC	= vox_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= vox_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= vox_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= vox_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm $(VOX_PARAMS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm $(VOX_PARAMS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)