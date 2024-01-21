
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>
#include <openssl/rand.h>

#include "../../../sphincs-a-sha2-128s/api.h"

#define CTGRIND_SAMPLE_SIZE 100

unsigned char *pk;
unsigned char *sk;

int main() {
	pk = calloc(CRYPTO_PUBLICKEYBYTES, sizeof(unsigned char)); 
	sk = calloc(CRYPTO_SECRETKEYBYTES, sizeof(unsigned char));

	int result = 2 ;
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
		result = crypto_sign_keypair(pk,sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char)); 
	}

	free(pk);
	free(sk);
	return result; 
}
