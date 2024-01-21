
CC = clang

BASE_DIR  = ../../..

# MVARIANT_S =  MAYO_1 MAYO_2 MAYO_3 MAYO_5

SOURCE_FILES_COMMON_SYS  = ${BASE_DIR}/src/common/randombytes_system.c ${BASE_DIR}/src/common/aes_c.c         ${BASE_DIR}/src/common/aes128ctr.c ${BASE_DIR}/src/common/fips202.c ${BASE_DIR}/src/common/mem.c

SOURCE_FILES_MAYO = ${BASE_DIR}/src/mayo.c ${BASE_DIR}/src/params.c ${BASE_DIR}/src/bitsliced_arithmetic.c

COMPILE_FLAGS = -Werror -Wextra -Wno-unused-parameter -fno-strict-aliasing -std=c99  -DENABLE_AESNI=ON

INC_PLATFORM = ${BASE_DIR}/src/generic



SRC = $(SOURCE_FILES_MAYO) $(SOURCE_FILES_COMMON_SYS)
MVARIANT_LOWER = ${BASE_DIR}/src/mayo_3
SIGN = ${MVARIANT_LOWER}/api.c

COMPILE_FLAGS += -DMAYO_VARIANT=mayo_3

INCS_DIR = -I $(BASE_DIR)/include -I $(INC_PLATFORM) -I $(BASE_DIR)/src/common -I $(MVARIANT_LOWER)
INCS = $(wildcard $(BASE_DIR)/include/*.h) $(wildcard $(INC_PLATFORM)/*.h) $(MVARIANT_LOWER)/api.h          $(wildcard $(BASE_DIR)/src/common/*.h) $(wildcard $(BASE_DIR)/src/*.h)


BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/mayo_keypair
BUILD_SIGN		= $(BUILD)/mayo_sign

EXECUTABLE_KEYPAIR_BC	= mayo_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= mayo_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= mayo_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= mayo_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm $(COMPILE_FLAGS) $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm $(COMPILE_FLAGS) $(INCS_DIR) -c -g $(SIGN) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
