PLATFORM=avx2
CC=gcc

TOOLS_FLAGS :=
TOOL_LINK_LIBS :=
CTTEST_LIB_CFLAGS :=

CFLAGS=-march=native -mtune=native -O3 -fomit-frame-pointer -fwrapv -fPIC -fPIE -fopenmp -Wno-deprecated-declarations -Wno-unused-result -fPIC $(TOOLS_FLAGS) # -ggdb3 # -DQRUOV_PRG_SHAKE
LDFLAGS=-lcrypto -Wl,-Bstatic -lcrypto -Wl,-Bdynamic -lm
# CFLAGS=-march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -fopenmp -Wno-deprecated-declarations -Wno-unused-result -pg -g # -ggdb3
# LDFLAGS=-lcrypto -Wl,-Bstatic -lcrypto -Wl,-Bdynamic -lm -pg -g
OBJS=Fql.o PQCgenKAT_sign.o qruov.o rng.o sign.o matrix.o mgf.o

.SUFFIXES:
.SUFFIXES: .rsp .req .diff .c .o .h

.PHONY: all clean

INSTANCE:=qruov5q127L3v306m105
CTTEST_LIB = libcttest.so
BUILD_CTLIB = ../../build/$(INSTANCE)
CTTEST_LIB_CFLAGS := $(CFLAGS)


all: qruov_config.h api.h PQCgenKAT_sign $(CTTEST_LIB)
	#bash -c "time ./PQCgenKAT_sign"

$(CTTEST_LIB): Makefile ${OBJS}
	mkdir -p $(BUILD_CTLIB)
	echo $(CTTEST_LIB_CFLAGS) > $(BUILD_CTLIB)/cflags.txt
	$(CC) ${OBJS} ${CFLAGS} -shared -o $(BUILD_CTLIB)/$(CTTEST_LIB) ${LDFLAGS}


PQCgenKAT_sign: Makefile ${OBJS}
	${CC} ${OBJS} ${CFLAGS} ${LDFLAGS} -o $@

qruov_config.h: qruov_config_h_gen.c
	${CC} @qruov_config.txt -DQRUOV_PLATFORM=${PLATFORM} -DQRUOV_CONFIG_H_GEN ${CFLAGS} ${LDFLAGS} qruov_config_h_gen.c
	./a.out > qruov_config.h
	rm a.out

api.h: api_h_gen.c
	${CC} -DAPI_H_GEN ${CFLAGS} ${LDFLAGS} api_h_gen.c
	./a.out > api.h
	rm a.out

clean:
	rm -f PQCgenKAT_sign PQCsignKAT_*.req PQCsignKAT_*.rsp ${OBJS}
	rm $(BUILD_CTLIB)/$(CTTEST_LIB)
