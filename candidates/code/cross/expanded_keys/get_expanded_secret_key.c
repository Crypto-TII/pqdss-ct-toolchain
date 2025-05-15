
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


#if defined(RSDP)
static
void expand_pk(FP_ELEM V_tr[K][N-K],
                        const uint8_t seed_pk[KEYPAIR_SEED_LENGTH_BYTES]){

  /* Expansion of pk->seed, explicit domain separation for CSPRNG as in keygen */
  const uint16_t dsc_csprng_seed_pk = CSPRNG_DOMAIN_SEP_CONST + (3*T+2);

  CSPRNG_STATE_T csprng_state_mat;
  csprng_initialize(&csprng_state_mat, seed_pk, KEYPAIR_SEED_LENGTH_BYTES, dsc_csprng_seed_pk);
  csprng_fp_mat(V_tr,&csprng_state_mat);
}
#elif defined(RSDPG)
static
void expand_pk(FP_ELEM V_tr[K][N-K],
                        FZ_ELEM W_mat[M][N-M],
                        const uint8_t seed_pk[KEYPAIR_SEED_LENGTH_BYTES]){

  /* Expansion of pk->seed, explicit domain separation for CSPRNG as in keygen */
  const uint16_t dsc_csprng_seed_pk = CSPRNG_DOMAIN_SEP_CONST + (3*T+2);

  CSPRNG_STATE_T csprng_state_mat;
  csprng_initialize(&csprng_state_mat, seed_pk, KEYPAIR_SEED_LENGTH_BYTES, dsc_csprng_seed_pk);

  csprng_fz_mat(W_mat, &csprng_state_mat);
  csprng_fp_mat(V_tr, &csprng_state_mat);
}
#endif



#if defined(RSDP)
static
void expand_sk(FZ_ELEM e_bar[N],
                         FP_ELEM V_tr[K][N-K],
                         const uint8_t seed_sk[KEYPAIR_SEED_LENGTH_BYTES]){
  uint8_t seed_e_seed_pk[2][KEYPAIR_SEED_LENGTH_BYTES];

  /* Expansion of sk->seed, explicit domain separation for CSPRNG, as in keygen */
  const uint16_t dsc_csprng_seed_sk = CSPRNG_DOMAIN_SEP_CONST + (3*T+1);

  CSPRNG_STATE_T csprng_state;
  csprng_initialize(&csprng_state, seed_sk, KEYPAIR_SEED_LENGTH_BYTES, dsc_csprng_seed_sk);
  csprng_randombytes((uint8_t *)seed_e_seed_pk,
                     2*KEYPAIR_SEED_LENGTH_BYTES,
                     &csprng_state);

  expand_pk(V_tr, seed_e_seed_pk[1]);

  /* Expansion of seede, explicit domain separation for CSPRNG as in keygen */
  const uint16_t dsc_csprng_seed_e = CSPRNG_DOMAIN_SEP_CONST + (3*T+3);

  CSPRNG_STATE_T csprng_state_e_bar;
  csprng_initialize(&csprng_state_e_bar, seed_e_seed_pk[0], KEYPAIR_SEED_LENGTH_BYTES, dsc_csprng_seed_e);
  csprng_fz_vec(e_bar, &csprng_state_e_bar);
}
#elif defined(RSDPG)
static
void expand_sk(FZ_ELEM e_bar[N],
                         FZ_ELEM e_G_bar[M],
                         FP_ELEM V_tr[K][N-K],
                         FZ_ELEM W_mat[M][N-M],
                         const uint8_t seed_sk[KEYPAIR_SEED_LENGTH_BYTES]){
  uint8_t seed_e_seed_pk[2][KEYPAIR_SEED_LENGTH_BYTES];
  CSPRNG_STATE_T csprng_state;

  /* Expansion of sk->seed, explicit domain separation for CSPRNG, as in keygen */
  const uint16_t dsc_csprng_seed_sk = CSPRNG_DOMAIN_SEP_CONST + (3*T+1);

  csprng_initialize(&csprng_state, seed_sk, KEYPAIR_SEED_LENGTH_BYTES, dsc_csprng_seed_sk);
  csprng_randombytes((uint8_t *)seed_e_seed_pk,
                     2*KEYPAIR_SEED_LENGTH_BYTES,
                     &csprng_state);

  expand_pk(V_tr, W_mat, seed_e_seed_pk[1]);

  /* Expansion of seede, explicit domain separation for CSPRNG as in keygen */
  const uint16_t dsc_csprng_seed_e = CSPRNG_DOMAIN_SEP_CONST + (3*T+3);

  CSPRNG_STATE_T csprng_state_e_bar;
  csprng_initialize(&csprng_state_e_bar, seed_e_seed_pk[0], KEYPAIR_SEED_LENGTH_BYTES, dsc_csprng_seed_e);
  csprng_fz_inf_w(e_G_bar,&csprng_state_e_bar);
#if (defined(HIGH_PERFORMANCE_X86_64) && defined(RSDPG) )
    alignas(EPI8_PER_REG) uint16_t W_mat_avx[M][ROUND_UP(N-M,EPI16_PER_REG)] = {{0}};
    for(int i = 0; i < M; i++){
      for (int j = 0; j < N-M; j++){
         W_mat_avx[i][j] = W_mat[i][j];
      }
    }
  fz_inf_w_by_fz_matrix(e_bar,e_G_bar,W_mat_avx);
#else
  fz_inf_w_by_fz_matrix(e_bar,e_G_bar,W_mat);
#endif
  fz_dz_norm_n(e_bar);
}
#endif





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
    for (int i=0; i < N - 1; i++){
        fprintf(file, "%02X", e_bar[i]);
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
        get_expanded_sk(e_bar,tp_buff);
        // Write to output file
        print_expanded_key(out_file, e_bar);
        fprintf(out_file, "\n");
    }
    fclose(key_file);
    fclose(out_file);
}


int main(){
//    create_expanded_secrets();
    unsigned char sm[CRYPTO_BYTES + 4] = {0};
    unsigned long long smlen = CRYPTO_BYTES + 4;
    const unsigned char m[4] = {0x01, 0x02, 0x03, 0x04};
    unsigned long long mlen = 4;
    unsigned char sk[CRYPTO_SECRETKEYBYTES] = {0xE7, 0xDD, 0xE1, 0x40, 0x79, 0x8F, 0x25, 0xF1, 0x8A, 0x47, 0xC0, 0x33, 0xF9, 0xCC, 0xD5, 0x84, 0xEE, 0xA9, 0x5A, 0xA6, 0x1E, 0x26, 0x98, 0xD5, 0x4D, 0x49, 0x80, 0x6F, 0x30, 0x47, 0x15, 0xBD};
    int res = crypto_sign(sm, &smlen, m, mlen, sk);
    printf("\n==== res = %d====\n", res);
    return 0;
}


