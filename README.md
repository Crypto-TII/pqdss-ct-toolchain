# Toolchain consisting of binsec - timecop - dudect


## What is in this repository ? 
This repository contains the following folders:

* `candidates`: contains the Post-Quantum Digital Signatures Schemes (PQDSS) implementations, selected for the 2nd round at the NIST Call
  for proposals for PQC-based signature schemes. The candidates are classified according to the type-based signature scheme. Here
  are the different folders: `code`, `lattice`, `mpc-in-the-head`, `symmetric`, `isogeny`, `mutlivariate`.
*  `cttoolchain`: consist of the following files:
    * `cli.py`: Command-Line-Interface to run the tests (ct tests on pqdss implementations - generic tests);
    * `ct_toolchain.py`: main script to use the toolchain;
    * `pqdss_ct_tests.py`: script to run constant-time tests on pqdss implementations;
    * `tools.py`: contains functions for custom templates and execution for the constant-time tests on pqdss implementations;
    * `utils.py`: contains common used functions
* `pqdss-toolchain`: contains required files (*Dockerfile*, *.sh* files) and additional libraries source files, namely valgrind,
    to build a Docker image consisting of the required packages and requirements to compile and run constant-time tests on the implementations
    with the following constant-time check tools: binsec, timecop, dudect.
* `user_entry_point`: contains files on the user entry point for the different tests.
  * `candidates.json`: pqdss candidates information
 
    

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


## Docker

### Docker Installation

For Docker Desktop installation, please visit:  https://docs.docker.com/install/

### Build locally Docker image

#### Base image: binsec/binsec:latest 

```shell
cd pqdss-toolchain && docker build -t DOCKER_IMAGE_NAME:TAG -f toolchain-from-binsec-dockerfile/Dockerfile .
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

## Feature supported 

Our toolchain supports the following feature:

- `pqdss-ct-tests`: constant-time tests on pqdss implementations


To see the list of features supported by our toolchain, type:

```shell
python3 cttoolchain/ct_toolchain.py --help 
```
Or 

```shell
python3 cttoolchain/ct_toolchain.py -h 
```

Here are some options
### Command-Line-Interface (CLI) Flags
- `tools`: list of tools that a given candidate will be tested with, i.e. binsec, timecop and dudect. The tools are white space-separated
- `candidate`: NIST candidate. Ex: mirath, perk, ryde, sqisign etc.
- `instances`: the list of the different parameters set based folders. 
    Ex: mirath_tcith_1a_fast  mirath_tcith_1a_short etc.. The instance folders are white space-separated.
- `compile`: by default, its value is ***yes***. If the targeted executable has already been generated in a previous execution, and if 
   we just want to run the test, then set this option to ***no***.
- `run`: by default, its value is ***yes***. If we just want to compile, then set this option to ***no***.
- `depth`: this flag is meant for the use of binsec tool. The default value in our implementation is ***1000000***. The default value
    set by the authors of binsec tool is ***1000000***.
- `algorithms`: the patterns of the algorithm to be tested. default value: ***sign***
- `additional_options`: additional build/compilation options with CMakeList.txt/Makefile
- `number_measurements`: number of measurements for Dudect. The default value is ***1e4***.
- `timeout`: timeout in seconds for dudect execution. The default value is ***900***. To run dudect without *timeout*, set the value of this
  option to ***no***

The list of the options are not exhaustive and depends on the feature (pqdss ct tests and generic ct tests).


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

#### All instances of all candidates

```shell
python3 cttoolchain/ct_toolchain.py --all tools=TOOL OPTION1=VALUE1  OPTION2=VALUE2 ...
```

##### Example

Run tests with Timecop for all the candidates.

```shell
python3 cttoolchain/ct_toolchain.py --all tools=timecop  
```

#### Structure of the folders created with the scripts

Here's the structure of the generated files:

```
CANDIDATE
└── TOOL
    └── INSTANCE     
        ├── CANDIDATE_sign
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
- `candidate`: ryde
- `Instance`: ryde1f


```
python3 toolchain-scripts/toolchain_script.py --candidate ryde --tools binsec --instances ryde1f
```

```
mpc-in-the-head
└── ryde
        ├── binsec
            └── ryde1f
                ├── ryde_sign
                    ├── cfg_sign.ini
                    ├── crypto_sign_output.txt
                    ├── sign.toml
                    ├── test_harness_crypto_sign
                    ├── test_harness_crypto_sign.c
                    ├── test_harness_crypto_sign.gdb
                    └── test_harness_crypto_sign.snapshot
```

**NOTE**

There some other specific cases, but for all the candidates, the common path to the generated files is:

`CANDIDATE/TOOL`.

For the specific case of `Timecop`, our toolchain generates two additional files: a `summary` of the findings and its
corresponding `json file`.


```
python3 toolchain-scripts/toolchain_script.py --candidate ryde --tools timecop --instances ryde1f
```

```
mpc-in-the-head
└── ryde
        ├── Timecop
            └── ryde1f
                └── ryde_sign
                    ├── crypto_sign_output.txt
                    ├── crypto_sign_output_report.json
                    ├── crypto_sign_output_summary.log
                    ├── test_harness_crypto_sign
                    └── test_harness_crypto_sign.c

```

**NOTE**: For `mirath`, the test harness has already been created into each instance.

#### Specific cases


- ryde - mirath:

For the instances `ryde3s - ryde5f -  ryde5s` and for `mirath_tcith_3*_short - mirath_tcith_5*_* - `, the stack size must be increased:

```yaml
ulimit -s 16384 
```

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


- less - cross

For the previous candidates, all the instances are compiled and run sequentially. 
The script invocation has no option `--instances`

```shell
python3 cttoolchain/ct_toolchain.py pqdss-ct-tests --tools TOOL --candidate less
```



#### Constant Time Tests results raw-output

For a given tool, the information on the execution of the tests on a given instance of a given candidate can be found in:

`CANDIDATE/TOOL/INSTANCE/CANDIDATE_sign/crypto_sign_output.txt`

#### Specific cases

- For the candidates `less - cross - sqisign`, the raw-output can be found in: 

`CANDIDATE/TOOL/CANDIDATE_sign/crypto_sign_output.txt`

There some other specific cases, but for all the candidates, the common path to find the constant time 
tests raw-output is: 

`CANDIDATE/TOOL`.

The tests with `Timecop` produce two additional files, namely `crypto_sign_output_summary.log` and its 
corresponding `crypto_sign_output_report.json` file which consist in a summary of the issues raised by the tools.


