
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>
#include "api.h"

uint8_t pk[CRYPTO_PUBLICKEYBYTES] ;
uint8_t sk[CRYPTO_SECRETKEYBYTES] ;

int main(){
	crypto_sign_keypair(pk, sk);
	int result =  crypto_sign_keypair(pk, sk);
	exit(result);
} 
