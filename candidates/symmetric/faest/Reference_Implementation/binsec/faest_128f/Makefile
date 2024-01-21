
CC?=gcc
CXX?=g++
CFLAGS+=-g -O3 -std=gnu11 -march=native

SRC_DIR = ../../faest_128f
BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/faest_keypair
BUILD_SIGN		= $(BUILD)/faest_sign

CPPFLAGS+=-I$(SRC_DIR)/sha3

SOURCES=$(filter-out $(SRC_DIR)/randomness.c,$(wildcard $(SRC_DIR)/*.c)) $(wildcard $(SRC_DIR)/sha3/*.c) $(wildcard $(SRC_DIR)/sha3/*.s)
SOURCES +=$(SRC_DIR)/NIST-KATs/rng.c

LIBFAEST=$(SRC_DIR)/libfaest.a

EXECUTABLE_KEYPAIR	 = faest_keypair/test_harness_crypto_sign_keypair
EXECUTABLE_SIGN		 = faest_sign/test_harness_crypto_sign

TOOL_LIBS = 
TOOL_FLAGS = -g


all: $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
.PHONY: all

$(LIBFAEST): $(SOURCES:.c=.o) $(SOURCES:.s=.o)
	ar rcs $@ $^

%.c.o: %.c
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c.o $(LIBFAEST) $(SRC_DIR)/randomness.c.o
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(CPPFLAGS) $(TOOL_FLAGS) $(LDFLAGS) $^ -lcrypto $(TOOL_LIBS) -o $(BUILD)/$@

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c.o $(LIBFAEST) $(SRC_DIR)/randomness.c.o
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) $(CPPFLAGS) $(TOOL_FLAGS) $(LDFLAGS) $^ -lcrypto $(TOOL_LIBS) -o $(BUILD)/$@


clean: 
	rm -f $(SRC_DIR)/*.d $(SRC_DIR)/*.o $(LIBFAEST) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
.PHONY: clean
