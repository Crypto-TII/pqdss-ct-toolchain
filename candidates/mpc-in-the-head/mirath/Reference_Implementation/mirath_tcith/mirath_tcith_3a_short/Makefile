CFLAGS = -std=c11 -Wall -Wextra -pedantic -mavx -mavx2 -mbmi -mbmi2 -maes

MIRATH = .
COMMON = $(MIRATH)/common
RIJNDAEL = $(COMMON)/rijndael
PARAMETERS = $(MIRATH)/parameters
ARITH = $(MIRATH)/arith
ARITH_X = $(ARITH)/q_16
ARITH_MU = $(ARITH_X)/mu_short

INCLUDES = -I$(PARAMETERS) -I$(ARITH_MU) -I$(ARITH_X) -I$(ARITH) -I$(RIJNDAEL) -I$(COMMON) -I$(MIRATH)

LIBS = -lcrypto

TMP=rng.o $(subst common/random.o, ,$(patsubst common/%.c,common/%.o,$(wildcard common/*.c)))
OBJ=$(subst common/KeccakP-1600-times4-SIMD256.o, ,$(TMP))
OBJ+=$(patsubst %.c,%.o,$(wildcard *.c))

OBJ_MAIN = $(filter-out PQCgenKAT_sign.o, $(OBJ))
OBJ_KATS = $(filter-out main.o, $(OBJ))

VPATH = $(PARAMETERS):$(ARITH_MU):$(ARITH_X):$(ARITH):$(RIJNDAEL):$(COMMON):$(MIRATH)

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    CFLAGS += -I/usr/local/opt/openssl/include
    LIBS += -L/usr/local/opt/openssl/lib
endif

all: PQCgenKAT_sign mirath_3a_s

%.o: %.c
	$(CC) -D_SHA3_ $(INCLUDES) -c -o $@ $< $(CFLAGS)

rng.o: rng.c
	$(CC) -c $(CFLAGS) -o $@ $<

mirath_3a_s: main.o sign.o $(OBJ_MAIN)
	$(CC) -o $@ $^ $(LIBS)

PQCgenKAT_sign: PQCgenKAT_sign.o sign.o $(OBJ_KATS)
	$(CC) -o $@ $^ $(LIBS)

run: PQCgenKAT_sign
	./PQCgenKAT_sign

.PHONY: clean

clean:
	rm -f *.o *.su
	rm -f common/*.o
	rm -f mirath_3a_s
	rm -f PQCgenKAT_sign
	rm -f PQCsignKAT_*.req
	rm -f PQCsignKAT_*.rsp
