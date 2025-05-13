
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

#include "api.h"

void store_buffer(const void* buffer, size_t length, FILE* file, const char* variable_name) {
    fprintf(file, "%s=", variable_name);
    if (!file) {
        perror("Error while opening file");
        return;
    }
    const unsigned char* bytes = (const unsigned char*) buffer;
    for (size_t i = 0; i < length; ++i) {
        fprintf(file, "%02X", bytes[i]);  // Hexadecimal format
    }
    fprintf(file, "\n");
}

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
    FILE *keys;
    keys = fopen("candidates/mpc-in-the-head/mirath/dudect/mirath_tcith_5a_short/mirath_sign/keys.txt", "a");
    randombytes_dudect(input_data, c->number_measurements * c->chunk_size);
    for (size_t i = 0; i < c->number_measurements; i++) {
        memset(input_data + (size_t)i * c->chunk_size, 0xF7, MESSAGE_LENGTH*sizeof(const unsigned char));
        const size_t offset = (size_t)i * c->chunk_size;
        unsigned char pk[CRYPTO_PUBLICKEYBYTES] = {0};
        unsigned char *sk = (unsigned char *)input_data + offset + MESSAGE_LENGTH*sizeof(const unsigned char);
        (void)crypto_sign_keypair(pk, sk);
        store_buffer(sk, SECRET_KEY_BYTE_LENGTH, keys, "sk");
    }
    fclose(keys);
}

int main(int argc, char **argv)
{
	(void)argc;
	(void)argv;

	const size_t chunk_size = sizeof(const unsigned char)*MESSAGE_LENGTH + SECRET_KEY_BYTE_LENGTH*sizeof(const unsigned char); 

	dudect_config_t config = {
		.chunk_size = chunk_size,
		.number_measurements = 10000.0,
	};
	dudect_ctx_t ctx;

	dudect_init(&ctx, &config);

    FILE *distributions;
    distributions = fopen("candidates/mpc-in-the-head/mirath/dudect/mirath_tcith_5a_short/mirath_sign/measurements_mirath_tcith_5a_short.txt", "w");

	dudect_state_t state = DUDECT_NO_LEAKAGE_EVIDENCE_YET;
	while (state == DUDECT_NO_LEAKAGE_EVIDENCE_YET) {
		state = dudect_main(&ctx);
		for(int i=0;i<10000.0;i++){
            fprintf(distributions, "%ld\n", ctx.exec_times[i]);
			}
		}
	fclose(distributions);
	dudect_free(&ctx);
	return (int)state;
}
