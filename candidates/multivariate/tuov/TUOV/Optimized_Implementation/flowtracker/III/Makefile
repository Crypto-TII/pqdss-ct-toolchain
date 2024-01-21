
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
PROJ        = III
SRC_DIR     := $(BASE_DIR)/$(PROJ)

INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)


INCPATH  += -I$(BASE_DIR)/nistkat
INCS = $(wildcard $(BASE_DIR)/*.h)

SRC  = $(filter-out  $(SRC_DIR)/sign.c ,$(wildcard $(SRC_DIR)/*.c))
RNG	 = $(BASE_DIR)/nistkat/rng.c
SRC  += $(RNG)
SIGN = $(SRC_DIR)/sign.c

BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/tuov_keypair
BUILD_SIGN		= $(BUILD)/tuov_sign

EXECUTABLE_KEYPAIR_BC	= tuov_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= tuov_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= tuov_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= tuov_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
