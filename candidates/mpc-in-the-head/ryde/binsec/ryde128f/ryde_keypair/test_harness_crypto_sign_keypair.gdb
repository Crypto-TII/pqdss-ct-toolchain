
set pagination off
set env LD_BIND_NOW=1
set env GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX2_Usable
break main
start
generate-core-file candidates/mpc-in-the-head/ryde/binsec/ryde128f/ryde_keypair/test_harness_crypto_sign_keypair.snapshot
kill
quit
