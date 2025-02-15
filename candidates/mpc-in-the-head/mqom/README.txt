MQOM2
=====

This submission package is composed of the following folders:

KAT/
    mqom2_<category>_<field>_<tradeoff>_<variant>/
        KAT vectors for mqom2_<category>_<field>_<tradeoff>_<variant>.

Optimized_Implementation_AVX2/
    mqom2_<category>_<field>_<tradeoff>_<variant>/
        AVX2-based Optimized implementation for mqom2_<category>_<field>_<tradeoff>_<variant>.

Optimized_Implementation_GFNI/
    mqom2_<category>_<field>_<tradeoff>_<variant>/
        GFNI-based Optimized implementation for mqom2_<category>_<field>_<tradeoff>_<variant>.

Reference_Implementation/
    mqom2_<category>_<field>_<tradeoff>_<variant>/
        Reference implementation for mqom2_<category>_<field>_<tradeoff>_<variant>.

Reference_Implementation_Python/
    Generic Reference implementation in Python3.

Supporting_Documentation/
    cover_sheet.pdf
    specifications.pdf
    IP_Statements/
        IP statements of submitters

Notes
======

Each implementation under Reference_Implementation and
Optimized_Implementation_AVX2/GFNI has its own Makefile; when used, it compiles
the code along with the test vector generator. Execute
    > make sign; ./sign
which produces the .req and .rsp files, which should match the ones
provided in KAT/.
