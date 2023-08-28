CC=gcc
CFLAGS=-std=c11 -Wall -Wextra -pedantic -g
DEPS=$(wildcard ../*.h)
OBJ=$(patsubst ../%.c,../%.o,$(wildcard ../*.c))
OBJ+=$(patsubst ../%.s,../%.o,$(wildcard ../*.s))

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	CFLAGS :=  ${CFLAGS} -lcrypto
    ASMFLAGS := ${CFLAGS}
endif
ifeq ($(UNAME_S),Darwin)
    CFLAGS :=  ${CFLAGS} -I/usr/local/opt/openssl/include
	LIBS :=-L/usr/local/opt/openssl/lib -lcrypto
endif



all: test_harness_keypair

%.o: %.s
	$(CC) -c $(ASMFLAGS) -o $@ $<

%.o: %.c $(DEPS)
	$(CC) -c $(CFLAGS)  -o $@ $<


test_harness_keypair: test_harness_keypair.o $(OBJ)
	$(CC) ${LIBDIR} -o $@ $^ $(CFLAGS)    $(LIBS)



run: test_harness_keypair
	./test_harness_keypair

.PHONY: clean

clean:
	rm -f *.o *.su
	rm -f ../*.o ../*.su
	rm -f ./test_harness_keypair
