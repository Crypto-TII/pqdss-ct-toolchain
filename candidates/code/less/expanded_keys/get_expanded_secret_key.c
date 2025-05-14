
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "LESS.h"
#include "utils.h"
#include "api.h"

// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES


void get_expanded_sk(monomial_t private_Q[NUM_KEYPAIRS-1], uint8_t secret_key[SECRET_KEY_LENGTH]) {
    prikey_t *sk_struct = (prikey_t *)secret_key;
    SHAKE_STATE_STRUCT sk_shake_state;
    initialize_csprng(&sk_shake_state, sk_struct->compressed_sk, PRIVATE_KEY_SEED_LENGTH_BYTES);
    unsigned char private_monomial_seeds[NUM_KEYPAIRS - 1][PRIVATE_KEY_SEED_LENGTH_BYTES];
    /* Generating seed for public code G_0 */
    /* Done to follow the same sequence as in the key generation and signing implementation. Otherwise, the derived
     * seeds don't match*/
    unsigned char G_0_seed[SEED_LENGTH_BYTES];
    csprng_randombytes(G_0_seed, SEED_LENGTH_BYTES, &sk_shake_state);
    /* The first private key monomial is an ID matrix, no need for random
     * generation, hence NUM_KEYPAIRS-1 */
    for (uint32_t i = 0; i < NUM_KEYPAIRS - 1; i++) {
        csprng_randombytes(private_monomial_seeds[i],
                           PRIVATE_KEY_SEED_LENGTH_BYTES,
                           &sk_shake_state);
        monomial_t private_Q_inv;
        monomial_sample_prikey(&private_Q_inv, private_monomial_seeds[i]);
        monomial_inv(&private_Q[i], &private_Q_inv);
    }
}



void print_expanded_key(FILE *file, monomial_t private_Q[NUM_KEYPAIRS-1]) {
    for (int i=0; i < NUM_KEYPAIRS - 1; i++){
        for (int j=0; j < N; j++){
            fprintf(file, "%02X", private_Q[i].coefficients[j]);
        }
        for (int j=0; j < N; j++){
            fprintf(file, "%04X", private_Q[i].permutation[j]);
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
        monomial_t private_Q[NUM_KEYPAIRS-1];
        get_expanded_sk(private_Q, tp_buff);
        // Write to output file
        print_expanded_key(out_file, private_Q);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    create_expanded_secrets();
    return 0;
}


