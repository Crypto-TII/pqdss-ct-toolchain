
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "data_structures.h"
#include "parameters.h"
#include "api.h"
#include "parsing.h"



void get_expanded_sk(perm_t p, const uint8_t secret_key[SEED_BYTES]) {
    sig_perk_perm_set_random(p, secret_key);
}

// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES

void print_permutation(FILE *file, perm_t p) {
    for (int i=0; i<PARAM_N1-1; i++){
        fprintf(file, "%02X ", p[i]);
    }
    fprintf(file, "%02X", p[PARAM_N1-1]);
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

    char line[2* (CRYPTO_SECRETKEYBYTES+2)];
    uint8_t tp_buff[SECRET_KEY_LENGTH];

    perk_private_key_t private_key = {0};

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
        sig_perk_private_key_from_bytes(&private_key, tp_buff);
        get_expanded_sk(private_key.pi,tp_buff);
        // Write to output file
        fprintf(out_file, "pi;");
        print_permutation(out_file, private_key.pi);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
    return 0;
}


