
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>
#include "../../../../Preon128/Preon128A/api.h"
#include "../../../../Preon128/Preon128A/rng.h"

#define CTGRIND_SAMPLE_SIZE 100
#define max_message_length 3300

unsigned char *sm;
unsigned long long smlen;
unsigned char *m;
unsigned long long mlen;
unsigned char sk[CRYPTO_SECRETKEYBYTES];

void generate_test_vectors() {
	//Fill randombytes
	randombytes(m, mlen);
	randombytes(sk, CRYPTO_SECRETKEYBYTES);
} 

int main() {

	m = (unsigned char *)calloc(mlen, sizeof(unsigned char));
	sm = (unsigned char *)calloc(mlen+CRYPTO_BYTES, sizeof(unsigned char)); 


	int result = 2 ; 
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		mlen = 33*(i+1);
		generate_test_vectors(); 
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
		result = crypto_sign(sm, &smlen, m, mlen, sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
	}

	free(sm); 
	free(m);
	return result;
}
