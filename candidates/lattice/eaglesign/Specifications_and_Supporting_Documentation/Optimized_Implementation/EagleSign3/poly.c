/*
 * Implementors: EagleSign Team
 * This implementation is highly inspired from Dilithium and
 * Falcon Signatures' implementations
 */

#include <stdint.h>
#include <stdio.h>
#include "params.h"
#include "poly.h"
#include "ntt.h"
#include "reduce.h"
#include "symmetric.h"
#include <immintrin.h>

void poly_add(poly *c, const poly *a, const poly *b)
{
  unsigned int i;
  __m256i q___ = _mm256_set1_epi16(Q);
  for (i = 0; i < N; i += 16)
  {
    __m256i coeffs_a = _mm256_loadu_si256((__m256i *)&a->coeffs[i]);
    __m256i coeffs_b = _mm256_loadu_si256((__m256i *)&b->coeffs[i]);

    __m256i result = _mm256_add_epi16(coeffs_a, coeffs_b);

    __m256i q_shifted = _mm256_srli_epi16(q___, 1);
    __m256i q_negated = _mm256_sub_epi16(_mm256_setzero_si256(), q___);

    __m256i tmp1 = _mm256_add_epi16(result, q_shifted);
    tmp1 = _mm256_srli_epi16(tmp1, Q_BIT_SIZE - 1);
    tmp1 = _mm256_sub_epi16(_mm256_setzero_si256(), tmp1);
    tmp1 = _mm256_and_si256(q___, tmp1);

    q_shifted = _mm256_add_epi16(q_shifted, _mm256_set1_epi16(1));
    __m256i tmp2 = _mm256_sub_epi16(result, q_shifted);
    tmp2 = _mm256_srli_epi16(tmp2, Q_BIT_SIZE - 1);
    tmp2 = _mm256_sub_epi16(_mm256_setzero_si256(), tmp2);
    tmp2 = _mm256_and_si256(q_negated, _mm256_xor_si256(tmp2, _mm256_set1_epi16(-1)));
    __m256i tmp_ = _mm256_or_si256(tmp2, tmp1);
    result = _mm256_add_epi16(result, tmp_);

    _mm256_storeu_si256((__m256i *)&c->coeffs[i], result);
  }
}

void poly_sub(poly *c, const poly *a, const poly *b)
{
  unsigned int i;
  __m256i q___ = _mm256_set1_epi16(Q);
  for (i = 0; i < N; i += 16)
  {
    __m256i coeffs_a = _mm256_loadu_si256((__m256i *)&a->coeffs[i]);
    __m256i coeffs_b = _mm256_loadu_si256((__m256i *)&b->coeffs[i]);

    __m256i result = _mm256_sub_epi16(coeffs_a, coeffs_b);

    __m256i q_shifted = _mm256_srli_epi16(q___, 1);
    __m256i q_negated = _mm256_sub_epi16(_mm256_setzero_si256(), q___);

    __m256i tmp1 = _mm256_add_epi16(result, q_shifted);
    tmp1 = _mm256_srli_epi16(tmp1, Q_BIT_SIZE - 1);
    tmp1 = _mm256_sub_epi16(_mm256_setzero_si256(), tmp1);
    tmp1 = _mm256_and_si256(q___, tmp1);

    q_shifted = _mm256_add_epi16(q_shifted, _mm256_set1_epi16(1));
    __m256i tmp2 = _mm256_sub_epi16(result, q_shifted);
    tmp2 = _mm256_srli_epi16(tmp2, Q_BIT_SIZE - 1);
    tmp2 = _mm256_sub_epi16(_mm256_setzero_si256(), tmp2);
    tmp2 = _mm256_and_si256(q_negated, _mm256_xor_si256(tmp2, _mm256_set1_epi16(-1)));

    __m256i tmp_ = _mm256_or_si256(tmp2, tmp1);
    result = _mm256_add_epi16(result, tmp_);

    _mm256_storeu_si256((__m256i *)&c->coeffs[i], result);
  }
}

void poly_ntt(poly *a)
{

  ntt(a->coeffs, LOG_N);
}

void poly_invntt_tomont(poly *a)
{

  invntt_tomont(a->coeffs, LOG_N);
}

void poly_pointwise_montgomery(poly *c, const poly *a, const poly *b)
{
  __m256i q_ = _mm256_set1_epi32(Q);
  __m128i q__ = _mm_set1_epi16(Q);
  __m256i zeros = _mm256_setzero_si256();
  __m128i zeros_ = _mm_setzero_si128();
  __m256i q0i = _mm256_set1_epi32(Q0I);
  __m256i r2 = _mm256_set1_epi32(R2);
  __m256i two_one = _mm256_set1_epi32(TWO_POWER_SIZE_Q_MINUS_ONE);

  for (int i = 0; i < N; i += 8)
  {
    // Loading a and b into 128 bits like registries
    __m128i a_data = _mm_loadu_si128((__m128i *)&a->coeffs[i]);
    __m128i b_data = _mm_loadu_si128((__m128i *)&b->coeffs[i]);

    /*
     * Adding q: for a,b such that -Q/2<= a,b < Q/2,
     * compute r_a, r_b := a, b mod Q such that
     * 0 <= r_a, r_b < Q
     */
    __m128i tmp_ = _mm_srli_epi16(a_data, Q_BIT_SIZE - 1);
    tmp_ = _mm_sub_epi16(zeros_, tmp_);
    tmp_ = _mm_and_si128(q__, tmp_);
    a_data = _mm_add_epi16(a_data, tmp_);

    tmp_ = _mm_srli_epi16(b_data, Q_BIT_SIZE - 1);
    tmp_ = _mm_sub_epi16(zeros_, tmp_);
    tmp_ = _mm_and_si128(q__, tmp_);
    b_data = _mm_add_epi16(b_data, tmp_);

    // casting a and b into 32-bits elements
    __m256i a_vec = _mm256_cvtepi16_epi32(a_data);
    __m256i b_vec = _mm256_cvtepi16_epi32(b_data);

    /*
     * Computing a * b mod (R^2)
     * Recall that R := 2^16 mod Q, meaning
     * that R^2 := 2^32 mod Q
     */

    __m256i z = _mm256_mullo_epi32(a_vec, b_vec);

    // Computing z = a*b/R mod Q
    __m256i w = _mm256_mullo_epi32(z, q0i);
    w = _mm256_and_si256(w, two_one);
    w = _mm256_mullo_epi32(w, q_);

    z = _mm256_add_epi32(z, w);
    z = _mm256_srli_epi32(z, Q_BIT_SIZE);
    z = _mm256_sub_epi32(z, q_);

    __m256i tmp = _mm256_srli_epi32(z, DOUBLE_Q_BIT_SIZE - 1);
    tmp = _mm256_sub_epi32(zeros, tmp);
    tmp = _mm256_and_si256(q_, tmp);
    z = _mm256_add_epi32(z, tmp);

    /*
     * Computing a*b mod Q = z*(R^2)/R mod Q
     * Recall that z = a*b/R mod Q
     */
    z = _mm256_mullo_epi32(z, r2);
    w = _mm256_mullo_epi32(z, q0i);
    w = _mm256_and_si256(w, two_one);
    w = _mm256_mullo_epi32(w, q_);

    z = _mm256_add_epi32(z, w);
    z = _mm256_srli_epi32(z, Q_BIT_SIZE);
    z = _mm256_sub_epi32(z, q_);

    tmp = _mm256_srli_epi32(z, DOUBLE_Q_BIT_SIZE - 1);
    tmp = _mm256_sub_epi32(zeros, tmp);
    tmp = _mm256_and_si256(q_, tmp);
    z = _mm256_add_epi32(z, tmp);

    // Extracting a*b as a 32 bits elements
    __m128i low_half = _mm256_extractf128_si256(z, 0);
    __m128i high_half = _mm256_extractf128_si256(z, 1);
    __m128i result = _mm_packus_epi32(low_half, high_half);

    /*
     * For finite field element y with 0 <= y < Q, compute r \equiv y(mod Q)
     * such that r is between -q/2 and +q/2.
     */

    __m128i q_shifted = _mm_srli_epi16(q__, 1);
    __m128i q_negated = _mm_sub_epi16(_mm_setzero_si128(), q__);

    __m128i tmp1 = _mm_add_epi16(result, q_shifted);
    tmp1 = _mm_srli_epi16(tmp1, Q_BIT_SIZE - 1);
    tmp1 = _mm_sub_epi16(_mm_setzero_si128(), tmp1);
    tmp1 = _mm_and_si128(q__, tmp1);

    q_shifted = _mm_add_epi16(q_shifted, _mm_set1_epi16(1));
    __m128i tmp2 = _mm_sub_epi16(result, q_shifted);
    tmp2 = _mm_srli_epi16(tmp2, Q_BIT_SIZE - 1);
    tmp2 = _mm_sub_epi16(_mm_setzero_si128(), tmp2);
    tmp2 = _mm_and_si128(q_negated, _mm_xor_si128(tmp2, _mm_set1_epi16(-1)));

    tmp_ = _mm_or_si128(tmp2, tmp1);
    result = _mm_add_epi16(result, tmp_);

    _mm_storeu_si128((__m128i *)&c->coeffs[i], result);
  }
}

static unsigned int rej_uniform(S_Q_SIZE *a,
                                unsigned int len,
                                const uint8_t *buf,
                                unsigned int buflen)
{
  unsigned int ctr, pos;
  Q_SIZE t;

  ctr = pos = 0;
  while (ctr < len && pos + 2 <= buflen)
  {
    t = buf[pos++];
    t |= (Q_SIZE)buf[pos++] << 8;
    t &= 0x3FFF;

    if (t < Q)
      a[ctr++] = t;
  }

  return ctr;
}

#define POLY_UNIFORM_NBLOCKS ((768 + STREAM128_BLOCKBYTES - 1) / STREAM128_BLOCKBYTES)
void poly_uniform(poly *a,
                  const uint8_t seed[SEEDBYTES],
                  uint16_t nonce)
{
  unsigned int i, ctr, off;
  unsigned int buflen = POLY_UNIFORM_NBLOCKS * STREAM128_BLOCKBYTES;
  uint8_t buf[POLY_UNIFORM_NBLOCKS * STREAM128_BLOCKBYTES + 1];
  stream128_state state;

  stream128_init(&state, seed, nonce);
  stream128_squeezeblocks(buf, POLY_UNIFORM_NBLOCKS, &state);

  ctr = rej_uniform(a->coeffs, N, buf, buflen);

  while (ctr < N)
  {
    off = buflen % 2;
    for (i = 0; i < off; ++i)
      buf[i] = buf[buflen - off + i];

    stream128_squeezeblocks(buf + off, 1, &state);
    buflen = STREAM128_BLOCKBYTES + off;
    ctr += rej_uniform(a->coeffs + ctr, N - ctr, buf, buflen);
  }
}

static unsigned int rej_challenge(S_Q_SIZE *c,
                                  unsigned int *ctr,
                                  const uint8_t *buf,
                                  unsigned int buflen,
                                  uint64_t signs,
                                  unsigned int *h,
                                  int T_param)
{
  Q_SIZE t;
  unsigned int pos = 0;
  uint64_t v;

  while ((*ctr) < N && (*h) < T_param && pos + 3 <= buflen && signs != 0)
  {
    t = buf[pos++];
    t |= (Q_SIZE)buf[pos++] << 8;
    t &= 0x3FF;

    if (t < (*ctr))
    {
      c[*ctr] = c[t];

      v = 1 - 2 * (signs & 1);
      v += ((-Q) & ~-((v - (Q >> 1)) >> 63)) | (Q & -((v + (Q >> 1)) >> 63));

      c[t] = (S_Q_SIZE)v;
      signs >>= 1;
      *ctr += 1;
      *h += 1;
    }
  }
}

void poly_challenge_y1_c(poly *c, const uint8_t seed[SEEDBYTES],
                         uint16_t nonce, int param)
{
  unsigned int i, ctr, off, b, pos, h = 0, T_param;
  unsigned int buflen = POLY_UNIFORM_NBLOCKS * STREAM128_BLOCKBYTES;
  uint8_t buf[POLY_UNIFORM_NBLOCKS * STREAM128_BLOCKBYTES + 2];
  stream128_state state;

  stream128_init(&state, seed, nonce);
  stream128_squeezeblocks(buf, POLY_UNIFORM_NBLOCKS, &state);

  uint64_t signs;

  for (i = 0; i < N; ++i)
    c->coeffs[i] = 0;

  T_param = TAU * param + (1 - param) * T;

  ctr = N - T_param;

  while (ctr < N)
  {
    off = buflen % 3;
    for (i = 0; i < off; ++i)
      buf[i] = buf[buflen - off + i];

    stream128_squeezeblocks(buf + off, 1, &state);
    buflen = STREAM128_BLOCKBYTES + off;

    signs = 0;
    for (i = 0; i < 8; ++i)
      signs |= (uint64_t)buf[i] << 8 * i;

    rej_challenge(c->coeffs, &ctr, buf, buflen, signs, &h, T_param);
  }
  poly_ntt(c);
}

static unsigned int rej_eta(S_Q_SIZE *a,
                            unsigned int len,
                            const uint8_t *buf,
                            unsigned int buflen,
                            unsigned int eta)
{
  unsigned int ctr, pos;
  Q_SIZE t0, t1, t2, t3;

  ctr = pos = 0;

  while (ctr < len && pos < buflen - 1)
  {
    if (eta == 1)
    {
      t0 = buf[pos] & 0x03;
      t1 = (buf[pos] >> 2) & 0x03;
      t2 = (buf[pos] >> 4) & 0x03;
      t3 = buf[pos++] >> 6;
      if (t0 < 3)
        a[ctr++] = 1 - t0;
      if (t1 < 3 && ctr < len)
        a[ctr++] = 1 - t1;
      if (t2 < 3 && ctr < len)
        a[ctr++] = 1 - t2;
      if (t3 < 3 && ctr < len)
        a[ctr++] = 1 - t3;
    }

    else if (eta == 2)
    {
      t0 = buf[pos] & 0x07;
      t1 = buf[pos++] >> 5;
      if (t0 < 5)
        a[ctr++] = 2 - t0;
      if (t1 < 5 && ctr < len)
        a[ctr++] = 2 - t1;
    }

    else if (eta == 3)
    {
      t0 = buf[pos] & 0x07;
      t1 = buf[pos++] >> 5;
      if (t0 < 7)
        a[ctr++] = 3 - t0;
      if (t1 < 7 && ctr < len)
        a[ctr++] = 3 - t1;
    }

    else if (eta == 32)
    {
      t0 = buf[pos++] & 0x7f;
      if (t0 < 65)
        a[ctr++] = 32 - t0;
    }

    else if (eta == 64)
    {
      t0 = buf[pos++];
      if (t0 < 129)
        a[ctr++] = 64 - t0;
    }
  }

  return ctr;
}

void poly_uniform_eta_y2(poly *a,
                         const uint8_t seed[CRHBYTES],
                         uint16_t nonce)
{
  unsigned int ctr, POLY_UNIFORM_ETA_NBLOCKS = ((227 + STREAM256_BLOCKBYTES - 1) / STREAM256_BLOCKBYTES);
  unsigned int buflen = POLY_UNIFORM_ETA_NBLOCKS * STREAM256_BLOCKBYTES;
  uint8_t buf[POLY_UNIFORM_ETA_NBLOCKS * STREAM256_BLOCKBYTES];
  stream256_state state;

  stream256_init(&state, seed, nonce);
  stream256_squeezeblocks(buf, POLY_UNIFORM_ETA_NBLOCKS, &state);

  ctr = rej_eta(a->coeffs, N, buf, buflen, ETAY2);

  while (ctr < N)
  {
    stream256_squeezeblocks(buf, 1, &state);
    ctr += rej_eta(a->coeffs + ctr, N - ctr, buf, STREAM256_BLOCKBYTES, ETAY2);
  }
  poly_ntt(a);
}

void poly_uniform_eta_g(poly *a,
                        const uint8_t seed[CRHBYTES],
                        uint16_t nonce)
{
  unsigned int ctr, POLY_UNIFORM_ETA_NBLOCKS = ((227 + STREAM256_BLOCKBYTES - 1) / STREAM256_BLOCKBYTES);
  unsigned int buflen = POLY_UNIFORM_ETA_NBLOCKS * STREAM256_BLOCKBYTES;
  uint8_t buf[POLY_UNIFORM_ETA_NBLOCKS * STREAM256_BLOCKBYTES];
  stream256_state state;

  stream256_init(&state, seed, nonce);
  stream256_squeezeblocks(buf, POLY_UNIFORM_ETA_NBLOCKS, &state);

  ctr = rej_eta(a->coeffs, N, buf, buflen, ETAG);

  while (ctr < N)
  {
    stream256_squeezeblocks(buf, 1, &state);
    ctr += rej_eta(a->coeffs + ctr, N - ctr, buf, STREAM256_BLOCKBYTES, ETAG);
  }
  poly_ntt(a);
}

void poly_uniform_eta_d(poly *a,
                        const uint8_t seed[CRHBYTES],
                        uint16_t nonce)
{
  unsigned int ctr, POLY_UNIFORM_ETA_NBLOCKS = ((227 + STREAM256_BLOCKBYTES - 1) / STREAM256_BLOCKBYTES);
  unsigned int buflen = POLY_UNIFORM_ETA_NBLOCKS * STREAM256_BLOCKBYTES;
  uint8_t buf[POLY_UNIFORM_ETA_NBLOCKS * STREAM256_BLOCKBYTES];
  stream256_state state;

  stream256_init(&state, seed, nonce);
  stream256_squeezeblocks(buf, POLY_UNIFORM_ETA_NBLOCKS, &state);

  ctr = rej_eta(a->coeffs, N, buf, buflen, ETAD);

  while (ctr < N)
  {
    stream256_squeezeblocks(buf, 1, &state);
    ctr += rej_eta(a->coeffs + ctr, N - ctr, buf, STREAM256_BLOCKBYTES, ETAD);
  }
  poly_ntt(a);
}

void polyQ_pack(uint8_t *r, const poly *a)
{
  unsigned int i;
  Q_SIZE t[8];

#if Q == 12289
  for (i = 0; i < N / 4; ++i)
  {
    t[0] = (1 << (LOGQ - 1)) - a->coeffs[4 * i + 0];
    t[1] = (1 << (LOGQ - 1)) - a->coeffs[4 * i + 1];
    t[2] = (1 << (LOGQ - 1)) - a->coeffs[4 * i + 2];
    t[3] = (1 << (LOGQ - 1)) - a->coeffs[4 * i + 3];

    r[7 * i + 0] = t[0];
    r[7 * i + 1] = t[0] >> 8;
    r[7 * i + 1] |= t[1] << 6;
    r[7 * i + 2] = t[1] >> 2;
    r[7 * i + 3] = t[1] >> 10;
    r[7 * i + 3] |= t[2] << 4;
    r[7 * i + 4] = t[2] >> 4;
    r[7 * i + 5] = t[2] >> 12;
    r[7 * i + 5] |= t[3] << 2;
    r[7 * i + 6] = t[3] >> 6;
  }
#elif Q == 7681
  for (i = 0; i < N / 8; ++i)
  {
    t[0] = (1 << (LOGQ - 1)) - a->coeffs[8 * i + 0];
    t[1] = (1 << (LOGQ - 1)) - a->coeffs[8 * i + 1];
    t[2] = (1 << (LOGQ - 1)) - a->coeffs[8 * i + 2];
    t[3] = (1 << (LOGQ - 1)) - a->coeffs[8 * i + 3];
    t[4] = (1 << (LOGQ - 1)) - a->coeffs[8 * i + 4];
    t[5] = (1 << (LOGQ - 1)) - a->coeffs[8 * i + 5];
    t[6] = (1 << (LOGQ - 1)) - a->coeffs[8 * i + 6];
    t[7] = (1 << (LOGQ - 1)) - a->coeffs[8 * i + 7];

    r[13 * i + 0] = t[0];
    r[13 * i + 1] = t[0] >> 8;
    r[13 * i + 1] |= t[1] << 5;
    r[13 * i + 2] = t[1] >> 3;
    r[13 * i + 3] = t[1] >> 11;
    r[13 * i + 3] |= t[2] << 2;
    r[13 * i + 4] = t[2] >> 6;
    r[13 * i + 4] |= t[3] << 7;
    r[13 * i + 5] = t[3] >> 1;
    r[13 * i + 6] = t[3] >> 9;
    r[13 * i + 6] |= t[4] << 4;
    r[13 * i + 7] = t[4] >> 4;
    r[13 * i + 8] = t[4] >> 12;
    r[13 * i + 8] |= t[5] << 1;
    r[13 * i + 9] = t[5] >> 7;
    r[13 * i + 9] |= t[6] << 6;
    r[13 * i + 10] = t[6] >> 2;
    r[13 * i + 11] = t[6] >> 10;
    r[13 * i + 11] |= t[7] << 3;
    r[13 * i + 12] = t[7] >> 5;
  }
#endif
}

void polyQ_unpack(poly *r, const uint8_t *a)
{
  unsigned int i;

#if Q == 12289
  for (i = 0; i < N / 4; ++i)
  {
    r->coeffs[4 * i + 0] = a[7 * i + 0];
    r->coeffs[4 * i + 0] |= (Q_SIZE)a[7 * i + 1] << 8;
    r->coeffs[4 * i + 0] &= 0x3fff;

    r->coeffs[4 * i + 1] = a[7 * i + 1] >> 6;
    r->coeffs[4 * i + 1] |= (Q_SIZE)a[7 * i + 2] << 2;
    r->coeffs[4 * i + 1] |= (Q_SIZE)a[7 * i + 3] << 10;
    r->coeffs[4 * i + 1] &= 0x3fff;

    r->coeffs[4 * i + 2] = a[7 * i + 3] >> 4;
    r->coeffs[4 * i + 2] |= (Q_SIZE)a[7 * i + 4] << 4;
    r->coeffs[4 * i + 2] |= (Q_SIZE)a[7 * i + 5] << 12;
    r->coeffs[4 * i + 2] &= 0x3fff;

    r->coeffs[4 * i + 3] = a[7 * i + 5] >> 2;
    r->coeffs[4 * i + 3] |= (Q_SIZE)a[7 * i + 6] << 6;
    r->coeffs[4 * i + 3] &= 0x3fff;

    r->coeffs[4 * i + 0] = (1 << (LOGQ - 1)) - r->coeffs[4 * i + 0];
    r->coeffs[4 * i + 1] = (1 << (LOGQ - 1)) - r->coeffs[4 * i + 1];
    r->coeffs[4 * i + 2] = (1 << (LOGQ - 1)) - r->coeffs[4 * i + 2];
    r->coeffs[4 * i + 3] = (1 << (LOGQ - 1)) - r->coeffs[4 * i + 3];
  }

#elif Q == 7681
  for (i = 0; i < N / 8; ++i)
  {
    r->coeffs[8 * i + 0] = a[13 * i + 0];
    r->coeffs[8 * i + 0] |= (Q_SIZE)a[13 * i + 1] << 8;
    r->coeffs[8 * i + 0] &= 0x1fff;

    r->coeffs[8 * i + 1] = a[13 * i + 1] >> 5;
    r->coeffs[8 * i + 1] |= (Q_SIZE)a[13 * i + 2] << 3;
    r->coeffs[8 * i + 1] |= (Q_SIZE)a[13 * i + 3] << 11;
    r->coeffs[8 * i + 1] &= 0x1fff;

    r->coeffs[8 * i + 2] = a[13 * i + 3] >> 2;
    r->coeffs[8 * i + 2] |= (Q_SIZE)a[13 * i + 4] << 6;
    r->coeffs[8 * i + 2] &= 0x1fff;

    r->coeffs[8 * i + 3] = a[13 * i + 4] >> 7;
    r->coeffs[8 * i + 3] |= (Q_SIZE)a[13 * i + 5] << 1;
    r->coeffs[8 * i + 3] |= (Q_SIZE)a[13 * i + 6] << 9;
    r->coeffs[8 * i + 3] &= 0x1fff;

    r->coeffs[8 * i + 4] = a[13 * i + 6] >> 4;
    r->coeffs[8 * i + 4] |= (Q_SIZE)a[13 * i + 7] << 4;
    r->coeffs[8 * i + 4] |= (Q_SIZE)a[13 * i + 8] << 12;
    r->coeffs[8 * i + 4] &= 0x1fff;

    r->coeffs[8 * i + 5] = a[13 * i + 8] >> 1;
    r->coeffs[8 * i + 5] |= (Q_SIZE)a[13 * i + 9] << 7;
    r->coeffs[8 * i + 5] &= 0x1fff;

    r->coeffs[8 * i + 6] = a[13 * i + 9] >> 6;
    r->coeffs[8 * i + 6] |= (Q_SIZE)a[13 * i + 10] << 2;
    r->coeffs[8 * i + 6] |= (Q_SIZE)a[13 * i + 11] << 10;
    r->coeffs[8 * i + 6] &= 0x1fff;

    r->coeffs[8 * i + 7] = a[13 * i + 11] >> 3;
    r->coeffs[8 * i + 7] |= (Q_SIZE)a[13 * i + 12] << 5;
    r->coeffs[8 * i + 7] &= 0x1fff;

    r->coeffs[8 * i + 0] = (1 << (LOGQ - 1)) - r->coeffs[8 * i + 0];
    r->coeffs[8 * i + 1] = (1 << (LOGQ - 1)) - r->coeffs[8 * i + 1];
    r->coeffs[8 * i + 2] = (1 << (LOGQ - 1)) - r->coeffs[8 * i + 2];
    r->coeffs[8 * i + 3] = (1 << (LOGQ - 1)) - r->coeffs[8 * i + 3];
    r->coeffs[8 * i + 4] = (1 << (LOGQ - 1)) - r->coeffs[8 * i + 4];
    r->coeffs[8 * i + 5] = (1 << (LOGQ - 1)) - r->coeffs[8 * i + 5];
    r->coeffs[8 * i + 6] = (1 << (LOGQ - 1)) - r->coeffs[8 * i + 6];
    r->coeffs[8 * i + 7] = (1 << (LOGQ - 1)) - r->coeffs[8 * i + 7];
  }
#endif
}

void polyG_pack(uint8_t *r, const poly *a, unsigned int logeta)
{
  unsigned int i;

  if (logeta == 2)
  {
    Q_SIZE t[4];
    for (i = 0; i < N / 4; ++i)
    {
      t[0] = (1 << (logeta - 1)) - a->coeffs[4 * i + 0];
      t[1] = (1 << (logeta - 1)) - a->coeffs[4 * i + 1];
      t[2] = (1 << (logeta - 1)) - a->coeffs[4 * i + 2];
      t[3] = (1 << (logeta - 1)) - a->coeffs[4 * i + 3];

      r[i] = t[0];
      r[i] |= t[1] << 2;
      r[i] |= t[2] << 4;
      r[i] |= t[3] << 6;
    }
  }

  else if (logeta == 3)
  {
    Q_SIZE t[8];
    for (i = 0; i < N / 8; ++i)
    {
      t[0] = (1 << (logeta - 1)) - a->coeffs[8 * i + 0];
      t[1] = (1 << (logeta - 1)) - a->coeffs[8 * i + 1];
      t[2] = (1 << (logeta - 1)) - a->coeffs[8 * i + 2];
      t[3] = (1 << (logeta - 1)) - a->coeffs[8 * i + 3];
      t[4] = (1 << (logeta - 1)) - a->coeffs[8 * i + 4];
      t[5] = (1 << (logeta - 1)) - a->coeffs[8 * i + 5];
      t[6] = (1 << (logeta - 1)) - a->coeffs[8 * i + 6];
      t[7] = (1 << (logeta - 1)) - a->coeffs[8 * i + 7];

      r[3 * i + 0] = t[0];
      r[3 * i + 0] |= t[1] << 3;
      r[3 * i + 0] |= t[2] << 6;
      r[3 * i + 1] = t[2] >> 2;
      r[3 * i + 1] |= t[3] << 1;
      r[3 * i + 1] |= t[4] << 4;
      r[3 * i + 1] |= t[5] << 7;
      r[3 * i + 2] = t[5] >> 1;
      r[3 * i + 2] |= t[6] << 2;
      r[3 * i + 2] |= t[7] << 5;
    }
  }
}

void polyG_unpack(poly *r, const uint8_t *a, unsigned int logeta)
{
  unsigned int i;
  if (logeta == 2)
  {
    for (i = 0; i < N / 4; ++i)
    {
      r->coeffs[4 * i + 0] = a[i];
      r->coeffs[4 * i + 0] &= 0x3;

      r->coeffs[4 * i + 1] = a[i] >> 2;
      r->coeffs[4 * i + 1] &= 0x3;

      r->coeffs[4 * i + 2] = a[i] >> 4;
      r->coeffs[4 * i + 2] &= 0x3;

      r->coeffs[4 * i + 3] = a[i] >> 6;
      r->coeffs[4 * i + 3] &= 0x3;

      r->coeffs[4 * i + 0] = (1 << (logeta - 1)) - r->coeffs[4 * i + 0];
      r->coeffs[4 * i + 1] = (1 << (logeta - 1)) - r->coeffs[4 * i + 1];
      r->coeffs[4 * i + 2] = (1 << (logeta - 1)) - r->coeffs[4 * i + 2];
      r->coeffs[4 * i + 3] = (1 << (logeta - 1)) - r->coeffs[4 * i + 3];
    }
  }
  else if (logeta == 3)
  {
    for (i = 0; i < N / 8; ++i)
    {
      r->coeffs[8 * i + 0] = a[3 * i + 0];
      r->coeffs[8 * i + 0] &= 0x7;

      r->coeffs[8 * i + 1] = a[3 * i + 0] >> 3;
      r->coeffs[8 * i + 1] &= 0x7;

      r->coeffs[8 * i + 2] = a[3 * i + 0] >> 6;
      r->coeffs[8 * i + 2] |= (Q_SIZE)a[3 * i + 1] << 2;
      r->coeffs[8 * i + 2] &= 0x7;

      r->coeffs[8 * i + 3] = a[3 * i + 1] >> 1;
      r->coeffs[8 * i + 3] &= 0x7;

      r->coeffs[8 * i + 4] = a[3 * i + 1] >> 4;
      r->coeffs[8 * i + 4] &= 0x7;

      r->coeffs[8 * i + 5] = a[3 * i + 1] >> 7;
      r->coeffs[8 * i + 5] |= (Q_SIZE)a[3 * i + 2] << 1;
      r->coeffs[8 * i + 5] &= 0x7;

      r->coeffs[8 * i + 6] = a[3 * i + 2] >> 2;
      r->coeffs[8 * i + 6] &= 0x7;

      r->coeffs[8 * i + 7] = a[3 * i + 2] >> 5;
      r->coeffs[8 * i + 7] &= 0x7;

      r->coeffs[8 * i + 0] = (1 << (logeta - 1)) - r->coeffs[8 * i + 0];
      r->coeffs[8 * i + 1] = (1 << (logeta - 1)) - r->coeffs[8 * i + 1];
      r->coeffs[8 * i + 2] = (1 << (logeta - 1)) - r->coeffs[8 * i + 2];
      r->coeffs[8 * i + 3] = (1 << (logeta - 1)) - r->coeffs[8 * i + 3];
      r->coeffs[8 * i + 4] = (1 << (logeta - 1)) - r->coeffs[8 * i + 4];
      r->coeffs[8 * i + 5] = (1 << (logeta - 1)) - r->coeffs[8 * i + 5];
      r->coeffs[8 * i + 6] = (1 << (logeta - 1)) - r->coeffs[8 * i + 6];
      r->coeffs[8 * i + 7] = (1 << (logeta - 1)) - r->coeffs[8 * i + 7];
    }
  }
}

void polyZ_pack(uint8_t *r, const poly *a, unsigned int logeta)
{
  unsigned int i;
  if (logeta == 8)
  {
    Q_SIZE t;
    for (i = 0; i < N; ++i)
    {
      t = (1 << (logeta - 1)) - a->coeffs[i];
      r[i] = t;
    }
  }

  else if (logeta == 9)
  {
    Q_SIZE t[8];
    for (i = 0; i < N / 8; ++i)
    {
      t[0] = (1 << (logeta - 1)) - a->coeffs[8 * i + 0];
      t[1] = (1 << (logeta - 1)) - a->coeffs[8 * i + 1];
      t[2] = (1 << (logeta - 1)) - a->coeffs[8 * i + 2];
      t[3] = (1 << (logeta - 1)) - a->coeffs[8 * i + 3];
      t[4] = (1 << (logeta - 1)) - a->coeffs[8 * i + 4];
      t[5] = (1 << (logeta - 1)) - a->coeffs[8 * i + 5];
      t[6] = (1 << (logeta - 1)) - a->coeffs[8 * i + 6];
      t[7] = (1 << (logeta - 1)) - a->coeffs[8 * i + 7];

      r[9 * i + 0] = t[0];
      r[9 * i + 1] = t[0] >> 8;
      r[9 * i + 1] |= t[1] << 1;
      r[9 * i + 2] = t[1] >> 7;
      r[9 * i + 2] |= t[2] << 2;
      r[9 * i + 3] = t[2] >> 6;
      r[9 * i + 3] |= t[3] << 3;
      r[9 * i + 4] = t[3] >> 5;
      r[9 * i + 4] |= t[4] << 4;
      r[9 * i + 5] = t[4] >> 4;
      r[9 * i + 5] |= t[5] << 5;
      r[9 * i + 6] = t[5] >> 3;
      r[9 * i + 6] |= t[6] << 6;
      r[9 * i + 7] = t[6] >> 2;
      r[9 * i + 7] |= t[7] << 7;
      r[9 * i + 8] = t[7] >> 1;
    }
  }

  else if (logeta == 10)
  {
    for (i = 0; i < N / 4; ++i)
    {
      Q_SIZE t[4];
      t[0] = (1 << (logeta - 1)) - a->coeffs[4 * i + 0];
      t[1] = (1 << (logeta - 1)) - a->coeffs[4 * i + 1];
      t[2] = (1 << (logeta - 1)) - a->coeffs[4 * i + 2];
      t[3] = (1 << (logeta - 1)) - a->coeffs[4 * i + 3];

      r[5 * i + 0] = t[0];
      r[5 * i + 1] = t[0] >> 8;
      r[5 * i + 1] |= t[1] << 2;
      r[5 * i + 2] = t[1] >> 6;
      r[5 * i + 2] |= t[2] << 4;
      r[5 * i + 3] = t[2] >> 4;
      r[5 * i + 3] |= t[3] << 6;
      r[5 * i + 4] = t[3] >> 2;
    }
  }

  else if (logeta == 11)
  {
    Q_SIZE t[8];
    for (i = 0; i < N / 8; ++i)
    {
      t[0] = (1 << (logeta - 1)) - a->coeffs[8 * i + 0];
      t[1] = (1 << (logeta - 1)) - a->coeffs[8 * i + 1];
      t[2] = (1 << (logeta - 1)) - a->coeffs[8 * i + 2];
      t[3] = (1 << (logeta - 1)) - a->coeffs[8 * i + 3];
      t[4] = (1 << (logeta - 1)) - a->coeffs[8 * i + 4];
      t[5] = (1 << (logeta - 1)) - a->coeffs[8 * i + 5];
      t[6] = (1 << (logeta - 1)) - a->coeffs[8 * i + 6];
      t[7] = (1 << (logeta - 1)) - a->coeffs[8 * i + 7];

      r[11 * i + 0] = t[0];
      r[11 * i + 1] = t[0] >> 8;
      r[11 * i + 1] |= t[1] << 3;
      r[11 * i + 2] = t[1] >> 5;
      r[11 * i + 2] |= t[2] << 6;
      r[11 * i + 3] = t[2] >> 2;
      r[11 * i + 4] = t[2] >> 10;
      r[11 * i + 4] |= t[3] << 1;
      r[11 * i + 5] = t[3] >> 7;
      r[11 * i + 5] |= t[4] << 4;
      r[11 * i + 6] = t[4] >> 4;
      r[11 * i + 6] |= t[5] << 7;
      r[11 * i + 7] = t[5] >> 1;
      r[11 * i + 8] = t[5] >> 9;
      r[11 * i + 8] |= t[6] << 2;
      r[11 * i + 9] = t[6] >> 6;
      r[11 * i + 9] |= t[7] << 5;
      r[11 * i + 10] = t[7] >> 3;
    }
  }
}

void polyZ_unpack(poly *r, const uint8_t *a, unsigned int logeta)
{
  unsigned int i;
  if (logeta == 8)
  {
    for (i = 0; i < N; ++i)
    {
      r->coeffs[i] = a[i] & 0xff;
      r->coeffs[i] = (1 << (logeta - 1)) - r->coeffs[i];
    }
  }

  else if (logeta == 9)
  {
    for (i = 0; i < N / 8; ++i)
    {
      r->coeffs[8 * i + 0] = a[9 * i + 0];
      r->coeffs[8 * i + 0] |= (Q_SIZE)a[9 * i + 1] << 8;
      r->coeffs[8 * i + 0] &= 0x1ff;

      r->coeffs[8 * i + 1] = a[9 * i + 1] >> 1;
      r->coeffs[8 * i + 1] |= (Q_SIZE)a[9 * i + 2] << 7;
      r->coeffs[8 * i + 1] &= 0x1ff;

      r->coeffs[8 * i + 2] = a[9 * i + 2] >> 2;
      r->coeffs[8 * i + 2] |= (Q_SIZE)a[9 * i + 3] << 6;
      r->coeffs[8 * i + 2] &= 0x1ff;

      r->coeffs[8 * i + 3] = a[9 * i + 3] >> 3;
      r->coeffs[8 * i + 3] |= (Q_SIZE)a[9 * i + 4] << 5;
      r->coeffs[8 * i + 3] &= 0x1ff;

      r->coeffs[8 * i + 4] = a[9 * i + 4] >> 4;
      r->coeffs[8 * i + 4] |= (Q_SIZE)a[9 * i + 5] << 4;
      r->coeffs[8 * i + 4] &= 0x1ff;

      r->coeffs[8 * i + 5] = a[9 * i + 5] >> 5;
      r->coeffs[8 * i + 5] |= (Q_SIZE)a[9 * i + 6] << 3;
      r->coeffs[8 * i + 5] &= 0x1ff;

      r->coeffs[8 * i + 6] = a[9 * i + 6] >> 6;
      r->coeffs[8 * i + 6] |= (Q_SIZE)a[9 * i + 7] << 2;
      r->coeffs[8 * i + 6] &= 0x1ff;

      r->coeffs[8 * i + 7] = a[9 * i + 7] >> 7;
      r->coeffs[8 * i + 7] |= (Q_SIZE)a[9 * i + 8] << 1;
      r->coeffs[8 * i + 7] &= 0x1ff;

      r->coeffs[8 * i + 0] = (1 << (logeta - 1)) - r->coeffs[8 * i + 0];
      r->coeffs[8 * i + 1] = (1 << (logeta - 1)) - r->coeffs[8 * i + 1];
      r->coeffs[8 * i + 2] = (1 << (logeta - 1)) - r->coeffs[8 * i + 2];
      r->coeffs[8 * i + 3] = (1 << (logeta - 1)) - r->coeffs[8 * i + 3];
      r->coeffs[8 * i + 4] = (1 << (logeta - 1)) - r->coeffs[8 * i + 4];
      r->coeffs[8 * i + 5] = (1 << (logeta - 1)) - r->coeffs[8 * i + 5];
      r->coeffs[8 * i + 6] = (1 << (logeta - 1)) - r->coeffs[8 * i + 6];
      r->coeffs[8 * i + 7] = (1 << (logeta - 1)) - r->coeffs[8 * i + 7];
    }
  }

  else if (logeta == 10)
  {
    for (i = 0; i < N / 4; ++i)
    {
      r->coeffs[4 * i + 0] = a[5 * i + 0];
      r->coeffs[4 * i + 0] |= (Q_SIZE)a[5 * i + 1] << 8;
      r->coeffs[4 * i + 0] &= 0x3ff;

      r->coeffs[4 * i + 1] = a[5 * i + 1] >> 2;
      r->coeffs[4 * i + 1] |= (Q_SIZE)a[5 * i + 2] << 6;
      r->coeffs[4 * i + 1] &= 0x3ff;

      r->coeffs[4 * i + 2] = a[5 * i + 2] >> 4;
      r->coeffs[4 * i + 2] |= (Q_SIZE)a[5 * i + 3] << 4;
      r->coeffs[4 * i + 2] &= 0x3ff;

      r->coeffs[4 * i + 3] = a[5 * i + 3] >> 6;
      r->coeffs[4 * i + 3] |= (Q_SIZE)a[5 * i + 4] << 2;
      r->coeffs[4 * i + 3] &= 0x3ff;

      r->coeffs[4 * i + 0] = (1 << (logeta - 1)) - r->coeffs[4 * i + 0];
      r->coeffs[4 * i + 1] = (1 << (logeta - 1)) - r->coeffs[4 * i + 1];
      r->coeffs[4 * i + 2] = (1 << (logeta - 1)) - r->coeffs[4 * i + 2];
      r->coeffs[4 * i + 3] = (1 << (logeta - 1)) - r->coeffs[4 * i + 3];
    }
  }

  else if (logeta == 11)
  {
    for (i = 0; i < N / 8; ++i)
    {
      r->coeffs[8 * i + 0] = a[11 * i + 0];
      r->coeffs[8 * i + 0] |= (Q_SIZE)a[11 * i + 1] << 8;
      r->coeffs[8 * i + 0] &= 0x7ff;

      r->coeffs[8 * i + 1] = a[11 * i + 1] >> 3;
      r->coeffs[8 * i + 1] |= (Q_SIZE)a[11 * i + 2] << 5;
      r->coeffs[8 * i + 1] &= 0x7ff;

      r->coeffs[8 * i + 2] = a[11 * i + 2] >> 6;
      r->coeffs[8 * i + 2] |= (Q_SIZE)a[11 * i + 3] << 2;
      r->coeffs[8 * i + 2] |= (Q_SIZE)a[11 * i + 4] << 10;
      r->coeffs[8 * i + 2] &= 0x7ff;

      r->coeffs[8 * i + 3] = a[11 * i + 4] >> 1;
      r->coeffs[8 * i + 3] |= (Q_SIZE)a[11 * i + 5] << 7;
      r->coeffs[8 * i + 3] &= 0x7ff;

      r->coeffs[8 * i + 4] = a[11 * i + 5] >> 4;
      r->coeffs[8 * i + 4] |= (Q_SIZE)a[11 * i + 6] << 4;
      r->coeffs[8 * i + 4] &= 0x7ff;

      r->coeffs[8 * i + 5] = a[11 * i + 6] >> 7;
      r->coeffs[8 * i + 5] |= (Q_SIZE)a[11 * i + 7] << 1;
      r->coeffs[8 * i + 5] |= (Q_SIZE)a[11 * i + 8] << 9;
      r->coeffs[8 * i + 5] &= 0x7ff;

      r->coeffs[8 * i + 6] = a[11 * i + 8] >> 2;
      r->coeffs[8 * i + 6] |= (Q_SIZE)a[11 * i + 9] << 6;
      r->coeffs[8 * i + 6] &= 0x7ff;

      r->coeffs[8 * i + 7] = a[11 * i + 9] >> 5;
      r->coeffs[8 * i + 7] |= (Q_SIZE)a[11 * i + 10] << 3;
      r->coeffs[8 * i + 7] &= 0x7ff;

      r->coeffs[8 * i + 0] = (1 << (logeta - 1)) - r->coeffs[8 * i + 0];
      r->coeffs[8 * i + 1] = (1 << (logeta - 1)) - r->coeffs[8 * i + 1];
      r->coeffs[8 * i + 2] = (1 << (logeta - 1)) - r->coeffs[8 * i + 2];
      r->coeffs[8 * i + 3] = (1 << (logeta - 1)) - r->coeffs[8 * i + 3];
      r->coeffs[8 * i + 4] = (1 << (logeta - 1)) - r->coeffs[8 * i + 4];
      r->coeffs[8 * i + 5] = (1 << (logeta - 1)) - r->coeffs[8 * i + 5];
      r->coeffs[8 * i + 6] = (1 << (logeta - 1)) - r->coeffs[8 * i + 6];
      r->coeffs[8 * i + 7] = (1 << (logeta - 1)) - r->coeffs[8 * i + 7];
    }
  }
}