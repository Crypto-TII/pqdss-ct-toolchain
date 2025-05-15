
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "CROSS.h"
#include "csprng_hash.h"
#include "fp_arith.h"
#include "merkle_tree.h"
#include "api.h"

// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES


void get_expanded_sk(FZ_ELEM e_bar[N], uint8_t secret_key[SECRET_KEY_LENGTH]) {
    FP_ELEM V_tr[K][N-K];
    sk_t *sk_struct = (sk_t *)secret_key;
#if defined(RSDP)
    expand_sk(e_bar, V_tr, sk_struct->seed_sk);
#elif defined(RSDPG)
    FZ_ELEM e_G_bar[M];
    FZ_ELEM W_mat[M][N-M];
    expand_sk(e_bar, e_G_bar, V_tr, W_mat, sk_struct->seed_sk);
#endif
}



void print_expanded_key(FILE *file, FZ_ELEM e_bar[N]) {
    for (int i=0; i < NUM_KEYPAIRS - 1; i++){
        fprintf(file, "%02X", e_bar[j]);
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
        FZ_ELEM e_bar[N];
        get_expanded_sk(FZ_ELEM e_bar,tp_buff);
        // Write to output file
        print_expanded_key(out_file, e_bar);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
    return 0;
}


