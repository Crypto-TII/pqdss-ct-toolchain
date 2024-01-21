
CC = gcc

CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls -Wshadow -Wvla         -Wpointer-arith -O3 -march=native -mtune=native

BASE_DIR = ../../SNOVA-24-5-16-4-esk

BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/snova_keypair
BUILD_SIGN		= $(BUILD)/snova_sign 

KEYPAIR_FOLDER 	= snova_keypair
SIGN_FOLDER 	= snova_sign

EXECUTABLE_KEYPAIR      = snova_keypair/test_harness_crypto_sign_keypair
EXECUTABLE_SIGN         = snova_sign/test_harness_crypto_sign

TOOL_LIBS = 
TOOL_FLAGS = -static -g

#BUILD_OUT_PATH = $(BASE_DIR)/build/
BUILD_OUT_PATH = $(BUILD)/

OLIST = $(BUILD_OUT_PATH)rng.o $(BUILD_OUT_PATH)snova.o

# snova params
SNOVA_V = 24
SNOVA_O = 5
SNOVA_L = 4
SK_IS_SEED = 0 # 0: sk = ssk; 1: sk = esk 
TURBO = 1
CRYPTO_ALGNAME = "SNOVA_$(SNOVA_V)_$(SNOVA_O)_$(SNOVA_L)"
SNOVA_PARAMS = -D v_SNOVA=$(SNOVA_V) -D o_SNOVA=$(SNOVA_O) -D l_SNOVA=$(SNOVA_L) -D sk_is_seed=$(SK_IS_SEED)         -D CRYPTO_ALGNAME=$(CRYPTO_ALGNAME) -D TURBO=$(TURBO)


all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

# $(BASE_DIR)/build/rng.o:
# 	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/build/rng.o $(BASE_DIR)/rng.c -lcrypto
# 
# $(BASE_DIR)/build/snova.o: $(BASE_DIR)/build/rng.o
# 	$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/snova.o $(BASE_DIR)/snova.c -lcrypto
# 
# $(BASE_DIR)/build/sign.o: $(BASE_DIR)/build/snova.o
# 	$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BASE_DIR)/build/sign.o $(BASE_DIR)/sign.c -lcrypto

$(BUILD)/rng.o:
	$(CC) $(CFLAGS) -c -o $(BUILD)/rng.o $(BASE_DIR)/rng.c -lcrypto

$(BUILD)/snova.o: $(BUILD)/rng.o
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/snova.o $(BASE_DIR)/snova.c -lcrypto

$(BUILD)/sign.o: $(BUILD)/snova.o
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) -c -o $(BUILD)/sign.o $(BASE_DIR)/sign.c -lcrypto 

$(EXECUTABLE_KEYPAIR): $(BUILD)/sign.o
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(CFLAGS) $(TOOL_FLAGS) $(SNOVA_PARAMS) $(OLIST) $(BUILD)/sign.o         $(EXECUTABLE_KEYPAIR).c -o $(BUILD)/$@ -lcrypto $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(BUILD)/sign.o
	mkdir -p $(BUILD_SIGN)
	$(CC) $(CFLAGS) $(SNOVA_PARAMS) $(TOOL_FLAGS) $(OLIST) $(BUILD)/sign.o         $(EXECUTABLE_SIGN).c -o $(BUILD)/$@ -lcrypto $(TOOL_LIBS)

clean:
	rm -f $(BASE_DIR)/build/*.o *.a
	rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 
