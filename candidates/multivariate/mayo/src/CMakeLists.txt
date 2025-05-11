# SPDX-License-Identifier: Apache-2.0

set(SOURCE_FILES_COMMON_SYS common/randombytes_system.c common/aes_c.c common/aes128ctr.c common/aes_neon.c common/fips202.c common/mem.c)

add_library(mayo_common_sys ${SOURCE_FILES_COMMON_SYS})
target_include_directories(mayo_common_sys PRIVATE common ../include)
target_compile_options(mayo_common_sys PUBLIC ${C_OPT_FLAGS})

set(SOURCE_FILES_COMMON_TEST common/randombytes_ctrdrbg.c common/aes_c.c common/aes128ctr.c common/aes_neon.c common/fips202.c common/mem.c)

add_library(mayo_common_test ${SOURCE_FILES_COMMON_TEST})
target_include_directories(mayo_common_test PRIVATE common ../include)
target_compile_options(mayo_common_test PUBLIC ${C_OPT_FLAGS})

if (ENABLE_CT_TESTING)
    target_compile_definitions(mayo_common_sys PUBLIC ENABLE_CT_TESTING)
    target_compile_definitions(mayo_common_test PUBLIC ENABLE_CT_TESTING)
endif()

if (ENABLE_AESNI)
    message("AES-NI enabled")
    target_compile_definitions(mayo_common_sys PUBLIC ENABLE_AESNI)
    target_compile_definitions(mayo_common_test PUBLIC ENABLE_AESNI)
endif()

if (ENABLE_AESNEON)
    message("AES-NEON enabled")
    target_compile_definitions(mayo_common_sys PUBLIC ENABLE_AESNEON)
    target_compile_definitions(mayo_common_test PUBLIC ENABLE_AESNEON)
endif()

set(SOURCE_FILES_MAYO mayo.c params.c arithmetic.c)

if (${MAYO_BUILD_TYPE} MATCHES "avx2")
    message("Building for avx2")
    set(INC_PLATFORM ${PROJECT_SOURCE_DIR}/src/AVX2 ${PROJECT_SOURCE_DIR}/src/generic)
    add_definitions(-DMAYO_AVX)
elseif (${MAYO_BUILD_TYPE} MATCHES "neon")
    message("Building for neon")
    set(INC_PLATFORM ${PROJECT_SOURCE_DIR}/src/neon ${PROJECT_SOURCE_DIR}/src/generic)
    add_definitions(-DMAYO_NEON)
else()
    set(INC_PLATFORM ${PROJECT_SOURCE_DIR}/src/generic)
endif()


# Constant-time - benchmarks tests
set(TOOLS_FLAGS "-std=c11")
set(TOOL_NAME "dudect")
set(TOOL_TEMPLATE_PATTERN "dude")
set(TOOL_LINK_LIBS "-lm")
set(TOOL_FOLDER ../${TOOL_NAME})

# == Constant-time tests
option(RUN_CT_TESTS "Run constant time tests" OFF)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${TOOLS_FLAGS}")
#set(TOOL_FOLDER ../${TOOL_NAME})
message("=======TOOL_FOLDER: ${TOOL_FOLDER}")
set(TOOL_TEMPLATE_PATTERN "dude")
set(TEST_HARNESS_KEYPAIR mayo_keypair/${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair.c)
set(TEST_HARNESS_SIGN mayo_sign/${TOOL_TEMPLATE_PATTERN}_crypto_sign.c)

set(BUILD_KEYPAIR ${TOOL_FOLDER}/mayo_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/mayo_sign)
# == Benchmarks
option(RUN_BENCHMARKS "Run custom benchmarks" OFF)
set(BENCHMARK_TESTS "benchmarks")
set(BENCHMARKS_FOLDER ../${BENCHMARK_TESTS})
set(SRC_BENCHMARK ${BENCHMARKS_FOLDER}/bench)
#set(TOOL_TEMPLATE_PATTERN "dude")
# Constant-time - benchmarks tests

set(BUILD_KEYPAIR ${TOOL_FOLDER}/mayo_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/mayo_sign)

option(EXPANDED_KEYS "Get expanded keys" ON)
set(EXPANDED_KEYS_FOLDER "expanded_keys")
set(EXPANDED_KEYS_DIR "${EXPANDED_KEYS_FOLDER}/mayo_1")

if (ENABLE_PARAMS_DYNAMIC)
    # mayo and mayo_test libraries
    add_library(mayo ${SOURCE_FILES_MAYO})
    target_link_libraries(mayo PUBLIC mayo_common_sys)
    target_include_directories(mayo PUBLIC ../include . PRIVATE common ${INC_PLATFORM})
    add_library(mayo_test ${SOURCE_FILES_MAYO})
    target_link_libraries(mayo_test PUBLIC mayo_common_test)
    target_include_directories(mayo_test PUBLIC ../include . PRIVATE common ${INC_PLATFORM})

    target_compile_definitions(mayo PUBLIC ENABLE_PARAMS_DYNAMIC)
    target_compile_definitions(mayo_test PUBLIC ENABLE_PARAMS_DYNAMIC)


    if (EXPANDED_KEYS)
        message(":::::::::::: Get expanded keys =========")
#        set(EXPANDED_KEY_NAME ../expanded_keys/mayo_1/get_expanded_secret_key_${MVARIANT_LOWER})
        set(EXPANDED_KEY_NAME ../expanded_keys/mayo_1/get_expanded_secret_key_mayo_1)
        add_executable(${EXPANDED_KEY_NAME}  ../expanded_keys/mayo_1/get_expanded_secret_key.c)
#        target_link_libraries(${EXPANDED_KEY_NAME} ${MVARIANT_LOWER}_nistapi)
        target_link_libraries(${EXPANDED_KEY_NAME} mayo_1)
#        target_include_directories(${EXPANDED_KEY_NAME} PRIVATE ../include ../src/${MVARIANT_LOWER})
        target_include_directories(${EXPANDED_KEY_NAME} PRIVATE ../include ../src/mayo_1)
        set_target_properties(${EXPANDED_KEY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../expanded_keys/mayo_1)
    endif (EXPANDED_KEYS)

    # mayo_<x>_nistapi libraries
    foreach(MVARIANT ${MVARIANT_S})
        string(TOLOWER ${MVARIANT} MVARIANT_LOWER)
        set(SOURCE_FILES_VARIANT ${MVARIANT_LOWER}/api.c)
        add_library(${MVARIANT_LOWER}_nistapi ${SOURCE_FILES_VARIANT})
        target_link_libraries(${MVARIANT_LOWER}_nistapi PRIVATE mayo)
        target_compile_definitions(${MVARIANT_LOWER}_nistapi PUBLIC ENABLE_PARAMS_DYNAMIC)
        target_include_directories(${MVARIANT_LOWER}_nistapi PUBLIC ${MVARIANT_LOWER} ${INC_PLATFORM})
        add_library(${MVARIANT_LOWER}_test_nistapi ${SOURCE_FILES_VARIANT})
        target_link_libraries(${MVARIANT_LOWER}_test_nistapi PRIVATE mayo_test)
        target_compile_definitions(${MVARIANT_LOWER}_test_nistapi PUBLIC ENABLE_PARAMS_DYNAMIC)
        target_include_directories(${MVARIANT_LOWER}_test_nistapi PUBLIC ${MVARIANT_LOWER} ${INC_PLATFORM})

        # Constant-time and benchmarks
        # === Constant-time tests
        if (RUN_CT_TESTS)
            #Test harness for crypto_sign_keypair
            set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair_${MVARIANT_LOWER})

            add_executable(${TARGET_BINARY_NAME}  ${TOOL_FOLDER}/mayo_keypair/${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair.c)
            target_link_libraries(${TARGET_BINARY_NAME} ${MVARIANT_LOWER}_nistapi ${M_LIB} ${TOOL_LINK_LIBS})
            target_include_directories(${TARGET_BINARY_NAME} PRIVATE ../include ../src/${MVARIANT_LOWER})
            set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_KEYPAIR})
            #Test harness for crypto_sign
            set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_${MVARIANT_LOWER})
            add_executable(${TARGET_BINARY_NAME}  ${TOOL_FOLDER}/mayo_sign/${TOOL_TEMPLATE_PATTERN}_crypto_sign.c)
            target_include_directories(${TARGET_BINARY_NAME} PRIVATE ../include ../src/${MVARIANT_LOWER})
            target_link_libraries(${TARGET_BINARY_NAME}  ${MVARIANT_LOWER}_nistapi ${M_LIB} ${TOOL_LINK_LIBS})
            set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_SIGN})
        endif (RUN_CT_TESTS)
        # === Benchmark tests
        if (RUN_BENCHMARKS)
            set(TEST_BENCH bench_${MVARIANT_LOWER})
            #            add_executable(${TEST_BENCH} ${SRC_BENCHMARK}.c)
            add_executable(${TEST_BENCH} ../${BENCHMARK_TESTS}/src/${MVARIANT_LOWER}/bench.c)
            target_link_libraries(${TEST_BENCH} PRIVATE ${MVARIANT_LOWER}_nistapi m cpucycles)
            #            set_target_properties(${TEST_BENCH} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BENCHMARKS_FOLDER})
            set_target_properties(${TEST_BENCH} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../../${BENCHMARK_TESTS}/src/${MVARIANT_LOWER})
        endif (RUN_BENCHMARKS)
    endforeach()

else()
    FOREACH(MVARIANT ${MVARIANT_S})
        string(TOLOWER ${MVARIANT} MVARIANT_LOWER)
        add_library(${MVARIANT_LOWER} ${SOURCE_FILES_MAYO})
        target_link_libraries(${MVARIANT_LOWER} PUBLIC mayo_common_sys)
        target_include_directories(${MVARIANT_LOWER} PUBLIC ../include . PRIVATE common ${INC_PLATFORM})
        add_library(${MVARIANT_LOWER}_test ${SOURCE_FILES_MAYO})
        target_link_libraries(${MVARIANT_LOWER}_test PUBLIC mayo_common_test)
        target_include_directories(${MVARIANT_LOWER}_test PUBLIC ../include . PRIVATE common ${INC_PLATFORM})
        target_compile_definitions(${MVARIANT_LOWER} PUBLIC MAYO_VARIANT=${MVARIANT})
        target_compile_definitions(${MVARIANT_LOWER}_test PUBLIC MAYO_VARIANT=${MVARIANT})
    ENDFOREACH()

    foreach(MVARIANT ${MVARIANT_S})
        string(TOLOWER ${MVARIANT} MVARIANT_LOWER)
        set(SOURCE_FILES_VARIANT ${MVARIANT_LOWER}/api.c)
        add_library(${MVARIANT_LOWER}_nistapi ${SOURCE_FILES_VARIANT})
        target_link_libraries(${MVARIANT_LOWER}_nistapi PRIVATE ${MVARIANT_LOWER})
        target_include_directories(${MVARIANT_LOWER}_nistapi PUBLIC ${MVARIANT_LOWER} PUBLIC ../include ${INC_PLATFORM})
        add_library(${MVARIANT_LOWER}_test_nistapi ${SOURCE_FILES_VARIANT})
        target_link_libraries(${MVARIANT_LOWER}_test_nistapi PRIVATE ${MVARIANT_LOWER}_test)
        target_include_directories(${MVARIANT_LOWER}_test_nistapi PUBLIC ${MVARIANT_LOWER} ${INC_PLATFORM})
        target_compile_definitions(${MVARIANT_LOWER}_nistapi PUBLIC MAYO_VARIANT=${MVARIANT})
        target_compile_definitions(${MVARIANT_LOWER}_test_nistapi PUBLIC MAYO_VARIANT=${MVARIANT})

        # Constant-time and benchmarks
        # === Constant-time tests
        if (RUN_CT_TESTS)
            #Test harness for crypto_sign_keypair
            set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair_${MVARIANT_LOWER})
            message("=======TARGET_BINARY_NAME: ${TARGET_BINARY_NAME}")
            message("=======TARGET_BINARY_NAME: ${TARGET_BINARY_NAME}")
#            add_executable(${TARGET_BINARY_NAME}  ${TOOL_FOLDER}/mayo_keypair/${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair.c)
            add_executable(${TARGET_BINARY_NAME}  ${TOOL_FOLDER}/src/${MVARIANT_LOWER}/${TEST_HARNESS_KEYPAIR})
            target_link_libraries(${TARGET_BINARY_NAME} ${MVARIANT_LOWER}_nistapi ${M_LIB} ${TOOL_LINK_LIBS})
            target_include_directories(${TARGET_BINARY_NAME} PRIVATE ../include ../src/${MVARIANT_LOWER})
#            set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_KEYPAIR})
            set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${TOOL_FOLDER}/src/${MVARIANT_LOWER}/mayo_keypair)
            #Test harness for crypto_sign
            set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_${MVARIANT_LOWER})
#            add_executable(${TARGET_BINARY_NAME}  ${TOOL_FOLDER}/mayo_sign/${TOOL_TEMPLATE_PATTERN}_crypto_sign.c)
            add_executable(${TARGET_BINARY_NAME}  ${TOOL_FOLDER}/src/${MVARIANT_LOWER}/${TEST_HARNESS_SIGN})
            target_include_directories(${TARGET_BINARY_NAME} PRIVATE ../include ../src/${MVARIANT_LOWER})
            target_link_libraries(${TARGET_BINARY_NAME}  ${MVARIANT_LOWER}_nistapi ${M_LIB} ${TOOL_LINK_LIBS})
#            set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_SIGN})
            set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${TOOL_FOLDER}/src/${MVARIANT_LOWER}/mayo_sign)
        endif (RUN_CT_TESTS)
        # === Benchmark tests
        if (RUN_BENCHMARKS)
            set(TEST_BENCH bench_${MVARIANT_LOWER})
            #            add_executable(${TEST_BENCH} ${SRC_BENCHMARK}.c)
            add_executable(${TEST_BENCH} ../${BENCHMARK_TESTS}/src/${MVARIANT_LOWER}/bench.c)
            target_link_libraries(${TEST_BENCH} PRIVATE ${MVARIANT_LOWER}_nistapi m cpucycles)
            #            set_target_properties(${TEST_BENCH} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BENCHMARKS_FOLDER})
            set_target_properties(${TEST_BENCH} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../../${BENCHMARK_TESTS}/src/${MVARIANT_LOWER})
        endif (RUN_BENCHMARKS)

        if (EXPANDED_KEYS)
            set(EXPANDED_KEY_NAME get_expanded_secret_key_${MVARIANT_LOWER})
            add_executable(${EXPANDED_KEY_NAME}  ../expanded_keys/${MVARIANT_LOWER}/get_expanded_secret_key.c)
            target_link_libraries(${EXPANDED_KEY_NAME} ${MVARIANT_LOWER}_nistapi)
            target_include_directories(${EXPANDED_KEY_NAME} PRIVATE ../include ../src/${MVARIANT_LOWER})
            set_target_properties(${EXPANDED_KEY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./../${EXPANDED_KEYS_FOLDER}/${MVARIANT_LOWER})
        endif (EXPANDED_KEYS)

    endforeach()
#    if (EXPANDED_KEYS)
#        set(EXPANDED_KEY_NAME get_expanded_secret_key_mayo_1)
#        add_executable(${EXPANDED_KEY_NAME}  ../expanded_keys/mayo_1/get_expanded_secret_key.c)
##        target_link_libraries(${EXPANDED_KEY_NAME} mayo_1)
#        target_link_libraries(${EXPANDED_KEY_NAME} mayo_1_nistapi)
#        target_include_directories(${EXPANDED_KEY_NAME} PRIVATE ../include ../src/mayo_1)
#        set_target_properties(${EXPANDED_KEY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./../${EXPANDED_KEYS_DIR})
#    endif (EXPANDED_KEYS)
endif()

