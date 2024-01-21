
CC = clang

LD =    $(CC)
ifndef PROJ
PROJ = Ip
# PROJ = Is
#PROJ = III
#PROJ = V
endif

BASE_DIR    = ../../..
PROJ        = amd64/III
SRC_DIR     := $(BASE_DIR)/$(PROJ)

INCPATH  := -I/usr/local/include -I/opt/local/include -I/usr/include -I$(SRC_DIR)
LIBPATH  = -L/usr/local/lib -L/opt/local/lib -L/usr/lib
LIBS     = -lcrypto

SRCS           :=  $(wildcard $(SRC_DIR)/*.c)
RNG				=$(BASE_DIR)/amd64/nistkat/rng.c
SRCS    += $(RNG)
SIGN = $(SRC_DIR)/sign.c

INCPATH      += -I$(BASE_DIR)/amd64/nistkat
INCS = $(wildcard $(BASE_DIR)/*.h)


BUILD			= build
BUILD_KEYPAIR	= $(BUILD)/uov_keypair
BUILD_SIGN		= $(BUILD)/uov_sign

EXECUTABLE_KEYPAIR_BC	= uov_keypair/rbc_crypto_sign_keypair.bc
EXECUTABLE_KEYPAIR_RBC	= uov_keypair/rbc_crypto_sign_keypair.rbc
EXECUTABLE_SIGN_BC		= uov_sign/rbc_crypto_sign.bc
EXECUTABLE_SIGN_RBC		= uov_sign/rbc_crypto_sign.rbc

all: $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)



$(EXECUTABLE_KEYPAIR_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_KEYPAIR_BC)

$(EXECUTABLE_KEYPAIR_RBC): $(EXECUTABLE_KEYPAIR_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_KEYPAIR_BC) > $(BUILD)/$(EXECUTABLE_KEYPAIR_RBC)

$(EXECUTABLE_SIGN_BC): $(SIGN) $(SRC) $(INCS)
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) -emit-llvm -c -g $(SIGN) $(INCPATH) -o $(BUILD)/$(EXECUTABLE_SIGN_BC)

$(EXECUTABLE_SIGN_RBC): $(EXECUTABLE_SIGN_BC)
	opt -instnamer -mem2reg $(BUILD)/$(EXECUTABLE_SIGN_BC) > $(BUILD)/$(EXECUTABLE_SIGN_RBC)

.PHONY: clean

clean:
	rm -f $(BUILD)/*.out $(BUILD)/*.txt $(BUILD)/*.dot
	rm -f $(EXECUTABLE_KEYPAIR_BC) $(EXECUTABLE_KEYPAIR_RBC) $(EXECUTABLE_SIGN_BC) $(EXECUTABLE_SIGN_RBC)
