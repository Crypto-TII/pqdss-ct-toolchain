
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#define DUDECT_IMPLEMENTATION
#include <dudect.h>

#define MESSAGE_LENGTH 256

#define SECRET_KEY_BYTE_LENGTH CRYPTO_SECRETKEYBYTES
#define SIGNATURE_MESSAGE_BYTE_LENGTH (MESSAGE_LENGTH + CRYPTO_BYTES)

#include "../../../mirith_avx2_Ia_short/sign.h"
#include "../../../mirith_avx2_Ia_short/api.h"

uint8_t do_one_computation(uint8_t *data) {

	size_t sig_msg_len = SIGNATURE_MESSAGE_BYTE_LENGTH; //the signature length could be initialized to 0.
	uint8_t sig_msg[SIGNATURE_MESSAGE_BYTE_LENGTH] = {0};
	size_t msg_len = MESSAGE_LENGTH; //  the message length could be also randomly generated.
	uint8_t *msg = (uint8_t*)data + 0; 
	uint8_t *sk = (uint8_t*)data + MESSAGE_LENGTH*sizeof(uint8_t) ; 

	uint8_t ret_val = 0;
	const int result = crypto_sign(sig_msg, &sig_msg_len, msg, msg_len, sk);
	ret_val ^= (uint8_t) result ^ sig_msg[0] ^ sig_msg[SIGNATURE_MESSAGE_BYTE_LENGTH - 1];
	return ret_val;
}

void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {
	randombytes_dudect(input_data, c->number_measurements * c->chunk_size);
	uint8_t public_key[CRYPTO_PUBLICKEYBYTES] = {0};
	uint8_t fixed_secret_key[CRYPTO_SECRETKEYBYTES] = {0};
	(void)crypto_sign_keypair(public_key, fixed_secret_key);
	for (size_t i = 0; i < c->number_measurements; i++) {
		classes[i] = randombit();
			if (classes[i] == 0) {
				memset(input_data + (size_t)i * c->chunk_size, 0x01, MESSAGE_LENGTH*sizeof(uint8_t));
				memcpy(input_data + (size_t)i * c->chunk_size+MESSAGE_LENGTH*sizeof(uint8_t), 
				        fixed_secret_key, SECRET_KEY_BYTE_LENGTH*sizeof(uint8_t));
			} else {
				const size_t offset = (size_t)i * c->chunk_size;
				uint8_t pk[CRYPTO_PUBLICKEYBYTES] = {0};
				uint8_t *sk = input_data + offset + MESSAGE_LENGTH;
				(void)crypto_sign_keypair(pk, sk);
			}
		}
	}

int main(int argc, char **argv)
{
	(void)argc;
	(void)argv;

	const size_t chunk_size = sizeof(uint8_t)*MESSAGE_LENGTH + SECRET_KEY_BYTE_LENGTH*sizeof(uint8_t); 

	dudect_config_t config = {
		.chunk_size = chunk_size,
		.number_measurements = 1e3,
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
