CC=    clang
LD=    clang

ifndef PROJ
PROJ = Ip
#PROJ = Is
#PROJ = III
#PROJ = V
endif

SRC_DIR  := $(PROJ)

TOOLS_FLAGS:=-std=c11
TOOL_LINK_LIBS:=-lm
CTTEST_LIB_CFLAGS:=

CFLAGS   := -O3 $(CFLAGS) -std=c99 -Wall -Wextra -Wpedantic -Werror -fno-omit-frame-pointer -fPIC $(TOOLS_FLAGS)
INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
LDFLAGS  := $(LDFLAGS)
LIBPATH  = -L/usr/local/lib -L/opt/local/lib -L/usr/lib
LIBS     = -lcrypto

CFLAGS += -flax-vector-conversions

SRCS           :=  $(wildcard $(SRC_DIR)/*.c)
SRCS_O         :=  $(SRCS:.c=.o)
SRCS_O_NOTDIR  :=  $(notdir $(SRCS_O))

OBJ = $(SRCS_O_NOTDIR)

EXE= sign_api-test

ifdef KAT
	CFLAGS       += -D_NIST_KAT_
	SRC_EXT_DIRS := nistkat
	INCPATH      += -I./nistkat
	OBJ          += rng.o
	EXE          += PQCgenKAT_sign
endif

CTTEST_LIB = libcttest.so
BUILD_CTLIB = build
CTTEST_LIB_CFLAGS := $(filter-out -Werror,$(CFLAGS))

.INTERMEDIATE:  $(OBJ)
.PHONY: all clean

#all: $(EXE)
all: $(CTTEST_LIB)

$(CTTEST_LIB): $(OBJ)
	mkdir -p $(BUILD_CTLIB)/$(SRC_DIR)
	echo $(CTTEST_LIB_CFLAGS) > $(BUILD_CTLIB)/$(SRC_DIR)/cflags.txt
	$(LD) $(LDFLAGS) $(LIBPATH) $(OBJ) -shared -o $(BUILD_CTLIB)/$(SRC_DIR)/$(CTTEST_LIB) $(LIBS)


sign_api-test: $(OBJ) sign_api-test.c
	$(CC) $(CFLAGS) $(INCPATH) $(LDFLAGS) $(LIBPATH) $^ -o $@ $(LIBS)

PQCgenKAT_sign: $(OBJ) PQCgenKAT_sign.o
	$(LD) $(LDFLAGS) $(LIBPATH) -o $@ $^ $(LIBS)

PQCgenKAT_sign.o: nistkat/PQCgenKAT_sign.c
	$(CC) $(CFLAGS) $(INCPATH) -c $<

%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) $(INCPATH) -c $<

%.o: %.c
	$(CC) $(CFLAGS) $(INCPATH) -c $<

define GEN_O
%.o: $(1)/%.c
	$(CC) $(CFLAGS) $(INCPATH) -c $$<
endef
$(foreach dir, $(SRC_EXT_DIRS), $(eval $(call GEN_O,$(dir))))


clean:
	-rm -f *.o *.req *.rsp PQCgenKAT_sign $(EXE);
	-rm -rf $(BUILD_CTLIB)/$(SRC_DIR)
