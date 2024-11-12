
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#include "poison.h"
#include "sign.h"


uint8_t *pk;
uint8_t *sk;

int main() {
	pk = calloc(CRYPTO_PUBLICKEYBYTES, sizeof(uint8_t)); 
	sk = calloc(CRYPTO_SECRETKEYBYTES, sizeof(uint8_t));

	int result = 2 ;
	poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
	result = crypto_sign_keypair(pk,sk); 
	unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t)); 
	free(pk);
	free(sk);
	return result; 
}
