/*
 * Support functions for signatures (hash-to-point).
 *
 * ==========================(LICENSE BEGIN)============================
 *
 * Copyright (c) 2023  Squirrels Project
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * ===========================(LICENSE END)=============================
 *
 * @author   Guilhem Niot <guilhem.niot@gniot.fr>
 */

#include "inner.h"

/* see inner.h */
void Zf(hash_to_point)(inner_shake256_context *sc, discrete_vector *x) {
  for (int i = 0; i < SQUIRRELS_D-1; i++) {
    uint8_t buf[2];
    uint32_t w;

    inner_shake256_extract(sc, (void *)buf, sizeof buf);
    w = ((unsigned)buf[0] << 8) | (unsigned)buf[1];
    w = w & (SQUIRRELS_Q - 1); // Assumes that Q is a power of 2

    x->coeffs[i] = w;
  }

  x->coeffs[SQUIRRELS_D-1] = 0;
}
