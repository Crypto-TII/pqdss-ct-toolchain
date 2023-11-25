
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#include <ctgrind.h>


#include "../../utils/utils.h"

#define DEFAULT_CTGRIND_SAMPLE_SIZE 100


uint8_t a[50];

uint8_t b[50];

int len = 10;

void generate_test_vectors() {
	//DEFAULT: Fill randombytes

    //randombytes(a, DEFAULT_VALUE*long);
} 

int main() {
	//DEFAULT:
	//a = (uint8_t *)calloc(DEFAULT_VALUE, sizeof(uint8_t));

	uint8_t result ; 
	for (int i = 0; i < DEFAULT_CTGRIND_SAMPLE_SIZE; i++) {
		generate_test_vectors(); 

    	ct_poison(a, 50 * sizeof(uint8_t));

		result = nct_compare_two_byte_arrays(a, b, len); 

    	ct_unpoison(a, 50 * sizeof(uint8_t));

	}

	//DEFAULT:
	//free(a); 
	return result;
}
