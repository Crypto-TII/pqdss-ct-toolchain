
# Run tests


## Constant-time tests

## Benchmark tests

```shell
python3 cttool-draft/main_test.py benchmark --entry_point candidates.json --candidate CANIDATE --instances INSTANCE --cpu_cores_isolated 1 --benchmark_template yes
```

### Example

```shell
python3 cttool-draft/main_test.py benchmark --entry_point candidates.json --candidate perk --instances perk-128-fast-3 --cpu_cores_isolated 1 --benchmark_template yes --custom_bench yes --candidate_bench no
```