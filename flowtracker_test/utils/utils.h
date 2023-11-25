// =============================================
// ==    Classification: TII CONFIDENTIAL     ==
// =============================================

#ifndef CT_ALGO_UTILS_IS_GREATER_THAN_H
#define CT_ALGO_UTILS_IS_GREATER_THAN_H

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "time.h"



uint8_t nct_compare_two_byte_arrays(uint8_t *a, uint8_t *b, int len);
uint8_t ct_compare_two_byte_arrays(uint8_t *a, uint8_t *b, int len);
int8_t rejection_sampling(uint8_t *source, int source_len, uint16_t *secret, int bound );



#endif //CT_ALGO_UTILS_IS_GREATER_THAN_H
