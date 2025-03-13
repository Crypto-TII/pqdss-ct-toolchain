cmake_minimum_required(VERSION 3.10)
project(aq_vole_impl)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Default build type: Release" FORCE)
endif()

# the main library is in C and low-level crypto contain assembly files
#set(CMAKE_C_FLAGS_DEBUG "-O0 -g3 -Wall -Werror")
set(CMAKE_C_FLAGS_DEBUG "-O0 -g3 -Wall")
#set(CMAKE_C_FLAGS_RELEASE "-O3 -g3 -Wall -Werror -DNDEBUG")
set(CMAKE_C_FLAGS_RELEASE "-O3 -g3 -Wall -DNDEBUG")
enable_language(ASM)

set(BUILD_TESTING ON CACHE BOOL "Build Tests")
set(BUILD_KATS ON CACHE BOOL "Build KATs")
set(USE_REFERENCE_CODE_ONLY OFF CACHE BOOL "Build ONLY the reference code (not constant time, C only)")

# detect architecture
if (CMAKE_SYSTEM_PROCESSOR MATCHES "(x86)|(X86_LINUX)|(amd64)|(AMD64)")
    set(X86_LINUX ON)
    set(AARCH64 OFF)
else ()
    set(X86_LINUX OFF)
endif ()
if (CMAKE_SYSTEM_PROCESSOR MATCHES "(aarch64)|(arm64)")
    set(AARCH64 ON)
endif ()

if (CMAKE_SYSTEM_NAME MATCHES "(Windows)|(MSYS)")
    set(WIN32 ON)
endif ()
if (WIN32)
    #overrides for win32
    set(X86_LINUX OFF)
    set(AARCH64 OFF)
    set(X86_WIN32 ON)
else()
    set(X86_WIN32 OFF)
    set(WIN32 OFF)
endif (WIN32)

message(STATUS "--> WIN32: ${WIN32}")
message(STATUS "--> X86_WIN32: ${X86_WIN32}")
message(STATUS "--> X86_LINUX: ${X86_LINUX}")
message(STATUS "--> AARCH64: ${AARCH64}")

message(STATUS "BUILD_TESTING: ${BUILD_TESTING}")
message(STATUS "BUILD_KATS: ${BUILD_KATS}")
message(STATUS "USE_REFERENCE_CODE_ONLY: ${USE_REFERENCE_CODE_ONLY}")

add_subdirectory(lib/sha3)
add_subdirectory(lib/aes)

if (BUILD_KATS)
    set(kats_incs ${CMAKE_SOURCE_DIR}/src)
    set(kats_libs)
    # searching for libcrypto (for KATs only)
    find_path(crypto_inc NAMES openssl/conf.h)
    find_library(crypto NAMES crypto)
    if (crypto_inc AND crypto)
        message(STATUS "Found libcrypto: I=${crypto_inc} L=${crypto}")
        set(kats_incs ${kats_incs} ${crypto_inc})
        set(kats_libs ${kats_libs} ${crypto})
    else ()
        message(FATAL_ERROR "Libcrypto not found (required for NIST's KATs): I=${crypto_inc} L=${crypto}")
    endif ()
endif (BUILD_KATS)


set(VOLE_SRCS
        src/commons.c
        src/vole_private.h
        src/sdith_prng.h
        src/sdith_prng.c
        src/gf256.c
        src/gf192.c
        src/matrix_vector_products_f2.c
        src/matrix_transpose_f2.c
        src/ggm.c
        src/ggm.h
        src/vole_expansion.c
        src/piop_circuit.c
        src/gf128.c
        src/rsd.c
        src/sdith_prng_private.h
        src/commons.h
        src/sdith_signature.c
        src/sdith_signature_parameters.c
        src/vole_to_piop.c
        src/vole_parameters.cpp
        src/sdith_arithmetic.h
        src/sdith_algebra.h
        src/sdith_vole_to_piop.h
        src/sdith_rsd.h
        src/sdith_piop_circuits.h
        src/vole_parameters.h
        src/vole_generation.h
        src/sdith_signature.h
)
set(VOLE_SRCS_AVX2
        src/gf128_avx2.c
        src/gf192_avx2.c
        src/gf256_avx2.c
        src/matrix_vector_products_f2_avx2.c
        src/sdith_prng_avx2.c
        src/vole_parameters_avx2.cpp
)
set_source_files_properties(${VOLE_SRCS_AVX2} PROPERTIES COMPILE_OPTIONS "-mpclmul;-msse2;-mavx2")

if (X86_LINUX)
    # On X86_LINUX targets, the optional AVX2 parts are compiled
    add_library(vole STATIC ${VOLE_SRCS} ${VOLE_SRCS_AVX2})
else ()
    # On other targets, only the optional AVX2 parts are compiled
    add_library(vole STATIC ${VOLE_SRCS})
endif ()
target_link_libraries(vole sha3 aes m)


if (BUILD_TESTING)
add_executable(bench_sdith test/bench_sdith.c)
target_link_libraries(bench_sdith vole)
target_compile_definitions(bench_sdith PRIVATE CAT5A)
target_include_directories(bench_sdith PRIVATE ${test_incs} src)

enable_testing()
add_test(bench_sdith bench_sdith)
endif (BUILD_TESTING)

if (BUILD_KATS)
add_subdirectory(generator)
endif (BUILD_KATS)


# Constant-time tests - Benchmarks
set(INSTANCE sdith_cat5_short)
# == Constant-time tests
option(RUN_CT_TESTS "Run constant time tests" OFF)
set(TOOLS_FLAGS "-Wall -g -Wextra")
set(TOOLS_CFLAGS ${TOOLS_FLAGS})
set(TOOL_NAME "timecop")
set(TOOL_TEMPLATE_PATTERN "taint")
set(TOOL_LINK_LIBS "")
set(TOOL_FOLDER ../../${TOOL_NAME})


set(BUILD_KEYPAIR ${TOOL_FOLDER}/${INSTANCE}/sdith_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/${INSTANCE}/sdith_sign)


if (${TOOL_NAME} MATCHES "dudect")
    set(TOOLS_CFLAGS "")
endif()

set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} ${TOOLS_CFLAGS}")


# == Benchmarks
option(RUN_BENCHMARKS "Run custom benchmarks" OFF)
set(BENCHMARK_TESTS "benchmarks")
set(BENCHMARKS_FOLDER ../../${BENCHMARK_TESTS}/${INSTANCE})
set(SRC_BENCHMARK ${BENCHMARKS_FOLDER}/bench)
# Constant-time - benchmarks tests


if (RUN_CT_TESTS)
    #Test harness for crypto_sign_keypair
    set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair)
    add_executable(${TARGET_BINARY_NAME}
            ${TOOL_FOLDER}/${INSTANCE}/sdith_keypair/${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair.c
            ${CMAKE_SOURCE_DIR}/generator/rng.c ${CMAKE_SOURCE_DIR}/generator/rng.h ${CMAKE_SOURCE_DIR}/generator/sign.c)
    target_link_libraries(${TARGET_BINARY_NAME} vole ${kats_libs})
    target_include_directories(${TARGET_BINARY_NAME} PRIVATE ${kats_incs} ${CMAKE_SOURCE_DIR}/generator)
    set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_KEYPAIR})

    #Test harness for crypto_sign
    set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign)
    add_executable(${TARGET_BINARY_NAME} ${TOOL_FOLDER}/${INSTANCE}/sdith_sign/${TOOL_TEMPLATE_PATTERN}_crypto_sign.c
            ${CMAKE_SOURCE_DIR}/generator/rng.c ${CMAKE_SOURCE_DIR}/generator/rng.h ${CMAKE_SOURCE_DIR}/generator/sign.c)
    target_link_libraries(${TARGET_BINARY_NAME} vole ${kats_libs})
    target_include_directories(${TARGET_BINARY_NAME} PRIVATE ${kats_incs} ${CMAKE_SOURCE_DIR}/generator)
    set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_SIGN})
endif (RUN_CT_TESTS)

if (RUN_BENCHMARKS)
    set(TEST_BENCH bench)
    add_executable(${TEST_BENCH} ${SRC_BENCHMARK}.c ${CMAKE_SOURCE_DIR}/generator/rng.c
            ${CMAKE_SOURCE_DIR}/generator/rng.h ${CMAKE_SOURCE_DIR}/generator/sign.c)
    target_link_libraries(${TEST_BENCH} vole)
    target_compile_definitions(${TEST_BENCH} PRIVATE CAT1B)
    target_include_directories(${TEST_BENCH} PRIVATE ${kats_incs} ${CMAKE_SOURCE_DIR}/generator)
    set_target_properties(${TEST_BENCH} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BENCHMARKS_FOLDER})
endif (RUN_BENCHMARKS)