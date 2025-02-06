#define _GNU_SOURCE

#include <unistd.h>
#include <sys/syscall.h>

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "randombytes.h"
#include "api.h"


#define NB_TEST 25
#define NB_SAMPLES 25



inline static uint64_t cpucyclesStart (void) {
    unsigned hi, lo;
    __asm__ __volatile__ (	"CPUID\n\t"
                "RDTSC\n\t"
                "mov %%edx, %0\n\t"
                "mov %%eax, %1\n\t"
                : "=r" (hi), "=r" (lo)
                :
                : "%rax", "%rbx", "%rcx", "%rdx");

    return ((uint64_t) lo) ^ (((uint64_t) hi) << 32);
}



inline static uint64_t cpucyclesStop (void) {
    unsigned hi, lo;
    __asm__ __volatile__(	"RDTSCP\n\t"
                "mov %%edx, %0\n\t"
                "mov %%eax, %1\n\t"
                "CPUID\n\t"
                : "=r" (hi), "=r" (lo)
                :
                : "%rax", "%rbx", "%rcx", "%rdx");

    return ((uint64_t) lo) ^ (((uint64_t) hi) << 32);
}



int main(void) {

    unsigned long long ryde_5f_mlen = 1;
    unsigned long long ryde_5f_smlen;
    unsigned char ryde_5f_m[ryde_5f_mlen];
    ryde_5f_m[0] = 0;

    unsigned char ryde_5f_pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char ryde_5f_sk[CRYPTO_SECRETKEYBYTES];
    unsigned char ryde_5f_sm[CRYPTO_BYTES + ryde_5f_mlen];

    unsigned long long timer, t1, t2;
    unsigned long long ryde_5f_keypair_mean = 0, ryde_5f_crypto_sign_mean = 0, ryde_5f_crypto_sign_open_mean = 0;
    int ryde_5f_failures = 0;



    unsigned char seed[48] = {0};
//    (void)syscall(SYS_getrandom, seed, 48, 0);
    randombytes_init(seed, NULL, 256);



    /*************/
    /* RYDE-5F */
    /*************/

    // Cache memory heating
    for(size_t i = 0 ; i < NB_TEST ; i++) {
        crypto_sign_keypair(ryde_5f_pk, ryde_5f_sk);
    }



    // Measurement
    for(size_t i = 0 ; i < NB_SAMPLES ; i++) {
        printf("Benchmark (crypto_sign_keypair):\t");
        printf("%2lu%%", 100 * i / NB_SAMPLES);
        fflush(stdout);
        printf("\r\x1b[K");

        timer = 0;

        for(size_t j = 0 ; j < NB_TEST ; j++) {
            randombytes(seed, 48);
            randombytes_init(seed, NULL, 256);

            t1 = cpucyclesStart();
            crypto_sign_keypair(ryde_5f_pk, ryde_5f_sk);
            t2 = cpucyclesStop();

            timer += t2 - t1;
        }

        ryde_5f_keypair_mean += timer / NB_TEST;
    }
    printf("\nBenchmark (crypto_sign_keypair)\n");



    for(size_t i = 0 ; i < NB_SAMPLES ; i++) {
        printf("Benchmark (crypto_sign):\t");
        printf("%2lu%%", 100 * i / NB_SAMPLES);
        fflush(stdout);
        printf("\r\x1b[K");

        randombytes(seed, 48);
        randombytes_init(seed, NULL, 256);

        crypto_sign_keypair(ryde_5f_pk, ryde_5f_sk);
        timer = 0;

        for(size_t j = 0 ; j < NB_TEST ; j++) {
            randombytes(seed, 48);
            randombytes_init(seed, NULL, 256);

            t1 = cpucyclesStart();
            crypto_sign(ryde_5f_sm, &ryde_5f_smlen, ryde_5f_m, ryde_5f_mlen, ryde_5f_sk);
            t2 = cpucyclesStop();

            timer += t2 - t1;
        }

        ryde_5f_crypto_sign_mean += timer / NB_TEST;
    }
    printf("Benchmark (crypto_sign)\n");



    for(size_t i = 0 ; i < NB_SAMPLES ; i++) {
        printf("Benchmark (crypto_sign_open):\t");
        printf("%2lu%%", 100 * i / NB_SAMPLES);
        fflush(stdout);
        printf("\r\x1b[K");

        randombytes(seed, 48);
        randombytes_init(seed, NULL, 256);

        crypto_sign_keypair(ryde_5f_pk, ryde_5f_sk);
        crypto_sign(ryde_5f_sm, &ryde_5f_smlen, ryde_5f_m, ryde_5f_mlen, ryde_5f_sk);
        if (crypto_sign_open(ryde_5f_m, &ryde_5f_mlen, ryde_5f_sm, ryde_5f_smlen, ryde_5f_pk) == -1) { ryde_5f_failures++; }
        timer = 0;

        for(size_t j = 0 ; j < NB_TEST ; j++) {
            randombytes(seed, 48);
            randombytes_init(seed, NULL, 256);

            t1 = cpucyclesStart();
            crypto_sign_open(ryde_5f_m, &ryde_5f_mlen, ryde_5f_sm, ryde_5f_smlen, ryde_5f_pk);
            t2 = cpucyclesStop();

            timer += t2 - t1;
        }

        ryde_5f_crypto_sign_open_mean += timer / NB_TEST;
    }
    printf("Benchmark (crypto_sign_open)\n");



    printf("\n RYDE-5F");
    printf("\n  Failures: %i", ryde_5f_failures);
    printf("\n  crypto_sign_keypair: %lld CPU cycles", ryde_5f_keypair_mean / NB_SAMPLES);
    printf("\n  crypto_sign:         %lld CPU cycles", ryde_5f_crypto_sign_mean / NB_SAMPLES);
    printf("\n  crypto_sign_open:    %lld CPU cycles", ryde_5f_crypto_sign_open_mean / NB_SAMPLES);
    printf("\n\n");

    return 0;
}

