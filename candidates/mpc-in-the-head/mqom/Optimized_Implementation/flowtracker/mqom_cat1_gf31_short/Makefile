
CC = clang

BASE_DIR = ../../mqom_cat1_gf31_short

ALL_FLAGS?= -DPARAM_HYPERCUBE_7R -DPARAM_GF31 -DPARAM_L1 -DPARAM_RND_EXPANSION_X4         -DHASHX4 -DXOFX4 -DPRGX4 -DNDEBUG -mavx

INCS = $(wildcard $(BASE_DIR)/*.h)
#SRC  = $(wildcard $(BASE_DIR)/*.c)) 
SRC  = $(filter-out  $(SRC_DIR)/sign.c  $(SRC_DIR)/keygen.c,$(wildcard $(SRC_DIR)/*.c))
SIGN = $(BASE_DIR)/sign.c
KEYGEN = $(BASE_DIR)/keygen.c

HASH_PATH=$(BASE_DIR)/sha3

BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/mqom_keypair
BUILD_SIGN		= $(BUILD)/mqom_sign

EXECUTABLE_KEYPAIR_BC	= mqom_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= mqom_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= mqom_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= mqom_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(KEYGEN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm $(ALL_FLAGS) -I $(HASH_PATH)/avx2 -c -g $(KEYGEN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm $(ALL_FLAGS) -I $(HASH_PATH)/avx2 -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
