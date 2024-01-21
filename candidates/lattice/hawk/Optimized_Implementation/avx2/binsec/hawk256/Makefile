
CC = c99
CFLAGS = -Wall -Wextra -Wshadow -Wundef -O2
LD = $(CC)
LDFLAGS =
LIBS =

BASE_DIR = ../../hawk256
BUILD					= build
BUILD_KEYPAIR			= $(BUILD)/hawk_keypair
BUILD_SIGN			= $(BUILD)/hawk_sign

OBJCORE = $(BASE_DIR)/hawk_kgen.o $(BASE_DIR)/hawk_sign.o $(BASE_DIR)/hawk_vrfy.o $(BASE_DIR)/ng_fxp.o     $(BASE_DIR)/ng_hawk.o $(BASE_DIR)/ng_mp31.o $(BASE_DIR)/ng_ntru.o $(BASE_DIR)/ng_poly.o      $(BASE_DIR)/ng_zint31.o $(BASE_DIR)/sha3.o
HEAD = $(BASE_DIR)/hawk.h $(BASE_DIR)/hawk_inner.h $(BASE_DIR)/hawk_config.h $(BASE_DIR)/sha3.h
NG_HEAD = $(BASE_DIR)/ng_config.h $(BASE_DIR)/ng_inner.h $(BASE_DIR)/sha3.h
OBJAPI = $(BASE_DIR)/api.o
OBJEXTRA_KEYPAIR = $(BASE_DIR)/rng.o $(EXECUTABLE_KEYPAIR).o
OBJEXTRA_SIGN = $(BASE_DIR)/rng.o $(EXECUTABLE_SIGN).o



BINSEC_STATIC_FLAG  = -static
EXECUTABLE_KEYPAIR	    = hawk_keypair/test_harness_crypto_sign_keypair
EXECUTABLE_SIGN		    = hawk_sign/test_harness_crypto_sign

$(BASE_DIR)/hawk_kgen.o: $(BASE_DIR)/hawk_kgen.c $(HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/hawk_kgen.o $(BASE_DIR)/hawk_kgen.c

$(BASE_DIR)/hawk_sign.o: $(BASE_DIR)/hawk_sign.c $(HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/hawk_sign.o $(BASE_DIR)/hawk_sign.c

$(BASE_DIR)/hawk_vrfy.o: $(BASE_DIR)/hawk_vrfy.c $(HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/hawk_vrfy.o $(BASE_DIR)/hawk_vrfy.c

$(BASE_DIR)/ng_fxp.o: $(BASE_DIR)/ng_fxp.c $(NG_HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_fxp.o $(BASE_DIR)/ng_fxp.c

$(BASE_DIR)/ng_hawk.o: $(BASE_DIR)/ng_hawk.c $(NG_HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_hawk.o $(BASE_DIR)/ng_hawk.c

$(BASE_DIR)/ng_mp31.o: $(BASE_DIR)/ng_mp31.c $(NG_HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_mp31.o $(BASE_DIR)/ng_mp31.c

$(BASE_DIR)/ng_ntru.o: $(BASE_DIR)/ng_ntru.c $(NG_HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_ntru.o $(BASE_DIR)/ng_ntru.c

$(BASE_DIR)/ng_poly.o: $(BASE_DIR)/ng_poly.c $(NG_HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_poly.o $(BASE_DIR)/ng_poly.c

$(BASE_DIR)/ng_zint31.o: $(BASE_DIR)/ng_zint31.c $(NG_HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/ng_zint31.o $(BASE_DIR)/ng_zint31.c

$(BASE_DIR)/sha3.o: $(BASE_DIR)/sha3.c $(NG_HEAD)
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/sha3.o $(BASE_DIR)/sha3.c

$(BASE_DIR)/api.o: $(BASE_DIR)/api.c $(BASE_DIR)/api.h $(BASE_DIR)/hawk.h $(BASE_DIR)/sha3.h
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/api.o $(BASE_DIR)/api.c

$(BASE_DIR)/rng.o: $(BASE_DIR)/rng.c $(BASE_DIR)/rng.h
	$(CC) $(CFLAGS) -c -o $(BASE_DIR)/rng.o $(BASE_DIR)/rng.c

$(EXECUTABLE_KEYPAIR).o: $(EXECUTABLE_KEYPAIR).c $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
	$(CC) $(CFLAGS) -c -o $(EXECUTABLE_KEYPAIR).o $(EXECUTABLE_KEYPAIR).c

$(EXECUTABLE_SIGN).o: $(EXECUTABLE_SIGN).c $(BASE_DIR)/api.h $(BASE_DIR)/rng.h
	$(CC) $(CFLAGS) -c -o $(EXECUTABLE_SIGN).o $(EXECUTABLE_SIGN).c

all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)


$(EXECUTABLE_KEYPAIR): $(OBJCORE) $(OBJAPI) $(OBJEXTRA_KEYPAIR)
	mkdir -p $(BUILD)  
	mkdir -p $(BUILD_KEYPAIR)
	$(LD) $(LDFLAGS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) -o $(BUILD)/$(EXECUTABLE_KEYPAIR) $(OBJCORE)         $(OBJAPI) $(OBJEXTRA_KEYPAIR) $(LIBS)

$(EXECUTABLE_SIGN): $(OBJCORE) $(OBJAPI) $(OBJEXTRA_SIGN)
	mkdir -p $(BUILD)  
	mkdir -p $(BUILD_SIGN)
	$(LD) $(LDFLAGS) $(BINSEC_STATIC_FLAGS) $(DEBUG_G_FLAG) -o $(BUILD)/$(EXECUTABLE_SIGN) $(OBJCORE)         $(OBJAPI) $(OBJEXTRA_SIGN) $(LIBS)


clean:
	-rm -f $(OBJCORE) $(OBJAPI) $(OBJEXTRA_KEYPAIR) $(OBJEXTRA_SIGN) $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
