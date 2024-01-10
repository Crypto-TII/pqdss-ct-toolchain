#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <protocols.h>
#include "sig.h"
#include <ctgrind.h>
#include "../../src/nistapi/lvl1/api.h"

#define CTGRIND_SAMPLE_SIZE 100

unsigned char sm [CRYPTO_BYTES + 32];
unsigned long long smlen = CRYPTO_BYTES + 32;
unsigned char m[32];
unsigned long long mlen = 32;
uint8_t sk[CRYPTO_SECRETKEYBYTES] ;

int main() {

    int result = 2 ;
    for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
        ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
        result = sqisign_sign(sm, &smlen, m, mlen, sk);
        ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
    }

    return result;
}