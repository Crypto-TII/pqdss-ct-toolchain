# NOTES


## Timecop

- keypair: OK
- sign: 

### Issue 1

```shell
rand_range_q_state_elements <-- generator_SF_seed_expand <-- LESS_sign <-- crypto_sign  
```

```shell
- DEF_RAND_STATE(rand_range_q_state_elements, FQ_ELEM, 0, Q-1)
- rand_range_q_state_elements(&csprng_state, res->values[i], N-K);
```

Into LESS_sign
```shell
// Public G_0 expansion
rref_generator_mat_t G0_rref;
generator_SF_seed_expand(&G0_rref, SK->G_0_seed);
```

State: False positif: the parameters of the `generator_SF_seed_expand` are `public`

### Issue 2
Function: `int generator_RREF(generator_mat_t *G, uint8_t is_pivot_column[N_pad])`

`generator_RREF <-- prepare_digest_input`

```shell
while (pivc < N) {
            while (j < K) {
                sc = G->values[j][pivc];
                if (sc != 0) { // ISSUE 2
                    goto found;
                }

                j++;
            }
            pivc++;     /* move to next col */
            j = i;      /*starting from row to red */
        }
```

```shell
generator_mat_t G_dagger; //G in the previous algorithm
memset(&G_dagger,0,sizeof(generator_mat_t));
generator_monomial_mul(&G_dagger, G, Q_in);
```

```shell
generator_mat_t full_G0;
generator_rref_expand(&full_G0, &G0_rref);
...
...
prepare_digest_input(&V_array, &Q_bar_actions[i], &full_G0, &Q_tilde);
```

