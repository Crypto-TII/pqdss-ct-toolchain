
CC=    gcc
LD=    gcc

ifndef opt
opt = avx2
#opt = u64
endif

ifndef PROJ
PROJ = Ip
# PROJ = Is
#PROJ = III
#PROJ = V
endif

BASE_DIR    = ../..
PROJ        = III
SRC_DIR     := $(BASE_DIR)/$(PROJ)

CFLAGS	 := -O3 -std=c11 -Wall -Wextra -Wpedantic -fno-omit-frame-pointer
INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
LDFLAGS  := $(LDFLAGS)
LIBPATH  = -L/usr/local/lib -L/opt/local/lib -L/usr/lib
LIBS     = -lcrypto

CFLAGS += -mavx2 -maes

ifeq ($(opt), avx2)
    CFLAGS += -D_BLAS_AVX2_
endif
ifeq ($(opt), u64)
    CFLAGS += -D_BLAS_UINT64_
endif

ifeq ($(PROJ), Ip)
    CFLAGS += -D_TUOV256_112_44
endif
ifeq ($(PROJ), Is)
    CFLAGS += -D_TUOV16_160_64
endif
ifeq ($(PROJ), III)
    CFLAGS += -D_TUOV256_184_72
endif
ifeq ($(PROJ), V)
    CFLAGS += -D_TUOV256_244_96
endif

ifdef pkc
CFLAGS += -D_TUOV_PKC
endif

ifdef skc
CFLAGS += -D_TUOV_PKC_SKC
endif

SRCS           :=  $(wildcard $(SRC_DIR)/*.c)
# SRCS_O         :=  $(SRCS:.c=.o)
# SRCS_O_NOTDIR  :=  $(notdir $(SRCS_O))

#OBJ = $(SRCS_O_NOTDIR)
OBJ = $(patsubst $(SRC_DIR)/%.c,$(BUILD)/%.o,$(SRCS))

CFLAGS       += -D_NIST_KAT_
INCPATH      += -I$(BASE_DIR)/nistkat
RNG				=$(BASE_DIR)/nistkat/rng.c
OBJ          += $(BUILD)/rng.o



BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/tuov_keypair
BUILD_SIGN		= $(BUILD)/tuov_sign 

KEYPAIR_FOLDER 	= tuov_keypair
SIGN_FOLDER 	= tuov_sign

BUILD_DIRS_ALL = $(BUILD) $(BUILD_KEYPAIR) $(BUILD_SIGN)

EXECUTABLE_KEYPAIR      = tuov_keypair/dude_crypto_sign_keypair
EXECUTABLE_SIGN         = tuov_sign/dude_crypto_sign

TOOL_LIBS = -lm
TOOL_FLAGS = -std=c11

all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)


$(BUILD)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIRS_ALL)
	${hide}$(CC) -o $@ $< $(CFLAGS) $(INCPATH) -c

$(BUILD)/rng.o: $(RNG)
	${hide}$(CC) -o $@ $< $(CFLAGS) $(INCPATH) -c

$(BUILD_DIRS_ALL): %:
	mkdir -p $@

$(EXECUTABLE_KEYPAIR): $(OBJ) $(EXECUTABLE_KEYPAIR).c
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	${hide}$(CC) $(CFLAGS) $(TOOL_FLAGS) $(INCPATH) $(LDFLAGS) $(LIBPATH) $^         -o $(BUILD)/$@ $(LIBS) $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(OBJ) $(EXECUTABLE_SIGN).c
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	${hide}$(CC) $(CFLAGS) $(TOOL_FLAGS) $(INCPATH) $(LDFLAGS) $(LIBPATH) $^         -o $(BUILD)/$@ $(LIBS) $(TOOL_LIBS)

clean:
	 ${hide}-rm -f build/*.o $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
