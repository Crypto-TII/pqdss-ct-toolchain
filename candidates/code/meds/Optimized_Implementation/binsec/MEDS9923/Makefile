
CC = gcc
LDFLAGS =  -L/usr/local/lib
CFLAGS = -I/usr/local/include -Wunused-variable -Wunused-function -mavx2
LIBFLAGS = -lcrypto -lssl -lm

BASE_DIR = ../pqsigrm613


CFILES := $(shell find $(BASE_DIR)/src -name '*.c' | sed -e 's/\.c/\.o/')

OBJS = ${CFILES}

BUILD					= build
BUILD_KEYPAIR			= $(BUILD)/meds_keypair
BUILD_SIGN			= $(BUILD)/meds_sign

TOOL_LIBS = 
TOOL_FLAGS = -static -g

EXECUTABLE_KEYPAIR	    = meds_keypair/test_harness_crypto_sign_keypair
EXECUTABLE_SIGN		    = meds_sign/test_harness_crypto_sign

ifeq ($(DEBUG), 1)
	DBG_FLAGS = -g -O0 -DDEBUG
else
	DBG_FLAGS = -g -O2 -DNDEBUG -Wunused-variable -Wunused-function   
endif

all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

%.o : %.c
	$(CC) $(CFLAGS) $(DBG_FLAGS) -o $@ -c $<

$(EXECUTABLE_KEYPAIR): ${OBJS} meds_keypair/$(EXECUTABLE_KEYPAIR).c
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(LDFLAGS) $(CFLAGS) $(TOOL_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(TOOL_LIBS)

$(EXECUTABLE_SIGN): ${OBJS} meds_sign/$(EXECUTABLE_SIGN).c
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) $(LDFLAGS) $(CFLAGS) $(TOOL_FLAGS) $(DBG_FLAGS) -o $(BUILD)/$@ $^ $(LIBFLAGS) $(TOOL_LIBS)

matrix.o : matrix.h
rng.o : rng.h
api.o : api.h

clean:
	cd  $(BASE_DIR)/src; rm -f *.o; cd ..
	rm -f *.o
	 cd ../../meds
	rm -f  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
