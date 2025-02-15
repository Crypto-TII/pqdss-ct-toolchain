cmake_minimum_required(VERSION 3.0.0)
project(LESS)
enable_language(C ASM)
set(CMAKE_C_STANDARD 99)
set(CMAKE_VERBOSE_MAKEFILE OFF)

find_package(OpenSSL)

# needed for nvim
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "")
if(CMAKE_EXPORT_COMPILE_COMMANDS)
    set(CMAKE_CXX_STANDARD_INCLUDE_DIRECTORIES
            ${CMAKE_CXX_IMPLICIT_INCLUDE_DIRECTORIES})
endif()

# Set a default build type if none was specified
set(default_build_type "Release")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
    set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE STRING "Choose the type of build." FORCE)
    # Set the possible values of build type for cmake-gui
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

option(USE_SANITIZE "enable compiler memory sanitation" OFF)

# default compilation picks reference codebase
option(USE_REFERENCE "Use reference implementation" OFF)

# use AVX2 implementations.
option(USE_AVX2 "Use the AVX2 Optimized Implementation." ON)
option(USE_NEON "Use the NEON Optimized Implementation." OFF)
# option(USE_M4 "Use the M4 Optimized Omplementation." OFF)

# default compilation picks reference codebase
if(USE_REFERENCE)
    message(STATUS "Using the Reference Implementation")
    set(BASE_DIR ../Reference_Implementation)
    set(USE_AVX2 OFF)
    set(USE_NEON OFF)
    # set(USE_M4 OFF)
elseif(USE_NEON)
    message(STATUS "Using the NEON Implementation")
    set(BASE_DIR ../Optimized_Implementation/neon)
    set(USE_AVX2 OFF)
    #  set(USE_M4 OFF)
    set(USE_REFERENCE OFF)
    #elseif(USE_M4)
    #  message(STATUS "Using the M4 Implementation")
    #  set(BASE_DIR ../../Optimized_Implementation/m4)
    #  set(USE_AVX2 OFF)
    #  set(USE_NEON OFF)
    #  set(USE_REFERENCE OFF)
elseif(USE_AVX2)
    message(STATUS "Using the AVX2 Implementation")
    set(BASE_DIR ../Optimized_Implementation/avx2)
    set(USE_NEON OFF)
    #  set(USE_M4 OFF)
    set(USE_REFERENCE OFF)
else()
    message( FATAL_ERROR "No implementation specified, aborting." )
endif()

include(CheckCCompilerFlag)
unset(COMPILER_SUPPORTS_MARCH_NATIVE CACHE)
check_c_compiler_flag(-march=native COMPILER_SUPPORTS_MARCH_NATIVE)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -flto -ftree-vectorize -funroll-loops -Wall -Wpedantic -pedantic ")

if(USE_SANITIZE)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address -fsanitize=pointer-compare ")
endif()

if(CMAKE_BUILD_TYPE MATCHES Release)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 ")
    if(COMPILER_SUPPORTS_MARCH_NATIVE)
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=native")
    endif()
    if(lto_supported)
        message(STATUS "IPO / LTO enabled")
        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
    endif()
elseif(CMAKE_BUILD_TYPE MATCHES MinSizeRel)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mtune=native -Os -g0")
    if(COMPILER_SUPPORTS_MARCH_NATIVE)
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=native")
    endif()
    if(lto_supported)
        message(STATUS "IPO / LTO enabled")
        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
    endif()
else() # Debug, RelWithDebInfo, etc
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address -fsanitize=pointer-compare")
    message(STATUS "Building in Debug mode!")
endif()

if(USE_AVX2)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DUSE_AVX2 -mavx -mavx2 -mbmi -mbmi2")
endif()

if(USE_NEON)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DUSE_NEON -flax-vector-conversions")
endif()

message(STATUS "Compilation flags:" ${CMAKE_C_FLAGS})




find_library(KECCAK_LIB keccak)
if(NOT KECCAK_LIB)
    set(STANDALONE_KECCAK 1)
endif()


set(HEADERS
        ${BASE_DIR}/include/api.h
        ${BASE_DIR}/include/codes.h
        ${BASE_DIR}/include/fips202.h
        ${BASE_DIR}/include/fq_arith.h
        ${BASE_DIR}/include/keccakf1600.h
        ${BASE_DIR}/include/LESS.h
        ${BASE_DIR}/include/monomial_mat.h
        ${BASE_DIR}/include/parameters.h
        ${BASE_DIR}/include/rng.h
        ${BASE_DIR}/include/seedtree.h
        ${BASE_DIR}/include/sha3.h
        ${BASE_DIR}/include/utils.h
)

if(STANDALONE_KECCAK)
    message(STATUS "Employing standalone SHA-3")
    set(KECCAK_EXTERNAL_LIB "")
    set(KECCAK_EXTERNAL_ENABLE "")
    list(APPEND COMMON_SOURCES ${BASE_DIR}/lib/fips202.c)
else()
    message(STATUS "Employing libkeccak")
    set(KECCAK_EXTERNAL_LIB keccak)
    set(KECCAK_EXTERNAL_ENABLE "-DSHA_3_LIBKECCAK")
endif()


set(SOURCES
        ${COMMON_SOURCES}
        ${BASE_DIR}/lib/codes.c
        ${BASE_DIR}/lib/LESS.c
        ${BASE_DIR}/lib/monomial.c
        ${BASE_DIR}/lib/canonical.c
        ${BASE_DIR}/lib/rng.c
        ${BASE_DIR}/lib/seedtree.c
        ${BASE_DIR}/lib/sign.c
        ${BASE_DIR}/lib/sort.c
        ${BASE_DIR}/lib/transpose.c
        ${BASE_DIR}/lib/keccakf1600.c
        ${BASE_DIR}/lib/utils.c
        ${BASE_DIR}/lib/sign.c
)

if(USE_AVX2)
    set(SOURCES ${SOURCES} ${BASE_DIR}/lib/KeccakP-1600-AVX2.s)
    set(SOURCES ${SOURCES} ${BASE_DIR}/lib/transpose_avx2.c)
    set(HEADERS ${HEADERS} ${BASE_DIR}/include/macro.h)
endif()

if(USE_NEON)
    set(SOURCES ${SOURCES} ${BASE_DIR}/lib/transpose_neon.c)
    set(HEADERS ${HEADERS} ${BASE_DIR}/include/macro.h)
endif()


# Constant-time tests - Benchmarks
# == Constant-time tests
option(RUN_CT_TESTS "Run constant time tests" OFF)
set(TOOLS_FLAGS "-Wall -g -Wextra")
set(TOOL_NAME "timecop")
set(TOOL_TEMPLATE_PATTERN "taint")
set(TOOL_LINK_LIBS "")
set(TOOL_FOLDER ../${TOOL_NAME})

set(BUILD_KEYPAIR ${TOOL_FOLDER}/less_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/less_sign)

# == Benchmarks
#option(RUN_BENCHMARKS "Run custom benchmarks" OFF)
option(RUN_BENCHMARKS "Run custom benchmarks" ON)
set(BENCHMARK_TESTS "benchmarks")
set(BENCHMARKS_FOLDER ../${BENCHMARK_TESTS})
set(SRC_BENCHMARK ${BENCHMARKS_FOLDER}/bench)
# Constant-time - benchmarks tests

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${TOOLS_FLAGS}")


include_directories(${BASE_DIR}/include)

foreach(category "252" "400" "548")
    if(${category} EQUAL "252")
        set(PARAM_TARGETS "192" "68" "45")
    elseif(${category} EQUAL "400")
        set(PARAM_TARGETS "220" "102")
    elseif(${category} EQUAL "548")
        set(PARAM_TARGETS "345" "137")
    endif()

    foreach(optimize_target ${PARAM_TARGETS})
        #Constant-time and benchmarks
        # === Constant-time tests
        if (RUN_CT_TESTS)
            set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair_${category}_${optimize_target})
            add_executable(${TARGET_BINARY_NAME} ${HEADERS} ${SOURCES}
                    ${TOOL_FOLDER}/less_keypair/${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair.c)
            target_include_directories(${TARGET_BINARY_NAME} PRIVATE
                    ${BASE_DIR}/include ${OPENSSL_INCLUDE_DIR}
                    ./include)
            target_link_libraries(${TARGET_BINARY_NAME}  ${CTGRIND_LIB} ${M_LIB} ${SANITIZE} ${KECCAK_EXTERNAL_LIB})
            set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_KEYPAIR})
            set_property(TARGET ${TARGET_BINARY_NAME} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY=${category} -DTARGET=${optimize_target} ${KECCAK_EXTERNAL_ENABLE} ")

            #Test harness for crypto_sign
            set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_${category}_${optimize_target})
            add_executable(${TARGET_BINARY_NAME} ${HEADERS} ${SOURCES}
                    ${TOOL_FOLDER}/less_sign/${TOOL_TEMPLATE_PATTERN}_crypto_sign.c)
            target_include_directories(${TARGET_BINARY_NAME} PRIVATE
                    ${BASE_DIR}/include ${OPENSSL_INCLUDE_DIR}
                    ./include)
            target_link_libraries(${TARGET_BINARY_NAME}  ${CTGRIND_LIB} ${M_LIB} ${SANITIZE} ${KECCAK_EXTERNAL_LIB})
            set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_SIGN})
            set_property(TARGET ${TARGET_BINARY_NAME} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY=${category} -DTARGET=${optimize_target} ${KECCAK_EXTERNAL_ENABLE} ")
        endif ()
        # === Benchmark tests
        if (RUN_BENCHMARKS)
            set(TEST_BENCH bench_${category}_${optimize_target})
            add_executable(${TEST_BENCH} ${HEADERS} ${SOURCES} ${SRC_BENCHMARK}.c)
            target_include_directories(${TEST_BENCH} PRIVATE  ${BASE_DIR}/include ${OPENSSL_INCLUDE_DIR})
            target_link_libraries(${TEST_BENCH}  ${SANITIZE} ${KECCAK_EXTERNAL_LIB} m cpucycles)
            set_target_properties(${TEST_BENCH} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BENCHMARKS_FOLDER})
            set_property(TARGET ${TEST_BENCH} APPEND PROPERTY
                    COMPILE_FLAGS "-DCATEGORY=${category} -DTARGET=${optimize_target} ${KECCAK_EXTERNAL_ENABLE} ")
        endif ()
    endforeach(optimize_target)
endforeach(category)
