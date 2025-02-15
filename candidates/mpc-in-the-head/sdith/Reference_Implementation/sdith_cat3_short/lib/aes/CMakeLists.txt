set(AES_SRCS_GENERIC
        rijndael256.c
        rijndael256.h
        aes_ansi_ref.c
        aes128_ctrle.h
        aes128_ctrle_ref.c
        aes128_ctrle_special_ref.c
        aes128_ctrle_generics.impl.h
        rijndael256_ctrle.h
        rijndael256_ctrle_generics.impl.h
        rijndael256_ctrle_ref.c
        rijndael256_ctrle_special_ref.c
)


add_library(aes STATIC ${AES_SRCS_GENERIC})
target_include_directories(aes PUBLIC .)
