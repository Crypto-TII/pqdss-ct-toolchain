
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "qruov.h"
#include "api.h"
#include "post_sample.h"

// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES

static inline void save64(const uint64_t s, uint8_t dst[8]) {
    uint8_t * src = (uint8_t *) &s ;
    dst[ 0] = src[ 7] ;
    dst[ 1] = src[ 6] ;
    dst[ 2] = src[ 5] ;
    dst[ 3] = src[ 4] ;
    dst[ 4] = src[ 3] ;
    dst[ 5] = src[ 2] ;
    dst[ 6] = src[ 1] ;
    dst[ 7] = src[ 0] ;
}

static void ExpandMatrixVxM (
        uint8_t *  src, // input src[L*V*M]
        MATRIX_VxM   A  // output
) {
    uint8_t * s = src ;
    for(int i=0;i<QRUOV_V;i++){
        for(int j=0;j<QRUOV_M;j++){
            for(int k=0;k<QRUOV_L;k++){
                A[i][k][j] = *s++ ;
            }
        }
        VECTOR_M_CLEAR_TAIL(A[i]) ;
    }
}

/* ---------------------------------------------------------
   random sampling
   --------------------------------------------------------- */

static inline void rejsamp_and_q (
        const unsigned int tau,
        uint8_t * dst
){
    for(int i=0; i<tau; i++){ dst[i] &= QRUOV_q ; }
}

static inline void rejsamp_rejection_with_aux(
        const unsigned int length,
        const uint8_t *    aux,
        uint8_t *    dst
){
    while(*aux==QRUOV_q)aux++ ;
    for(int i=0; i<length; i++){
        if(*dst==QRUOV_q){
            *dst = *aux++ ;
            while(*aux==QRUOV_q)aux++ ;
        }
        *dst++ ;
    }
}

static inline void RejSamp(
        const unsigned int length,
        const unsigned int tau,    // tau = tau(length) > length
        uint8_t *    dst     // dst[tau]
){
    rejsamp_and_q (tau, dst) ;
    rejsamp_rejection_with_aux (length, dst+length, dst) ;
}


/* -----------------------------------------------------
  PRG
   ----------------------------------------------------- */

static EVP_CIPHER_CTX * PRG_init_aes_ctr(const uint8_t seed[QRUOV_SEED_LEN]){
    EVP_CIPHER_CTX * ctx = EVP_CIPHER_CTX_new() ;
    EVP_EncryptInit_ex(ctx, EVP_AES_CTR(), NULL, seed, NULL) ;
    return ctx ;
}
static void PRG_yield_aes_ctr(EVP_CIPHER_CTX * ctx, int length, uint8_t * dst){
    int out_len ;
    memset(dst, 0, length) ;
    EVP_EncryptUpdate(ctx, dst, &out_len, dst, length) ;
}
static void PRG_final_aes_ctr(EVP_CIPHER_CTX * ctx){ EVP_CIPHER_CTX_free(ctx) ; }
static EVP_CIPHER_CTX * PRG_copy_aes_ctr(EVP_CIPHER_CTX * src){
    EVP_CIPHER_CTX * dst = EVP_CIPHER_CTX_new() ;
    EVP_CIPHER_CTX_copy(dst, src) ;
    return dst ;
}

static EVP_MD_CTX * PRG_init_shake(const uint8_t seed[QRUOV_SEED_LEN]){
    EVP_MD_CTX * ctx = EVP_MD_CTX_new() ;
    EVP_DigestInit_ex(ctx, EVP_SHAKE(), NULL) ;
    EVP_DigestUpdate(ctx, seed, QRUOV_SEED_LEN) ;
    return ctx ;
}
/* PRG_yield_shake() may be called just once in openssl 1.x */
static void PRG_yield_shake(EVP_MD_CTX * ctx, int length, uint8_t * dst){ EVP_DigestFinalXOF(ctx, dst, length) ; }
static void PRG_final_shake(EVP_MD_CTX * ctx){ EVP_MD_CTX_free(ctx) ; }
static EVP_MD_CTX * PRG_copy_shake(EVP_MD_CTX * src){
    EVP_MD_CTX * dst = EVP_MD_CTX_new() ;
    EVP_MD_CTX_copy(dst, src) ;
    return dst ;
}

static MGF_CTX_s * PRG_init_mgf(const uint8_t seed[QRUOV_SEED_LEN]){ return MGF_init(seed, QRUOV_SEED_LEN, malloc(sizeof(MGF_CTX))) ; }
static void PRG_yield_mgf(MGF_CTX_s * ctx, int length, uint8_t * dst){ MGF_yield (ctx, dst, length) ; }
static void PRG_final_mgf(MGF_CTX_s * ctx){ MGF_final(ctx) ; free(ctx) ; }
static MGF_CTX_s * PRG_copy_mgf(MGF_CTX_s * src){
    MGF_CTX_s * dst = malloc(sizeof(MGF_CTX)) ;
    MGF_CTX_copy(src, dst) ;
    return dst ;
}

static inline void RejSampPRG_aes_ctr(
        EVP_CIPHER_CTX *   ctx,
        const uint64_t     index,
        const unsigned int length,
        const unsigned int tau,    // tau = tau(length) > length
        uint8_t *    dst     // dst[tau]
){
    int out_len ;
    uint8_t iv[16] = {0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0} ;
    save64(index, iv) ;
    EVP_EncryptInit_ex(ctx, NULL, NULL, NULL, iv) ;
    memset(dst, 0, tau) ;
    EVP_EncryptUpdate(ctx, dst, &out_len, dst, tau) ;
    RejSamp(length, tau, dst) ;
}

static inline void RejSampPRG_shake(
        EVP_MD_CTX *       ctx,
        const uint64_t     index,
        const unsigned int length,
        const unsigned int tau,    // tau = tau(length) > length
        uint8_t *    dst     // dst[tau]
){
    uint8_t iv[2] ;
    save16((uint16_t)index, iv) ;
    EVP_DigestUpdate(ctx, iv, 2) ;
    EVP_DigestFinalXOF(ctx, dst, tau) ;
    RejSamp(length, tau, dst) ;
}

/* -------------------------------------------
  Expand_mu(), Hash() -> shake256 only
   ------------------------------------------- */


static void copy_Expand_sk(
        const QRUOV_SEED seed_sk,  // input
        MATRIX_VxM Sd,             // output
        MATRIX_MxV SdT
){
    const int n2 = QRUOV_L * QRUOV_V * QRUOV_M ;
    uint8_t   r2[QRUOV_tau2] ;
    QRUOV_PRG_CTX * ctx = PRG_init(seed_sk) ;
    RejSampPRG(ctx, 0, n2, QRUOV_tau2, r2) ;
    ExpandMatrixVxM(r2, Sd) ;
    MATRIX_TRANSPOSE_VxM(Sd, SdT) ;

    PRG_final(ctx) ;
    OPENSSL_cleanse(r2, QRUOV_tau2) ;
}

inline static void copy_restore_QRUOV_SEED (const uint8_t * pool, size_t * pool_bits, QRUOV_SEED seed) {
    size_t index = (*pool_bits >> 3) ;
    memcpy(seed, pool+index, QRUOV_SEED_LEN) ;
    *pool_bits += (QRUOV_SEED_LEN<<3) ;
}


void get_expanded_sk(MATRIX_VxM Sd, MATRIX_MxV SdT, uint8_t secret_key[SECRET_KEY_LENGTH]) {
    QRUOV_SEED seed_sk;
    size_t sk_pool_bits = 0;
    copy_restore_QRUOV_SEED(secret_key, &sk_pool_bits, seed_sk) ;
    copy_Expand_sk(seed_sk, Sd, SdT);
}


void print_sd(FILE *file, MATRIX_VxM Sd) {
    for(int i=0;i<QRUOV_V;i++){
        for(int j=0;j<QRUOV_M;j++){
            for(int k=0;k<QRUOV_L;k++){
                fprintf(file, "%02X", Sd[i][k][j]);
            }
        }
    }
}


// Converts hex string to byte array
int hexstr_to_bytes(const char *hexstr, uint8_t *buffer, size_t bufsize) {
    size_t len = strlen(hexstr);
    if (len % 2 != 0 || bufsize < len / 2) return -1;
    for (size_t i = 0; i < len / 2; i++) {
        sscanf(hexstr + 2 * i, "%2hhx", &buffer[i]);
    }
    return 0;
}

void create_expanded_secrets() {
    FILE *key_file = fopen("keys.txt", "r");
    if (!key_file) {
        perror("Failed to open keys.txt");
        return;
    }

    FILE *out_file = fopen("expanded_secrets.txt", "a");
    if (!out_file) {
        perror("Failed to open expanded_secrets.txt");
        fclose(key_file);
        return;
    }

    char line[2* (CRYPTO_SECRETKEYBYTES+2)];
    uint8_t tp_buff[SECRET_KEY_LENGTH];


    while (fgets(line, sizeof(line), key_file)) {
        // Remove newline and leading 'sk=' if present
        char *key_start = strstr(line, "sk=");
        if (!key_start){
            continue;
        }
        key_start += 3;
        char *newline = strchr(key_start, '\n');
        if (newline){
            *newline = '\0';
        }

        // Convert hex to bytes
        if (hexstr_to_bytes(key_start, tp_buff, SECRET_KEY_LENGTH) != 0) {
            fprintf(stderr, "Failed to parse key: %s\n", key_start);
            continue;
        }
        // Get expanded secret
        // const uint8_t secret_key[SEED_BYTES]
        MATRIX_VxM Sd;
        MATRIX_MxV SdT;
        get_expanded_sk(Sd, SdT, tp_buff);
        // Write to output file
        print_sd(out_file, Sd);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
    return 0;
}


