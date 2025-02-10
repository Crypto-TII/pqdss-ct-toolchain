
TOOLS_FLAGS :=
TOOL_LINK_LIBS :=
CTTEST_LIB_CFLAGS :=

INSTANCE = mirath_tcith_5b_short
BENCHMARK_FOLDER = ../../../../benchmarks

CFLAGS =-O3 -std=c11 -Wall -Wextra -pedantic -mavx -mavx2 -mbmi -mbmi2 -maes -fPIC $(TOOLS_FLAGS)

MIRATH = .
COMMON = $(MIRATH)/common
RIJNDAEL = $(COMMON)/rijndael
PARAMETERS = $(MIRATH)/parameters
ARITH = $(MIRATH)/arith
ARITH_X = $(ARITH)/q_2
ARITH_MU = $(ARITH_X)/mu_12

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

OBJ_CUSTOM_BENCH = $(filter-out PQCgenKAT_sign.o main.o, $(OBJ))
CTTEST_LIB = libcttest.so
BUILD_CTLIB = build
CTTEST_LIB_CFLAGS = $(CFLAGS)


#all: PQCgenKAT_sign mirath_5b_s
all: custom_bench

%.o: %.c
	$(CC) -D_SHA3_ $(INCLUDES) -c -o $@ $< $(CFLAGS)

rng.o: rng.c
	$(CC) -c $(CFLAGS) -o $@ $<

mirath_5b_s: main.o sign.o $(OBJ_MAIN)
	$(CC) -o $@ $^ $(LIBS)

PQCgenKAT_sign: PQCgenKAT_sign.o sign.o $(OBJ_KATS)
	$(CC) -o $@ $^ $(LIBS)

custom_bench: custom_bench.o sign.o $(OBJ_CUSTOM_BENCH)
	mkdir -p $(BENCHMARK_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) -o $(BENCHMARK_FOLDER)/$(INSTANCE)/bench $^ $(LIBS) -lm -lcpucycles


run: PQCgenKAT_sign
	./PQCgenKAT_sign

.PHONY: clean

clean:
	rm -f *.o *.su
	rm -f common/*.o
	rm -f mirath_5b_s
	rm -f PQCgenKAT_sign
	rm -f PQCsignKAT_*.req
	rm -f PQCsignKAT_*.rsp
	rm -rf $(BENCHMARK_FOLDER)/$(INSTANCE)/bench
