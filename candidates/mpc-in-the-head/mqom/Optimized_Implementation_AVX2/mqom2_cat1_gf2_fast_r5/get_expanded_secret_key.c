
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
    for (int i=0; i<FIELD_BASE_PACKING(MQOM2_PARAM_MQ_N)-1; i++){
        fprintf(file, "%0X ", x[i]);
    }
    fprintf(file, "%0X", x[FIELD_BASE_PACKING(MQOM2_PARAM_MQ_N)-1]);
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
        fprintf(out_file, "x;");
        print_vec(out_file, x);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
//    unsigned long long mlen = 4;
//    unsigned char sm[4 + CRYPTO_BYTES] = {0};
//    unsigned long long smlen = 0;
//    const unsigned char m[4] = {0x01, 0x01, 0x01, 0x01};
//    const unsigned  char sk[CRYPTO_SECRETKEYBYTES] = {0xDB, 0xCF, 0xE7, 0x68, 0x69, 0x1B, 0x5C, 0x5F, 0xEC, 0x84, 0xA8, 0xD1, 0x25, 0xCB, 0x74, 0xED, 0x53, 0x0F, 0x8A, 0xFB, 0xC7, 0x45, 0x36, 0xB9, 0xA9, 0x63, 0xB4, 0xF1, 0xC4, 0xCB, 0x73, 0x8B, 0x2E, 0x3A, 0x4D, 0xF5, 0xE7, 0x8D, 0x88, 0xCC, 0x4D, 0x25, 0x41, 0x59, 0xBA, 0x7D, 0x24, 0x3F, 0x84, 0xF0, 0x74, 0x06, 0x2D, 0xEB, 0x7C, 0xEC, 0x00, 0xBE, 0x40, 0x68, 0x82, 0x0E, 0x59, 0x8A, 0x23, 0xD6, 0x7E, 0x15, 0x8F, 0xBB, 0x7B, 0xBD, 0xFD, 0xD1, 0x09, 0x34, 0xE9, 0xC4, 0x90, 0x32, 0xBA, 0x54, 0xF7, 0x7B, 0xA8, 0x30, 0x6C, 0x23, 0xC4, 0xCA, 0xF0, 0x63, 0x37, 0x4A, 0x0F, 0x7B, 0x74, 0xB3, 0x98, 0x9D, 0xF8, 0x2E, 0x52, 0xC7, 0x82, 0xA8, 0x6E, 0x92, 0xD0, 0x4B, 0x1B, 0xF4, 0x4F, 0x58, 0x28, 0x9F, 0x3D, 0xFF, 0xFE, 0x05, 0x53, 0x65, 0x3C, 0xCC, 0x74, 0x0A, 0xDB, 0xCB, 0x81, 0x6B, 0xF5, 0xD4, 0xAA, 0x54, 0xFB, 0xE1, 0xEA, 0xEA, 0x2D, 0x29, 0x44, 0xB5, 0x46, 0x2C, 0x58, 0xF5, 0x82, 0x95, 0x20, 0xEE, 0xFC, 0x62, 0xD1, 0x83, 0xF6, 0x13, 0xFB, 0x47, 0xA2, 0xAC, 0xE5, 0xCE, 0x44, 0x01};
//    printf("\n------=============RUN  crypto_sign\n");
//    int res = crypto_sign(sm, &smlen, m, mlen, sk);
//    printf("\n------res = %d\n", res);
    return 0;
}


