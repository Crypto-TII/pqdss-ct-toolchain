// =============================================
// ==    Classification: TII CONFIDENTIAL     ==
// =============================================


#include "utils.h"



//int8_t utils_random_byte_array(uint8_t *a, int len){
//    int i;
//    time_t t;
//    /* Intializes random number generator */
//    srand((unsigned) time(&t));
//    /* Generate  len random numbers bytes (from 0 to 255) */
//    for( i = 0 ; i < len ; i++ ) {
//        a[i] = (rand())% 256 ;
//    }
//    return 0 ;
//}


// Generate a random byte a
//uint8_t utils_random_byte(){
//    time_t t;
//    uint8_t a ;
//    /* Intializes random number generator */
//    srand((unsigned) time(&t));
//    /* Generate a number  in the range 0 to 255 */
//    a = (rand())% 256 ;
//    return a ;
//}

// Input : byte arrays a and b
// Output: 0 or 1
// Return
//   0 if a = b
//   1 if a !=b


uint8_t nct_compare_two_byte_arrays(uint8_t *a, uint8_t *b, int len) {
    int i ;

    for (i=0; i<len; i++){
        if (a[i] != b[i]){
            return 1;
        }
    }
    return 0;
}

uint8_t ct_compare_two_byte_arrays(uint8_t *a, uint8_t *b, int len) {
    int i ;
    uint8_t r = 0 ;
    for (i=0; i<len; i++){
        r |=a[i] ^ b[i] ;
    }
    return (uint8_t)(-r)>>7;
}

// Reduce a given number to a desired range
// return
// value - bound   if value >= bound
// value  otherwise

int16_t utils_conditional_modular_subtraction(int16_t value, const int16_t bound){
    value -= bound;
    value += (value>>15) & bound;
    return value ;
}


int8_t ct_rejection_sampling(uint8_t *source, int source_len, uint16_t *secret, int bound ){
    uint16_t i, j, sel, d ;
    i =0 ;
    j = 0 ;
    while (j< source_len ){
        d = source[i] | (source[i+1]<<8) ;
        if(d < bound){
            sel = 1 ;
        }
        else {
            sel = 0 ;
        }
        secret[j] ^= (-sel) & (d^ secret[j]) ;
        j +=sel ;
        i +=2 ;
    }
    return 0 ;
}


int8_t nct_rejection_sampling(uint8_t *source, int source_len, uint16_t *secret, int bound ){
    uint16_t  d ;
    int i = 0 , j = 0;
    while ( j < source_len) {
    d = source[i] | (source[i+1]<<8);
    if ( d < bound )
        secret [j++] = d ;
    i += 2;
    }
    return 0 ;
}


