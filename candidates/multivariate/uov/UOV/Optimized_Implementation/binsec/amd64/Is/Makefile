
CC ?=    clang
LD =    $(CC)


ifndef PROJ
PROJ = Ip
# PROJ = Is
#PROJ = III
#PROJ = V
endif

BASE_DIR    = ../../..
PROJ        = amd64/Is
SRC_DIR     := $(BASE_DIR)/$(PROJ)

CFLAGS   := -O3 $(CFLAGS) -std=c99 -Wall -Wextra -Wpedantic -Werror -fno-omit-frame-pointer
INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
LDFLAGS  := $(LDFLAGS)
LIBPATH  = -L/usr/local/lib -L/opt/local/lib -L/usr/lib
LIBS     = -lcrypto

CFLAGS += 


SRCS           :=  $(wildcard $(SRC_DIR)/*.c)

OBJ = $(patsubst $(SRC_DIR)/%.c,$(BUILD)/%.o,$(SRCS))

CFLAGS       += -D_NIST_KAT_
INCPATH      += -I$(BASE_DIR)/amd64/nistkat
RNG				=$(BASE_DIR)/amd64/nistkat/rng.c
#RNG				=$(SRC_DIR)/nistkat/rng.c
OBJ          += $(BUILD)/rng.o



BUILD           = build
BUILD_KEYPAIR	= $(BUILD)/uov_keypair
BUILD_SIGN		= $(BUILD)/uov_sign 

KEYPAIR_FOLDER 	= uov_keypair
SIGN_FOLDER 	= uov_sign

BUILD_DIRS_ALL = $(BUILD) $(BUILD_KEYPAIR) $(BUILD_SIGN)


EXECUTABLE_KEYPAIR      = uov_keypair/test_harness_crypto_sign_keypair
EXECUTABLE_SIGN         = uov_sign/test_harness_crypto_sign

TOOL_LIBS = 
TOOL_FLAGS = -g

.INTERMEDIATE:  $(OBJ)
.PHONY: all clean

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
