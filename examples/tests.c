//
// Created by Gilbert Ndollane Dione on 24/08/2024.
//

#include <string.h>
#include "tests.h"


int compare_byte_arrays(uint8_t *array1, uint8_t *array2, int length){
    for (int i=0; i < length; i++){
        if (array1[i] != array2[i]){ return 1; }
    }
    return 0;
}

int ct_compare_byte_arrays(uint8_t *array1, uint8_t *array2, int length){
    uint8_t res = 0;
    for (int i=0; i < length; i++){
        res |= array1[i] ^ array2[i];
    }
    return (int)res;
}

int conditional_assignment(uint8_t *dest, uint16_t dest_length, uint8_t *src, uint8_t cond){
    if (cond != 0){
        memcpy(dest, src, sizeof(dest_length));
    }
    return 0;
}