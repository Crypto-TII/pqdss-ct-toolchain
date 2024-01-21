
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

#define DUDECT_IMPLEMENTATION
#include <dudect.h>

#include "../../../../src/mayo_2/api.h"

uint8_t do_one_computation(uint8_t *data) {
	unsigned char pk[CRYPTO_PUBLICKEYBYTES] = {0};;
	unsigned char sk[CRYPTO_SECRETKEYBYTES] = {0};;

	int result = crypto_sign_keypair(pk,sk);
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
		.chunk_size = 32,
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
