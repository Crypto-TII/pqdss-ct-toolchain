
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <ctgrind.h>
#include <openssl/rand.h>
#include <time.h> 

#include "../../../mirith_avx2_Ia_fast/sign.h"
#include "../../../mirith_avx2_Ia_fast/api.h"

#define CTGRIND_SAMPLE_SIZE 100
#define message_length_define 256


uint8_t *sig_msg;
size_t *sig_msg_len;
uint8_t msg[message_length_define];
size_t msg_len = message_length_define;
uint8_t sk[CRYPTO_SECRETKEYBYTES];

void generate_test_vectors() {
	//Fill randombytes
	srand(time(NULL));
	//msg_len = rand(); 
	//msg_len = 1024 ;//256 ; 
	for (size_t i=0;i<msg_len;i++){
		uint8_t val = rand() &0xFF;
		msg[i] = val;
	}
	for (size_t i=0;i<CRYPTO_SECRETKEYBYTES;i++){
		uint8_t val = rand() &0xFF;
		sk[i] = val;
	}
	//*sig_msg_len = msg_len + CRYPTO_BYTES ;
} 

int main() {

	//msg = (uint8_t *)calloc(msg_len, sizeof(uint8_t));
	//sk = (uint8_t *)calloc(CRYPTO_SECRETKEYBYTES, sizeof(uint8_t));
	sig_msg_len = (size_t *)calloc(1, sizeof(size_t));
	sig_msg = (uint8_t *)calloc(*sig_msg_len, sizeof(uint8_t)); 

	int result = 2 ; 
	for (int i = 0; i < CTGRIND_SAMPLE_SIZE; i++) {
		generate_test_vectors(); 
		ct_poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
		result = crypto_sign(sig_msg, sig_msg_len, msg, msg_len, sk); 
		ct_unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
	}

	free(sig_msg); 
	free(sig_msg_len);
	//free(msg);
	//free(sk);
	return result;
}
