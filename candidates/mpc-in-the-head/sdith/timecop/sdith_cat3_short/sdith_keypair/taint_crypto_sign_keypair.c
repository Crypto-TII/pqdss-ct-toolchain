
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#include "poison.h"
#include "api.h"


unsigned char *pk;
unsigned char *sk;

int main() {
	pk = calloc(CRYPTO_PUBLICKEYBYTES, sizeof(unsigned char)); 
	sk = calloc(CRYPTO_SECRETKEYBYTES, sizeof(unsigned char));

	int result = 2 ;
	poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
	result = crypto_sign_keypair(pk,sk); 
	unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char)); 
	free(pk);
	free(sk);
	return result; 
}
