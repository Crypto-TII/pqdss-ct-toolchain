//
// Created by Gilbert Ndollane Dione on 28/07/2023.
//


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "../prng.h"
#include "../sign.h"
#include "../api.h"


uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;
uint8_t sk[CRYPTO_SECRETKEYBYTES] ;


int main(){
    int result =  crypto_sign_keypair(pk, sk);
    exit(result);
}
