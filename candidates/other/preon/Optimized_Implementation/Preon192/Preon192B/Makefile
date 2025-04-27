CC = cc

TOOLS_FLAGS:=-std=c11
TOOL_LINK_LIBS:=-lm
CTTEST_LIB_CFLAGS:=

CFLAGS := ${CFLAGS} -DUSE_PREON192B -DAES192=1 -DUSE_PRNG -O3 -fPIC $(TOOLS_FLAGS)
LFLAGS := ${LFLAGS} -lm -lssl -lcrypto
#OBJS = $(patsubst %.c, %.o, $(wildcard *.c))
OBJS = $(patsubst %.c, %.o, $(filter-out PQCgenKAT_sign.c, $(wildcard *.c)))


CTTEST_LIB = libcttest.so
BUILD_CTLIB = build
CTTEST_LIB_CFLAGS = $(CFLAGS)

all: $(CTTEST_LIB)


#all: $(OBJS)
#	@test -e .stopmakeonce || $(CC) $(CFLAGS) $(OBJS) $(LFLAGS) -o PQCgenKAT_sign
#	@test -e .stopmakeonce && rm .stopmakeonce || true

$(CTTEST_LIB): $(OBJS)
	mkdir -p $(BUILD_CTLIB)
	echo $(CTTEST_LIB_CFLAGS) > $(BUILD_CTLIB)/cflags.txt
	$(CC) $(CFLAGS) $(OBJS) $(LFLAGS) -shared -o $(BUILD_CTLIB)/$(CTTEST_LIB) $(TOOL_LINK_LIBS) -lcrypto


%.o: %.c
	@$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean 

clean:
	@rm -f *.o PQCgenKAT_sign
	@rm -rf $(BUILD_CTLIB)
