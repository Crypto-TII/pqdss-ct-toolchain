
#!/bin/sh
opt -basicaa -load AliasSets.so -load DepGraph.so -load bSSA2.so -bssa2    -xmlfile rbc_crypto_sign_keypair.xml ../build/mirith_keypair/rbc_crypto_sign_keypair.rbc 2>crypto_sign_keypair_output.out
