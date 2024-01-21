
CC = clang

BASE_DIR = ../../perk-128-fast-3/src
SRC_DIR  = ../../perk-128-fast-3


INCS = $(wildcard $(BASE_DIR)/*.h)
CRYPTOCODE_INCS = $(SRC_DIR)/lib/cryptocode
RANDOMBYTES_INCS = $(SRC_DIR)/lib/randombytes
XKCP_INCS = $(SRC_DIR)/lib/XKCP
#SRC  = $(wildcard $(BASE_DIR)/*.c)) 
SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c ,$(wildcard $(SRC_DIR)/*.c))
SIGN = $(BASE_DIR)/sign.c

BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/perk_keypair
BUILD_SIGN		= $(BUILD)/perk_sign

EXECUTABLE_KEYPAIR_BC	= perk_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= perk_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= perk_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= perk_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm -I $(CRYPTOCODE_INCS) -I $(XKCP_INCS) -I $(RANDOMBYTES_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm -I $(CRYPTOCODE_INCS) -I $(XKCP_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
