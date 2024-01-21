
CC?=gcc
ALL_FLAGS?=-O3 -flto -fPIC -std=c11 -march=native -Wall -Wextra -Wpedantic -Wshadow         	-DPARAM_HYPERCUBE_7R -DPARAM_GF31 -DPARAM_L1 -DPARAM_RND_EXPANSION_X4 -DHASHX4 -DXOFX4  -DPRGX4 -DNDEBUG -mavx

ALL_FLAGS+=$(EXTRA_ALL_FLAGS) -g 

BASE_DIR = ../../mqom_cat1_gf31_short

SYM_OBJ= $(BASE_DIR)/rnd.o $(BASE_DIR)/hash.o $(BASE_DIR)/xof.o
ARITH_OBJ= $(BASE_DIR)/gf31-matrix.o $(BASE_DIR)/gf31.o
MPC_OBJ= $(BASE_DIR)/mpc.o $(BASE_DIR)/witness.o $(BASE_DIR)/serialization-specific.o $(BASE_DIR)/precomputed.o
CORE_OBJ= $(BASE_DIR)/keygen.o $(BASE_DIR)/sign.o $(BASE_DIR)/views.o $(BASE_DIR)/commit.o         	$(BASE_DIR)/sign-mpcith-hypercube.o $(BASE_DIR)/tree.o

HASH_PATH=$(BASE_DIR)/sha3
HASH_MAKE_OPTIONS=PLATFORM=avx2 
HASH_INCLUDE=-I$(BASE_DIR)/sha3 -I. -I$(BASE_DIR)/sha3/avx2

BUILD					= build
BUILD_KEYPAIR			= $(BUILD)/mqom_keypair
BUILD_SIGN			= $(BUILD)/mqom_sign

EXECUTABLE_KEYPAIR_OBJ	    = mqom_keypair/taint_crypto_sign_keypair.o $(BASE_DIR)/generator/rng.o
EXECUTABLE_SIGN_OBJ		    = mqom_sign/taint_crypto_sign.o $(BASE_DIR)/generator/rng.o

EXECUTABLE_KEYPAIR  = mqom_keypair/taint_crypto_sign_keypair
EXECUTABLE_SIGN     = mqom_sign/taint_crypto_sign

TOOL_LIBS = -lctgrind -lm
TOOL_FLAGS = -Wall -ggdb  -std=c99  -Wextra


%.o : %.c
	$(CC) -c $(ALL_FLAGS) $(HASH_INCLUDE) -I. $< -o $@

all: $(EXECUTABLE_KEYPAIR) $(EXECUTABLE_SIGN) 

libhash:
	$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH)

$(EXECUTABLE_KEYPAIR): $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
	mkdir -p $(BUILD) 
	mkdir -p $(BUILD_KEYPAIR)
	$(CC) $(EXECUTABLE_KEYPAIR_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ)         	$(TOOL_FLAGS) $(ALL_FLAGS) -L$(HASH_PATH) -L. $(TOOL_LIBS) -lhash -lcrypto -o $(BUILD)/$@

$(EXECUTABLE_SIGN): $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) libhash
	mkdir -p $(BUILD)
	mkdir -p $(BUILD_SIGN)
	$(CC) $(EXECUTABLE_SIGN_OBJ) $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ) $(TOOL_FLAGS)         	$(ALL_FLAGS) -L$(HASH_PATH) -L. $(TOOL_LIBS) -lhash -lcrypto -o $(BUILD)/$@

clean:
	rm -f $(SYM_OBJ) $(ARITH_OBJ) $(MPC_OBJ) $(CORE_OBJ)
	rm -f $(EXECUTABLE_KEYPAIR_OBJ) $(EXECUTABLE_SIGN_OBJ)  
	rm -rf unit-*
	$(HASH_MAKE_OPTIONS) make -C $(HASH_PATH) clean
