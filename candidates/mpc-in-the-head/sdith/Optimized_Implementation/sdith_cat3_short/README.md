# vole-sd

## prerequisites (ssl is for KATs)

```sh
apt install libssl-dev cmake build-essential
```

## build

```sh
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

# test

```sh
# bench 
./build/bench_sdith

# benchmarks (better in Release mode)
./build/generator/PQCGenKat_sign
```

