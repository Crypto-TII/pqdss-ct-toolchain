
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "params.h"

#include "ov_keypair.h"
#include "ov.h"
#include "blas.h"
#include "ov_blas.h"
#include "api.h"

// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES


//void get_expanded_sk(sk_t *sk_struct, uint8_t secret_key[SECRET_KEY_LENGTH]) {
//    sk_struct = (sk_t *)secret_key;
//}



void print_expanded_key(FILE *file, sk_t *sk_struct) {
    for (int i=0; i < LEN_SKSEED; i++){
        fprintf(file, "%02X", sk_struct->sk_seed[i]);
    }
    for (int i=0; i < (_V_BYTE * _O); i++){
        fprintf(file, "%02X", sk_struct->O[i]);
    }
}

void print_expanded_key1(FILE *file, uint8_t secret_key[SECRET_KEY_LENGTH]) {
    for (int i=0; i < SECRET_KEY_LENGTH; i++){
        fprintf(file, "%02X", secret_key[i]);
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
//        sk_t sk_struct = {0};
//        get_expanded_sk(&sk_struct, tp_buff);
        // Write to output file
        print_expanded_key(out_file, (sk_t *)tp_buff);
//        print_expanded_key(out_file, &sk_struct);
//        print_expanded_key(out_file, tp_buff);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
    return 0;
}


