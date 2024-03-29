#include <stdint.h>

#ifndef api_h
#define api_h

#define LAMBDA  128
#define N  13
#define LOG_Q  32
#define PRIME  4294967291lu
#define C  458
#define K  14
#define ROUND 16

/*///////////////////////////////////////////////////////////////////////
//////////////////////////// OTHER PARAMETER ////////////////////////////
///////////////////////////////////////////////////////////////////////*/

#define LEN   (N*(N-1)*(N-2)/6)
#define ALT_SIZE (LEN*LOG_Q/8)
#define MAT_SIZE (N*N*LOG_Q/8)
#define SEED_SIZE (LAMBDA/8)

/*///////////////////////////////////////////////////////////////////////
//////////////////////////// NIST PARAMETER //////////////////////////////
///////////////////////////////////////////////////////////////////////*/

int crypto_sign_keypair(uint8_t *pk, uint8_t *sk);
int crypto_sign(uint8_t *sm, uint64_t *smlen, const uint8_t *m, uint64_t mlen, const uint8_t *sk);
int crypto_sign_open(uint8_t *m, uint64_t *mlen, const uint8_t *sm, uint64_t smlen, const uint8_t *pk);

#define CRYPTO_ALGNAME "ALTEQ"
#define CRYPTO_SECRETKEYBYTES (SEED_SIZE)
#define CRYPTO_PUBLICKEYBYTES (C*ALT_SIZE+SEED_SIZE)
#define CRYPTO_BYTES ((ROUND-K+2)*SEED_SIZE+K*MAT_SIZE)

#endif
