
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>

#include "../../include/sign.h"
#include "../../include/randombytes.h"

#define CTGRIND_SAMPLE_SIZE 100
#define max_message_length 3300


uint8_t *sm;
size_t smlen;
uint8_t *m;
size_t mlen;
uint8_t sk[CRYPTO_SECRETKEYBYTES];

void generate_test_vectors() {
	//Fill randombytes
	randombytes(m, mlen);
	randombytes(sk, CRYPTO_SECRETKEYBYTES);
} 

int main() {

	m = (uint8_t *)calloc(mlen, sizeof(uint8_t));
	sm = (uint8_t *)calloc(mlen+CRYPTO_BYTES, sizeof(uint8_t)); 


	int result = 2 ; 
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		mlen = 33*(i+1);
		generate_test_vectors(); 
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
		result = crypto_sign_sign(sm, &smlen, m, mlen, sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
	}

	free(sm); 
	free(m);
	return result;
}
