//
// Examples of generics tests
//
#include <stdint.h>

#ifndef PQDSS_CT_TOOLCHAIN_TESTS_H
#define PQDSS_CT_TOOLCHAIN_TESTS_H

int compare_byte_arrays(uint8_t *array1, uint8_t *array2, int length);
int ct_compare_byte_arrays(uint8_t *array1, uint8_t *array2, int length);
int conditional_assignment(uint8_t *dest, uint16_t dest_length, uint8_t *src, uint8_t cond);

#endif //PQDSS_CT_TOOLCHAIN_TESTS_H
