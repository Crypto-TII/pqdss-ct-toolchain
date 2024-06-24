# 

## Generate src test file

```shell
python3 draft/ct_toolchain.py generic_tests --tools TOOL_NAME --target_basename FUNCTION_NAME --target_header RELATIVE_PATH_TO_THE_HEADER_FILE --test_harness PATH_TO_TEST_FILE_TO_BE_GENERATED
```


## Example

```shell
python3 draft/ct_toolchain.py generic_tests --tools ctgrind --target_basename crypto_sign --target_header candidates/mpc-in-the-head/mirith/Optimized_Implementation/mirith_avx2_Ia_fast/sign.h  --test_harness TEST/my_test.c 
```

The test file `my_test.c` will be generated into the folder `TEST`.

`NB`: The supported tools are: 
- binsec
- ctgrind
- dudect
- flowtracker

## Compilation

Each tool comes with its required flags to compile a given target

- ctgrind: ` -Wall -ggdb  -std=c99  -Wextra`
- dudect: `-std=c11`


## Execution

- ctgrind: `valgrind -s --track-origins=yes --leak-check=full --show-leak-kinds=all --verbose --log-file=GIVEN_LOG_FILE  ./PATH_TO_EXECUTABLE`
- dudect: `timeout TIMEOUT_IN_SECONDS_OR_HOUR ./PATH_TO_EXECUTABLE`