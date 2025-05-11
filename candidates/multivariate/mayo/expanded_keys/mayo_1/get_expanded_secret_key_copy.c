
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdalign.h>
#include "mayo.h"
#include "api.h"


//#define MAYO_PARAMS &MAYO_1
#define MAYO_PARAMS 0


void get_expanded_sk(mayo_params_t *p, unsigned char *csk, sk_t secret_key) {
    mayo_expand_sk(p, csk, &secret_key);
}

// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES

void print_csk_sk_t(FILE *file, mayo_params_t *p, const unsigned char *csk, sk_t secret_key) {
    for (int i=0; i<PARAM_csk_bytes(p); i++){
        fprintf(file, "%02X", csk[i]);
    }
    for (int i=0; i<PARAM_P1_limbs(p) + PARAM_P2_limbs(p); i++){
        fprintf(file, "%016lX", secret_key.p[i]);
    }
    for (int i=0; i<PARAM_o(p) + PARAM_v(p); i++){
        fprintf(file, "%02X", secret_key.O[i]);
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


//    alignas(32) sk_t sk = {0};

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
        unsigned char *csk = (unsigned char *)tp_buff;
//        alignas(32) sk_t  secret_key = {0};
        alignas(32) sk_t  secret_key;
//        sk_t  secret_key = {0};
        get_expanded_sk(MAYO_PARAMS, tp_buff, secret_key);
        // Write to output file
        print_csk_sk_t(out_file, MAYO_PARAMS, csk, secret_key);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
//    unsigned char sm[4 + CRYPTO_BYTES] = {0};
//    size_t smlen = 4 + CRYPTO_BYTES;
//    const unsigned char m[4] = {0x01, 0x02, 0x03, 0x04};
//    size_t mlen = 4;
//    unsigned char sk[CRYPTO_SECRETKEYBYTES] = {0x73, 0xE8, 0x79, 0x50, 0xDA, 0x8F, 0x2C, 0xC9, 0x4E, 0x3A, 0xE3, 0xCC, 0xBE, 0x3B, 0x0D, 0xC2, 0xF4, 0x6B, 0x21, 0xE6, 0x52, 0x2C, 0x7F, 0x01};
//    crypto_sign(sm, &smlen, m, mlen, sk);
    return 0;
}


