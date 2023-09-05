#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <protocols.h>
#include "sig.h"
#include "../../src/nistapi/lvl3/api.h"

unsigned char sm [CRYPTO_BYTES + 32];
unsigned long long smlen = CRYPTO_BYTES + 32;
unsigned char m[32];
unsigned long long mlen = 32;
uint8_t sk[CRYPTO_SECRETKEYBYTES] ;

int main(){
    //***CAUTION*** Only the first function called will be instrumentalize by binsec
    int result =  sqisign_sign(sm, &smlen, m, mlen, sk);
    exit(result);
}