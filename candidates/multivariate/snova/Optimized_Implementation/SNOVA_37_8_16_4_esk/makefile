CC = gcc

TOOLS_FLAGS:=-std=c11
TOOL_LINK_LIBS:=-lm
CTTEST_LIB_CFLAGS:=

CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla -Wpointer-arith -O3 -march=native -mtune=native -fPIC $(TOOLS_FLAGS)

BUILD_OUT_PATH = ./build/

OLIST = $(BUILD_OUT_PATH)rng.o $(BUILD_OUT_PATH)snova.o

# snova params
SNOVA_V = 37
SNOVA_O = 8
SNOVA_L = 4
SK_IS_SEED = 0 # 0: sk = ssk; 1: sk = esk
TURBO = 1
CRYPTO_ALGNAME = \"SNOVA_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L)\"
SNOVA_PARAMS = -D v_SNOVA=$(SNOVA_V) -D o_SNOVA=$(SNOVA_O) -D l_SNOVA=$(SNOVA_L) -D sk_is_seed=$(SK_IS_SEED) -D CRYPTO_ALGNAME=$(CRYPTO_ALGNAME) -D TURBO=$(TURBO)

CTTEST_LIB = libcttest.so
BUILD_CTLIB = build
CTTEST_LIB_CFLAGS = $(CFLAGS)

all: $(CTTEST_LIB)

clean:
	rm -f ./build/*.o *.a 

clean_all: 
	rm -f ./build/*.o *.a *.log *.req *.rsp

create_build_dir:
	mkdir -p  $(BUILD_CTLIB)

$(CTTEST_LIB): create_build_dir | build/sign.o
	mkdir -p $(BUILD_CTLIB)
	echo $(CTTEST_LIB_CFLAGS) > $(BUILD_CTLIB)/cflags.txt
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(OLIST) ./build/sign.o -shared -o $(BUILD_CTLIB)/$(CTTEST_LIB) $(TOOL_LINK_LIBS) -lcrypto


build/rng.o: 
	$(CC) $(CFLAGS) -c -o ./build/rng.o ./rng.c -lcrypto

build/snova.o: build/rng.o
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o ./build/snova.o ./snova.c -lcrypto

build/sign.o: build/snova.o
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o ./build/sign.o ./sign.c -lcrypto

test: build/rng.o build/snova.o
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(OLIST) ./test/test.c -o test.a -lcrypto
	./test.a > test-$(SNOVA_V)-$(SNOVA_O)-$(SNOVA_L).log

test_api: build/rng.o build/snova.o build/sign.o
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(OLIST) ./test/test_api.c ./build/sign.o -o test_api.a -lcrypto
	./test_api.a > test_api_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L).log


PQCgenKAT: build/sign.o
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(OLIST) ./build/sign.o ./PQCgenKAT_sign.c -o ./PQCgenKAT.a -lcrypto
	./PQCgenKAT.a
