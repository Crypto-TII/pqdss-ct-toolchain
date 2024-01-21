
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>
#include "../../../hawk256/api.h"
#include "../../../hawk256/rng.h"

#define CTGRIND_SAMPLE_SIZE 100
#define max_message_length 3300

unsigned char *sm;
unsigned long long smlen;
const unsigned char *m;
unsigned long long mlen;
const unsigned char sk[CRYPTO_SECRETKEYBYTES];

void generate_test_vectors() {
	//Fill randombytes
	randombytes(m, mlen);
	randombytes(sk, CRYPTO_SECRETKEYBYTES);
} 

int main() {

	m = (const unsigned char *)calloc(mlen, sizeof(const unsigned char));
	sm = (unsigned char *)calloc(mlen+CRYPTO_BYTES, sizeof(unsigned char)); 


	int result = 2 ; 
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		mlen = 33*(i+1);
		generate_test_vectors(); 
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(const unsigned char));
		result = crypto_sign(sm, &smlen, m, mlen, sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(const unsigned char));
	}

	free(sm); 
	free(m);
	return result;
}
