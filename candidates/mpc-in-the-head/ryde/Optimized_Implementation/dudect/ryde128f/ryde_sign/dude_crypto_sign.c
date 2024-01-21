
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#define DUDECT_IMPLEMENTATION
#include <dudect.h>

#define MESSAGE_LENGTH 3300

#include "../../../ryde128f/src/api.h"

uint8_t do_one_computation(uint8_t *data) {
	unsigned long long smlen = MESSAGE_LENGTH+CRYPTO_BYTES;
	unsigned char sm[MESSAGE_LENGTH+CRYPTO_BYTES] = {0x00};
	unsigned long long mlen = MESSAGE_LENGTH; // // See how to generate randomly the message length 
	unsigned char m[MESSAGE_LENGTH] = {2,0xe1,8,4,0xd2,0xea,3,4}; 
	unsigned char sk[CRYPTO_SECRETKEYBYTES]= {0};
	/* We can either fix msg and msg_len or generate them randomly from <data>
	1. Fix msg and msg_len: chunk_size = CRYPTO_SECRETKEYBYTES
	2. Generate randomly msg and msg_len: chunk_size = CRYPTO_SECRETKEYBYTES + msg_len + NUMBER_BYTES(msg_len)
	*/
	memcpy(sk, data, CRYPTO_SECRETKEYBYTES);

	int result = crypto_sign(sm, &smlen, m, mlen, sk);
	return result;
}

void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {
	randombytes_dudect(input_data, c->number_measurements * c->chunk_size);
	for (size_t i = 0; i < c->number_measurements; i++) {
		classes[i] = randombit();
			if (classes[i] == 0) {
				memset(input_data + (size_t)i * c->chunk_size, 0x00, c->chunk_size);
			} else {
    // leave random
			}
		}
	}

int main(int argc, char **argv)
{
	(void)argc;
	(void)argv;

	dudect_config_t config = {
		.chunk_size = CRYPTO_SECRETKEYBYTES,
		.number_measurements = 1000,
	};
	dudect_ctx_t ctx;

	dudect_init(&ctx, &config);

	dudect_state_t state = DUDECT_NO_LEAKAGE_EVIDENCE_YET;
	while (state == DUDECT_NO_LEAKAGE_EVIDENCE_YET) {
		state = dudect_main(&ctx);
	}
	dudect_free(&ctx);
	return (int)state;
}
