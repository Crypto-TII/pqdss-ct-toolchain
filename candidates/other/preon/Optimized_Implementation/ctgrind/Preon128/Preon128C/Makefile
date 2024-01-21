
CC = cc
CFLAGS := ${CFLAGS} -DUSE_PREON128C -DAES128=1 -DUSE_PRNG -O3
LFLAGS := ${LFLAGS} -lm -lssl -lcrypto


BASE_DIR = ../../../Preon128/Preon128C

BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/preon_keypair
BUILD_SIGN		= $(BUILD)/preon_sign

TOOL_LIBS = -lctgrind -lm
TOOL_FLAGS = -Wall -ggdb  -std=c99  -Wextra

SRC_FILES := $(filter-out  $(BASE_DIR)/PQCgenKAT_sign.c ,$(wildcard $(BASE_DIR)/*.c))

EXECUTABLE_KEYPAIR	 = preon_keypair/taint_crypto_sign_keypair
EXECUTABLE_SIGN		 = preon_sign/taint_crypto_sign


all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

%.o: %.c
	@$(CC) $(CFLAGS) -c $< -o $@

$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(SRC_FILES)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(SRC_FILES) $< $(LFLAGS) $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(SRC_FILES)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(SRC_FILES) $< $(LFLAGS) $(TOOL_LIBS)

.PHONY: clean  

clean:
	@rm -f $(BASE_DIR)/*.o 
	@rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
