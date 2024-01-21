
cmake_minimum_required(VERSION 3.5)
project(MAYO VERSION 1.0 LANGUAGES C CXX ASM)

set(MAYO_SO_VERSION "0")
set(CMAKE_C_STANDARD 99)

option(ENABLE_STRICT "Build with strict compile options." ON)

if(ENABLE_STRICT)
   message("Enable strict flag ON")
endif()
set(BASE_DIR  ../../..)


SET(MVARIANT "mayo_1")

include(${BASE_DIR}/.cmake/flags.cmake)
include(${BASE_DIR}/.cmake/sanitizers.cmake)
include(${BASE_DIR}/.cmake/target.cmake)

set(SOURCE_FILES_COMMON_SYS 
    ${BASE_DIR}/src/common/randombytes_system.c 
    ${BASE_DIR}/src/common/aes_c.c 
    ${BASE_DIR}/src/common/aes128ctr.c 
    ${BASE_DIR}/src/common/fips202.c 
    ${BASE_DIR}/src/common/mem.c
)

add_library(mayo_common_sys ${SOURCE_FILES_COMMON_SYS})
target_include_directories(mayo_common_sys PRIVATE ${BASE_DIR}/src/common ${BASE_DIR}/include)
target_compile_options(mayo_common_sys PUBLIC ${C_OPT_FLAGS})


if (ENABLE_AESNI)
    message("AES-NI enabled")
    target_compile_definitions(mayo_common_sys PUBLIC ENABLE_AESNI)
endif()

set(SOURCE_FILES_MAYO 
    ${BASE_DIR}/src/mayo.c 
    ${BASE_DIR}/src/params.c 
    ${BASE_DIR}/src/bitsliced_arithmetic.c
)

set(HEADER_FILES_MAYO
    ${BASE_DIR}/src/bitsliced_arithmetic.h
)


if (${MAYO_BUILD_TYPE} MATCHES "avx2")
    set(INC_PLATFORM ${PROJECT_SOURCE_DIR}/src/AVX2)
    add_definitions(-DMAYO_AVX)
else()
    set(INC_PLATFORM ${BASE_DIR}/src/generic)
    # set(INC_PLATFORM ${PROJECT_SOURCE_DIR}/src/generic)
endif()

find_library(CTGRIND_LIB ctgrind)
if(NOT CTGRIND_LIB)
	message("ctgrind library not found")
endif()

find_library(M_LIB m)
if(NOT M_LIB)
	message("m library not found")
endif()

set(BUILD build)
set(BUILD_KEYPAIR mayo_keypair)
set(BUILD_SIGN mayo_sign)


if (ENABLE_PARAMS_DYNAMIC)
    # mayo and libraries
    add_library(mayo ${SOURCE_FILES_MAYO})
    target_link_libraries(mayo PUBLIC mayo_common_sys)
    target_include_directories(mayo PUBLIC ${BASE_DIR}/include PRIVATE {BASE_DIR}/common ${INC_PLATFORM})
    target_compile_definitions(mayo PUBLIC ENABLE_PARAMS_DYNAMIC)


    # mayo_<x>_nistapi libraries
    set(SOURCE_FILES_VARIANT ${BASE_DIR}/src/${MVARIANT}/api.c)
    add_library(${MVARIANT}_nistapi ${SOURCE_FILES_VARIANT})
    target_link_libraries(${MVARIANT}_nistapi PRIVATE mayo)
    target_include_directories(${MVARIANT}_nistapi PUBLIC ${MVARIANT} ${INC_PLATFORM})

    # crypto_sign_keypair
    set(TARGET_KEYPAIR_BINARY_NAME taint_crypto_sign_keypair_${MVARIANT})
    add_executable(${TARGET_KEYPAIR_BINARY_NAME} mayo_keypair/taint_crypto_sign_keypair.c)

    target_link_libraries(${TARGET_KEYPAIR_BINARY_NAME} PRIVATE ctgrind m  ${MVARIANT}_nistapi)

    # crypto_sign_keypair
    set(TARGET_SIGN_BINARY_NAME taint_crypto_sign_${MVARIANT})
    add_executable(${TARGET_SIGN_BINARY_NAME} mayo_sign/taint_crypto_sign.c)

    target_link_libraries(${TARGET_SIGN_BINARY_NAME} PRIVATE ctgrind m  ${MVARIANT}_nistapi)

else()
    add_library(${MVARIANT} ${SOURCE_FILES_MAYO} ${HEADER_FILES_MAYO})
    target_link_libraries(${MVARIANT} PUBLIC mayo_common_sys)
    target_include_directories(${MVARIANT} PUBLIC ${BASE_DIR}/include  PRIVATE ${BASE_DIR}/src/common ${BASE_DIR}/src ${INC_PLATFORM})
    string(TOUPPER ${MVARIANT} MVARIANT_UPPER)
    target_compile_definitions(${MVARIANT} PUBLIC MAYO_VARIANT=${MVARIANT_UPPER})


    set(SOURCE_FILES_VARIANT ${BASE_DIR}/src/${MVARIANT}/api.c ${BASE_DIR}/src/${MVARIANT}/api.h)
    add_library(${MVARIANT}_nistapi ${SOURCE_FILES_VARIANT})
    target_link_libraries(${MVARIANT}_nistapi PRIVATE ${MVARIANT})
    target_include_directories(${MVARIANT}_nistapi PUBLIC ${MVARIANT} PUBLIC ${BASE_DIR}/include ${BASE_DIR}/src/${MVARIANT})

    # crypto_sign_keypair
    set(TARGET_KEYPAIR_BINARY_NAME taint_crypto_sign_keypair_${MVARIANT})
    add_executable(${TARGET_KEYPAIR_BINARY_NAME} ./mayo_keypair/taint_crypto_sign_keypair.c)

    target_link_libraries(${TARGET_KEYPAIR_BINARY_NAME} PRIVATE ctgrind m  ${MVARIANT}_nistapi)
    set_target_properties(${TARGET_KEYPAIR_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${BUILD_KEYPAIR})

    # crypto_sign_keypair
    set(TARGET_SIGN_BINARY_NAME taint_crypto_sign_${MVARIANT})
    add_executable(${TARGET_SIGN_BINARY_NAME} mayo_sign/taint_crypto_sign.c)

    target_link_libraries(${TARGET_SIGN_BINARY_NAME} PRIVATE ctgrind m  ${MVARIANT}_nistapi)
    set_target_properties(${TARGET_SIGN_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${BUILD_SIGN})
endif()
