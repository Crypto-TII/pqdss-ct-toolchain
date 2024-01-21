
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>
#include "../../../mirith_avx2_Ia_fast/sign.h"
#include "../../../mirith_avx2_Ia_fast/api.h"
#include "../../../mirith_avx2_Ia_fast/nist/rng.h"

#define CTGRIND_SAMPLE_SIZE 100
#define max_message_length 3300

uint8_t *sig_msg;
size_t sig_msg_len = 0;
//size_t *sig_msg_len;
uint8_t *msg;
size_t msg_len = 0;
uint8_t sk[CRYPTO_SECRETKEYBYTES] = {0};

void generate_test_vectors() {
	//Fill randombytes
	randombytes(msg, msg_len);
	//randombytes(sk, CRYPTO_SECRETKEYBYTES);
	uint8_t public_key[CRYPTO_PUBLICKEYBYTES] = {0};
	(void)crypto_sign_keypair(public_key, sk);
} 

int main() {
	int result = 2 ; 
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		msg_len = 33*(i+1);
		msg = (uint8_t *)calloc(msg_len, sizeof(uint8_t));
		sig_msg = (uint8_t *)calloc(msg_len+CRYPTO_BYTES, sizeof(uint8_t));

		generate_test_vectors(); 
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
		result = crypto_sign(sig_msg, &sig_msg_len, msg, msg_len, sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
		free(sig_msg);
		free(msg);
	}
	return result;
}
