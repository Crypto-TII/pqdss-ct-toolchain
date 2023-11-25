
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#define DUDECT_IMPLEMENTATION
#include <dudect.h>



#include "../../utils/utils.h"

uint8_t do_one_computation(uint8_t *data) {

    uint8_t a[50];

    uint8_t b[50];

    int len = 50;
    memcpy(a, data, 50);
    memcpy(b, data+50, 50);
	//Do the needed process on the input <<data>>
	uint8_t result = nct_compare_two_byte_arrays(a, b, len);
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
		.chunk_size = 10,
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
