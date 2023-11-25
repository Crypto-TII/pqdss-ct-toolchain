
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#include "../../utils/utils.h"

#define SIZE (1 << 4)
uint8_t a[SIZE];
uint8_t b[SIZE];
int len = SIZE;


int main(){
	uint8_t result =  nct_compare_two_byte_arrays(a, b, len);
	exit(result);
}
