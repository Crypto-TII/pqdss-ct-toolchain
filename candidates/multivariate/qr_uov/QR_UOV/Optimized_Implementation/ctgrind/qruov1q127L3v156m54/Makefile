
CC=gcc
CFLAGS=-O3 -fomit-frame-pointer -Wno-unused-result -Wno-aggressive-loop-optimizations         -I. -fopenmp # -DQRUOV_HASH_LEGACY # -ggdb3 
LDFLAGS=-lcrypto -Wl,-Bstatic -lcrypto -Wl,-Bdynamic -lm

BASE_DIR = ../../qruov1q127L3v156m54/portable64
BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/qr_uov_keypair
BUILD_SIGN		= $(BUILD)/qr_uov_sign


EXECUTABLE_KEYPAIR	    = qr_uov_keypair/taint_crypto_sign_keypair
EXECUTABLE_SIGN		    = qr_uov_sign/taint_crypto_sign

TOOL_LIBS = -lctgrind
TOOL_FLAGS = -Wall -ggdb  -std=c99  -Wextra

OBJS=$(BASE_DIR)/Fql.o $(BASE_DIR)/mgf.o  $(BASE_DIR)/qruov.o $(BASE_DIR)/rng.o         $(BASE_DIR)/sign.o $(BASE_DIR)/matrix.o

.PHONY: all clean

all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

$(EXECUTABLE_KEYPAIR): Makefile $(EXECUTABLE_KEYPAIR).c $(OBJS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	${CC} ${OBJS} ${CFLAGS} $(TOOL_FLAGS) ${LDFLAGS} $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ $(TOOL_LIBS)

$(EXECUTABLE_SIGN): Makefile $(EXECUTABLE_SIGN).c $(OBJS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	${CC} ${OBJS} ${CFLAGS} $(TOOL_FLAGS) ${LDFLAGS} $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ $(TOOL_LIBS)


clean:
	rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
