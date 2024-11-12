
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#include "poison.h"
#include "sign.h"
#include "toolchain_randombytes.h"

#define TIMECOP_NUMBER_OF_EXECUTION 1
#define max_message_length 3300

int main() {
	uint8_t *sig_msg;
	size_t sig_msg_len = 0;
	//size_t *sig_msg_len;
	uint8_t *msg;
	size_t msg_len = 0;
	uint8_t sk[CRYPTO_SECRETKEYBYTES] = {0};
	int result = 2 ; 
	for (int i = 0; i < TIMECOP_NUMBER_OF_EXECUTION; i++) {
		msg_len = 33*(i+1);
		msg = (uint8_t *)calloc(msg_len, sizeof(uint8_t));
		sig_msg = (uint8_t *)calloc(msg_len+CRYPTO_BYTES, sizeof(uint8_t));

		randombytes(msg, msg_len);
		uint8_t public_key[CRYPTO_PUBLICKEYBYTES] = {0};
		(void)crypto_sign_keypair(public_key, sk);

		poison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
		result = crypto_sign(sig_msg, &sig_msg_len, msg, msg_len, sk); 
		unpoison(sk, CRYPTO_SECRETKEYBYTES * sizeof(uint8_t));
		free(sig_msg);
		free(msg);
	}
	return result;
}
