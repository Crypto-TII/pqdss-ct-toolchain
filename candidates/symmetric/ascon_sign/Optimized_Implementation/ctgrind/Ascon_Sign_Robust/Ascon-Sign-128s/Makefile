
THASH = robust

CC=/usr/bin/gcc
CFLAGS=-Wall -Wextra -Wpedantic -O3 -std=c99 -Wconversion -Wmissing-prototypes -DPARAMS=$(PARAMS) $(EXTRA_CFLAGS)

BASE_DIR = ../../../Ascon_Sign_Robust/Ascon-Sign-128s

BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/ascon_sign_keypair
BUILD_SIGN		= $(BUILD)/ascon_sign_sign


SOURCES =  $(BASE_DIR)/address.c $(BASE_DIR)/randombytes.c $(BASE_DIR)/merkle.c $(BASE_DIR)/wots.c         $(BASE_DIR)/wotsx1.c $(BASE_DIR)/utils.c $(BASE_DIR)/utilsx1.c $(BASE_DIR)/fors.c $(BASE_DIR)/sign.c

SOURCES += $(BASE_DIR)/hash_ascon.c $(BASE_DIR)/ascon_opt64/ascon.c $(BASE_DIR)/ascon_opt64/permutations.c          $(BASE_DIR)/thash_ascon_$(THASH).c


DET_SOURCES = $(SOURCES:randombytes.%=rng.%)

EXECUTABLE_KEYPAIR	    = ascon_sign_keypair/taint_crypto_sign_keypair
EXECUTABLE_SIGN		    = ascon_sign_sign/taint_crypto_sign

TOOL_LIBS = -lctgrind -lm
TOOL_FLAGS = -Wall -ggdb  -std=c99  -Wextra

default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 

all:  $(EXECUTABLE_KEYPAIR)  $(EXECUTABLE_SIGN) 

$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR).c $(DET_SOURCES)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN).c $(DET_SOURCES)
	mkdir -p $(BUILD_SIGN)
	$(CC) $(CFLAGS) $(TOOL_FLAGS) -o $(BUILD)/$@ $(DET_SOURCES) $< -lcrypto $(TOOL_LIBS)

clean:
	-$(RM)  $(EXECUTABLE_SIGN)
	-$(RM)  $(EXECUTABLE_KEYPAIR) 
