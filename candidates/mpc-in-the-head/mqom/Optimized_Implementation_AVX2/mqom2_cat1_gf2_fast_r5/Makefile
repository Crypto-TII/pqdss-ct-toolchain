KECCAK_AVX2=1
RIJNDAEL_AES_NI=1
FIELDS_AVX2=1

TOOLS_FLAGS:=-Wall -g -Wextra
TOOL_LINK_LIBS:=
CTTEST_LIB_CFLAGS:=

# Compiler detection
# Detect if we are using clang or gcc
CLANG :=  $(shell $(CC) -v 2>&1 | grep clang)
ifeq ($(CLANG),)
  GCC :=  $(shell $(CC) -v 2>&1 | grep gcc)
endif

ifneq ($(CLANG),)
  # get clang version e.g. 14.1.3
  CLANG_VERSION := $(shell $(CROSS_COMPILE)$(CC) -dumpversion)
  # convert to single number e.g. 14 * 100 + 1
  CLANG_VERSION := $(shell echo $(CLANG_VERSION) | cut -f1-2 -d. | sed -e 's/\./*100+/g')
  # Calculate value - e.g. 1401
  CLANG_VERSION := $(shell echo $$(($(CLANG_VERSION))))
  # Comparison results (true if true, empty if false)
  CLANG_VERSION_GTE_12 := $(shell [ $(CLANG_VERSION) -ge 1200 ]  && echo true)
  CLANG_VERSION_GTE_13 := $(shell [ $(CLANG_VERSION) -ge 1300 ]  && echo true)
  CLANG_VERSION_GTE_16 := $(shell [ $(CLANG_VERSION) -ge 1600 ]  && echo true)
  CLANG_VERSION_GTE_17 := $(shell [ $(CLANG_VERSION) -ge 1700 ]  && echo true)
  CLANG_VERSION_GTE_18 := $(shell [ $(CLANG_VERSION) -ge 1800 ]  && echo true)
  CLANG_VERSION_GTE_19 := $(shell [ $(CLANG_VERSION) -ge 1900 ]  && echo true)
endif

# Keccak related stuff, in the form of an external library
LIB_HASH_DIR = sha3
LIB_HASH = $(LIB_HASH_DIR)/libhash.a
# Adjust the include dir depending on the target platform
ifeq ($(KECCAK_AVX2),1)
  # AVX2 optimized
  LIB_HASH_INCLUDES = $(LIB_HASH_DIR) $(LIB_HASH_DIR)/avx2
  PLATFORM=avx2
else
  # Generic portable C 64-bit optimized
  LIB_HASH_INCLUDES = $(LIB_HASH_DIR) $(LIB_HASH_DIR)/opt64
  PLATFORM=opt64
endif

# Rinjdael related stuff
RIJNDAEL_DIR = rijndael
RIJNDAEL_INCLUDES = $(RIJNDAEL_DIR)
RIJNDAEL_SRC_FILES = $(RIJNDAEL_DIR)/rijndael_ref.c $(RIJNDAEL_DIR)/rijndael_table.c $(RIJNDAEL_DIR)/rijndael_aes_ni.c
RIJNDAEL_OBJS   = $(patsubst %.c,%.o, $(filter %.c,$(RIJNDAEL_SRC_FILES)))
RIJNDAEL_OBJS  += $(patsubst %.s,%.o, $(filter %.s,$(RIJNDAEL_SRC_FILES)))
RIJNDAEL_OBJS  += $(patsubst %.S,%.o, $(filter %.S,$(RIJNDAEL_SRC_FILES)))

# Fields related stuff
# TODO
FIELDS_DIR = fields
FIELDS_INCLUDES = $(FIELDS_DIR)

# MQOM2 related elements
MQOM2_DIR = .
MQOM2_INCLUDES = $(MQOM2_DIR)
MQOM2_SRC_FILES = $(MQOM2_DIR)/xof.c $(MQOM2_DIR)/prg.c $(MQOM2_DIR)/ggm_tree.c $(MQOM2_DIR)/expand_mq.c $(MQOM2_DIR)/keygen.c $(MQOM2_DIR)/blc.c $(MQOM2_DIR)/piop.c $(MQOM2_DIR)/sign.c
MQOM2_OBJS   = $(patsubst %.c,%.o, $(filter %.c,$(MQOM2_SRC_FILES)))
MQOM2_OBJS  += $(patsubst %.s,%.o, $(filter %.s,$(MQOM2_SRC_FILES)))
MQOM2_OBJS  += $(patsubst %.S,%.o, $(filter %.S,$(MQOM2_SRC_FILES)))

OBJS = $(RIJNDAEL_OBJS) $(MQOM2_OBJS)

# AR and RANLIB
AR ?= ar
RANLIB ?= ranlib

# Basic CFLAGS
CFLAGS ?= -g -O3 -march=native -mtune=native -Wall -Wextra -Werror -DNDEBUG -fPIC $(TOOLS_FLAGS)
# Include the necessary headers
CFLAGS += $(foreach DIR, $(LIB_HASH_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(RIJNDAEL_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(FIELDS_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(MQOM2_INCLUDES), -I$(DIR))
CFLAGS += -Wall -Wextra -Werror
# Possibly append user provided extra CFLAGS
CFLAGS += $(EXTRA_CFLAGS)

ifneq ($(GCC),)
  # Remove gcc's -Warray-bounds and -W-stringop-overflow/-W-stringop-overread as they give many false positives
  CFLAGS += -Wno-array-bounds -Wno-stringop-overflow -Wno-stringop-overread
endif

######## Compilation toggles
## Adjust the optimization targets depending on the platform
ifeq ($(RIJNDAEL_TABLE),1)
  # Table based optimzed *non-constant time* Rijndael
  CFLAGS += -DRIJNDAEL_TABLE
else ifeq ($(RIJNDAEL_AES_NI),1)
  # AES-NI (requires support on the x86 platform) constant time Rijndael
  CFLAGS += -DRIJNDAEL_AES_NI
else
  # Reference constant time (slow) Rijndael
  CFLAGS += -DRIJNDAEL_CONSTANT_TIME_REF
endif
ifeq ($(FIELDS_REF),1)
  # Reference implementation for fields
  CFLAGS += -DFIELDS_REF
endif
ifeq ($(FIELDS_AVX2),1)
  # Force AVX2 implementation for fields
  CFLAGS += -DFIELDS_AVX2
endif
ifeq ($(FIELDS_GFNI),1)
  # Force GFNI implementation for fields
  CFLAGS += -DFIELDS_GFNI
endif

## Togles for various analysis and other useful stuff
# Static analysis of gcc
ifeq ($(FANALYZER),1)
  CFLAGS += -fanalyzer
endif
# Force Link Time Optimizations
# XXX: warning, this can be agressive and yield wrong results with -O3
ifeq ($(FLTO),1)
  CFLAGS += -flto
endif
# Use the sanitizers
ifeq ($(USE_SANITIZERS),1)
CFLAGS += -fsanitize=undefined -fsanitize=address -fsanitize=leak
endif
ifeq ($(WNOERROR), 1)
  # Sometimes "-Werror" might be too much, this can be overriden
  CFLAGS := $(subst -Werror,,$(CFLAGS))
endif
ifneq ($(PARAM_SECURITY),)
  # Adjust the security parameters as asked to
  CFLAGS += -DMQOM2_PARAM_SECURITY=$(PARAM_SECURITY)
endif

RNG_OBJ=generator/rng.o

CTTEST_LIB = libcttest.so
BUILD_CTLIB = build
CTTEST_LIB_CFLAGS = $(CFLAGS)

CTTEST_LIB_CFLAGS = $(filter-out -Isha3 -Isha3/avx2 -Irijndael -Ifields,$(CFLAGS))
CTTEST_LIB_CFLAGS += -I candidates/mpc-in-the-head/mqom/Optimized_Implementation_AVX2/mqom2_cat1_gf2_fast_r3/sha3
CTTEST_LIB_CFLAGS += -I candidates/mpc-in-the-head/mqom/Optimized_Implementation_AVX2/mqom2_cat1_gf2_fast_r3/sha3/avx2
CTTEST_LIB_CFLAGS += -I candidates/mpc-in-the-head/mqom/Optimized_Implementation_AVX2/mqom2_cat1_gf2_fast_r3/rijndael
CTTEST_LIB_CFLAGS += -I candidates/mpc-in-the-head/mqom/Optimized_Implementation_AVX2/mqom2_cat1_gf2_fast_r3/fields


#all: libhash $(OBJS)
all: $(CTTEST_LIB)

libhash:
	@echo "[+] Compiling libhash"
	cd $(LIB_HASH_DIR) && PLATFORM=$(PLATFORM) make

.c.o:
	$(CC) $(CFLAGS) -c -o $@ $<

.s.o:
	$(CC) $(CFLAGS) -c -o $@ $<

.S.o:
	$(CC) $(CFLAGS) -c -o $@ $<

$(CTTEST_LIB): libhash $(OBJS) $(RNG_OBJ)
	mkdir -p $(BUILD_CTLIB)
	echo $(CTTEST_LIB_CFLAGS) > $(BUILD_CTLIB)/cflags.txt
	$(CC) $(CFLAGS) $(OBJS) $(RNG_OBJ) $(LIB_HASH) -shared -o $(BUILD_CTLIB)/$(CTTEST_LIB) -lcrypto #generator/rng.c


sign: libhash $(OBJS)
	$(CC) $(CFLAGS) generator/PQCgenKAT_sign.c generator/rng.c $(OBJS) $(LIB_HASH) -lcrypto -o sign

kat_gen: libhash $(OBJS)
	$(CC) $(CFLAGS) generator/PQCgenKAT_sign.c generator/rng.c $(OBJS) $(LIB_HASH) -lcrypto -o kat_gen

kat_check: libhash $(OBJS)
	$(CC) $(CFLAGS) generator/PQCgenKAT_check.c generator/rng.c $(OBJS) $(LIB_HASH) -lcrypto -o kat_check

bench: libhash $(OBJS)
	$(CC) $(CFLAGS) benchmark/bench.c benchmark/timing.c $(OBJS) $(LIB_HASH) -lm -o bench

clean:
	@cd $(LIB_HASH_DIR) && make clean
	@find . -name "*.o" -type f -delete
	@rm -f kat_gen kat_check bench
	@rm -rf $(BUILD_CTLIB)
