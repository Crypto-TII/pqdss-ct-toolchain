
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "snova.h"
#include "api.h"

// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES

//
#if OPTIMISATION != 0
#define gen_F gen_F_ref
#endif



void get_expanded_sk(snova_key_elems *key_elems, sk_gf16 *sk_upk, uint8_t secret_key[SECRET_KEY_LENGTH]) {
    snova_init();
#if sk_is_seed
    uint8_t *pk_seed = secret_key;
    uint8_t *sk_seed = secret_key + seed_length_public;
    gen_seeds_and_T12(key_elems->T12, sk_seed);
    gen_A_B_Q_P(&(key_elems->map1), pk_seed);
    gen_F(&(key_elems->map2), &(key_elems->map1), key_elems->T12);
#else
    sk_unpack(sk_upk, secret_key);
#endif

}




void print_permutation(FILE *file, snova_key_elems *key_elems, sk_gf16 *sk_upk) {
#if sk_is_seed
    // T12
    for (int i=0; i<v_SNOVA; i++){
        for (int j=0; j<o_SNOVA; j++){
            fprintf(file, "%02X", key_elems->T12[i][j]);
        }
    }
    // F11
    for (int i=0; i<m_SNOVA; i++){
        for (int j=0; j<v_SNOVA; j++){
            for (int k=0; k<v_SNOVA; k++){
                fprintf(file, "%02X", key_elems->map2.F11[i][j][k]);
            }
        }
    }
    // F12
    for (int i=0; i<m_SNOVA; i++){
        for (int j=0; j<v_SNOVA; j++){
            for (int k=0; k<o_SNOVA; k++){
                fprintf(file, "%02X", key_elems->map2.F12[i][j][k]);
            }
        }
    }
    // F21
    for (int i=0; i<m_SNOVA; i++){
        for (int j=0; j<o_SNOVA; j++){
            for (int k=0; k<v_SNOVA; k++){
                fprintf(file, "%02X", key_elems->map2.F21[i][j][k]);
            }
        }
    }

#else
    // T12
    for (int i=0; i<v_SNOVA; i++){
        for (int j=0; j<o_SNOVA; j++){
            fprintf(file, "%02X", sk_upk->T12[i][j]);
        }
    }
    // F11
    for (int i=0; i<m_SNOVA; i++){
        for (int j=0; j<v_SNOVA; j++){
            for (int k=0; k<v_SNOVA; k++){
                fprintf(file, "%02X", sk_upk->F11[i][j][k]);
            }
        }
    }
    // F12
    for (int i=0; i<m_SNOVA; i++){
        for (int j=0; j<v_SNOVA; j++){
            for (int k=0; k<o_SNOVA; k++){
                fprintf(file, "%02X", sk_upk->F12[i][j][k]);
            }
        }
    }
    // F21
    for (int i=0; i<m_SNOVA; i++){
        for (int j=0; j<o_SNOVA; j++){
            for (int k=0; k<v_SNOVA; k++){
                fprintf(file, "%02X", sk_upk->F21[i][j][k]);
            }
        }
    }
#endif
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
        snova_key_elems key_elems;
        sk_gf16 sk_upk;
        get_expanded_sk(&key_elems, &sk_upk, tp_buff);
        // Write to output file
        print_permutation(out_file, &key_elems, &sk_upk);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
    snova_init();
    create_expanded_secrets();
    return 0;
}


