
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>
#include <openssl/rand.h>

#include "../../include/sign.h"

#define CTGRIND_SAMPLE_SIZE 100

uint8_t *pk;
uint8_t *sk;

int main() {
	pk = calloc(CRYPTO_PUBLICKEYBYTES, sizeof(uint8_t)); 
	sk = calloc(CRYPTO_SECRETKEYBYTES, sizeof(uint8_t));

	int result = 2 ;
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
		result = crypto_sign_keypair(pk,sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t)); 
	}

	free(pk);
	free(sk);
	return result; 
}
