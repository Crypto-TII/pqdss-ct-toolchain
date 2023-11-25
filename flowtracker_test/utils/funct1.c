//
// Created by Gilbert Ndollane Dione on 18/11/2023.
//

//#include "funct1.h"
//#include "utils.h"
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "time.h"

int call_compare(uint8_t *array1, uint8_t *array2, int len){
    int res ;
    for (i=0; i<len; i++){
        if (array1[i] != array2[i]){
            return 1;
        }

    }
    return 0;
}


//int call_compare(uint8_t *array1, uint8_t *array2, int len, int result){
//    int res ;
//    result = nct_compare_two_byte_arrays(array1, array2, len) ;
//    if (result ==1){
//        res = 1 ;
//    }
//    else{
//        res = -1;
//    }
//
//    return res;
//}
