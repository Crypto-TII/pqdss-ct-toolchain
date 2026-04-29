cmake_minimum_required(VERSION 3.0.0)
project(FAEST)
enable_language(C ASM)
set(CMAKE_C_STANDARD 99)
set(CMAKE_VERBOSE_MAKEFILE OFF)

find_package(OpenSSL REQUIRED)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "")

set(default_build_type "Release")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE STRING "Choose the type of build." FORCE)
endif()

option(USE_REFERENCE "Use reference implementation" ON)
option(USE_EM "Use EM variants" OFF)

if(USE_REFERENCE)
    message(STATUS "Using the Reference Implementation")
    set(BASE_DIR ../Reference_Implementation)
else()
    message(FATAL_ERROR "Only Reference Implementation is supported")
endif()

set(TOOLS_FLAGS "-std=c11")
set(TOOL_NAME "dudect")
set(TOOL_TEMPLATE_PATTERN "dude")
set(TOOL_LINK_LIBS "m")
set(INSTANCE "faest_128f" CACHE STRING "FAEST instance")

set(TOOL_FOLDER ../../timecop)
set(BUILD_KEYPAIR ${TOOL_FOLDER}/${INSTANCE}/faest_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/${INSTANCE}/faest_sign)

if(INSTANCE STREQUAL "faest_128f")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_128f)
    set(FAEST_SOURCE faest_128f.c)
    set(FAEST_HEADER faest_128f.h)
elseif(INSTANCE STREQUAL "faest_128s")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_128s)
    set(FAEST_SOURCE faest_128s.c)
    set(FAEST_HEADER faest_128s.h)
elseif(INSTANCE STREQUAL "faest_192f")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_192f)
    set(FAEST_SOURCE faest_192f.c)
    set(FAEST_HEADER faest_192f.h)
elseif(INSTANCE STREQUAL "faest_192s")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_192s)
    set(FAEST_SOURCE faest_192s.c)
    set(FAEST_HEADER faest_192s.h)
elseif(INSTANCE STREQUAL "faest_256f")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_256f)
    set(FAEST_SOURCE faest_256f.c)
    set(FAEST_HEADER faest_256f.h)
elseif(INSTANCE STREQUAL "faest_256s")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_256s)
    set(FAEST_SOURCE faest_256s.c)
    set(FAEST_HEADER faest_256s.h)
elseif(INSTANCE STREQUAL "faest_em_128f")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_em_128f)
    set(FAEST_SOURCE faest_em_128f.c)
    set(FAEST_HEADER faest_em_128f.h)
elseif(INSTANCE STREQUAL "faest_em_128s")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_em_128s)
    set(FAEST_SOURCE faest_em_128s.c)
    set(FAEST_HEADER faest_em_128s.h)
elseif(INSTANCE STREQUAL "faest_em_192f")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_em_192f)
    set(FAEST_SOURCE faest_em_192f.c)
    set(FAEST_HEADER faest_em_192f.h)
elseif(INSTANCE STREQUAL "faest_em_192s")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_em_192s)
    set(FAEST_SOURCE faest_em_192s.c)
    set(FAEST_HEADER faest_em_192s.h)
elseif(INSTANCE STREQUAL "faest_em_256f")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_em_256f)
    set(FAEST_SOURCE faest_em_256f.c)
    set(FAEST_HEADER faest_em_256f.h)
elseif(INSTANCE STREQUAL "faest_em_256s")
    set(FAEST_INSTANCE_DIR ${BASE_DIR}/faest_em_256s)
    set(FAEST_SOURCE faest_em_256s.c)
    set(FAEST_HEADER faest_em_256s.h)
else()
    message(FATAL_ERROR "Unknown instance: ${INSTANCE}")
endif()

set(FAEST_IMPL_DIR ${FAEST_INSTANCE_DIR})

set(HEADERS
    ${FAEST_IMPL_DIR}/api.h
    ${FAEST_IMPL_DIR}/compat.h
    ${FAEST_IMPL_DIR}/crypto_sign.h
    ${FAEST_IMPL_DIR}/faest.h
    ${FAEST_IMPL_DIR}/${FAEST_HEADER}
    ${FAEST_IMPL_DIR}/macros.h
)

set(SOURCES
    ${FAEST_IMPL_DIR}/aes.c
    ${FAEST_IMPL_DIR}/bavc.c
    ${FAEST_IMPL_DIR}/compat.c
    ${FAEST_IMPL_DIR}/crypto_sign.c
    ${FAEST_IMPL_DIR}/faest.c
    ${FAEST_IMPL_DIR}/${FAEST_SOURCE}
    ${FAEST_IMPL_DIR}/faest_aes.c
    ${FAEST_IMPL_DIR}/fields.c
    ${FAEST_IMPL_DIR}/instances.c
    ${FAEST_IMPL_DIR}/owf.c
    ${FAEST_IMPL_DIR}/random_oracle.c
    ${FAEST_IMPL_DIR}/randomness.c
    ${FAEST_IMPL_DIR}/universal_hashing.c
    ${FAEST_IMPL_DIR}/utils.c
    ${FAEST_IMPL_DIR}/vole.c
    ${FAEST_IMPL_DIR}/sha3/KeccakHash.c
    ${FAEST_IMPL_DIR}/sha3/KeccakHashtimes4.c
    ${FAEST_IMPL_DIR}/sha3/KeccakP-1600-opt64.c
    ${FAEST_IMPL_DIR}/sha3/KeccakP-1600-times4-on1.c
    ${FAEST_IMPL_DIR}/sha3/KeccakSponge.c
    ${FAEST_IMPL_DIR}/sha3/KeccakSpongetimes4.c
)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${TOOLS_FLAGS} -O3 -std=gnu11 -march=native")

include_directories(${FAEST_IMPL_DIR})
include_directories(${FAEST_IMPL_DIR}/sha3)
include_directories(${OPENSSL_INCLUDE_DIR})

add_library(cttest SHARED ${SOURCES} ${HEADERS})
target_link_libraries(cttest OpenSSL::Crypto)
