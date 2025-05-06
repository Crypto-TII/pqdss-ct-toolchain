
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <ctype.h>
//#include "randombytes.h"
//#include "hash_fips202.h"
#include "parameters.h"
#include "parsing.h"
#include "tcith.h"
#include "ggm_tree.h"
#include "signature.h"
//#include "rng.h"
#include "api.h"
//
//
//#define	MAX_MARKER_LEN		50
//
//#define KAT_SUCCESS          0
//#define KAT_FILE_OPEN_ERROR -1
//#define KAT_DATA_ERROR      -3
//#define KAT_CRYPTO_FAILURE  -4
//
//
//int
//FindMarker(FILE *infile, const char *marker)
//{
//    char	line[MAX_MARKER_LEN];
//    int		i, len;
//    int curr_line;
//
//    len = (int)strlen(marker);
//    if ( len > MAX_MARKER_LEN-1 )
//        len = MAX_MARKER_LEN-1;
//
//    for ( i=0; i<len; i++ )
//    {
//        curr_line = fgetc(infile);
//        line[i] = curr_line;
//        if (curr_line == EOF )
//            return 0;
//    }
//    line[len] = '\0';
//
//    while ( 1 ) {
//        if ( !strncmp(line, marker, len) )
//            return 1;
//
//        for ( i=0; i<len-1; i++ )
//            line[i] = line[i+1];
//        curr_line = fgetc(infile);
//        line[len-1] = curr_line;
//        if (curr_line == EOF )
//            return 0;
//        line[len] = '\0';
//    }
//
//    // shouldn't get here
//    return 0;
//}
//
//int ReadHex(FILE *infile, unsigned char *A, int Length, char *str)
//{
//    int			i, ch, started;
//    unsigned char	ich;
//
//    if ( Length == 0 ) {
//        A[0] = 0x00;
//        return 1;
//    }
//    memset(A, 0x00, Length);
//    started = 0;
//    if ( FindMarker(infile, str) )
//        while ( (ch = fgetc(infile)) != EOF ) {
//            if ( !isxdigit(ch) ) {
//                if ( !started ) {
//                    if ( ch == '\n' )
//                        break;
//                    else
//                        continue;
//                }
//                else
//                    break;
//            }
//            started = 1;
//            if ( (ch >= '0') && (ch <= '9') )
//                ich = ch - '0';
//            else if ( (ch >= 'A') && (ch <= 'F') )
//                ich = ch - 'A' + 10;
//            else if ( (ch >= 'a') && (ch <= 'f') )
//                ich = ch - 'a' + 10;
//            else // shouldn't ever get here
//                ich = 0;
//
//            for ( i=0; i<Length-1; i++ )
//                A[i] = (A[i] << 4) | (A[i+1] >> 4);
//            A[Length-1] = (A[Length-1] << 4) | ich;
//        }
//    else
//        return 0;
//
//    return 1;
//}
//
//
////void get_expanded_sk(uint8_t *secret_key) {
////    rbc_53_mat H;
////    rbc_53_vec s, y;
////    rbc_53_mat_fq C;
////    ryde_1f_secret_key_from_string(y, H, s, C, secret_key);
////}
//


#define RBC_VEC_SIZE RYDE_1F_PARAM_R  // Number of elements in the vector
#define RBC_MAT_COLS  (RYDE_1F_PARAM_N - RYDE_1F_PARAM_R)
#define RBC_MAT_ROWS  RYDE_1F_PARAM_R


void get_expanded_sk(uint8_t *secret_key, rbc_53_mat H, rbc_53_vec s, rbc_53_vec y, rbc_53_mat_fq C) {
//    rbc_53_field_init();
    ryde_1f_secret_key_from_string(y, H, s, C, secret_key);
}
//
//
//void set_expanded_secret_keys(const char *keys_file){
//    FILE *sk_keys_file = fopen(keys_file, "r");
//    if ( sk_keys_file == NULL ) {
//        printf("Couldn't open <%s> for write\n", keys_file);
//    }
//    uint8_t sk[CRYPTO_SECRETKEYBYTES] = {0};
//    rbc_53_mat H;
//    rbc_53_vec s;
//    rbc_53_vec y;
//    rbc_53_mat_fq C;
//    // Initialize variables related to secret key and public key
//    rbc_53_mat_init(&H, RYDE_1F_PARAM_N - RYDE_1F_PARAM_K, RYDE_1F_PARAM_K);
//    rbc_53_vec_init(&y, RYDE_1F_PARAM_N - RYDE_1F_PARAM_K);
//    rbc_53_vec_init(&s, RYDE_1F_PARAM_R);
//    rbc_53_mat_fq_init(&C, RYDE_1F_PARAM_R, RYDE_1F_PARAM_N - RYDE_1F_PARAM_R);
//    unsigned char sk_hex[2*CRYPTO_SECRETKEYBYTES+10] = {0};
//    for (int i=0; i<10; i++){
//        ReadHex(sk_keys_file, sk_hex, 2*CRYPTO_SECRETKEYBYTES+10, "sk=");
//        printf("sk_hex = %s\n", sk_hex);
//        get_expanded_sk(sk, H, s, y, C);
//    }
//    fclose(sk_keys_file);
//}
//
////void set_expanded_secret_keys(const char *filename) {
////    printf("\n=========LORD JESUS CHRIST\n");
////    printf("\nFile name: %s\n", filename);
////}
//
//
//int main(){
//    const char *sk_filename = "/Users/gilbertndollanedione/Desktop/pqdss-signature/pqdss-ct-toolchain/candidates/mpc-in-the-head/ryde/dudect/ryde1f/ryde_sign/keys.txt";
////    set_expanded_secret_keys(sk_filename);
//    FILE *file = fopen("keys.txt", "r");
//    if (file == NULL){
//        printf("\nNOT OPEN:=======\n");
//    }
////    set_expanded_secret_keys("keys.txt");
//    char sk_hex[CRYPTO_SECRETKEYBYTES] = {0};
//    ReadHex(file, (unsigned  char *)sk_hex, CRYPTO_SECRETKEYBYTES, "sk=");
////            FILE *fptr; = fopen("file.txt", "r");
//
//    for (int i=0; i<CRYPTO_SECRETKEYBYTES; i++) {
//        printf("%2x ", sk_hex[i]);
//    }
//    printf("%s\n", sk_hex);
//
//    // Buffer to store 50 characters at a time
////    char buff[CRYPTO_SECRETKEYBYTES];
////
////    // Reading strings till fgets returns NULL
////    while (fgets(buff, CRYPTO_SECRETKEYBYTES, file)) {
////        printf("%s", buff);
////    };
//
////    fclose(fptr);
//    fclose(file);
//    return 0;
//}


// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES  // 32 bytes = 64 hex characters

// Replace with actual types for your implementation
//typedef struct { /* ... */ } rbc_53_mat;
//typedef struct { /* ... */ } rbc_53_vec;
//typedef struct { /* ... */ } rbc_53_mat_fq;

// Assume these functions/definitions are available
//void get_expanded_sk(uint8_t *secret_key, rbc_53_mat H, rbc_53_vec s, rbc_53_vec y, rbc_53_mat_fq C);
//void print_vec(FILE *f, rbc_53_vec vec);
//void print_mat(FILE *f, rbc_53_mat mat);
//void print_mat_fq(FILE *f, rbc_53_mat_fq mat_fq);

void print_vec(FILE *f, rbc_53_vec vec) {
    for (int i = 0; i < RBC_VEC_SIZE; i++) {
        for (int j = 0; j < RBC_53_ELT_SIZE; j++) {
            fprintf(f, "%016lX", vec[i][j]);
        }
        if (i < RBC_VEC_SIZE - 1)
            fprintf(f, " ");
    }
}

void print_mat(FILE *f, rbc_53_mat mat) {
    for (int i = 0; i < RBC_MAT_ROWS; i++) {
        for (int j = 0; j < RBC_53_ELT_SIZE; j++) {
            fprintf(f, "%016lX", mat[i][j]);
        }
        if (i < RBC_MAT_ROWS - 1)
            fprintf(f, " ");
    }
}

void print_mat_fq(FILE *f, rbc_53_mat_fq mat_fq) {
    for (int i = 0; i < RBC_MAT_ROWS; i++) {
        for (int j = 0; j < RBC_MAT_COLS; j++) {
            fprintf(f, "%016lX", mat_fq[i][j]);
            if (j < RBC_MAT_COLS - 1)
                fprintf(f, ",");
        }
        if (i < RBC_MAT_ROWS - 1)
            fprintf(f, " ");
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
    FILE *key_file = fopen("src/keys.txt", "r");
    if (!key_file) {
        perror("Failed to open keys.txt");
        return;
    }

    FILE *out_file = fopen("src/expanded_secrets.txt", "a");
    if (!out_file) {
        perror("Failed to open expanded_secrets.txt");
        fclose(key_file);
        return;
    }

//    char line[256];
    char line[2* (CRYPTO_SECRETKEYBYTES+2)];
    uint8_t tp_buff[SECRET_KEY_LENGTH];

    rbc_53_field_init();
    // Replace these with actual memory allocation or declarations as needed
    rbc_53_mat H;
    rbc_53_vec s, y;
    rbc_53_mat_fq C;

    //  Initialize variables related to secret key and public key
    rbc_53_mat_init(&H, RYDE_1F_PARAM_N - RYDE_1F_PARAM_K, RYDE_1F_PARAM_K);
    rbc_53_vec_init(&y, RYDE_1F_PARAM_N - RYDE_1F_PARAM_K);
    rbc_53_vec_init(&s, RYDE_1F_PARAM_R);
    rbc_53_mat_fq_init(&C, RYDE_1F_PARAM_R, RYDE_1F_PARAM_N - RYDE_1F_PARAM_R);

    while (fgets(line, sizeof(line), key_file)) {
        // Remove newline and leading 'sk=' if present
        char *key_start = strstr(line, "sk=");
        if (!key_start) continue;
        key_start += 3;
        printf("\n---line: %s\n", line);
        char *newline = strchr(key_start, '\n');
        if (newline) *newline = '\0';

        // Convert hex to bytes
        if (hexstr_to_bytes(key_start, tp_buff, SECRET_KEY_LENGTH) != 0) {
            fprintf(stderr, "Failed to parse key: %s\n", key_start);
            continue;
        }
        for (int i = 0; i< SECRET_KEY_LENGTH; i++){
            printf("%2x ", tp_buff[i]);
        }
        printf("\n");
        // Get expanded secret
        get_expanded_sk(tp_buff, H, s, y, C);

        // Write to output file
        fprintf(out_file, "s;");
//        print_vec(out_file, y);
//        fprintf(out_file, " ");
//        print_mat(out_file, H);
//        fprintf(out_file, " ");
        print_vec(out_file, s);
        fprintf(out_file, " \n");
        fprintf(out_file, "C;");
        print_mat_fq(out_file, C);
        fprintf(out_file, "\n");
    }

    fclose(key_file);
    fclose(out_file);
}


int main(){
//    const char *sk_filename = "/Users/gilbertndollanedione/Desktop/pqdss-signature/pqdss-ct-toolchain/candidates/mpc-in-the-head/ryde/dudect/ryde1f/ryde_sign/keys.txt";
////    set_expanded_secret_keys(sk_filename);
//    FILE *file = fopen("keys.txt", "r");
//    if (file == NULL){
//        printf("\nNOT OPEN:=======\n");
//    }
////    set_expanded_secret_keys("keys.txt");
//    char sk_hex[CRYPTO_SECRETKEYBYTES] = {0};
//    ReadHex(file, (unsigned  char *)sk_hex, CRYPTO_SECRETKEYBYTES, "sk=");
////            FILE *fptr; = fopen("file.txt", "r");
//
//    for (int i=0; i<CRYPTO_SECRETKEYBYTES; i++) {
//        printf("%2x ", sk_hex[i]);
//    }
//    printf("%s\n", sk_hex);
//
//
//    fclose(file);
    create_expanded_secrets();
    unsigned long long mlen = 4;
    unsigned char sm[4 + CRYPTO_BYTES] = {0};
    unsigned long long smlen = 0;
    const unsigned char m[4] = {0x01, 0x01, 0x01, 0x01};
    const unsigned char sk[CRYPTO_SECRETKEYBYTES] = {0x53,0x0f, 0x8a, 0xfb, 0xc7, 0x45, 0x36, 0xb9, 0xa9, 0x63, 0xb4, 0xf1, 0xc4, 0xcb, 0x73, 0x8b, 0xdb, 0xcf, 0xe7, 0x68, 0x69, 0x1b, 0x5c, 0x5f, 0xec, 0x84, 0xa8, 0xd1, 0x25, 0xcb, 0x74, 0xed};
    int res = crypto_sign(sm, &smlen, m, mlen, sk);
    printf("\n------res = %d\n", res);
    return 0;
}
