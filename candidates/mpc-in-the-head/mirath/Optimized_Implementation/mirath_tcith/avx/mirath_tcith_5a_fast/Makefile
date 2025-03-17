TOOLS_FLAGS:=-std=c11
TOOL_LINK_LIBS:=-lm
CTTEST_LIB_CFLAGS:=

TOOL_NAME:=dudect
TEMPLATE_PATTERN:=dude

CT_TEST_DIR:=ct_tests
KEYPAIR:=crypto_sign_keypair
SIGN:=crypto_sign
KEYPAIR_TARGET:=$(TEMPLATE_PATTERN)_$(KEYPAIR)
SIGN_TARGET:=$(TEMPLATE_PATTERN)_$(SIGN)
CTTEST_FOLDER = ../../../../$(TOOL_NAME)


INSTANCE = mirath_tcith_5a_fast
BENCHMARK_FOLDER = ../../../../benchmarks

CFLAGS =-O3 -std=c11 -Wall -Wextra -pedantic -mavx -mavx2 -mbmi -mbmi2 -maes -fPIC $(TOOLS_FLAGS)

MIRATH = .
COMMON = $(MIRATH)/common
RIJNDAEL = $(COMMON)/rijndael
PARAMETERS = $(MIRATH)/parameters
ARITH = $(MIRATH)/arith
ARITH_X = $(ARITH)/q_16
ARITH_MU = $(ARITH_X)/mu_fast

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

OBJECT_CT_TESTS = $(filter-out PQCgenKAT_sign.o main.o custom_bench.o $(CT_TEST_DIR)/$(TOOL_NAME)/$(KEYPAIR_TARGET).o $(CT_TEST_DIR)/$(TOOL_NAME)/$(SIGN_TARGET).o, $(OBJ))


#all: PQCgenKAT_sign mirath_5a_f
all: crypto_sign_keypair crypto_sign #custom_bench

%.o: %.c
	$(CC) -D_SHA3_ $(INCLUDES) -c -o $@ $< $(CFLAGS)

rng.o: rng.c
	$(CC) -c $(CFLAGS) -o $@ $<

mirath_5a_f: main.o sign.o $(OBJ_MAIN)
	$(CC) -o $@ $^ $(LIBS)

PQCgenKAT_sign: PQCgenKAT_sign.o sign.o $(OBJ_KATS)
	$(CC) -o $@ $^ $(LIBS)

custom_bench: custom_bench.o sign.o $(OBJ_CUSTOM_BENCH)
	mkdir -p $(BENCHMARK_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) -o $(BENCHMARK_FOLDER)/$(INSTANCE)/bench $^ $(LIBS) -lm -lcpucycles

crypto_sign_keypair: $(CT_TEST_DIR)/$(TOOL_NAME)/$(KEYPAIR_TARGET).o sign.o $(OBJECT_CT_TESTS)
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)/mirath_keypair
	$(CC) $(CFLAGS) -o $(CTTEST_FOLDER)/$(INSTANCE)/mirath_keypair/$(KEYPAIR_TARGET) $^ $(LIBS) $(TOOL_LINK_LIBS)

crypto_sign: $(CT_TEST_DIR)/$(TOOL_NAME)/$(SIGN_TARGET).o sign.o $(OBJECT_CT_TESTS)
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)/mirath_sign
	$(CC) $(CFLAGS) -o $(CTTEST_FOLDER)/$(INSTANCE)/mirath_sign/$(SIGN_TARGET) $^ $(LIBS) $(TOOL_LINK_LIBS)


run: PQCgenKAT_sign
	./PQCgenKAT_sign

.PHONY: clean

clean:
	rm -f *.o *.su
	rm -f common/*.o
	rm -f mirath_5a_f
	rm -f PQCgenKAT_sign
	rm -f PQCsignKAT_*.req
	rm -f PQCsignKAT_*.rsp
	rm -f $(BENCHMARK_FOLDER)/$(INSTANCE)/bench
	rm -rf $(CTTEST_FOLDER)/$(INSTANCE)/$(TEMPLATE_PATTERN)_crypto_sign
	rm -f $(CTTEST_FOLDER)/$(INSTANCE)/mirath_keypair/$(TEMPLATE_PATTERN)_crypto_sign_keypair
	rm -f $(CTTEST_FOLDER)/$(INSTANCE)/mirath_sign/$(TEMPLATE_PATTERN)_crypto_sign
	rm -f $(CT_TEST_DIR)/$(TOOL_NAME)/$(KEYPAIR_TARGET).o
	rm -f $(CT_TEST_DIR)/$(TOOL_NAME)/$(SIGN_TARGET).o
