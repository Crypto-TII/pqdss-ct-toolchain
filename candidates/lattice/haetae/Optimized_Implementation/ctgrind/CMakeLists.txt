
cmake_minimum_required(VERSION 3.16)
project("" LANGUAGES ASM C CXX) # CXX for the google test

enable_testing() # Enables running `ctest`

set(BASE_DIR ..)

set(CMAKE_C_STANDARD 11)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/libs/)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/libs/)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/)
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin/)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(HAETAE_SRCS
  ${BASE_DIR}/src/consts.c
  ${BASE_DIR}/src/poly.c
  ${BASE_DIR}/src/ntt.S
  ${BASE_DIR}/src/invntt.S
  ${BASE_DIR}/src/pointwise.S
  ${BASE_DIR}/src/shuffle.S
  ${BASE_DIR}/src/fft.c
  ${BASE_DIR}/src/reduce.c
  ${BASE_DIR}/src/polyvec.c
  ${BASE_DIR}/src/polymat.c
  ${BASE_DIR}/src/polyfix.c
  ${BASE_DIR}/src/decompose.c
  ${BASE_DIR}/src/sampler.c
  ${BASE_DIR}/src/packing.c
  ${BASE_DIR}/src/sign.c
  ${BASE_DIR}/src/fixpoint.c
  ${BASE_DIR}/src/encoding.c
)

set(HAETAE_FIPS202_SRCS
  ${HAETAE_SRCS}
  ${BASE_DIR}/src/symmetric-shake.c
)
set(FIPS202_SRCS ${BASE_DIR}/src/fips202.c ${BASE_DIR}/src/fips202x4.c ${BASE_DIR}/src/f1600x4.S)

if(MSVC)
  set(C_FLAGS /nologo /O2 /W4 /wd4146 /wd4244)
else()
  set(C_FLAGS -O3 -fomit-frame-pointer -mavx2 -Wall -Wextra -Wpedantic)
endif()

find_package(OpenSSL REQUIRED)

include_directories(${BASE_DIR}/include)
include_directories(${BASE_DIR}/api)
link_directories(${BASE_DIR}/libs)

add_library(fips202 SHARED ${FIPS202_SRCS})
target_compile_options(fips202 PRIVATE -O3 -mavx2 -fomit-frame-pointer -fPIC)
add_library(RNG SHARED ${PROJECT_SOURCE_DIR}/${BASE_DIR}//src/randombytes.c)
target_compile_options(RNG PRIVATE -O3 -fomit-frame-pointer -fPIC)
target_link_libraries(RNG PUBLIC OpenSSL::Crypto)


# HAETAE 2 SHAKE ONLY
set(LIB_NAME2 ${PROJECT_NAME}2)
add_library(${LIB_NAME2} SHARED ${HAETAE_FIPS202_SRCS})
target_compile_definitions(${LIB_NAME2} PUBLIC HAETAE_MODE=2)
target_compile_options(${LIB_NAME2} PRIVATE ${C_FLAGS})
target_link_libraries(${LIB_NAME2} INTERFACE fips202 m)
target_link_libraries(${LIB_NAME2} PUBLIC RNG)

# HAETAE 3 SHAKE ONLY
set(LIB_NAME3 ${PROJECT_NAME}3)
add_library(${LIB_NAME3} SHARED ${HAETAE_FIPS202_SRCS})
target_compile_definitions(${LIB_NAME3} PUBLIC HAETAE_MODE=3)
target_compile_options(${LIB_NAME3} PRIVATE ${C_FLAGS})
target_link_libraries(${LIB_NAME3} INTERFACE fips202 m)
target_link_libraries(${LIB_NAME3} PUBLIC RNG)

# HAETAE 5 SHAKE ONLY
set(LIB_NAME5 ${PROJECT_NAME}5)
add_library(${LIB_NAME5} SHARED ${HAETAE_FIPS202_SRCS})
target_compile_definitions(${LIB_NAME5} PUBLIC HAETAE_MODE=5)
target_compile_options(${LIB_NAME5} PRIVATE ${C_FLAGS})
target_link_libraries(${LIB_NAME5} INTERFACE fips202 m)
target_link_libraries(${LIB_NAME5} PUBLIC RNG)


set(BUILD build)
set(BUILD_KEYPAIR haetae_keypair)
set(BUILD_SIGN haetae_sign)

find_library(CT_GRIND_LIB ctgrind)
foreach(category RANGE 2 3 5)
		set(TARGET_KEYPAIR_BINARY_NAME taint_${category})
		add_executable(${TARGET_KEYPAIR_BINARY_NAME} ./haetae_keypair/taint.c)
		target_link_libraries(${TARGET_KEYPAIR_BINARY_NAME}  ${LIB_NAME${category}} ${CT_GRIND_LIB} OpenSSL::Crypto)
		target_include_directories(${TARGET_KEYPAIR_BINARY_NAME} PUBLIC ../include)
		target_compile_definitions(${TARGET_KEYPAIR_BINARY_NAME} PUBLIC HAETAE_MODE=${category})
		set_target_properties(${TARGET_KEYPAIR_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${BUILD_KEYPAIR})

		set(TARGET_SIGN_BINARY_NAME taint_${category}_1)
		add_executable(${TARGET_SIGN_BINARY_NAME} ./haetae_sign/taint.c)
		target_include_directories(${TARGET_SIGN_BINARY_NAME} PUBLIC ../include)
		target_compile_definitions(${TARGET_SIGN_BINARY_NAME} PUBLIC HAETAE_MODE=${category})
		target_link_libraries(${TARGET_SIGN_BINARY_NAME}  ${LIB_NAME${category}} ${CT_GRIND_LIB} OpenSSL::Crypto)
		set_target_properties(${TARGET_SIGN_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ./${BUILD_SIGN})
endforeach(category)
