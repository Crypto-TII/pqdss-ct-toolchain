
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h> 
#include "api.h"

#define msg_length  3300
unsigned char sm[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len
unsigned long long smlen ;
volatile unsigned long long mlen = msg_length ;
unsigned char m[msg_length] ;
unsigned char sk[CRYPTO_SECRETKEYBYTES] ;

int main(){
	crypto_sign(sm, &smlen, m, mlen, sk);
	int result =  crypto_sign(sm, &smlen, m, mlen, sk);
	exit(result);
}
