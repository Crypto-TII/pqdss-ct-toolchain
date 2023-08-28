#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "../../mirith_hypercube_avx2_Va_short/prng.h"
#include "../../mirith_hypercube_avx2_Va_short/sign.h"
#include "../../mirith_hypercube_avx2_Va_short/api.h"


uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;
uint8_t sk[CRYPTO_SECRETKEYBYTES] ;


int main(){
      int result =  crypto_sign_keypair(pk, sk);
      exit(result);
}
