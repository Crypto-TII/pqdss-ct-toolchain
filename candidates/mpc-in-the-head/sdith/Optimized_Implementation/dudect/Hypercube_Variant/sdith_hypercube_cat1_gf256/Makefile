
SCRIPT_VERSION=v1.0
SCRIPT_AUTHOR=MIRA team

CC=gcc
C_FLAGS:=-O3 -flto -mavx2 -mpclmul -msse4.2 -maes -std=c99 -pedantic -Wall -Wextra -DSHAKE_TIMES4 -g 

BASE_DIR = ../../Hypercube_Variant/sdith_hypercube_cat1_gf256

RANDOMBYTES_SRC:=$(BASE_DIR)/lib/randombytes/randombytes.c
RANDOMBYTES_INCLUDE:=-I $(BASE_DIR)/lib/randombytes -lcrypto

XKCP_SRC:=$(BASE_DIR)/lib/XKCP
XKCP_SRC_SIMPLE:=$(XKCP_SRC)/SimpleFIPS202.c
XKCP_INCLUDE:=-I$(XKCP_SRC) -I$(XKCP_SRC)/avx2
XKCP_INCLUDE_SIMPLE:=-I $(XKCP_SRC)
XKCP_LINKER:=-L$(XKCP_SRC) -lshake

WRAPPER_SRC:=$(BASE_DIR)/src/wrapper
WRAPPER_INCLUDE:=-I $(WRAPPER_SRC)

FFI_SRC:=$(BASE_DIR)/src/finite_fields
FFI_INCLUDE:=-I $(FFI_SRC)

SRC:=$(BASE_DIR)/src
INCLUDE:=-I $(BASE_DIR)/src $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) $(RANDOMBYTES_INCLUDE)


MIRA_OBJS:=finite_fields.o keygen.o sign.o verify.o nist_sign.o mpc.o parsing.o tree.o
LIB_OBJS:=SimpleFIPS202.o randombytes.o

BUILD:=build
BIN:=build/bin
BUILD_KEYPAIR			= $(BUILD)/sdith_keypair
BUILD_SIGN			= $(BUILD)/sdith_sign

BINSEC_STATIC_FLAG      = -static
EXECUTABLE_KEYPAIR	    = sdith_keypair/dude_crypto_sign_keypair
EXECUTABLE_SIGN		    = sdith_sign/dude_crypto_sign

TOOL_LIBS = -lm
TOOL_FLAGS = -std=c11

folders:
	@echo -e "### Creating build/bin folders"
	mkdir -p $(BUILD)
	mkdir -p $(BIN)
	mkdir -p $(BUILD_KEYPAIR)
	mkdir -p $(BUILD_SIGN) 


randombytes.o: folders
	@echo -e "### Compiling $@"
	$(CC) $(C_FLAGS) -c $(RANDOMBYTES_SRC) $(RANDOMBYTES_INCLUDE) -o $(BIN)/$@

SimpleFIPS202.o: folders
	@echo -e "### Compiling $@"
	$(CC) $(C_FLAGS) -c $(XKCP_SRC_SIMPLE) $(XKCP_INCLUDE_SIMPLE) $(XKCP_INCLUDE) $(XKCP_LINKER)         -o $(BIN)/SimpleFIPS202.o

xkcp: folders
	@echo -e "### Compiling XKCP"
	make -C $(XKCP_SRC)


finite_fields.o: $(FFI_SRC)/finite_fields.c | folders
	@echo -e "### Compiling finite_fields"
	$(CC) $(C_FLAGS) -c $< $(FFI_INCLUDE) $(WRAPPER_INCLUDE) $(XKCP_INCLUDE) -o $(BIN)/$@

%.o: $(SRC)/%.c | folders
	@echo -e "### Compiling $@"
	$(CC) $(C_FLAGS) -c $< $(INCLUDE) -o $(BIN)/$@


all:  $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN)  ##@Build Build all the project

$(EXECUTABLE_KEYPAIR): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files
	@echo -e "### Compiling MIRA-128F (test harness keypair)"
	$(CC) $(TOOL_FLAGs) $(C_FLAGS) $(EXECUTABLE_KEYPAIR).c $(addprefix $(BIN)/, $^)         $(INCLUDE) $(XKCP_LINKER) $(TOOL_LIBS) -o $(BUILD)/$@

$(EXECUTABLE_SIGN): $(MIRA_OBJS) $(LIB_OBJS) | xkcp folders ##@Build generate KAT files
	@echo -e "### Compiling MIRA-128F (test harness sign)"
	$(CC) $(TOOL_FLAGs) $(C_FLAGS) $(EXECUTABLE_SIGN).c $(addprefix $(BIN)/, $^)         $(INCLUDE) $(XKCP_LINKER) $(TOOL_LIBS) -o $(BUILD)/$@

.PHONY: clean
clean:
	make -C $(XKCP_SRC) clean
	rm -f $(EXECUTABLE_KEYPAIR)
	rm -f $(EXECUTABLE_SIGN)
	rm -rf $(BUILD)/bin
