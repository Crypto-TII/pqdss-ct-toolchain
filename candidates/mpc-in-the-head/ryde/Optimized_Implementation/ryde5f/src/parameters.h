/**
 * \file parameters.h
 * \brief Parameters of the RYDE scheme
 */

#ifndef RYDE_5F_PARAMETER_H
#define RYDE_5F_PARAMETER_H

#define RYDE_5F_SECURITY 256                /**< Expected security level (bits) */
#define RYDE_5F_SECURITY_BYTES 32           /**< Expected security level (bytes) */

#define RYDE_5F_SECRET_KEY_BYTES 64         /**< Secret key size */
#define RYDE_5F_PUBLIC_KEY_BYTES 133        /**< Public key size */
#define RYDE_5F_SIGNATURE_BYTES 14609       /**< Signature size */

#define RYDE_5F_SALT_BYTES 64               /**< Expected salt (bytes) */
#define RYDE_5F_HASH_BYTES 64               /**< Expected hash (bytes) */

#define RYDE_5F_PARAM_Q 2                   /**< Parameter q of the scheme (finite field GF(q^m)) */
#define RYDE_5F_PARAM_M 67                  /**< Parameter m of the scheme (finite field GF(q^m)) */
#define RYDE_5F_PARAM_K 55                  /**< Parameter k of the scheme (code dimension) */
#define RYDE_5F_PARAM_N 67                  /**< Parameter n of the scheme (code length) */
#define RYDE_5F_PARAM_R 6                   /**< Parameter r of the scheme (rank of vectors) */

#define RYDE_5F_PARAM_M_MASK 0x7            /**< Mask related to the representation of finite field elements */
#define RYDE_5F_PARAM_M_BYTES 9             /**< Number of bytes required to store a GF(2^m) element */
#define RYDE_5F_PARAM_M_WORDS 2             /**< Number of 64-bits words required to store a GF(2^m) element */
#define RYDE_5F_VEC_K_BYTES 461             /**< Number of bytes required to store a vector of size k */
#define RYDE_5F_VEC_N_BYTES 562             /**< Number of bytes required to store a vector of size n */
#define RYDE_5F_VEC_R_BYTES 51              /**< Number of bytes required to store a vector of size r */
#define RYDE_5F_VEC_N_MINUS_ONE_BYTES 553   /**< Number of bytes required to store a vector of size (n - 1) */
#define RYDE_5F_VEC_R_MINUS_ONE_BYTES 42    /**< Number of bytes required to store a vector of size (r - 1) */
#define RYDE_5F_VEC_R_MINUS_ONE_MASK 0x7f   /**< Mask related to the representation of a vector of size (r - 1) */
#define RYDE_5F_VEC_RHO_BYTES 34            /**< Number of bytes required to store a vector of size rho */
#define RYDE_5F_VEC_RHO_MASK 0xf            /**< Mask related to the representation of a vector of size rho */
#define RYDE_5F_MAT_FQ_BYTES 46             /**< Number of bytes required to store a binary matrix of size r x (n - r) */
#define RYDE_5F_MAT_FQ_MASK 0x3f            /**< Mask related to the representation of a binary matrix of size r x (n - r) */

#define RYDE_5F_PARAM_N_1 256               /**< Parameter N_1 of the scheme */
#define RYDE_5F_PARAM_N_2 256               /**< Parameter N_2 of the scheme */
#define RYDE_5F_PARAM_N_1_BITS 8            /**< Parameter N_1 of the scheme (bits) */
#define RYDE_5F_PARAM_N_2_BITS 8            /**< Parameter N_2 of the scheme (bits) */
#define RYDE_5F_PARAM_N_1_BYTES 1           /**< Parameter N_1 of the scheme (bytes) */
#define RYDE_5F_PARAM_N_2_BYTES 1           /**< Parameter N_2 of the scheme (bytes) */
#define RYDE_5F_PARAM_N_1_MASK 0xff         /**< Parameter N_1 of the scheme (mask) */
#define RYDE_5F_PARAM_N_2_MASK 0xff         /**< Parameter N_2 of the scheme (mask) */
#define RYDE_5F_PARAM_TAU 36                /**< Parameter tau of the scheme (number of iterations) */
#define RYDE_5F_PARAM_TAU_1 36              /**< Parameter tau_1 of the scheme (number of iterations concerning N1) */
#define RYDE_5F_PARAM_TAU_2 0               /**< Parameter tau_2 of the scheme (number of iterations concerning N2) */
#define RYDE_5F_PARAM_RHO 4                 /**< Parameter rho of the scheme (dimension of the extension)*/

#define RYDE_5F_PARAM_TREE_LEAVES 9216      /**< Number of leaves in the tree */

#define RYDE_5F_PARAM_CHALLENGE_1_BYTES 402 /**< Number of bytes required to store the first challenge */
#define RYDE_5F_PARAM_CHALLENGE_2_BYTES 36  /**< Number of bytes required to store the second challenge */
#define RYDE_5F_PARAM_W_BYTES 1             /**< Number of bytes in the second hash to be zero */
#define RYDE_5F_PARAM_W_MASK 0xf0           /**< Mask for the most significant byte in the second hash */
#define RYDE_5F_PARAM_T_OPEN 244            /**< Maximum sibling path length allowed */

#endif
