#ifndef SNOVA_H
#define SNOVA_H

#include "shake/snova_shake.h"

#include "deriv_params.h"
#include "gf16_matrix.h"

typedef gf16m_t P11_t[m_SNOVA][v_SNOVA][v_SNOVA];
typedef gf16m_t P12_t[m_SNOVA][v_SNOVA][o_SNOVA];
typedef gf16m_t P21_t[m_SNOVA][o_SNOVA][v_SNOVA];
typedef gf16m_t Aalpha_t[m_SNOVA][alpha_SNOVA];
typedef gf16m_t Balpha_t[m_SNOVA][alpha_SNOVA];
typedef gf16m_t Qalpha1_t[m_SNOVA][alpha_SNOVA];
typedef gf16m_t Qalpha2_t[m_SNOVA][alpha_SNOVA];

typedef struct {
    P11_t P11;
    P12_t P12;
    P21_t P21;
    Aalpha_t Aalpha;
    Balpha_t Balpha;
    Qalpha1_t Qalpha1;
    Qalpha2_t Qalpha2;
} map_group1;


typedef gf16m_t T12_t[v_SNOVA][o_SNOVA];
typedef gf16m_t F11_t[m_SNOVA][v_SNOVA][v_SNOVA];
typedef gf16m_t F12_t[m_SNOVA][v_SNOVA][o_SNOVA];
typedef gf16m_t F21_t[m_SNOVA][o_SNOVA][v_SNOVA];

typedef struct {
    F11_t F11;
    F12_t F12;
    F21_t F21;
} map_group2;

typedef struct {
    Aalpha_t Aalpha;
    Balpha_t Balpha;
    Qalpha1_t Qalpha1;
    Qalpha2_t Qalpha2;
    T12_t T12;
    F11_t F11;
    F12_t F12;
    F21_t F21;
    uint8_t pt_public_key_seed[seed_length_public];
    uint8_t pt_private_key_seed[seed_length_private];
} sk_gf16;

typedef gf16m_t P22_t[m_SNOVA][o_SNOVA][o_SNOVA];
typedef uint8_t
    P22_byte_t[(m_SNOVA * o_SNOVA * o_SNOVA * lsq_SNOVA + 1) >> 1];  // byte

typedef struct {
    uint8_t pt_public_key_seed[seed_length_public];
    P22_byte_t P22;
} public_key;

typedef struct {
    uint8_t pt_public_key_seed[seed_length_public];
    P22_t P22;
    map_group1 map1;
} public_key_expand;

typedef struct {
    uint8_t pt_public_key_seed[seed_length_public];
    uint8_t P22_map1[((sizeof(P22_t) + sizeof(map_group1)) + 1) / 2];
} public_key_expand_pack;

typedef struct {
    map_group1 map1;
    T12_t T12;
    map_group2 map2;
    public_key pk;
} snova_key_elems;

#ifdef __cplusplus
extern "C" {
#endif

void shake256(const uint8_t* pt_seed_array, int input_bytes, uint8_t* pt_output_array,
              int output_bytes);

void snova_init(void);

void generate_keys_ssk(uint8_t* pk, uint8_t* ssk,
                       const uint8_t* pkseed, const uint8_t* skseed);
void generate_keys_esk(uint8_t* pk, uint8_t* esk,
                       const uint8_t* pkseed, const uint8_t* skseed);

void generate_pk_with_ssk(uint8_t* pk, const uint8_t* ssk);
void generate_pk_with_esk(uint8_t* pk, const uint8_t* esk);

void sign_digest_ssk(uint8_t* pt_signature, const uint8_t* digest,
                     uint64_t bytes_digest, uint8_t* array_salt,
                     const uint8_t* ssk);
void sign_digest_esk(uint8_t* pt_signature, const uint8_t* digest,
                     uint64_t bytes_digest, uint8_t* array_salt,
                     const uint8_t* esk);

void expand_public_pack(uint8_t* pkx_pck, const uint8_t *pk);

int verify_signture(const uint8_t* pt_digest, uint64_t bytes_digest,
                    const uint8_t* pt_signature, const uint8_t* pk);
int verify_signture_pkx(const uint8_t* pt_digest, uint64_t bytes_digest,
                            const uint8_t* pt_signature, const uint8_t* pk);

#ifdef __cplusplus
}
#endif

#endif

