CC=gcc
CFLAGS=-std=c11 -Wall -Wextra -pedantic -mavx2 -g -static
DEPS=$(wildcard ../../mirith_neon_Ia_short/*.h)
OBJ=$(patsubst ../../mirith_neon_Ia_short/%.c,../../mirith_neon_Ia_short/%.o,$(wildcard ../../mirith_neon_Ia_short/*.c))
OBJ+=$(patsubst ../../mirith_neon_Ia_short/%.s,../../mirith_neon_Ia_short/%.o,$(wildcard ../../mirith_neon_Ia_short/*.s))

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	ASMFLAGS := ${CFLAGS}
endif
ifeq ($(UNAME_S),Darwin)
	ASMFLAGS := ${CFLAGS} -x assembler-with-cpp -Wa,-defsym,old_gas_syntax=1 -Wa,-defsym,no_plt=1
endif


all: test_harness_crypto_sign_keypair test_harness_crypto_sign

%.o: %.s
	$(CC) -c $(ASMFLAGS) -o $@ $<

%.o: %.c $(DEPS)
	$(CC) -c $(CFLAGS) -o $@ $<


test_harness_crypto_sign_keypair: test_harness_crypto_sign_keypair.o $(OBJ)
	$(CC) ${LIBDIR} -o $@ $^ $(CFLAGS) $(LIBS)

test_harness_crypto_sign: test_harness_crypto_sign.o $(OBJ)
	$(CC) ${LIBDIR} -o $@ $^ $(CFLAGS) $(LIBS)

run: test_harness_crypto_sign
	./test_harness_crypto_sign

.PHONY: clean

clean:
	rm -f *.o *.su
	rm -f ../../mirith_neon_Ia_short/*.o ../../mirith_neon_Ia_short/*.su
	rm -f ./test_harness_crypto_sign
	rm -f ./test_harness_crypto_sign_keypair
