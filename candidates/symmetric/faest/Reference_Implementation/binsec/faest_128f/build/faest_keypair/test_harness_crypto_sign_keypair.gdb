
set env LD_BIND_NOW=1
set env GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX2_Usable
b main
start
generate-core-file test_harness_crypto_sign_keypair.snapshot
kill
quit
