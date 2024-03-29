#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <stdio.h>
#include <string.h>
#include <immintrin.h>

#include "sampling.h"
#include "../sha3/shake.h"
#include "../params.h"
#include "../util.h"
#include "../normaldist/normaldist.h"
#include "samplez.h"

#define FACTOR 49.78042331916893 // sqrt(sigma_prime_square - 1)

void multiply_fixed_float_avx2(double *E, size_t size, double factor, double *result)
{
	__m256d factor_vec = _mm256_set1_pd(factor);
	for (size_t i = 0; i < size; i += 4)
	{
		// __m256d e_avx2 = _mm256_setr_pd(-*E, -*(E + 1), -*(E + 2), -*(E + 3));
		__m256d e_avx2 = _mm256_loadu_pd(E);
		__m256d result_vec = _mm256_mul_pd(e_avx2, factor_vec);
		_mm256_storeu_pd(result + i, result_vec);
		E = E + 4;
	}
}

void samplep(int16_t *p, const uint8_t *sk, double *L_22, double *L_32, double *L_33, uint8_t seed[32])
{
	prng rng;
	get_seed(32, &rng, seed);
	uint8_t randomness[2 * PARAM_SEED_BYTES];
	prng_get_bytes(&rng, randomness, 2 * PARAM_SEED_BYTES);

	double factor1 = PARAM_q * PARAM_R / FACTOR, factor2 = PARAM_q * PARAM_R * FACTOR;
	
	// sample y ~ N(0, 1)
	double *y = malloc((PARAM_N + 2 * PARAM_M) * sizeof(double));
	normaldist(y, PARAM_N + 2 * PARAM_M, randomness); 
	double *y0 = y, *y1 = y + PARAM_M, *y2 = y + PARAM_M + PARAM_N;

	double *temp0 = malloc(PARAM_M * sizeof(double));
	double *temp1 = malloc(PARAM_N * sizeof(double));
	double *c = malloc((PARAM_N + 2 * PARAM_M) * sizeof(double));
	double *c0 = c, *c1 = c + PARAM_M, *c2 = c + PARAM_M + PARAM_N;
	multiply_fixed_float_avx2(y2, PARAM_M, factor2, c2);
	multiply_fixed_float_avx2(y2, PARAM_M, -factor1, y2);

	tri_mat_mul_avx2_con1(temp1, L_22, y1, PARAM_N); 
	
	// memcpy(c1, temp1, PARAM_N * sizeof(double));
	for (int i = 0; i < PARAM_N; i++)
		c1[i] = temp1[i];
	for (int i = 0; i < PARAM_N/4;i++){
		int16_t S[4*PARAM_M];
		unpack_mat_r_avx2(S, sk+2 * PARAM_M * PARAM_M / 8+PARAM_M*i, PARAM_M);
		real_mat_mul_avx2_con1_int16(temp1+4*i, S, y2, 4, PARAM_M);
		}
	real_mat_add(c1, c1, temp1, PARAM_N, 1);
	
	// tri_mat_mul(temp0, L_33, y0, PARAM_M, 1);
	tri_mat_mul_avx2_con1(temp0, L_33, y0, PARAM_M); 

	// memcpy(c0, temp0, PARAM_M * sizeof(double));
	for (int i = 0; i < PARAM_M; i++)
		c0[i] = temp0[i];
	
	real_mat_mul_avx2_con1(temp0, L_32, y1, PARAM_M, PARAM_N);
	real_mat_add(c0, c0, temp0, PARAM_M, 1);

	for (int i = 0; i < PARAM_M / 4;i++){
		int16_t E[4*PARAM_M];
		unpack_mat_r_avx2(E, sk+PARAM_M*i, PARAM_M);
		real_mat_mul_avx2_con1_int16(temp0+4*i, E, y2, 4, PARAM_M);
	}
	real_mat_add(c0, c0, temp0, PARAM_M, 1);
	
	prng rng_samplez;
	get_seed(32, &rng_samplez, randomness + PARAM_SEED_BYTES);
	// sample p with c[i] being the center
	for (int i = 0; i < PARAM_N + 2 * PARAM_M; i++)
		p[i] = samplez(c[i], &rng_samplez);
	
	free(y);
	free(temp0);
	free(temp1);
	free(c);

}

void sampleF(int16_t *z, int16_t *v, uint8_t seed[32])
{
	prng rng;
	get_seed(32, &rng, seed);
	for (int i = 0; i < PARAM_M; ++i)
		samplef(&z[i], v[i], &rng);
}

void samplef(int16_t *z, int16_t v, prng *rng)
{
	int16_t roundedv = (int16_t)floor(1.0 * v / PARAM_p + 0.5) % PARAM_q;
	if (roundedv < 0)
		roundedv += PARAM_q;
	*z = PARAM_q * base_sampler_RCDT_discrete_center(PARAM_q - roundedv, rng) - PARAM_q + roundedv;
}
