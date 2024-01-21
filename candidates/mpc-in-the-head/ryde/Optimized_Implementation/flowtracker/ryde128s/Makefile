
CC = clang

BASE_DIR = ../../ryde128s/src


RANDOMBYTES_INCS = ../../ryde128s/lib/randombytes
XKCP_INCS = ../../ryde128s/lib/XKCP
RBC_INCS = $(BASE_DIR)/rbc-31
RBC_SRC = $(wildcard $(BASE_DIR)/rbc-31/*.c))

INCS = $(wildcard $(BASE_DIR)/*.h)
#SRC  = $(wildcard $(BASE_DIR)/*.c)) 
SRC  = $(filter-out  $(SRC_DIR)/sign.c ,$(wildcard $(SRC_DIR)/*.c))
SIGN = $(BASE_DIR)/sign.c

BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/ryde_keypair
BUILD_SIGN		= $(BUILD)/ryde_sign

EXECUTABLE_KEYPAIR_BC	= ryde_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= ryde_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= ryde_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= ryde_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm -I $(RANDOMBYTES_INCS) -I $(XKCP_INCS) -I $(RBC_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm -I $(RANDOMBYTES_INCS) -I $(XKCP_INCS) -I $(RBC_INCS) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
