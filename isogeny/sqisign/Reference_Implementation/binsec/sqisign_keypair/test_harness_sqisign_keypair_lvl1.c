#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <protocols.h>
#include "sig.h"
#include "../../src/nistapi/lvl1/api.h"


uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;
uint8_t sk[CRYPTO_SECRETKEYBYTES] ;

int main(){
    //***CAUTION*** Only the first function called will be instrumentalize by binsec
    int result =  sqisign_keypair(pk, sk);
    exit(result);
}