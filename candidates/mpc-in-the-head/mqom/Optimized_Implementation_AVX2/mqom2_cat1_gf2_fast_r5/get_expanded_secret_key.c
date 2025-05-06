
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "mqom2_parameters.h"
#include "api.h"
#include "fields.h"


// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES


void get_expanded_sk(field_base_elt x[FIELD_BASE_PACKING(MQOM2_PARAM_MQ_N)], uint8_t secret_key[CRYPTO_SECRETKEYBYTES]) {
    field_base_parse(&secret_key[(2 * MQOM2_PARAM_SEED_SIZE) + BYTE_SIZE_FIELD_BASE(MQOM2_PARAM_MQ_M)], MQOM2_PARAM_MQ_N, x);
}


void print_vec(FILE *file, field_base_elt x[FIELD_BASE_PACKING(MQOM2_PARAM_MQ_N)]) {
    for (int i=0; i<FIELD_BASE_PACKING(MQOM2_PARAM_MQ_N); i++){
        fprintf(file, "%02X", x[i]);
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
    uint8_t tp_buff[SECRET_KEY_LENGTH] = {0};

    field_base_elt x[FIELD_BASE_PACKING(MQOM2_PARAM_MQ_N)] = {0};

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
        get_expanded_sk(x,tp_buff);
        // Write to output file
//        fprintf(out_file, "x;");
        print_vec(out_file, x);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
    return 0;
}


