
CC = clang
BASE_DIR = ../../sphincs-a-sha2-128f


PARAMETERS = sphincs-a-sha2-128f
THASH = simple

CFLAGS = $(EXTRA_CFLAGS) -DPARAMS=$(PARAMETERS)
PARAMS_INCS = $(BASE_DIR)/params

INCS = $(wildcard $(BASE_DIR)/*.h)
SRC  = $(filter-out  $(SRC_DIR)/sign.c $(SRC_DIR)/PQCgenKAT_sign.c,$(wildcard $(SRC_DIR)/*.c))
SIGN = $(BASE_DIR)/sign.c

BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/sphincs_alpha_keypair
BUILD_SIGN		= $(BUILD)/sphincs_alpha_sign

EXECUTABLE_KEYPAIR_BC	= sphincs_alpha_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= sphincs_alpha_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= sphincs_alpha_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= sphincs_alpha_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm $(CFLAGS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm $(CFLAGS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
