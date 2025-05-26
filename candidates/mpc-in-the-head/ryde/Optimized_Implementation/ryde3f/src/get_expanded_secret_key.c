
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <ctype.h>
#include <stdio.h>

#include "api.h"


// Replace with your actual type definitions
#define SECRET_KEY_LENGTH CRYPTO_SECRETKEYBYTES  // 32 bytes = 64 hex characters



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


    char line[2* (CRYPTO_SECRETKEYBYTES+2)];
    uint8_t tp_buff[SECRET_KEY_LENGTH];

    while (fgets(line, sizeof(line), key_file)) {
        // Remove newline and leading 'sk=' if present
        char *key_start = strstr(line, "sk=");
        if (!key_start) continue;
        key_start += 3;
        char *newline = strchr(key_start, '\n');
        if (newline) *newline = '\0';

        // Convert hex to bytes
        if (hexstr_to_bytes(key_start, tp_buff, SECRET_KEY_LENGTH) != 0) {
            fprintf(stderr, "Failed to parse key: %s\n", key_start);
            continue;
        }

        unsigned char sm[CRYPTO_BYTES + 4] = {0};
        unsigned long long smlen = CRYPTO_BYTES + 4;
        const unsigned char m[4] = {0x01, 0x02, 0x03, 0x04};
        unsigned long long mlen = 4;
        unsigned char *sk = (unsigned char *)tp_buff;
        crypto_sign(sm, &smlen, m, mlen, sk);
    }
    fclose(key_file);
}


int main(){
    create_expanded_secrets();
    return 0;
}
