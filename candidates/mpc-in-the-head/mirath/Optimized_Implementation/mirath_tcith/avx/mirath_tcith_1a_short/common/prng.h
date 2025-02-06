
#ifndef PRNG_H
#define PRNG_H

#include <stdint.h>
#include "hash.h"

#include "KeccakHash.h"
typedef Keccak_HashInstance mirath_prng_t;

#define shake_init Keccak_HashInitialize_SHAKE128
#define shake_absorb(a, b, c) Keccak_HashUpdate(a, b, (c)*8)
#define shake_finalize(prng) Keccak_HashFinal(prng, NULL)
#define shake_squeeze(a, b, c) Keccak_HashSqueeze ((c), (a), (b*8))

#define shake_256 SHAKE256

/* Initialize 'prng' from 'salt' and 'seed'.
 * If 'salt == NULL' then 'salt' is ignored.
 * If 'seed == NULL' then 'seed' is ignored. */
void mirath_prng_init(mirath_prng_t *prng, const uint8_t *salt, const seed_t seed, uint32_t seed_size_bytes);

/* Write 'length' pseudorandom bytes over 'target',
 * update the internal state of 'prng'. */
void mirath_prng(mirath_prng_t *prng, void *target, size_t length);

#endif
