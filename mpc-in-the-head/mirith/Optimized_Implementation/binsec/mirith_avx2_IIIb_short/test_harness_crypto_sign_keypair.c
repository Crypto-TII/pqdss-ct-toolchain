#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "../../mirith_avx2_IIIb_short/prng.h"
#include "../../mirith_avx2_IIIb_short/sign.h"
#include "../../mirith_avx2_IIIb_short/api.h"


uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;
uint8_t sk[CRYPTO_SECRETKEYBYTES] ;


int main(){
      int result =  crypto_sign_keypair(pk, sk);
      exit(result);
}
