
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "mirath_matrix_ff.h"
#include "mirath_parsing.h"
#include "mirath_ggm_tree.h"
#include "mirath_tcith.h"
#include "api.h"
#include "mirath_parameters.h"


// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES


void get_expanded_sk(ff_t S[MIRATH_VAR_FF_S_BYTES], ff_t C[MIRATH_VAR_FF_C_BYTES], const uint8_t *secret_key) {
    seed_t seed_sk = {0};
    memcpy(seed_sk, secret_key, MIRATH_SECURITY_BYTES);
    mirath_matrix_expand_seed_secret_matrix(S, C, seed_sk);
}


void print_s_and_p(FILE *file, ff_t S[MIRATH_VAR_FF_S_BYTES], ff_t C[MIRATH_VAR_FF_C_BYTES]) {
    // print S
    for (int i=0; i<MIRATH_VAR_FF_S_BYTES; i++){
        fprintf(file, "%02X", S[i]);
    }
    // print C
    for (int i=0; i<MIRATH_VAR_FF_C_BYTES; i++){
        fprintf(file, "%02X", C[i]);
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
        ff_t S[MIRATH_VAR_FF_S_BYTES] = {0};
        ff_t C[MIRATH_VAR_FF_C_BYTES] = {0};
        get_expanded_sk(S, C, tp_buff);
        // Write to output file
        print_s_and_p(out_file, S, C);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
    return 0;
}


