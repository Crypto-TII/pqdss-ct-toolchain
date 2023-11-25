
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#define DUDECT_IMPLEMENTATION
#include <dudect.h>



#include "../../utils/utils.h"

void generate_test_vectors() {
	//DEFAULT: Fill randombytes

    //randombytes(secret, DEFAULT_VALUE*long);
} 

uint8_t do_one_computation(uint8_t *data) {

    uint8_t source[1000];

    int source_len;

    uint16_t secret[1000];

    int bound;

	//Do the needed process on the input <<data>>
	int8_t result = rejection_sampling(source, source_len, secret, bound);
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
		.number_measurements = DEFAULT_VALUE,
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
