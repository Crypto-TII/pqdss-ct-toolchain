
SCRIPT_VERSION=v1.0
SCRIPT_AUTHOR=RYDE team

CC=gcc
C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4
C_FLAGS_VERBOSE:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -DVERBOSE

BASE_DIR = ../../ryde128f

RANDOMBYTES_SRC:=$(BASE_DIR)/lib/randombytes/randombytes.c
RANDOMBYTES_INCLUDE:=-I $(BASE_DIR)/lib/randombytes -lcrypto

XKCP_SRC:=$(BASE_DIR)/lib/XKCP
XKCP_SRC_SIMPLE:=$(XKCP_SRC)/SimpleFIPS202.c
XKCP_INCLUDE:=-I$(XKCP_SRC) -I$(XKCP_SRC)/avx2
XKCP_INCLUDE_SIMPLE:=-I $(XKCP_SRC)
XKCP_LINKER:=-L$(XKCP_SRC) -lshake

WRAPPER_SRC:=$(BASE_DIR)/src/wrapper
WRAPPER_INCLUDE:=-I $(WRAPPER_SRC)

RBC_SRC:=$(BASE_DIR)/src/rbc-31
RBC_INCLUDE:=-I $(RBC_SRC)

SRC:=$(BASE_DIR)/src
INCLUDE:=-I $(BASE_DIR)/src $(RBC_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) $(RANDOMBYTES_INCLUDE)

RYDE_OBJS:=rbc_31_elt.o rbc_31_vec.o rbc_31_qpoly.o rbc_31_vspace.o rbc_31_mat.o keypair.o signature.o                     verification.o mpc.o parsing.o tree.o sign.o
LIB_OBJS:=SimpleFIPS202.o randombytes.o

#BUILD:=bin/build
#BIN:=bin
BUILD:=build
BIN:=build/bin


	EXECUTABLE_KEYPAIR	    = dude_crypto_sign_keypair
	EXECUTABLE_SIGN		    = dude_crypto_sign

	BUILD_KEYPAIR			= $(BUILD)/ryde_keypair
	BUILD_SIGN			= $(BUILD)/ryde_sign

	SRC_KEYPAIR	    	= ryde_keypair/dude_crypto_sign_keypair.c
	SRC_SIGN		    	= ryde_sign/dude_crypto_sign.c

TOOL_LIBS = -lm
TOOL_FLAGS = -std=c11

folders:
	@echo -e "### Creating build folders"
	mkdir -p $(BUILD)
	mkdir -p $(BIN)

randombytes.o: folders
	@echo -e "### Compiling $@"
	$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BIN)/$@

SimpleFIPS202.o: folders
	@echo -e "### Compiling $@"
	$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER)            -o $(BIN)/SimpleFIPS202.o

xkcp: folders
	@echo -e "### Compiling XKCP"
	make -C $(XKCP_SRC)

rbc_%.o: $(RBC_SRC)/rbc_%.c | folders
	@echo -e "### Compiling $@"
	$(CC) $(C_FLAGS) -c $< $(RBC_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BIN)/$@

%.o: $(SRC)/%.c | folders
	@echo -e "### Compiling $@"
	$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BIN)/$@ 

default: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)
all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 


$(EXECUTABLE_KEYPAIR): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build dude_crypto_sign_keypair
	@echo -e "### Compiling test harness keypair"
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(TOOL_FLAGS) $(C_FLAGS) $(SRC_KEYPAIR) $(addprefix $(BIN)/, $^)         $(INCLUDE) $(XKCP_LINKER) -o $(BUILD_KEYPAIR)/$@ $(TOOL_LIBS)

$(EXECUTABLE_SIGN): $(RYDE_OBJS) $(LIB_OBJS) | xkcp folders ##@Build build dude_crypto_sign
	@echo -e "### Compiling test harness sign"
	mkdir -p $(BUILD_SIGN)
	$(CC) $(TOOL_FLAG) $(C_FLAGS) $(SRC_SIGN) $(addprefix $(BIN)/, $^)         $(INCLUDE) $(XKCP_LINKER) -o $(BUILD_SIGN)/$@ $(TOOL_LIBS)

.PHONY: clean
clean: ##@Miscellaneous Clean data
	make -C $(XKCP_SRC) clean
	rm -f $(EXECUTABLE_KEYPAIR)
	rm -f $(EXECUTABLE_SIGN)
	rm -rf $(BIN)
