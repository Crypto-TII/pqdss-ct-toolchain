
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h> 
#include "../../../mirith_avx2_Ib_short/sign.h"
#include "../../../mirith_avx2_Ib_short/api.h"

#define msg_length  256
uint8_t sig_msg[CRYPTO_BYTES+msg_length] ; //CRYPTO_BYTES + msg_len
size_t sig_msg_len ;
size_t msg_len = msg_length ;
uint8_t msg[msg_length] ;
uint8_t sk[CRYPTO_SECRETKEYBYTES] ;

int main(){
	int result =  crypto_sign(sig_msg, &sig_msg_len, msg, msg_len, sk);
	exit(result);
}