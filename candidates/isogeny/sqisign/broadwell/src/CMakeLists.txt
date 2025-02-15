add_subdirectory(common)

if(ENABLE_SIGN)
    add_subdirectory(quaternion)
endif()

add_subdirectory(mp)
add_subdirectory(gf)
add_subdirectory(precomp)
add_subdirectory(ec)
add_subdirectory(hd)
add_subdirectory(verification)

if(ENABLE_SIGN)
    add_subdirectory(id2iso)
    add_subdirectory(signature)
endif()


# Constant-time - benchmarks tests
# == Constant-time tests
option(RUN_CT_TESTS "Run constant time tests" OFF)
#set(TOOLS_FLAGS "-g")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${TOOLS_FLAGS}")
#set(TOOL_NAME "timecop")
#set(TOOL_FOLDER ../${TOOL_NAME})
set(TOOL_FOLDER ../../${TOOL_NAME})
set(BUILD_KEYPAIR ${TOOL_FOLDER}/sqisign_keypair)
set(BUILD_SIGN ${TOOL_FOLDER}/sqisign_sign)
# == Benchmarks
option(RUN_BENCHMARKS "Run custom benchmarks" OFF)
set(BENCHMARK_TESTS "benchmarks")
set(BENCHMARKS_FOLDER ../../${BENCHMARK_TESTS})
set(SRC_BENCHMARK ${BENCHMARKS_FOLDER}/bench)
# Constant-time - benchmarks tests


message(":::::::TOOL_TEMPLATE_PATTERN: ${TOOL_TEMPLATE_PATTERN}")


message("")


FOREACH(SVARIANT ${SVARIANT_S})
    string(TOLOWER ${SVARIANT} SVARIANT_LOWER)
    string(TOUPPER ${SVARIANT} SVARIANT_UPPER)
    set(SOURCE_FILES_VARIANT sqisign.c)

    # Library for SQIsign variant
    add_library(sqisign_${SVARIANT_LOWER} ${SOURCE_FILES_VARIANT})
    target_link_libraries(sqisign_${SVARIANT_LOWER} PUBLIC
        $<$<BOOL:${ENABLE_SIGN}>:${LIB_SIGNATURE_${SVARIANT_UPPER}}>
        ${LIB_VERIFICATION_${SVARIANT_UPPER}}
        $<$<BOOL:${ENABLE_SIGN}>:${LIB_ID2ISO_${SVARIANT_UPPER}}>
        $<$<BOOL:${ENABLE_SIGN}>:${LIB_QUATERNION}>
        ${LIB_MP}
        ${LIB_GF_${SVARIANT_UPPER}}
        ${LIB_EC_${SVARIANT_UPPER}}
        ${LIB_HD_${SVARIANT_UPPER}}
        ${LIB_PRECOMP_${SVARIANT_UPPER}}
        $<$<BOOL:${ENABLE_SIGN}>:GMP>
        sqisign_common_sys
    )

    target_include_directories(sqisign_${SVARIANT_LOWER} PUBLIC $<$<BOOL:${ENABLE_SIGN}>:${INC_SIGNATURE}> ${INC_VERIFICATION} $<$<BOOL:${ENABLE_SIGN}>:${INC_QUATERNION}> ${INC_PRECOMP_${SVARIANT_UPPER}} ${INC_MP} ${INC_EC} ${INC_GF} ${INC_GF_${SVARIANT_UPPER}} ${INC_COMMON} ${INC_HD} $<$<BOOL:${ENABLE_SIGN}>:${INC_ID2ISO}> ../include PRIVATE common/generic internal)
    target_compile_definitions(sqisign_${SVARIANT_LOWER} PUBLIC SQISIGN_VARIANT=${SVARIANT})

    # Library for SQIsign variant (test)
    add_library(sqisign_${SVARIANT_LOWER}_test ${SOURCE_FILES_VARIANT})
    target_link_libraries(sqisign_${SVARIANT_LOWER}_test PUBLIC
        $<$<BOOL:${ENABLE_SIGN}>:${LIB_SIGNATURE_${SVARIANT_UPPER}}>
        ${LIB_VERIFICATION_${SVARIANT_UPPER}}
        $<$<BOOL:${ENABLE_SIGN}>:${LIB_ID2ISO_${SVARIANT_UPPER}}>
        $<$<BOOL:${ENABLE_SIGN}>:${LIB_QUATERNION}>
        ${LIB_MP}
        ${LIB_GF_${SVARIANT_UPPER}}
        ${LIB_EC_${SVARIANT_UPPER}}
        ${LIB_HD_${SVARIANT_UPPER}}
        ${LIB_PRECOMP_${SVARIANT_UPPER}}
        $<$<BOOL:${ENABLE_SIGN}>:GMP>
        sqisign_common_test
    )

    target_include_directories(sqisign_${SVARIANT_LOWER}_test PUBLIC $<$<BOOL:${ENABLE_SIGN}>:${INC_SIGNATURE}> ${INC_VERIFICATION} $<$<BOOL:${ENABLE_SIGN}>:${INC_QUATERNION}> ${INC_PRECOMP_${SVARIANT_UPPER}} ${INC_MP} ${INC_EC} ${INC_GF} ${INC_GF_${SVARIANT_UPPER}} ${INC_COMMON} ${INC_HD} $<$<BOOL:${ENABLE_SIGN}>:${INC_ID2ISO}> ../include PRIVATE common/generic internal)
    target_compile_definitions(sqisign_${SVARIANT_LOWER}_test PUBLIC SQISIGN_VARIANT=${SVARIANT})

    # Library with NIST API
    set(SOURCE_FILE_NISTAPI nistapi/${SVARIANT_LOWER}/api.c)
    add_library(sqisign_${SVARIANT_LOWER}_nistapi ${SOURCE_FILE_NISTAPI})
    target_link_libraries(sqisign_${SVARIANT_LOWER}_nistapi PUBLIC sqisign_${SVARIANT_LOWER})
    target_include_directories(sqisign_${SVARIANT_LOWER}_nistapi PUBLIC nistapi/${SVARIANT_LOWER} PUBLIC ../include)
    target_compile_definitions(sqisign_${SVARIANT_LOWER}_nistapi PUBLIC SQISIGN_VARIANT=${SVARIANT})

    # Library with NIST API (test)
    add_library(sqisign_${SVARIANT_LOWER}_test_nistapi ${SOURCE_FILE_NISTAPI})
    target_link_libraries(sqisign_${SVARIANT_LOWER}_test_nistapi PUBLIC sqisign_${SVARIANT_LOWER}_test)
    target_include_directories(sqisign_${SVARIANT_LOWER}_test_nistapi PUBLIC nistapi/${SVARIANT_LOWER})
    target_compile_definitions(sqisign_${SVARIANT_LOWER}_test_nistapi PUBLIC SQISIGN_VARIANT=${SVARIANT})


    # Constant-time and benchmarks
    # === Constant-time tests
    if (RUN_CT_TESTS)
        set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair_${SVARIANT_LOWER})
        add_executable(${TARGET_BINARY_NAME}  ${TOOL_FOLDER}/sqisign_keypair/${TOOL_TEMPLATE_PATTERN}_crypto_sign_keypair.c)
        target_include_directories(${TARGET_BINARY_NAME} PUBLIC nistapi/${SVARIANT_LOWER})
#        target_link_libraries(${TARGET_BINARY_NAME} PRIVATE sqisign_${SVARIANT_LOWER}_nistapi ${TOOL_LINK_LIBS})
        target_link_libraries(${TARGET_BINARY_NAME} PRIVATE sqisign_${SVARIANT_LOWER}_nistapi ${TOOL_LINK_LIBS})
        set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_KEYPAIR})
        #Test harness for crypto_sign
        set(TARGET_BINARY_NAME ${TOOL_TEMPLATE_PATTERN}_crypto_sign_${SVARIANT_LOWER})
        add_executable(${TARGET_BINARY_NAME}  ${TOOL_FOLDER}/sqisign_sign/${TOOL_TEMPLATE_PATTERN}_crypto_sign.c)
        target_include_directories(${TARGET_BINARY_NAME} PUBLIC nistapi/${SVARIANT_LOWER})
#        target_link_libraries(${TARGET_BINARY_NAME} PRIVATE sqisign_${SVARIANT_LOWER}_nistapi ${TOOL_LINK_LIBS})
        target_link_libraries(${TARGET_BINARY_NAME} PRIVATE sqisign_${SVARIANT_LOWER}_nistapi ${TOOL_LINK_LIBS})
        set_target_properties(${TARGET_BINARY_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BUILD_SIGN})
    endif ()
    # === Benchmark tests
    if (RUN_BENCHMARKS)
        set(TEST_BENCH bench_${SVARIANT_LOWER})
        add_executable(${TEST_BENCH} ${SRC_BENCHMARK}.c)
        target_link_libraries(${TEST_BENCH} PRIVATE sqisign_${SVARIANT_LOWER}_nistapi m cpucycles)
        set_target_properties(${TEST_BENCH} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ../${BENCHMARKS_FOLDER})
    endif ()
ENDFOREACH()
