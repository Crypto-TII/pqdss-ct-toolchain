# Toolchain consisting of binsec - timecop - dudect


## What is in this repository ? 
This repository contains the following folders:

* `candidates`: contains the Post-Quantum Digital Signatures Schemes (PQDSS) implementations, selected for the 2nd round at the NIST Call
  for proposals for PQC-based signature schemes. The candidates are classified according to the type-based signature scheme. Here
  are the different folders: `code`, `lattice`, `mpc-in-the-head`, `symmetric`, `isogeny`, `mutlivariate`.
*  `cttoolchain`: consist of the following files:
    * `pqdss_benchmarks.py`: script to run benchmarks on pqdss implementations;
    * `cli.py`: Command-Line-Interface to run the tests (ct tests and benchmarks on pqdss implementations - generic tests);
    * `generics_ct_tests.py`: script to run generic constant-time tests given a binary (shared library of the target) to be linked to;
    * `ct_toolchain.py`: main script to use the toolchain;
    * `pqdss_ct_tests.py`: script to run constant-time tests on pqdss implementations;
    * `tools.py`: contains functions for custom templates and execution for the constant-time tests on pqdss implementations;
    * `utils.py`: contains common used functions
    * `tests_results`: Excel file consisting in a table of the results of the tests with the tools.
* `examples`: contains examples for generics constant-time tests
* `pqdss-toolchain`: contains required files (*Dockerfile*, *.sh* files) and additional libraries source files, namely gmp-6.1.2 and valgrind,
    to build a Docker image consisting of the required packages and requirements to compile and run constant-time tests on the implementations
    with the following constant-time check tools: binsec, timecop, dudect.
* `user_entry_point`: contains files on the user entry point for the different tests.
  * `candidates.json`: pqdss candidates information
  * `generics_tests.json`: contains information on targets to be tested (generic constant-time tests);
    

## Benefits of using our toolchain

- Tools libraries/packages: each of the tools above-mentioned has its requirements and necessary packages/libraries for 
compilation and execution of a given target. Our Dockerfile allows to not worry about 
 all those requirements as "everything" is already taken into account.
- Tool's required files to test a candidate: each of the tools need a specific file, related to the target
  to test. Our scripts allow to generate automatically all needed files (.c, .ini, .gdb, etc.).
- Tools commands to run tests on a target: each tool has its own commands (including necessary flags for compilation and commands for execution). 
Those requirements are also taken into account by our scripts.
- Test many instances of a (many) candidate(s):  generating required files, compiling and running tests for a given candidate and for all tools
 could take a non-negligible amount of time, especially when the tests must be performed on 
many instances of many candidates. Our scripts allow to gain a significant amount of time to achieve that goal.
- With our scripts, one can generate templates, improve them manually, compile and run tests. 


## Docker

### Docker Installation

For Docker Desktop installation, please visit:  https://docs.docker.com/install/

### Build locally Docker image

#### Base image: binsec/binsec:latest 

```shell
cd pqdss-toochain && docker build -t DOCKER_IMAGE_NAME:TAG -f toolchain-from-binsec-dockerfile/Dockerfile .
```

#### Example

```shell
cd pqdss-toolchain && docker build -t  my_image:0.1.0 -f toolchain-from-binsec-dockerfile/Dockerfile .
```


### Create a docker container mounted on the local directory

```shell
docker run -it -v $PWD:/home/CONTAINER_NAME DOCKER_IMAGE_NAME:TAG /bin/bash
```

#### Example

```shell
docker run -it -v $PWD:/home/pqdss_ct_tests my_image:0.1.0 /bin/bash
```

## Features supported 

Our toolchain supports the following features:

- `pqdss-ct-tests`: constant-time tests on pqdss implementations
- `pqdss-benchmarks`: benchmarks on pqdss implementations
- `generic-ct-tests`: generic constant-time tests


To see the list of features supported by our toolchain, type:

```shell
python3 cttoolchain/ct_toolchain.py --help 
```
Or 

```shell
python3 cttoolchain/ct_toolchain.py -h 
```


## List of options for each feature

To see the list of all options for a supported feature, type:

```
python3 cttoolchain/ct_toolchain.py FEATURE -h
```

### Example
```
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests -h
```

Here are some options
### Command-Line-Interface (CLI) Flags
- `entry_point`: path to the user entry point, i.e. .json file containing the information on the targets under tests.
- `tools`: list of tools that a given candidate will be tested with, i.e. binsec, timecop and dudect. The tools are white space-separated
- `candidate`: NIST candidate. Ex: mirith, sqisign, perk, mirath etc.
- `optimization_folder`: the Optimized Implementation folder. For most of the candidates, this 
    folder is named ***Optimized_Implementation***
- `instances`: the list of the different parameters set based folders. 
    Ex: mirith_avx2_Ia_fast  mirith_hypercube_avx2_IIIb_shortest etc.. The instance folders are white space-separated.
- `compile`: by default, its value is ***yes***. If the targeted executable has already been generated in a previous execution, and if 
   we just want to run the test, then set this option to ***no***.
- `run`: by default, its value is ***yes***. If we just want to compile, then set this option to ***no***.
- `depth`: this flag is meant for the use of binsec tool. The default value in our implementation is ***1000000***. But the default value
    set by the authors of binsec tool is ***1000***.
- `build`: the default name of build folder is *build*.
- `algorithms`: the patterns of the algorithm to be tested. default value: ***keypair***, ***sign***
- `cmake_addtional_definitions`: additional CMakeLists.txt definitions to compile the target candidate
- `additional_options`: additional build/compilation options with CMakeList.txt/Makefile
- `security_level`: candidate instance security level. This flag is specially for vox. The default value is ***256***
- `number_measurements`: number of measurements for Dudect. The default value is ***1e4***.
- `timeout`: timeout for dudect execution. The default value is ***86400***. To run dudect without *timeout*, set the value of this
  option to ***no***
- `ref_opt_add_implementation`: The target implementation to test. The possible values are: ***opt***, ***ref*** and ***add*** for 
 Reference, Optimized and Additional Implementations respectively.
- `cpu_cores_isolated`: list of cpu cores isolated, especially for benchmarks and tests with dudect.

The list of the options are not exhaustive and depends on the feature (pqdss ct tests/benchmarks and generic ct tests).


### Feature: pqdss-ct-tests

#### List of instances

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --candidate CANDIDATE --instances INSTANCES --tools TOOL
```
##### Example

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --candidate perk --instances perk-128-fast-3 --tools binsec
```

#### All instances

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --candidate CANDIDATE --tools TOOL
```
##### Example

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --candidate perk --tools binsec
```

#### Structure of the folders created with the scripts

Here's the structure of the generated files:

```
OPTIMISATION FOLDER
└── TOOL
    └── INSTANCE
        ├── CANDIDATE_keypair
        │   ├── required files for tests (.c file, .ini, .gdb, .snapshot)
        │   ├── TEST_HARNESS_crypto_sign_keypair
        │   └── output file of the test (.txt)
        └── CANDIDATE_sign
            ├── required files for tests (.c file, .ini, .gdb, .snapshot)
            ├── TEST_HARNESS_crypto_sign
            └── output file of the test (.txt)
```

`Remark`: According to the chosen tool, `TEST_HARNESS` is equal to the following patterns:
- `binsec`: test_harness
- `dudect`: dude
- `timecop`: taint

##### Example

- `tool`: binsec
- `candidate`: mirith
- `Optimizated Implementation folder`: Optimized_Implementation
- `Instance`: mirith_avx2_Ia_fast

Note: For each candidate, the Optimized implementation folder has a
default value: the one proposed by bidders.

```
python3 toolchain-scripts/toolchain_script.py --candidate mirith --tools binsec --instances mirith_avx2_Ia_fast
```

```
mpc-in-the-head
└── mirith
        ├── Optimized_Implementation
            ├── binsec
                └── mirith_avx2_Ia_fast
                    ├── mirith_keypair
                    │      ├── cfg_keypair.ini
                    │      ├── crypto_sign_keypair_output.txt
                    │      ├── test_harness_crypto_sign_keypair
                    │      ├── test_harness_crypto_sign_keypair.c
                    │      ├── test_harness_crypto_sign_keypair.gdb
                    │      └── test_harness_crypto_sign_keypair.snapshot
                    └── mirith_sign
                           ├── cfg_sign.ini
                           ├── crypto_sign_output.txt
                           ├── test_harness_crypto_sign
                           ├── test_harness_crypto_sign.c
                           ├── test_harness_crypto_sign.gdb
                           └── test_harness_crypto_sign.snapshot

```

#### Specific cases

- qruov

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --tools TOOL --candidate qruov --instances INSTANCE --additional_options platform=PLATFORM
```

where PLATFORM = avx2/avx512/portable64

 `avx2` is the default platform

- snova

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --tools TOOL --candidate snova --instances INSTANCE --additional_options platform=PLATFORM OPTIMISATION=OPTIMISATION_LEVEL

```

where PLATFORM = ref/opt/avx2 and OPTIMISATION_LEVEL=0/1/2
By default: PLATFORM=avx2 -  OPTIMISATION_LEVEL=2


- sqisign

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --tools TOOL --candidate sqisign  --additional_options SQISIGN_BUILD_TYPE=broadwell  CMAKE_BUILD_TYPE=Release

```

where PLATFORM = ref/opt/avx2 and OPTIMISATION_LEVEL=0/1/2
By default: PLATFORM=avx2 -  OPTIMISATION_LEVEL=2


- uov

`Remark`: Tests for uov must be done one instance at a time.

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --tools TOOL --candidate uov  --instance PLATFORM/INSTANCE 

```

where PLATFORM = amd64/avx2/gfni/neon and INSTANCE=I/II/III/I_pk/...

By default: PLATFORM=avx2

### Feature: pqdss-benchmarks

#### List of instances

```shell
python3 cttoolchain/ct_toolchain.py pqdss-benchmarks --candidate CANDIDATE --instances INSTANCES --cpu_cores_isolated CHOSEN_ISOLATED_CPU_CORE
```

##### Example

```shell
python3 cttoolchain/ct_toolchain.py pqdss-benchmarks --candidate mirith --instances mirith_avx2_Ia_fast --cpu_cores_isolated 8
```

#### All instances

```shell
python3 cttoolchain/ct_toolchain.py pqdss-benchmarks --candidate CANDIDATE --cpu_cores_isolated CHOSEN_ISOLATED_CPU_CORE
```

##### Example

```shell
python3 cttoolchain/ct_toolchain.py pqdss-benchmarks --candidate mirith --cpu_cores_isolated 8
```

### Feature: generic-ct-tests

#### User entry point

For generic constant-time tests, it is required from the user to fill a `.json` file (user entry point) with following information for a target:

```
{
  "targets": [
      {
          "TARGET_BASENAME": {
            "target_call": ,
            "target_return_type": ,
            "target_input_declaration": ,
            "target_include_header":,
            "link_binary": ,
            "path_to_include_directory": ,
            "secret_inputs": ,
            "compiler": ,
            "macro": ,
            "random_data": 
          }
      }
    
  ]
}
```

#### Example

```
{
    "targets": [
        {
          "ct_compare_byte_arrays": {
            "target_call": "ct_compare_byte_arrays(array1, array2, length)",
            "target_return_type": "void",
            "target_input_declaration": ["uint8_t array1[120]", "uint8_t *array2", "int length = 120"],
            "target_include_header": ["tests.h"],
            "link_binary": "examples/cttest.so",
            "path_to_include_directory": "examples",
            "secret_inputs": ["array1"],
            "compiler": "gcc",
            "macro": {"ARRAY_SIZE": 120},
            "random_data": {"array2": "120"}
          }
        }
    ]
}
```


```shell
python3 cttoolchain/ct_toolchain.py generic-ct-tests --entry_point PATH_TO_USER_ENTRY_POINT --target_basename TARGET_NAME --tools TOOL(S)
```

##### Example 

```shell
python3 cttoolchain/ct_toolchain.py generic-ct-tests --entry_point user_entry_point/generics_tests.json --target_basename TARGET_NAME --tools TOOL(S)
```


#### Generate templates only

```shell
python3 cttoolchain/ct_toolchain.py generic-ct-tests --entry_point PATH_TO_USER_ENTRY_POINT  --target_basename TARGET_NAME --tools TOOL(S) --template_only yes
```

#### Compile and run

When a template for a given tool is already generated, one can manually edit and improve it, then compile and run the tests.

```shell
python3 cttoolchain/ct_toolchain.py generic-ct-tests --entry_point PATH_TO_USER_ENTRY_POINT --target_basename TARGET_NAME --tools TOOL(S) --compile_run yes
```

#### Run only

When a template for a given tool is already generated and the test harness already compiled, 
one can directly run the tests with different options of the given tool.

```shell
python3 cttoolchain/ct_toolchain.py generic-ct-tests --entry_point PATH_TO_THE_USER_ENTRY_POINT --target_basename TARGET_NAME --tools TOOL(S) --run_only yes
```