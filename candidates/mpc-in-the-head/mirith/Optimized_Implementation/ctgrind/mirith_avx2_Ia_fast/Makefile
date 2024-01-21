
CC=gcc
CFLAGS=-std=c11 -Wall -Wextra -pedantic -mavx2 -g 

BASE_DIR = ../../mirith_avx2_Ia_fast


DEPS=$(wildcard $(BASE_DIR)/*.h)
OBJ=$(patsubst $(BASE_DIR)/%.c,$(BASE_DIR)/%.o,$(wildcard $(BASE_DIR)/*.c)) 
OBJ+=$(patsubst $(BASE_DIR)/%.s,$(BASE_DIR)/%.o,$(wildcard $(BASE_DIR)/*.s))

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	ASMFLAGS := ${CFLAGS}
endif
ifeq ($(UNAME_S),Darwin)
	ASMFLAGS := ${CFLAGS} -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
endif

BUILD					= build
BUILD_KEYPAIR			= $(BUILD)/mirith_keypair
BUILD_SIGN			= $(BUILD)/mirith_sign

EXECUTABLE_KEYPAIR	    = mirith_keypair/taint_crypto_sign_keypair
EXECUTABLE_SIGN		    = mirith_sign/taint_crypto_sign

TOOL_FLAGS = -Wall -ggdb  -std=c99  -Wextra
TOOL_LIBS = -lctgrind -lm

all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

%.o: %.s
	$(CC) -c $(ASMFLAGS) -o $@ $<

%.o: %.c $(DEPS)
	$(CC) -c $(CFLAGS) -o $@ $<

$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).o $(OBJ)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(LIBDIR) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) $(TOOL_LIBS) $(TOOL_FLAGS)

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).o $(OBJ)
	mkdir -p $(BUILD_SIGN)
	$(CC) $(LIBDIR) -o $(BUILD)/$@ $^ $(CFLAGS) $(LIBS) $(TOOL_LIBS) $(TOOL_FLAGS)


.PHONY: clean

clean:
	rm -f $(BASE_DIR)/*.o $(BASE_DIR)/*.su
	rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
