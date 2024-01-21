
CC=gcc
WARNING_FLAGS=-Wall -Wextra -Wpedantic

BASE_DIR = ../../prov2

SHAKE_PATH= $(BASE_DIR)/SHAKE
CFLAGS= -O2 -I./$(SHAKE_PATH)/sha3
KATFLAGS= -I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib
LDFLAGS= $(SHAKE_PATH)/sha3/libshake.a

PROV_OBJ= $(BASE_DIR)/field.o $(BASE_DIR)/matrix.o $(BASE_DIR)/prov.o
KAT_OBJ= $(BASE_DIR)/field.o $(BASE_DIR)/matrix.o $(BASE_DIR)/prov.o $(BASE_DIR)/api.o $(BASE_DIR)/rng.o
SHAKE_OBJ = $(SHAKE_PATH)/hash.o
SHAKE= $(BASE_DIR)/shake


BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/prov_keypair
BUILD_SIGN		= $(BUILD)/prov_sign 

EXECUTABLE_KEYPAIR      = prov_keypair/dude_crypto_sign_keypair
EXECUTABLE_SIGN         = prov_sign/dude_crypto_sign

TOOL_LIBS = -lm
TOOL_FLAGS = -std=c11


all: $(SHAKE) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)

.PHONY : clean $(BASE_DIR)/shake

$(BASE_DIR)/shake:
	$(MAKE) -C $(SHAKE_PATH)

$(BASE_DIR)/rng.o: $(BASE_DIR)/rng.c
	$(CC) -c -O2 -I/usr/local/opt/openssl/include $< -o $@


$(EXECUTABLE_KEYPAIR): $(KAT_OBJ) $(BASE_DIR)/rng.o
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(@).c $(CFLAGS) $(KATFLAGS) $(KAT_OBJ) $(SHAKE_OBJ) $(TOOL_FLAGS)         -o $(BUILD)/$@ $(LDFLAGS) -lssl -lcrypto $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(KAT_OBJ) $(BASE_DIR)/rng.o
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) $(@).c $(CFLAGS) $(KATFLAGS) $(KAT_OBJ) $(SHAKE_OBJ) $(TOOL_FLAGS)         -o $(BUILD)/$@ $(LDFLAGS) -lssl -lcrypto $(TOOL_LIBS)

clean:
	rm -f $(BASE_DIR)/*.o $(BASE_DIR)/*.a
	rm -f $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
