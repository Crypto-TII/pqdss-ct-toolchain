
CC = clang

BASE_DIR = ../../prov1

INCS = $(wildcard $(BASE_DIR)/*.h)
#SRC  = $(wildcard $(BASE_DIR)/*.c)) 
SRC  = $(filter-out  $(SRC_DIR)/api.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
SIGN = $(BASE_DIR)/api.c

BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/prov_keypair
BUILD_SIGN		= $(BUILD)/prov_sign

EXECUTABLE_KEYPAIR_BC	= prov_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= prov_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= prov_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= prov_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
