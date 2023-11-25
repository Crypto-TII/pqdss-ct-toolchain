
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>
#include "time.h"

#include <ctgrind.h>



#include "../../utils/utils.h"

#define DEFAULT_CTGRIND_SAMPLE_SIZE 50
#define default_length 20

uint8_t *source;

int source_len;

uint16_t *secret;

int bound;

void generate_test_vectors() {
	//DEFAULT: Fill randombytes
    time_t t;
    srand((unsigned) time(&t));
    source_len = 20 ;
    /* Generate  len random numbers bytes (from 0 to 255) */
    for(int i = 0 ; i < source_len ; i++ ) {
        source[i] = rand() & 0xFF ;
    }
    bound = rand() & 0x7FFF ;
    //randombytes(secret, DEFAULT_VALUE*long);
} 

int main() {
	//DEFAULT:
	//source = (uint8_t *)calloc(DEFAULT_VALUE, sizeof(uint8_t));

	int8_t result ;
    source = (uint8_t *)calloc(100, sizeof(uint8_t));
    secret = (uint16_t *)calloc(50, sizeof(uint16_t));
	for (int i = 0; i < DEFAULT_CTGRIND_SAMPLE_SIZE; i++) {
		generate_test_vectors(); 

    	ct_poison(secret, 50 * sizeof(uint16_t));

		result = rejection_sampling(source, source_len, secret, bound); 

    	ct_unpoison(secret, 50 * sizeof(uint16_t));

	}

	//DEFAULT:
	free(source);
    free(secret);
	return result;
}
