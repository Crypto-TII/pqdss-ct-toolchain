

#include<time.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <sys/random.h>
#include <cpucycles.h>

#include "api.h"

//#include "rng.h"
#include "toolchain_randombytes.h"


#define MINIMUM_MSG_LENGTH 1
#define MAXIMUM_MSG_LENGTH 3300
#define TOTAL_ITERATIONS   1e3


typedef  uint64_t ticks;


void swap(uint64_t* a, uint64_t* b)
{
    uint64_t t = *a;
    *a = *b;
    *b = t;
}

/* Perofroms one step of pivot sorting with the last
	element taken as pivot. */
int partition (uint64_t arr[], int low, int high)
{
    uint64_t pivot = arr[high];
    int i = (low - 1);

    int j;
    for(j = low; j <= high- 1; j++)
    {
        if(arr[j] < pivot)
        {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

void quicksort(uint64_t arr[], int low, int high)
{
    if (low < high)
    {
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}


int main(void)
{

    snova_init();
	unsigned long long i = 0;
	unsigned long long iterations = TOTAL_ITERATIONS;
	unsigned long long min_msg_len = MINIMUM_MSG_LENGTH;
	unsigned long long max_msg_len = MAXIMUM_MSG_LENGTH;
	unsigned long long mlen = 0;
	unsigned long long smlen = 0;

	int pass;

	// For storing clock cycle counts
    uint64_t cc_mean = 0, cc_stdev = 0,
	cc0, cc1,
	*cc_sample =(uint64_t *)malloc(iterations * sizeof(uint64_t));

	// For storing keypair
	unsigned char *pk = (unsigned char *)malloc(CRYPTO_PUBLICKEYBYTES * iterations * sizeof(unsigned char));
	unsigned char *sk = (unsigned char *)malloc(CRYPTO_SECRETKEYBYTES * iterations * sizeof(unsigned char));

	// For storing plaintext messages
	unsigned char *m = (unsigned char *)malloc(max_msg_len * iterations * sizeof(unsigned char));
	ct_randombytes(m, max_msg_len * iterations);
	mlen =  max_msg_len * iterations;
	if(mlen < max_msg_len * iterations){
		printf("Error in generating random messages\n");
		return -1;
	}

	// For storing signed messages
	unsigned char *sm = (unsigned char *)malloc((CRYPTO_BYTES + max_msg_len) * iterations * sizeof(unsigned char));

	printf("Candidate: snova\n");
	printf("Security Level: \n");
	printf("Instance: \n");

	// ================== KEYGEN ===================
	cc_mean = 0; cc_stdev = 0;
	//Gather statistics
	for (i = 0; i < iterations; i++)
	{

		cc0 = cpucycles();;
		pass = crypto_sign_keypair(&pk[i*CRYPTO_PUBLICKEYBYTES], &sk[i*CRYPTO_SECRETKEYBYTES]);
		cc1 = cpucycles();;
		cc_sample[i] = cc1 - cc0;
		cc_mean += cc_sample[i];

		if(pass){
			printf("Error in Keygen\n");
			return -1;
		}
	};
	printf("Algorithm: Keygen:\n");
	cc_mean /= iterations;
	quicksort(cc_sample, 0, iterations - 1);

	// Compute the standard deviation
	for (i = 0; i < iterations; ++i){
		cc_stdev += (cc_sample[i] - cc_mean)*(cc_sample[i] - cc_mean);
	}
	cc_stdev = sqrt(cc_stdev / iterations);

	printf("Average running time (million cycles): \t %7.03lf\n", (1.0 * cc_mean) / 1000000.0);
	printf("Standard deviation (million cycles): \t %7.03lf\n", (1.0 * cc_stdev) / 1000000.0);
	printf("Minimum running time (million cycles): \t %7.03lf\n", (1.0 * cc_sample[0]) / 1000000.0);
	printf("First quartile (million cycles): \t \t %7.03lf\n", (1.0 * cc_sample[iterations/4]) / 1000000.0);
	printf("Median (million cycles):    \t \t %7.03lf\n", (1.0 * cc_sample[iterations/2]) / 1000000.0);
	printf("Third quartile (million cycles): \t %7.03lf\n", (1.0 * cc_sample[(3*iterations)/4]) / 1000000.0);
	printf("Maximum running time (million cycles): \t %7.03lf\n", (1.0 * cc_sample[iterations-1]) / 1000000.0);
	printf("\n");

	// ================== SIGNING ===================
	cc_mean = 0; cc_stdev = 0;
	// Gather statistics
	for (i = 0; i < iterations; i++)
	{
		mlen = min_msg_len + i*(max_msg_len - min_msg_len)/(iterations);
		smlen = mlen + CRYPTO_BYTES;
		cc0 = cpucycles();;
		pass = crypto_sign(&sm[(CRYPTO_BYTES + max_msg_len)*i], &smlen, &m[max_msg_len*i], mlen, &sk[i*CRYPTO_SECRETKEYBYTES]);
		cc1 = cpucycles();;
		cc_sample[i] = cc1 - cc0;
		cc_mean += cc_sample[i];

		if(pass)
		{
			printf("Error in signing\n");
			return -1;
		}
	};
	printf("Candidate: snova\n");
	printf("Security Level: \n");
	printf("Instance: \n");
	printf("Algorithm: Sign:\n");
	cc_mean /= iterations;
	quicksort(cc_sample, 0, iterations - 1);

	// Compute the standard deviation

	for (i = 0; i < iterations; ++i){
		cc_stdev += (cc_sample[i] - cc_mean)*(cc_sample[i] - cc_mean);
}
	cc_stdev = sqrt(cc_stdev / iterations);

	printf("Average running time (million cycles): \t %7.03lf\n", (1.0 * cc_mean) / 1000000.0);
	printf("Standard deviation (million cycles): \t %7.03lf\n", (1.0 * cc_stdev) / 1000000.0);
	printf("Minimum running time (million cycles): \t %7.03lf\n", (1.0 * cc_sample[0]) / 1000000.0);
	printf("First quartile (million cycles): \t %7.03lf\n", (1.0 * cc_sample[iterations/4]) / 1000000.0);
	printf("Median (million cycles): \t %7.03lf\n", (1.0 * cc_sample[iterations/2]) / 1000000.0);
	printf("Third quartile (million cycles): \t %7.03lf\n", (1.0 * cc_sample[(3*iterations)/4]) / 1000000.0);
	printf("Maximum running time (million cycles): \t %7.03lf\n", (1.0 * cc_sample[iterations-1]) / 1000000.0);
	printf("\n");

	// ================== VERIFICATION ===================
	cc_mean = 0; cc_stdev = 0;
	// Gather statistics
	for (i = 0; i < iterations; i++)
	{
		mlen = min_msg_len + i*(max_msg_len - min_msg_len)/(iterations);
		smlen = mlen + CRYPTO_BYTES;
		cc0 = cpucycles();;
		pass = crypto_sign_open(&m[max_msg_len*i], &mlen, &sm[(CRYPTO_BYTES + max_msg_len)*i], smlen, &pk[i*CRYPTO_PUBLICKEYBYTES]);
		cc1 = cpucycles();;
		cc_sample[i] = cc1 - cc0;
		cc_mean += cc_sample[i];

		if(pass){
			printf("Verification failed\n");
			return -1;
		}
	};

	printf("Candidate: snova\n");
	printf("Security Level: \n");
	printf("Instance: \n");
	printf("Algorithm: Verify:\n");
	cc_mean /= iterations;
	quicksort(cc_sample, 0, iterations - 1);

	// Compute the standard deviation
	for (i = 0; i < iterations; ++i){
		cc_stdev += (cc_sample[i] - cc_mean)*(cc_sample[i] - cc_mean);
}
	cc_stdev = sqrt(cc_stdev / iterations);

	printf("Average running time (million cycles): \t %7.03lf\n", (1.0 * cc_mean) / 1000000.0);
	printf("Standard deviation (million cycles): \t %7.03lf\n", (1.0 * cc_stdev) / 1000000.0);
	printf("Minimum running time (million cycles): \t %7.03lf\n", (1.0 * cc_sample[0]) / 1000000.0);
	printf("First quartile (million cycles): \t %7.03lf\n", (1.0 * cc_sample[iterations/4]) / 1000000.0);
	printf("Median (million cycles): \t %7.03lf\n", (1.0 * cc_sample[iterations/2]) / 1000000.0);
	printf("Third quartile (million cycles): \t %7.03lf\n", (1.0 * cc_sample[(3*iterations)/4]) / 1000000.0);
	printf("Maximum running time (million cycles): \t %7.03lf\n", (1.0 * cc_sample[iterations-1]) / 1000000.0);
	printf("\n");

	// -----------------------------------------------------
	free(cc_sample);
	free(m);
	free(sm);
	free(pk);
	free(sk);
	return 0;
}

