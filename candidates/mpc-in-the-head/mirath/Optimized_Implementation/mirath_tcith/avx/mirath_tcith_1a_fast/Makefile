
TOOLS_FLAGS:=-g
TOOL_LINK_LIBS:=
CTTEST_LIB_CFLAGS:=
TOOL_NAME:=binsec
TEMPLATE_PATTERN:=test_harness

CT_TEST_DIR:=ct_tests
KEYPAIR:=crypto_sign_keypair
SIGN:=crypto_sign
KEYPAIR_TARGET:=$(TEMPLATE_PATTERN)_$(KEYPAIR)
SIGN_TARGET:=$(TEMPLATE_PATTERN)_$(SIGN)




INSTANCE = mirath_tcith_1a_fast
BENCHMARK_FOLDER = ../../../../benchmarks
CTTEST_FOLDER = ../../../../$(TOOL_NAME)


CFLAGS =-O3 -std=c11 -Wall -Wextra -pedantic -mavx -mavx2 -mbmi -mbmi2 -maes -fPIC $(TOOLS_FLAGS)


MIRATH = .
COMMON = $(MIRATH)/common
RIJNDAEL = $(COMMON)/rijndael
PARAMETERS = $(MIRATH)/parameters
ARITH = $(MIRATH)/arith
ARITH_X = $(ARITH)/q_16
ARITH_MU = $(ARITH_X)/mu_fast

#INCLUDES = -I$(PARAMETERS) -I$(ARITH_MU) -I$(ARITH_X) -I$(ARITH) -I$(RIJNDAEL) -I$(COMMON) -I$(MIRATH)
INCLUDES = -I. -I$(PARAMETERS) -I$(ARITH_MU) -I$(ARITH_X) -I$(ARITH) -I$(RIJNDAEL) -I$(COMMON) -I$(MIRATH)

LIBS = -lcrypto

TMP=rng.o $(subst common/random.o, ,$(patsubst common/%.c,common/%.o,$(wildcard common/*.c)))
OBJ=$(subst common/KeccakP-1600-times4-SIMD256.o, ,$(TMP))
#OBJ+=$(patsubst %.c,%.o,$(wildcard *.c))
OBJ+=$(patsubst %.c,%.o, $(filter-out custom_bench.c, $(wildcard *.c)) )

OBJ+= $(CT_TEST_DIR)/$(TOOL_NAME)/$(KEYPAIR_TARGET).o $(CT_TEST_DIR)/$(TOOL_NAME)/$(SIGN_TARGET).o


OBJ_MAIN = $(filter-out PQCgenKAT_sign.o, $(OBJ))
OBJ_KATS = $(filter-out main.o, $(OBJ))



VPATH = $(PARAMETERS):$(ARITH_MU):$(ARITH_X):$(ARITH):$(RIJNDAEL):$(COMMON):$(MIRATH)

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    CFLAGS += -I/usr/local/opt/openssl/include
    LIBS += -L/usr/local/opt/openssl/lib
endif

CTTEST_LIB = libcttest.so
BUILD_CTLIB = build
CTTEST_LIB_CFLAGS = $(CFLAGS)
OBJ_CUSTOM_BENCH = $(filter-out PQCgenKAT_sign.o main.o, $(OBJ))
#OBJ_CT_TESTS = $(filter-out PQCgenKAT_sign.o main.o custom_bench.o, $(OBJ))
#OBJ_CT_TESTS = $(filter-out PQCgenKAT_sign.o main.o custom_bench.o rng.o, $(OBJ))
#OBJ_CT_TESTS = $(filter-out PQCgenKAT_sign.o main.o custom_bench.o taint_crypto_sign.o rng.o, $(OBJ))
OBJ_CT_TESTS_GOOD = $(filter-out PQCgenKAT_sign.o main.o custom_bench.o ct_tests/taint_crypto_sign.o rng.o, $(OBJ))
#OBJ_CT_TESTS = $(filter-out PQCgenKAT_sign.o main.o custom_bench.o taint_crypto_sign.o, $(OBJ))

OBJECT_CT_TESTS = $(filter-out PQCgenKAT_sign.o main.o custom_bench.o $(CT_TEST_DIR)/$(TOOL_NAME)/$(KEYPAIR_TARGET).o $(CT_TEST_DIR)/$(TOOL_NAME)/$(SIGN_TARGET).o, $(OBJ))

$(info "=======OBJ_CT_TESTS: $(OBJECT_CT_TESTS)")
$(info "=======TEST_FOLDER_KP: $(CTTEST_FOLDER)/$(INSTANCE)/mirath_keypair")




#RUN_CT_TESTS:=
#
#ifndef RUN_CT_TESTS
#RUN_CT_TESTS:=
#endif
#
#CT_BENCH_TARGETS:=
#
#ifeq (RUN_CT_TESTS, ON)
#	CT_BENCH_TARGETS = CTTEST_LIB
#else
#	CT_BENCH_TARGETS = custom_bench
#endif
#
#
#$(info "====CT_BENCH_TARGETS: " $(CT_BENCH_TARGETS))

#all:  $(CTTEST_LIB) # TO BE FIXED: custom_bench
all:  crypto_sign_keypair crypto_sign # TO BE FIXED: custom_bench

%.o: %.c
	$(CC) -D_SHA3_ $(INCLUDES) -c -o $@ $< $(CFLAGS)

rng.o: rng.c
	$(CC) -c $(CFLAGS) -o $@ $<

#$(CTTEST_LIB): sign.o $(OBJ_CT_TESTS) parameters/mirath_param_128a.h  #sign.o
#	mkdir -p $(BUILD_CTLIB)
#	echo $(CTTEST_LIB_CFLAGS) > $(BUILD_CTLIB)/cflags.txt
#	$(CC) $(CFLAGS) $(INCLUDES) -shared -o $(BUILD_CTLIB)/$(CTTEST_LIB) $(LIBS) $(TOOL_LINK_LIBS)

$(CTTEST_LIB): $(OBJ_CT_TESTS)
	mkdir -p $(BUILD_CTLIB)
	echo $(CTTEST_LIB_CFLAGS) > $(BUILD_CTLIB)/cflags.txt
	$(CC) -D_SHA3_ $(CFLAGS) $(INCLUDES) $(OBJ_CT_TESTS) -shared -o $(BUILD_CTLIB)/$(CTTEST_LIB) $(LIBS) $(TOOL_LINK_LIBS)

ct_test: rng.o $(OBJ_CT_TESTS)
	mkdir -p $(BUILD_CTLIB)
	echo $(CTTEST_LIB_CFLAGS) > $(BUILD_CTLIB)/cflags.txt
	$(CC) -D_SHA3_ $(CFLAGS) $(INCLUDES) rng.o $(OBJ_CT_TESTS) -shared -o $(BUILD_CTLIB)/$(CTTEST_LIB) $(LIBS) $(TOOL_LINK_LIBS)

mirath_1a_f: main.o sign.o $(OBJ_MAIN)
	$(CC) -o $@ $^ $(LIBS)

PQCgenKAT_sign: PQCgenKAT_sign.o sign.o $(OBJ_KATS)
	$(CC) -o $@ $^ $(LIBS)

custom_bench: custom_bench.o sign.o $(OBJ_CUSTOM_BENCH)
	mkdir -p $(BENCHMARK_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) -o $(BENCHMARK_FOLDER)/$(INSTANCE)/bench $^ $(LIBS) -lm -lcpucycles

taint_crypto_sign: taint_crypto_sign.o sign.o $(OBJ_CT_TESTS)
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) -o $(CTTEST_FOLDER)/$(INSTANCE)/taint_crypto_sign $^ $(LIBS) $(TOOL_LINK_LIBS)

taint_crypto_sign_link1: taint_crypto_sign.o | $(CTTEST_LIB)
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) taint_crypto_sign.o -o $(CTTEST_FOLDER)/$(INSTANCE)/taint_crypto_sign_link $(LIBS) $(TOOL_LINK_LIBS) -L./build -lcttest

taint_crypto_sign_link_good_work: taint_crypto_sign.o rng.o | $(CTTEST_LIB)
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)
	$(CC) -D_SHA3_ $(CFLAGS) taint_crypto_sign.o rng.o -o $(CTTEST_FOLDER)/$(INSTANCE)/taint_crypto_sign_link $(LIBS) -L./build -lcttest $(TOOL_LINK_LIBS)

taint_crypto_sign_link_good_work_2: taint_crypto_sign.o | ct_test
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) taint_crypto_sign.o -o $(CTTEST_FOLDER)/$(INSTANCE)/taint_crypto_sign_link1 $(LIBS) -L./build -lcttest $(TOOL_LINK_LIBS)

taint_crypto_sign_link_good_work_3: taint_crypto_sign.o | ct_test
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) taint_crypto_sign.o -o taint_crypto_sign_link $(LIBS) -L./build -lcttest $(TOOL_LINK_LIBS)

taint_crypto_sign_link_good_work_4: ct_tests/taint_crypto_sign.o | ct_test
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) ct_tests/taint_crypto_sign.o -o ct_tests/taint_crypto_sign_link $(LIBS) -L./build -lcttest $(TOOL_LINK_LIBS)

taint_crypto_sign_link_good_work_5: ct_tests/taint_crypto_sign.o | ct_test
	mkdir -p $(CTTEST_FOLDER)/$(INSTANCE)
	$(CC) $(CFLAGS) ct_tests/taint_crypto_sign.o -o ct_tests/taint_crypto_sign_link $(LIBS) -L./build -lcttest $(TOOL_LINK_LIBS)


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
	rm -f mirath_1a_f
	rm -f PQCgenKAT_sign
	rm -f PQCsignKAT_*.req
	rm -f PQCsignKAT_*.rsp
	rm -rf $(BUILD_CTLIB)
	rm -rf $(BENCHMARK_FOLDER)/$(INSTANCE)/bench
	rm -rf $(CTTEST_FOLDER)/$(INSTANCE)/taint_crypto_sign
	rm $(CTTEST_FOLDER)/$(INSTANCE)/mirath_keypair/taint_crypto_sign_keypair
	rm $(CTTEST_FOLDER)/$(INSTANCE)/mirath_sign/taint_crypto_sign
	rm $(CT_TEST_DIR)/$(TOOL_NAME)/$(KEYPAIR_TARGET).o
	rm $(CT_TEST_DIR)/$(TOOL_NAME)/$(SIGN_TARGET).o
	rm ct_tests/taint_crypto_sign_link
	rm ct_tests/taint_crypto_sign.o
