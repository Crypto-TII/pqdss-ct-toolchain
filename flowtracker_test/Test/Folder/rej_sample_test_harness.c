
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#include "../../utils/utils.h"

#define length (1<<8)

uint8_t source[length];
int source_len = length;
uint16_t secret[length/2];
int bound;


int main(){
	int8_t result =  rejection_sampling(source, source_len, secret, bound);
	exit(result);
}
