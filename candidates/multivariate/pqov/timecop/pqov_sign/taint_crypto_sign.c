
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#include "poison.h"
#include "api.h"
#include "toolchain_randombytes.h"

#define TIMECOP_NUMBER_OF_EXECUTION 1
#define max_message_length 3300

int main() {
	unsigned char *sm;
	size_t smlen = 0;
	//size_t *smlen;
	unsigned char *m;
	size_t mlen = 0;
	unsigned char sk[CRYPTO_SECRETKEYBYTES] = {0};
	int result = 2 ; 
	for (int i = 0; i < TIMECOP_NUMBER_OF_EXECUTION; i++) {
		mlen = 33*(i+1);
		m = (unsigned char *)calloc(mlen, sizeof(unsigned char));
		sm = (unsigned char *)calloc(mlen+CRYPTO_BYTES, sizeof(unsigned char));

		ct_randombytes(m, mlen);
		unsigned char public_key[CRYPTO_PUBLICKEYBYTES] = {0};
		(void)crypto_sign_keypair(public_key, sk);

		poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
		result = crypto_sign(sm, &smlen, m, mlen, sk); 
		unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
		free(sm);
		free(m);
	}
	return result;
}
