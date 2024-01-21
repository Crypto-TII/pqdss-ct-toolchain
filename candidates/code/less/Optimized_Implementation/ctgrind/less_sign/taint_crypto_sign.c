
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>
#include "../../include/api.h"
#include "../../include/rng.h"

#define CTGRIND_SAMPLE_SIZE 100
#define max_message_length 3300

unsigned char *sm;
unsigned long long smlen = 0;
//unsigned long long *smlen;
unsigned char *m;
unsigned long long mlen = 0;
unsigned char sk[CRYPTO_SECRETKEYBYTES] = {0};

void generate_test_vectors() {
	//Fill randombytes
	randombytes(m, mlen);
	randombytes(sk, CRYPTO_SECRETKEYBYTES);
} 

int main() {
	int result = 2 ; 
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		mlen = 33*(i+1);
		m = (unsigned char *)calloc(mlen, sizeof(unsigned char));
		sm = (unsigned char *)calloc(mlen+CRYPTO_BYTES, sizeof(unsigned char));

		generate_test_vectors(); 
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
		result = crypto_sign(sm, &smlen, m, mlen, sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
		free(sm);
		free(m);
	}
	return result;
}
