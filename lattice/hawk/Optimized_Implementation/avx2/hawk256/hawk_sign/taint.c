
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>
#include <openssl/rand.h>
#include <time.h> 

#include "../../../hawk256/api.h"

#define CTGRIND_SAMPLE_SIZE 100
#define message_length_define 256


unsigned char *sm;
unsigned long long *smlen;
unsigned char m[message_length_define];
unsigned long long mlen = message_length_define;
unsigned char sk[CRYPTO_SECRETKEYBYTES];

void generate_test_vectors() {
	//Fill randombytes
	srand(time(NULL));
	//mlen = rand(); 
	//mlen = 1024 ;//256 ; 
	for (unsigned long long i=0;i<mlen;i++){
		unsigned char val = rand() &0xFF;
		m[i] = val;
	}
	for (size_t i=0;i<CRYPTO_SECRETKEYBYTES;i++){
		unsigned char val = rand() &0xFF;
		sk[i] = val;
	}
	//*smlen = mlen + CRYPTO_BYTES ;
} 

int main() {

	//m = (unsigned char *)calloc(mlen, sizeof(unsigned char));
	//sk = (unsigned char *)calloc(CRYPTO_SECRETKEYBYTES, sizeof(unsigned char));
	smlen = (unsigned long long *)calloc(1, sizeof(unsigned long long));
	sm = (unsigned char *)calloc(*smlen, sizeof(unsigned char)); 

	int result = 2 ; 
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		generate_test_vectors(); 
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
		result = crypto_sign(sm, smlen, m, mlen, sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(unsigned char));
	}

	free(sm); 
	free(smlen);
	//free(m);
	//free(sk);
	return result;
}
