CC=gcc

TOOLS_FLAGS :=

CFLAGS=-std=c11 -Wall -Wextra -pedantic -mavx2 -fPIC -Wall -g -Wextra $(TOOLS_FLAGS)
DEPS=$(wildcard ../*.h)
LIBS=-lcrypto
OBJ=rng.o $(subst ../random.o, ,$(patsubst ../%.c,../%.o,$(wildcard ../*.c)))
OBJ+=$(patsubst ../%.s,../%.o,$(wildcard ../*.s))

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    CFLAGS := ${CFLAGS} -lcrypto
endif
ifeq ($(UNAME_S),Darwin)
    CFLAGS := ${CFLAGS} -I/usr/local/opt/openssl/include
	LIBS :=-L/usr/local/opt/openssl/lib -lcrypto
    ASMFLAGS := ${CFLAGS} -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
endif


CTTEST_LIB = libcttest.so
BUILD_CTLIB = ../build

all: PQCgenKAT_sign $(CTTEST_LIB)

$(CTTEST_LIB): $(OBJ)
	mkdir -p $(BUILD_CTLIB)
	$(CC) -shared $(OBJ) $(LIBS) $(CFLAGS) -o $(BUILD_CTLIB)/$(CTTEST_LIB)

%.o: %.s
	$(CC) -c $(ASMFLAGS) -o $@ $< 

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

rng.o: rng.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)
	
PQCgenKAT_sign: PQCgenKAT_sign.o $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)
		
run: PQCgenKAT_sign
	./PQCgenKAT_sign

.PHONY: clean

clean:
	rm -f *.o *.su
	rm -f ../*.o ../*.su
	rm -f PQCgenKAT_sign
	rm -f PQCsignKAT_*.req
	rm -f PQCsignKAT_*.rsp
	rm -rf $(BUILD_CTLIB)
