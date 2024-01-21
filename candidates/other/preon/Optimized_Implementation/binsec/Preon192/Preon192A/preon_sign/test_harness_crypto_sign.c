
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h> 
#include "../../../../Preon192/Preon192A/api.h"

#define msg_length  256
unsigned char sm[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len
unsigned long long smlen ;
unsigned long long mlen = msg_length ;
unsigned char m[msg_length] ;
unsigned char sk[CRYPTO_SECRETKEYBYTES] ;

int main(){
	int result =  crypto_sign(sm, &smlen, m, mlen, sk);
	exit(result);
}
