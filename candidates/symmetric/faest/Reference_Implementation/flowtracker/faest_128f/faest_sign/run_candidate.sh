
#!/bin/sh
opt -basicaa -load AliasSets.so -load DepGraph.so -load bSSA2.so -bssa2    -xmlfile rbc_crypto_sign.xml ../build/faest_sign/rbc_crypto_sign.rbc 2>crypto_sign_output.out
