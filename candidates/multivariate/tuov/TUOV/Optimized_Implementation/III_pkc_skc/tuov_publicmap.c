/** \file tuov_publicmap.c 
 *  \brief The implementations for tuov_publicmap() in tuov.h
*/



#include "tuov_keypair.h"
#include "tuov.h"
#include "tuov_blas.h"




#define _MAX_N 256

#if _PUB_N > _MAX_N
error. _PUB_N > _MAX_N
#endif



#if 16 == _GFSIZE
#if _PUB_M_BYTE > 32
error. _PUB_M_BYTE > 32
#endif
#define TMPVEC_LEN 32
#else   // 256 == _GFSIZE
#if _PUB_M_BYTE > 128
error. _PUB_M_BYTE > 128
#endif
#define TMPVEC_LEN 128
#endif



#if 16 == _GFSIZE



static
void accu_eval_quad_gf16( unsigned char *accu_res, const unsigned char *trimat, const unsigned char *x_in_byte,
                          unsigned num_gfele_x, unsigned num_vinegar, unsigned vec_len ) {
    const unsigned char *_x = x_in_byte;
    unsigned char _xixj[_MAX_N] = {0};
    unsigned v = num_vinegar;
    unsigned o = num_gfele_x - num_vinegar;

    // P1
    for (unsigned i = 0; i < v; i++) {
        #if defined( _BLAS_AVX2_ )
        unsigned i_start = i - (i & 31);
        #elif defined( _BLAS_SSE_ ) 
        unsigned i_start = i - (i & 15);
        #elif defined( _BLAS_UINT64_ )
        unsigned i_start = i - (i & 7);
        #else
        unsigned i_start = i - (i & 3);
        #endif
        if ( !_x[i] ) {
            trimat += vec_len * (v - i);
            continue;
        }
        for (unsigned j = i; j < v; j++) {
            _xixj[j] = _x[j];
        }
        gfv_mul_scalar( _xixj + i_start, _x[i], v - i_start );
        for (unsigned j = i; j < v; j++) {
            unsigned idx = _xixj[j];
            #if defined(_BLAS_AVX2_ ) 
            gf256v_add( accu_res + TMPVEC_LEN * idx, trimat, vec_len );
            #else
            if (idx) {
                gf256v_add( accu_res + TMPVEC_LEN * idx, trimat, vec_len );
            }
            #endif
            trimat += vec_len;
        }
    }
    // P2
    for (unsigned i = 0; i < v; i++) {
        if ( !_x[i] ) {
            trimat += vec_len * o;
            continue;
        }
        for (unsigned j = 0; j < o; j++) {
            _xixj[j] = _x[v + j];
        }
        gfv_mul_scalar( _xixj, _x[i], o );
        for (unsigned j = 0; j < o; j++) {
            unsigned idx = _xixj[j];
            #if defined(_BLAS_AVX2_ ) 
            gf256v_add( accu_res + TMPVEC_LEN * idx, trimat, vec_len );
            #else
            if (idx) {
                gf256v_add( accu_res + TMPVEC_LEN * idx, trimat, vec_len );
            }
            #endif
            trimat += vec_len;
        }
    }
    // P3
    for (unsigned i = 0; i < o; i++) {
        #if defined( _BLAS_AVX2_ )
        unsigned i_start = i - (i & 31);
        #elif defined( _BLAS_SSE_ ) 
        unsigned i_start = i - (i & 15);
        #elif defined( _BLAS_UINT64_ )
        unsigned i_start = i - (i & 7);
        #else
        unsigned i_start = i - (i & 3);
        #endif
        if ( !_x[v + i] ) {
            trimat += vec_len * (o - i);
            continue;
        }
        for (unsigned j = i; j < o; j++) {
            _xixj[j] = _x[v + j];
        }
        gfv_mul_scalar( _xixj + i_start, _x[v + i], o - i_start );
        for (unsigned j = i; j < o; j++) {
            unsigned idx = _xixj[j];
            #if defined(_BLAS_AVX2_ ) 
            gf256v_add( accu_res + TMPVEC_LEN * idx, trimat, vec_len );
            #else
            if (idx) {
                gf256v_add( accu_res + TMPVEC_LEN * idx, trimat, vec_len );
            }
            #endif
            trimat += vec_len;
        }
    }
}




static
void madd_reduce_gf16( unsigned char *y, const unsigned char *tmp_res, unsigned vec_len ) {
    unsigned char tmp[TMPVEC_LEN];
    int accu_bit = 1;

    gf256v_set_zero( y, vec_len );
    // x1
    for (int i = 1; i < _GFSIZE; i += 2) {
        gf256v_add( y, tmp_res + TMPVEC_LEN * i, vec_len );
    }
    // x2
    accu_bit = 1 << 1; // 2
    gf256v_set_zero( tmp, vec_len );
    for (int i = accu_bit; i < _GFSIZE; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_res + TMPVEC_LEN * (i + j), vec_len );
        }
    }
    gf16v_madd( y, tmp, accu_bit,  vec_len );

    // x4
    accu_bit = 1 << 2; // 4
    gf256v_set_zero( tmp, vec_len );
    for (int i = accu_bit; i < _GFSIZE; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_res + TMPVEC_LEN * (i + j), vec_len );
        }
    }
    gf16v_madd( y, tmp, accu_bit,  vec_len );

    // x8
    accu_bit = 1 << 3; // 8
    gf256v_set_zero( tmp, vec_len );
    for (int i = accu_bit; i < _GFSIZE; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_res + TMPVEC_LEN * (i + j), vec_len );
        }
    }
    gf16v_madd( y, tmp, accu_bit,  vec_len );
}


#endif  // #if 16 == _GFSIZE





#if 256 == _GFSIZE


#define UNROLL_4

#ifdef UNROLL_4


static
void accu_eval_quad_gf256( unsigned char *accu_low, unsigned char *accu_high, const unsigned char *trimat, const unsigned char *x_in_byte,
                           unsigned num_gfele_x, unsigned num_vinegar, unsigned vec_len ) {
    const unsigned char *_x = x_in_byte;
    unsigned char _xixj[_MAX_N];
    unsigned v = num_vinegar;
    unsigned o = num_gfele_x - num_vinegar;
    unsigned n = num_gfele_x;

    #if defined( _BLAS_AVX2_ )
    unsigned tmpvec_len = ((vec_len + 31) >> 5) << 5;
    #elif defined( _BLAS_SSE_ )
    unsigned tmpvec_len = ((vec_len + 15) >> 4) << 4;
    #elif defined( _BLAS_UINT64_ )
    unsigned tmpvec_len = ((vec_len + 7) >> 3) << 3;
    #else
    unsigned tmpvec_len = ((vec_len + 3) >> 2) << 2;
    #endif

    // P1
    for (unsigned i = 0; i < v; i++) {
        #if defined( _BLAS_AVX2_ )
        unsigned i_start = i - (i & 31);
        #elif defined( _BLAS_SSE_ )
        unsigned i_start = i - (i & 15);
        #elif defined( _BLAS_UINT64_ )
        unsigned i_start = i - (i & 7);
        #else
        unsigned i_start = i - (i & 3);
        #endif
        for (unsigned j = i; j < v; j++) {
            _xixj[j] = _x[j];
        }
        gfv_mul_scalar( _xixj + i_start, _x[i], v - i_start );
        unsigned j = i;
        for (; j + 3 < v; j += 4) {
            unsigned idx0 = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx0 & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx0 >> 4), trimat, tmpvec_len );

            unsigned idx1 = _xixj[j + 1];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx1 & 0xf), trimat + vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx1 >> 4), trimat + vec_len, tmpvec_len );

            unsigned idx2 = _xixj[j + 2];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx2 & 0xf), trimat + 2 * vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx2 >> 4), trimat + 2 * vec_len, tmpvec_len );

            unsigned idx3 = _xixj[j + 3];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx3 & 0xf), trimat + 3 * vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx3 >> 4), trimat + 3 * vec_len, tmpvec_len );
            trimat += vec_len * 4;
        }
        for (; j < v; j++) {
            unsigned idx = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high  + TMPVEC_LEN * (idx >> 4), trimat, tmpvec_len );
            trimat += vec_len;
        }
    }
    // P2
    for (unsigned i = 0; i < v; i++) {
        for (unsigned j = 0; j < o; j++) {
            _xixj[j] = _x[v + j];
        }
        gfv_mul_scalar( _xixj, _x[i], o );
        unsigned j = 0;
        for (; j + 3 < o; j += 4) {
            unsigned idx0 = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx0 & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx0 >> 4), trimat, tmpvec_len );

            unsigned idx1 = _xixj[j + 1];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx1 & 0xf), trimat + vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx1 >> 4), trimat + vec_len, tmpvec_len );

            unsigned idx2 = _xixj[j + 2];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx2 & 0xf), trimat + 2 * vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx2 >> 4), trimat + 2 * vec_len, tmpvec_len );

            unsigned idx3 = _xixj[j + 3];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx3 & 0xf), trimat + 3 * vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx3 >> 4), trimat + 3 * vec_len, tmpvec_len );
            trimat += vec_len * 4;
        }
        for (; j < o; j++) {
            unsigned idx = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high  + TMPVEC_LEN * (idx >> 4), trimat, tmpvec_len );
            trimat += vec_len;
        }
    }
    // P3
    for (unsigned i = v; i < n - 1; i++) {
        #if defined( _BLAS_AVX2_ )
        unsigned i_start = i - (i & 31);
        #elif defined( _BLAS_SSE_ )
        unsigned i_start = i - (i & 15);
        #elif defined( _BLAS_UINT64_ )
        unsigned i_start = i - (i & 7);
        #else
        unsigned i_start = i - (i & 3);
        #endif
        for (unsigned j = i; j < n; j++) {
            _xixj[j] = _x[j];
        }
        gfv_mul_scalar( _xixj + i_start, _x[i], n - i_start );
        unsigned j = i;
        for (; j + 3 < n; j += 4) {
            unsigned idx0 = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx0 & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx0 >> 4), trimat, tmpvec_len );

            unsigned idx1 = _xixj[j + 1];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx1 & 0xf), trimat + vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx1 >> 4), trimat + vec_len, tmpvec_len );

            unsigned idx2 = _xixj[j + 2];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx2 & 0xf), trimat + 2 * vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx2 >> 4), trimat + 2 * vec_len, tmpvec_len );

            unsigned idx3 = _xixj[j + 3];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx3 & 0xf), trimat + 3 * vec_len, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx3 >> 4), trimat + 3 * vec_len, tmpvec_len );
            trimat += vec_len * 4;
        }
        for (; j < n; j++) {
            unsigned idx = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high  + TMPVEC_LEN * (idx >> 4), trimat, tmpvec_len );
            trimat += vec_len;
        }
    }
    for (unsigned i = n - 1; i < n; i++) {
        #if defined( _BLAS_AVX2_ )
        unsigned i_start = i - (i & 31);
        #elif defined( _BLAS_SSE_ )
        unsigned i_start = i - (i & 15);
        #elif defined( _BLAS_UINT64_ )
        unsigned i_start = i - (i & 7);
        #else
        unsigned i_start = i - (i & 3);
        #endif
        for (unsigned j = i; j < n; j++) {
            _xixj[j] = _x[j];
        }
        gfv_mul_scalar( _xixj + i_start, _x[i], n - i_start );
        for (unsigned j = i; j < n; j++) {
            unsigned idx = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx & 0xf), trimat, vec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx >> 4), trimat, vec_len );
            trimat += vec_len;
        }
    }

}

#else

static
void accu_eval_quad_gf256( unsigned char *accu_low, unsigned char *accu_high, const unsigned char *trimat, const unsigned char *x_in_byte,
                           unsigned num_gfele_x, unsigned num_vinegar, unsigned vec_len ) {
    const unsigned char *_x = x_in_byte;
    unsigned char _xixj[_MAX_N];
    unsigned v = num_vinegar;
    unsigned o = num_gfele_x - num_vinegar;
    unsigned n = num_gfele_x;

    #if defined( _BLAS_AVX2_ )
    unsigned tmpvec_len = ((vec_len + 31) >> 5) << 5;
    #elif defined( _BLAS_SSE_ )
    unsigned tmpvec_len = ((vec_len + 15) >> 4) << 4;
    #elif defined( _BLAS_UINT64_ )
    unsigned tmpvec_len = ((vec_len + 7) >> 3) << 3;
    #else
    unsigned tmpvec_len = ((vec_len + 3) >> 2) << 2;
    #endif

    // P1
    for (unsigned i = 0; i < v; i++) {
        #if defined( _BLAS_AVX2_ )
        unsigned i_start = i - (i & 31);
        #elif defined( _BLAS_SSE_ )
        unsigned i_start = i - (i & 15);
        #elif defined( _BLAS_UINT64_ )
        unsigned i_start = i - (i & 7);
        #else
        unsigned i_start = i - (i & 3);
        #endif
        for (unsigned j = i; j < v; j++) {
            _xixj[j] = _x[j];
        }
        gfv_mul_scalar( _xixj + i_start, _x[i], v - i_start );
        for (unsigned j = i; j < v; j++) {
            unsigned idx = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx >> 4), trimat, tmpvec_len );
            trimat += vec_len;
        }
    }
    // P2
    for (unsigned i = 0; i < v; i++) {
        for (unsigned j = 0; j < o; j++) {
            _xixj[j] = _x[v + j];
        }
        gfv_mul_scalar( _xixj, _x[i], o );
        for (unsigned j = 0; j < o; j++) {
            unsigned idx = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx >> 4), trimat, tmpvec_len );
            trimat += vec_len;
        }
    }
    // P3
    for (unsigned i = v; i < n - 1; i++) {
        #if defined( _BLAS_AVX2_ )
        unsigned i_start = i - (i & 31);
        #elif defined( _BLAS_SSE_ ) 
        unsigned i_start = i - (i & 15);
        #elif defined( _BLAS_UINT64_ )
        unsigned i_start = i - (i & 7);
        #else
        unsigned i_start = i - (i & 3);
        #endif
        for (unsigned j = i; j < n; j++) {
            _xixj[j] = _x[j];
        }
        gfv_mul_scalar( _xixj + i_start, _x[i], n - i_start );
        for (unsigned j = i; j < n; j++) {
            unsigned idx = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx & 0xf), trimat, tmpvec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx >> 4), trimat, tmpvec_len );
            trimat += vec_len;
        }
    }

    for (unsigned i = n - 1; i < n; i++) {
        #if defined( _BLAS_AVX2_ )
        unsigned i_start = i - (i & 31);
        #elif defined( _BLAS_SSE_ )
        unsigned i_start = i - (i & 15);
        #elif defined( _BLAS_UINT64_ )
        unsigned i_start = i - (i & 7);
        #else
        unsigned i_start = i - (i & 3);
        #endif
        for (unsigned j = i; j < n; j++) {
            _xixj[j] = _x[j];
        }
        gfv_mul_scalar( _xixj + i_start, _x[i], n - i_start );
        for (unsigned j = i; j < n; j++) {
            unsigned idx = _xixj[j];
            gf256v_add( accu_low  + TMPVEC_LEN * (idx & 0xf), trimat, vec_len );
            gf256v_add( accu_high + TMPVEC_LEN * (idx >> 4), trimat, vec_len );
            trimat += vec_len;
        }
    }
}

#endif

#undef UNROLL_4


static
void madd_reduce_gf256( unsigned char *y, const unsigned char *tmp_low, const unsigned char *tmp_high, unsigned vec_len ) {
    unsigned char tmp[TMPVEC_LEN];

    int accu_bit = 1;

    #if defined( _BLAS_AVX2_ )
    unsigned tmpvec_len = ((vec_len + 31) >> 5) << 5;
    #elif defined( _BLAS_SSE_ )
    unsigned tmpvec_len = ((vec_len + 15) >> 4) << 4;
    #elif defined( _BLAS_UINT64_ )
    unsigned tmpvec_len = ((vec_len + 7) >> 3) << 3;
    #else
    unsigned tmpvec_len = ((vec_len + 3) >> 2) << 2;
    #endif
    unsigned char tmp_y[TMPVEC_LEN * 4];

    gf256v_set_zero( tmp_y, tmpvec_len );
    // x1
    for (int i = 1; i < 16; i += 2) {
        gf256v_add( tmp_y, tmp_low + TMPVEC_LEN * i, tmpvec_len );
    }
    // x2
    accu_bit = 1 << 1; // 2
    gf256v_set_zero( tmp, tmpvec_len );
    for (int i = accu_bit; i < 16; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_low + TMPVEC_LEN * (i + j), tmpvec_len );
        }
    }
    gf256v_madd( tmp_y, tmp, accu_bit, tmpvec_len );

    // x4
    accu_bit = 1 << 2; // 4
    gf256v_set_zero( tmp, tmpvec_len );
    for (int i = accu_bit; i < 16; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_low + TMPVEC_LEN * (i + j), tmpvec_len );
        }
    }
    gf256v_madd( tmp_y, tmp, accu_bit, tmpvec_len );

    // x8
    accu_bit = 1 << 3; // 8
    gf256v_set_zero( tmp, tmpvec_len );
    for (int i = accu_bit; i < 16; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_low + TMPVEC_LEN * (i + j), tmpvec_len );
        }
    }
    gf256v_madd( tmp_y, tmp, accu_bit, tmpvec_len );

/////

    accu_bit = 1; // 16
    gf256v_set_zero( tmp, tmpvec_len );
    for (int i = 1; i < 16; i += 2) {
        gf256v_add( tmp, tmp_high + TMPVEC_LEN * (i), tmpvec_len );
    }
    gf256v_madd( tmp_y, tmp, accu_bit << 4, tmpvec_len );

    accu_bit = 1 << 1; // 32
    gf256v_set_zero( tmp, tmpvec_len );
    for (int i = accu_bit; i < 16; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_high + TMPVEC_LEN * (i + j), tmpvec_len );
        }
    }
    gf256v_madd( tmp_y, tmp, accu_bit << 4, tmpvec_len );

    accu_bit = 1 << 2; // 64
    gf256v_set_zero( tmp, tmpvec_len );
    for (int i = accu_bit; i < 16; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_high + TMPVEC_LEN * (i + j), tmpvec_len );
        }
    }
    gf256v_madd( tmp_y, tmp, accu_bit << 4, tmpvec_len );

    accu_bit = 1 << 3; // 128
    gf256v_set_zero( tmp, tmpvec_len );
    for (int i = accu_bit; i < 16; i += accu_bit * 2) {
        for (int j = 0; j < accu_bit; j++) {
            gf256v_add( tmp, tmp_high + TMPVEC_LEN * (i + j), tmpvec_len );
        }
    }
    gf256v_madd( tmp_y, tmp, accu_bit << 4, tmpvec_len );

    memcpy( y, tmp_y, vec_len );
}




#endif  // #if 256 == _GFSIZE



void tuov_publicmap( unsigned char *y, const unsigned char *trimat, const unsigned char *x ) {
    unsigned char _x[_MAX_N];
    for (unsigned i = 0; i < _PUB_N; i++) {
        _x[i] = gfv_get_ele( x, i );
    }

    #if 16 == _GFSIZE

    unsigned char tmp[TMPVEC_LEN * _GFSIZE] = {0};
    accu_eval_quad_gf16( tmp, trimat, _x, _PUB_N, _V, _PUB_M_BYTE );
    madd_reduce_gf16( y, tmp, _PUB_M_BYTE );

    #elif 256 == _GFSIZE

    unsigned char tmp_l[TMPVEC_LEN * 16] = {0};
    unsigned char tmp_h[TMPVEC_LEN * 16] = {0};
    accu_eval_quad_gf256( tmp_l, tmp_h, trimat, _x, _PUB_N, _V, _PUB_M_BYTE );
    madd_reduce_gf256( y, tmp_l, tmp_h, _PUB_M_BYTE );

    #else
error message:
    unsupported _GFSIZE
    #endif
}