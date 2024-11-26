
# Run tests


## Constant-time tests

## Benchmark tests

```shell
python3 cttool-draft/main_test.py benchmark  --candidate CANIDATE --instances INSTANCE
```

### Example

```shell
python3 cttool-draft/main_test.py benchmark --candidate perk --instances perk-128-fast-3
```

### Run all instances of a candidate

```shell
python3 cttool-draft/main_test.py benchmark  --candidate CANIDATE
```


### Run all instances of all candidates (IN PROGRESS)


```shell
 python3 cttool-draft/main_test.py --all benchmark
```