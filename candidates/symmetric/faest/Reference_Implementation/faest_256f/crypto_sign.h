/*
 *  SPDX-License-Identifier: MIT
 */

#ifndef CRYPTO_SIGN_256F_H
#define CRYPTO_SIGN_256F_H

#define CRYPTO_SECRETKEYBYTES (32 + 64 / 2)
#define CRYPTO_PUBLICKEYBYTES 64
#define CRYPTO_BYTES 28400
#define CRYPTO_ALGNAME "faest_256f"

int crypto_sign_keypair(unsigned char* pk, unsigned char* sk);
int crypto_sign(unsigned char* sm, unsigned long long* smlen, const unsigned char* m,
                unsigned long long mlen, const unsigned char* sk);
int crypto_sign_open(unsigned char* m, unsigned long long* mlen, const unsigned char* sm,
                     unsigned long long smlen, const unsigned char* pk);

#endif

// vim: ft=c
