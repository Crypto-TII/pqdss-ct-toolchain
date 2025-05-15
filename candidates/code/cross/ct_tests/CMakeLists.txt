cmake_minimum_required(VERSION 3.7)

project(CROSS C)
set(CMAKE_C_STANDARD 11)

set(CC gcc)
# set(CC clang)
set(CMAKE_C_FLAGS  "${CMAKE_C_FLAGS} -Wall -pedantic -Wuninitialized -march=native -O3 -g3")
# set(SANITIZE "-fsanitize=address -g3")
set(CMAKE_C_FLAGS  "${CMAKE_C_FLAGS} ${SANITIZE}")
message("Compilation flags:" ${CMAKE_C_FLAGS})

# by default, employ optimized implementation
#set(REFERENCE 0)
option(REFERENCE 0)


find_library(KECCAK_LIB keccak)
if(NOT KECCAK_LIB)
    set(STANDALONE_KECCAK 1)
endif()


# selection of specialized compilation units differing between ref and opt
# implementations.
set(REFERENCE_CODE_DIR ../Reference_Implementation)
set(OPTIMIZED_CODE_DIR ../Optimized_Implementation)

if(REFERENCE EQUAL 1)
    message("Compiling portable reference code")
    set(BASE_DIR ${REFERENCE_CODE_DIR})
    set(SPEC_HEADERS
            ${BASE_DIR}/include/sha3.h
            ${BASE_DIR}/include/csprng_hash.h
            ${BASE_DIR}/include/restr_arith.h
            ${BASE_DIR}/include/fp_arith.h )
    set(SPEC_SOURCES
            ${BASE_DIR}/lib/merkle.c
            ${BASE_DIR}/lib/seedtree.c
            ${BASE_DIR}/lib/CROSS.c
    )
else()
    message("Compiling optimized AVX2 code")
    set(BASE_DIR ${OPTIMIZED_CODE_DIR})
    set(SPEC_HEADERS
            ${BASE_DIR}/include/align.h
            ${BASE_DIR}/include/fips202x4.h
            ${BASE_DIR}/include/KeccakP-1600-times4-SnP.h
            ${BASE_DIR}/include/SIMD256-config.h
            ${BASE_DIR}/include/sha3.h
            ${BASE_DIR}/include/csprng_hash.h
            ${BASE_DIR}/include/architecture_detect.h
            ${BASE_DIR}/include/restr_arith.h
            ${BASE_DIR}/include/fp_arith.h )
    set(SPEC_SOURCES
            ${BASE_DIR}/lib/fips202x4.c
            ${BASE_DIR}/lib/KeccakP-1600-times4-SIMD256.c
            ${BASE_DIR}/lib/merkle.c
            ${BASE_DIR}/lib/seedtree.c
            ${BASE_DIR}/lib/CROSS.c
    )
endif()

set(COMMON_DIR ${REFERENCE_CODE_DIR})
set(HEADERS
        ${SPEC_HEADERS}
        ${COMMON_DIR}/include/api.h
        ${COMMON_DIR}/include/CROSS.h
        ${COMMON_DIR}/include/pack_unpack.h
        ${COMMON_DIR}/include/fips202.h
        ${COMMON_DIR}/include/keccakf1600.h
        ${COMMON_DIR}/include/parameters.h
        ${COMMON_DIR}/include/seedtree.h
        ${COMMON_DIR}/include/merkle_tree.h
)

if(STANDALONE_KECCAK)
    message("Employing standalone SHA-3")
    set(KECCAK_EXTERNAL_LIB "")
    set(KECCAK_EXTERNAL_ENABLE "")
    list(APPEND FALLBACK_SOURCES ${COMMON_DIR}/lib/keccakf1600.c)
    list(APPEND FALLBACK_SOURCES ${COMMON_DIR}/lib/fips202.c)
else()
    message("Employing libkeccak")
    set(KECCAK_EXTERNAL_LIB keccak)
    set(KECCAK_EXTERNAL_ENABLE "-DSHA_3_LIBKECCAK")
endif()


set(SOURCES
        ${SPEC_SOURCES}
        ${FALLBACK_SOURCES}
        ${COMMON_DIR}/lib/csprng_hash.c
        ${COMMON_DIR}/lib/pack_unpack.c
        ${COMMON_DIR}/lib/keccakf1600.c
        ${COMMON_DIR}/lib/fips202.c
        ${COMMON_DIR}/lib/sign.c
)

# Constant-time tests - Benchmarks
# == Constant-time tests
option(RUN_CT_TESTS "Run constant time tests" OFF)
set(TOOLS_FLAGS "-std=c11")
set(TOOL_NAME "dudect")
set(TOOL_TEMPLATE_PATTERN "dude")
set(TOOL_LINK_LIBS "m")
set(TOOL_FOLDER ../${TOOL_NAME})

set(BUILD_KEYPAIR ${TOOL_FOLDER}/cross_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/cross_sign)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${TOOLS_FLAGS}")

# == Benchmarks
option(RUN_BENCHMARKS "Run custom benchmarks" OFF)
#option(RUN_BENCHMARKS "Run custom benchmarks" ON)
set(BENCHMARK_TESTS "benchmarks")
set(BENCHMARKS_FOLDER ../${BENCHMARK_TESTS})
set(SRC_BENCHMARK ${BENCHMARKS_FOLDER}/bench)
# Constant-time - benchmarks tests

# EXPANDED KEYS
option(EXPANDED_KEYS "Get expanded keys" OFF)
set(EXPANDED_KEYS_FOLDER "expanded_keys")


foreach(category RANGE 1 5 2)
    set(RSDP_VARIANTS RSDP RSDPG)
    foreach(RSDP_VARIANT ${RSDP_VARIANTS})
        set(PARAM_TARGETS SIG_SIZE BALANCED SPEED)
        foreach(optimiz_target ${PARAM_TARGETS})
            if(optimiz_target STREQUAL SPEED)
                set(OMIT_SEED_TREE "-DNO_TREES=1")
            else()
                set(OMIT_SEED_TREE "")
            endif()
            #Constant-time and benchmarks
            # === Constant-time tests
            if (RUN_CT_TESTS)
                set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair_${category}_${RSDP_VARIANT}_${optimiz_target})
                add_executable(${TARGET_BINARY_NAME} ${HEADERS} ${SOURCES}
                        ${TOOL_FOLDER}/cross_keypair/${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair.c)
                target_include_directories(${TARGET_BINARY_NAME} PRIVATE ${BASE_DIR}/include ${COMMON_DIR}/include)
                target_link_libraries(${TARGET_BINARY_NAME} ${SANITIZE} ${KECCAK_EXTERNAL_LIB} ${TOOL_LINK_LIBS})
                set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_KEYPAIR})
                set_property(TARGET ${TARGET_BINARY_NAME} APPEND PROPERTY
                        COMPILE_FLAGS "${OMIT_SEED_TREE} -DCATEGORY_${category}=1 -D${optimiz_target}=1 -D${RSDP_VARIANT}=1 ${KECCAK_EXTERNAL_ENABLE} ")
                #Test harness for crypto_sign

                set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_${category}_${RSDP_VARIANT}_${optimiz_target})
                add_executable(${TARGET_BINARY_NAME} ${HEADERS} ${SOURCES}
                        ${TOOL_FOLDER}/cross_sign/${TOOL_TEMPLATE_PATTERN}_crypto_sign.c)
                target_include_directories(${TARGET_BINARY_NAME} PRIVATE ${BASE_DIR}/include ${COMMON_DIR}/include)
                target_link_libraries(${TARGET_BINARY_NAME} ${SANITIZE} ${KECCAK_EXTERNAL_LIB} ${TOOL_LINK_LIBS})
                set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_SIGN})
                set_property(TARGET ${TARGET_BINARY_NAME} APPEND PROPERTY
                        COMPILE_FLAGS "${OMIT_SEED_TREE} -DCATEGORY_${category}=1 -D${optimiz_target}=1 -D${RSDP_VARIANT}=1 ${KECCAK_EXTERNAL_ENABLE} ")
            endif ()
            # CT TESTS

            if (EXPANDED_KEYS)
                set(TARGET_BINARY_NAME get_expanded_secret_key_${category}_${RSDP_VARIANT}_${optimiz_target})
                add_executable(${TARGET_BINARY_NAME} ${HEADERS} ${SOURCES}
                        ../${EXPANDED_KEYS_FOLDER}/get_expanded_secret_key.c)
                target_include_directories(${TARGET_BINARY_NAME} PRIVATE ${BASE_DIR}/include ${COMMON_DIR}/include)
                target_link_libraries(${TARGET_BINARY_NAME} ${SANITIZE} ${KECCAK_EXTERNAL_LIB})
                set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${EXPANDED_KEYS_FOLDER})
                set_property(TARGET ${TARGET_BINARY_NAME} APPEND PROPERTY
                        COMPILE_FLAGS "${OMIT_SEED_TREE} -DCATEGORY_${category}=1 -D${optimiz_target}=1 -D${RSDP_VARIANT}=1 ${KECCAK_EXTERNAL_ENABLE} ")

            endif (EXPANDED_KEYS)


            if (RUN_BENCHMARKS)
                set(TEST_BENCH bench_${category}_${RSDP_VARIANT}_${optimiz_target})
                add_executable(${TEST_BENCH} ${HEADERS} ${SOURCES} ${SRC_BENCHMARK}.c)
                target_include_directories(${TEST_BENCH} PRIVATE ${BASE_DIR}/include ${COMMON_DIR}/include)
                target_link_libraries(${TEST_BENCH} m ${SANITIZE} ${KECCAK_EXTERNAL_LIB} cpucycles)
                set_target_properties(${TEST_BENCH} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BENCHMARKS_FOLDER})
                set_property(TARGET ${TEST_BENCH} APPEND PROPERTY
                        COMPILE_FLAGS "${OMIT_SEED_TREE} -DCATEGORY_${category}=1 -D${optimiz_target}=1 -D${RSDP_VARIANT}=1 ${KECCAK_EXTERNAL_ENABLE} ")
            endif ()
        endforeach(optimiz_target)
    endforeach(RSDP_VARIANT)
endforeach(category)
