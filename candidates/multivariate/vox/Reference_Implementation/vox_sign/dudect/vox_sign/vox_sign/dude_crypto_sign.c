
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#define DUDECT_IMPLEMENTATION
#include <dudect.h>

#define MESSAGE_LENGTH 3300

#define SECRET_KEY_BYTE_LENGTH CRYPTO_SECRETKEYBYTES
#define SIGNATURE_MESSAGE_BYTE_LENGTH (MESSAGE_LENGTH + CRYPTO_BYTES)

#include "../../../../vox_sign/api.h"

uint8_t do_one_computation(uint8_t *data) {

	unsigned long long smlen = SIGNATURE_MESSAGE_BYTE_LENGTH; //the signature length could be initialized to 0.
	unsigned char sm[SIGNATURE_MESSAGE_BYTE_LENGTH] = {0};
	unsigned long long mlen = MESSAGE_LENGTH; //  the message length could be also randomly generated.
	const unsigned char *m = (const unsigned char*)data + 0; 
	const unsigned char *sk = (const unsigned char*)data + MESSAGE_LENGTH*sizeof(const unsigned char) ; 

	uint8_t ret_val = 0;
	const int result = crypto_sign(sm, &smlen, m, mlen, sk);
	ret_val ^= (uint8_t) result ^ sm[0] ^ sm[SIGNATURE_MESSAGE_BYTE_LENGTH - 1];
	return ret_val;
}

void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {
	randombytes_dudect(input_data, c->number_measurements * c->chunk_size);
	const unsigned char public_key[CRYPTO_PUBLICKEYBYTES] = {0};
	const unsigned char fixed_secret_key[CRYPTO_SECRETKEYBYTES] = {0};
	(void)crypto_sign_keypair(public_key, fixed_secret_key);
	for (size_t i = 0; i < c->number_measurements; i++) {
		classes[i] = randombit();
			if (classes[i] == 0) {
				memset(input_data + (size_t)i * c->chunk_size, 0x01, MESSAGE_LENGTH*sizeof(const unsigned char));
				memcpy(input_data + (size_t)i * c->chunk_size+MESSAGE_LENGTH*sizeof(const unsigned char), 
				        fixed_secret_key, SECRET_KEY_BYTE_LENGTH*sizeof(const unsigned char));
			} else {
				const size_t offset = (size_t)i * c->chunk_size;
				const unsigned char pk[CRYPTO_PUBLICKEYBYTES] = {0};
				const unsigned char *sk = input_data + offset + MESSAGE_LENGTH;
				(void)crypto_sign_keypair(pk, sk);
			}
		}
	}

int main(int argc, char **argv)
{
	(void)argc;
	(void)argv;

	const size_t chunk_size = sizeof(const unsigned char)*MESSAGE_LENGTH + SECRET_KEY_BYTE_LENGTH*sizeof(const unsigned char); 

	dudect_config_t config = {
		.chunk_size = chunk_size,
		.number_measurements = 1e4,
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