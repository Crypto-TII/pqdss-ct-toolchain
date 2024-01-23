
# SPDX-License-Identifier: MIT

CC = gcc
CFLAGS += -I. -O3 -g -Wall -Wextra -march=native -fomit-frame-pointer
NISTFLAGS = -Wno-sign-compare -Wno-unused-but-set-variable -Wno-unused-parameter -Wno-unused-result
AVX2FLAGS = -mavx2 -mpclmul


BASE_DIR = ../../AIMer-l1-param3-avx2

IDIR = AIMer-l1-param3-avx2
DEPS = ../../$(IDIR)/portable_endian.h

SHAKE_PATH = $(BASE_DIR)/shake
SHAKE_LIB = libshake.a
LDFLAGS = $(SHAKE_PATH)/$(SHAKE_LIB)


INCS  = $(wildcard $(BASE_DIR)/*.h)

BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/aimer_keypair
BUILD_SIGN		= $(BUILD)/aimer_sign

EXECUTABLE_KEYPAIR      = aimer_keypair/taint_crypto_sign_keypair
EXECUTABLE_SIGN         = aimer_sign/taint_crypto_sign


TOOL_FLAGS = -Wall -ggdb  -std=c99  -Wextra
TOOL_LIBS = -lctgrind -lm

.PHONY: all

all: $(SHAKE_LIB) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

#$(BUILD)/.c.o:
#	$(CC) -c $(CFLAGS) $< -o $@

#.c.o:
#	$(CC) -c $(CFLAGS) $< -o $@

%.o: %.c
	$(CC) -c  $(CFLAGS) $^ -o $@

$(SHAKE_LIB):
	$(MAKE) -C $(SHAKE_PATH)


$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c  $(DEPS) $(BASE_DIR)/api.c  $(BASE_DIR)/field/field128.c  $(BASE_DIR)/aim128.c $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c  $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
	mkdir -p $(BUILD_KEYPAIR) 
	$(CC)  $(CFLAGS) $(TOOL_FLAGS) $(AVX2FLAGS)  -D_AIMER_L=3   $^ $(LDFLAGS) $(TOOL_LIBS) -lcrypto -o $(BUILD)/$@

#$(EXECUTABLE_KAT): $(EXECUTABLE_KAT).c api.c field/field128.c aim128.c rng.c hash.c tree.c aimer_internal.c aimer_instances.c aimer.c
#	$(CC) $(CFLAGS) $(AVX2FLAGS) -D_AIMER_L=1 $^ $(LDFLAGS) -lcrypto -o $@

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DEPS) $(BASE_DIR)/api.c $(BASE_DIR)/field/field128.c  $(BASE_DIR)/aim128.c   $(BASE_DIR)/rng.c $(BASE_DIR)/hash.c $(BASE_DIR)/tree.c $(BASE_DIR)/aimer_internal.c   $(BASE_DIR)/aimer_instances.c $(BASE_DIR)/aimer.c
	mkdir -p $(BUILD_SIGN) 
	$(CC)  $(CFLAGS) $(TOOL_FLAGS) $(AVX2FLAGS)  -D_AIMER_L=3  $^ $(LDFLAGS) $(TOOL_LIBS) -lcrypto -o $(BUILD)/$@


clean:
	rm -f $(wildcard *.o) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
	$(MAKE) -C $(SHAKE_PATH) clean   
