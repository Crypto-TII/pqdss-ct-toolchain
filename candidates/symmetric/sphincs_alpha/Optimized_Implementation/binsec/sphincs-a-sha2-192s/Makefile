
PARAMS = sphincs-a-sha2-192s
#PARAMS = sphincs-a-sha2-128f
THASH = simple

CC=/usr/bin/gcc
CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)

BASE_DIR = ../../sphincs-a-sha2-192s

SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c                     $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c                     $(BASE_DIR)/sign.c $(BASE_DIR)/uintx.c
HEADERS = $(BASE_DIR)/params.h $(BASE_DIR)/address.h $(BASE_DIR)/randombytes.h $(BASE_DIR)/merkle.h                     $(BASE_DIR)/wots.h $(BASE_DIR)/wotsx1.h $(BASE_DIR)/utils.h $(BASE_DIR)/utilsx1.h                     $(BASE_DIR)/fors.h $(BASE_DIR)/api.h  $(BASE_DIR)/hash.h $(BASE_DIR)/thash.h $(BASE_DIR)/uintx.h

ifneq (,$(findstring shake,$(PARAMS)))
	SOURCES += $(BASE_DIR)/fips202.c $(BASE_DIR)/hash_shake.c $(BASE_DIR)/thash_shake_$(THASH).c
	HEADERS += $(BASE_DIR)/fips202.h
endif
ifneq (,$(findstring haraka,$(PARAMS)))
	SOURCES += $(BASE_DIR)/haraka.c $(BASE_DIR)/hash_haraka.c $(BASE_DIR)/thash_haraka_$(THASH).c
	HEADERS += $(BASE_DIR)/haraka.h
endif
ifneq (,$(findstring sha2,$(PARAMS)))
	SOURCES += $(BASE_DIR)/sha2.c $(BASE_DIR)/hash_sha2.c $(BASE_DIR)/thash_sha2_$(THASH).c
	HEADERS += $(BASE_DIR)/sha2.h
endif

DET_SOURCES = $(SOURCES:randombytes.%=rng.%)
DET_HEADERS = $(HEADERS:randombytes.%=rng.%)

BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/sphincs_alpha_keypair
BUILD_SIGN		= $(BUILD)/sphincs_alpha_sign

TOOL_LIBS = 
TOOL_FLAGS = -g

	EXECUTABLE_KEYPAIR	 = sphincs_alpha_keypair/test_harness_crypto_sign_keypair
	EXECUTABLE_SIGN		 = sphincs_alpha_sign/test_harness_crypto_sign

.PHONY: clean 

default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES) $(DET_HEADERS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES) $(DET_HEADERS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)


clean:
	-$(RM) $(EXECUTABLE_KEYPAIR)
	-$(RM) $(EXECUTABLE_SIGN)
