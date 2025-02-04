set(SOURCE_FILES_COMMON_SYS common/randombytes_system.c common/aes_c.c common/aes128ctr.c common/fips202.c common/mem.c)

add_library(mayo_common_sys ${SOURCE_FILES_COMMON_SYS})
target_include_directories(mayo_common_sys PRIVATE common ../include)
target_compile_options(mayo_common_sys PUBLIC ${C_OPT_FLAGS})

set(SOURCE_FILES_COMMON_TEST common/randombytes_ctrdrbg.c common/aes_c.c common/aes128ctr.c common/fips202.c common/mem.c)

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

set(SOURCE_FILES_MAYO mayo.c params.c bitsliced_arithmetic.c)

if (${MAYO_BUILD_TYPE} MATCHES "avx2")
    set(INC_PLATFORM ${PROJECT_SOURCE_DIR}/src/AVX2)
    add_definitions(-DMAYO_AVX)
else()
    set(INC_PLATFORM ${PROJECT_SOURCE_DIR}/src/generic)
endif()


# Constant-time - benchmarks tests
# == Constant-time tests
option(RUN_CT_TESTS "Run constant time tests" OFF)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${TOOLS_FLAGS}")
set(TOOL_FOLDER ../${TOOL_NAME})
set(TOOL_TEMPLATE_PATTERN "test_harness")
set(BUILD_KEYPAIR ${TOOL_FOLDER}/sqisign_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/sqisign_sign)
# == Benchmarks
option(RUN_BENCHMARKS "Run custom benchmarks" OFF)
set(BENCHMARK_TESTS "benchmarks")
set(BENCHMARKS_FOLDER ../${BENCHMARK_TESTS})
set(SRC_BENCHMARK ${BENCHMARKS_FOLDER}/bench)
set(TOOL_TEMPLATE_PATTERN ${BENCHMARKS_FOLDER}/bench)
# Constant-time - benchmarks tests

set(BUILD_KEYPAIR ${TOOL_FOLDER}/mayo_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/mayo_sign)

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

    # mayo_<x>_nistapi libraries
    foreach(MVARIANT ${MVARIANT_S})
        string(TOLOWER ${MVARIANT} MVARIANT_LOWER)
        set(SOURCE_FILES_VARIANT ${MVARIANT_LOWER}/api.c)
        add_library(${MVARIANT_LOWER}_nistapi ${SOURCE_FILES_VARIANT})
        target_link_libraries(${MVARIANT_LOWER}_nistapi PRIVATE mayo)
        target_include_directories(${MVARIANT_LOWER}_nistapi PUBLIC ${MVARIANT_LOWER} ${INC_PLATFORM})
        add_library(${MVARIANT_LOWER}_test_nistapi ${SOURCE_FILES_VARIANT})
        target_link_libraries(${MVARIANT_LOWER}_test_nistapi PRIVATE mayo_test)
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
endif()
