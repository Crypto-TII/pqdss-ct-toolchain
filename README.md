# Toolchain consisting of binsec - ctgrind - dudect - flowtracker


## What is in this repository ? 
This repository contains the following folders: 
* `binsec-from-sources`: contains the folder gmp-6.1.2, a README.md and a Dockerfile that allow to build binsec from sources.
* `candidates`: contains the Post-Quantum Digital Signatures Schemes (PQDSS) implementations, submitted in the context of NIST Call 
for proposals for PQC-based signature schemes. The candidates are classified according to the type-based signature scheme. Here 
are the different folders: `code`, `lattice`, `mpc-in-the-head`, `symmetric`, `isogeny`, `mutlivariate` and `other`. The folder `candidates` contains
  the file `toolchain_randombytes.h` in which is defined the function `randombytes()` (copy of the function `randombytes()` of `dudect`). That function 
 is used to generate a random message as an input of `crypto_sign()` for the candidate `CROSS` (when the given tool is `ctgrind`). Indeed, we have some issues 
 to use the function `KAT_NIST_rng.h`  proposed by `CROSS` submitters.

* `toolchain`: contains required files (*Dockerfile*, *.sh* files) to build a Docker image consisting of the required packages
and requirements to compile and run candidates with the following constant-time check tools: binsec, ctgrind, dudect and flowtracker

* `toolchain-scripts`: consist of the following files 
  * `candidates_build.py`:  contains the functions that generate the *CMakeLists.txt/Makefile* of the candidates. For almost each candidate, the 
  content of the *CMakeLists.txt/Makefile* is a copy, except the targets for tests and kat files generation, of the one proposed in the candidate implementation.
  * `generic_functions.py`: contains generic functions for tools templates and other required files generation, functions to compile and run tools on the targets candidates 
  * `toolchain_script.py`: contains the functions `compile_run_candidate` 
  that allows to compile targets and run tests with a given tool. The scripts that create main parser and subparsers 
  for candidates are also part of this file.
* `tests_results`: Excel file consisting in a table of the results of the tests with the tools.


## Benefits of using our toolchain

- Tools libraries/packages: each of the tools above-mentioned has its requirements and necessary packages/libraries for 
compilation and execution of a given target. Our Dockerfile allows to not worry about 
 all those requirements as "everything" is already taken into account.
- Tool's required files to test a candidate: each of the tools need a specific file, related to the candidate
  to test. Our scripts allow to generate automatically all needed files (.c, .xml, .ini, etc.).
- Tools commands to run a candidate: each tool has its own commands (including necessary flags for compilation and commands for execution). 
Those requirements are also taken into account by our scripts.
- Test many instances of a (many) candidate(s):  generating required files, compiling and running a given candidate for all tools
 could take a non-negligible amount of time, especially when the tests must be performed on 
many instances of many candidates. Our scripts allow to gain a significant amount of time to achieve that goal.
- With our scripts, one can generate templates, improve them manually, compile and run tests. 


## Docker

### Docker Installation

For Docker Desktop installation, please visit:  https://docs.docker.com/install/

### Build locally Docker image

```shell
cd toochain
docker build -t DOCKER_IMAGE_NAME:VERSION .
```

### Create a docker container mounted on the local repository

```shell
docker run -it -v $PWD:/home/CONTAINER_NAME DOCKER_IMAGE_NAME:VERSION /bin/bash
```

## Build Binsec from sources

If, for any reason, one encounters issues on running binsec on some platforms, please build 
binsec from source by referring to: https://github.com/binsec/binsec/blob/master/INSTALL.md



## List of candidates already integrated

To see the list of all integrated candidates, type:

```
python3 toolchain-scripts/toolchain_script.py -h
```

## List of options to test a candidate

To see the list of all options for test of a given target (candidate), type:

```
python3 toolchain-scripts/toolchain_script.py CANDIDATE -h
```

## Example
```
python3 toolchain_script.py mirith -h
```
## Command-Line-Interface (CLI) Flags

- `tools`: list of tools that a given candidate will be tested with. Ex: binsec, ctgrind, dudect etc.. The tools are white space-separated

- `signature_type`: type-based signature. Ex: code, isogeny, lattice etc.
- `candidate`: NIST candidate. Ex: mirith, sqisign, perk, mira etc.
- `optimization_folder`: the Optimized Implementation folder. For most of the candidates, this 
    folder is named ***Optimized_Implementation***
- `instance_folders_list`: the list of the different parameters set based folders. 
    Ex: mirith_avx2_Ia_fast  mirith_hypercube_avx2_IIIb_shortest etc.. The instance folders are white space-separated.
- `rel_path_to_api`: the relative path to api.h from 
   *TOOL_NAME/INSTANCE_FOLDER/CANDIDATE_keypair(or sign)*. 
   Ex: From the folder *mpc-in-the-head/mirith/Optimized_Implementation/ctgrind/mirith_avx2_Ia_fast/mirith_keypair*, the real
   relative path to *api.h* would be: *rel_path_to_api ="../../../mirith_avx2_Ia_fast/api.h"*. But the script would add automatically the 
   name of the instance. Thus, *rel_path_to_api ="../../../api.h"*.
   If the file *api.h* doesn't contain the declaration of the crypto_sign_keypair and crypto_sign functions, then
   *rel_path_to_api = ""*.
- `rel_path_to_sign`: Similar to *rel_path_to_api*.
- `compile`: by default, its value is ***yes***. If the targeted executable has already been generated in a previous execution, and if 
   we just want to run the test, then set this option to ***no***.
- `run`: by default, its value is ***yes***. If we just want to compile, then set this option to ***no***.
- `depth`: this flag is meant for the use of binsec tool. The default value in our implementation is ***1000000***. But the default value
    set by the authors of binsec tool is ***1000***.
- `build`: the default name of build folder is *build*.
- `algorithms_patterns`: the patterns of the algorithm to be tested. default value: ***keypair***, ***sign***
- `is_rng_outside_folder`: for some of the candidates, the folder containing the header file, (rng.h, randombytes, etc.), in which is defined
the function that generates random data.
- `cmake_addtional_definitions`: additional CMakeLists.txt definitions to compile the target candidate
- `security_level`: candidate instance security level. This flag is specially for vox. The default value is ***256***
- `number_measurements`: number of measurements for Dudect. The default value is ***1e4***.
- `timeout`: timeout for dudect execution. The default value is ***86400***. To run dudect without *timeout*, set the value of this
  option to ***no***
- `ref_opt_add_implementation`: The target implementation to test. The possible values are: ***opt***, ***ref*** and ***add*** for 
 Reference, Optimized and Additional Implementations respectively.


## Compile and/or Run a candidate

To test a candidate by a targeted tool, run:

### Given one instance of the candidate

```
python3 toolchain-scripts/toolchain_script.py CANDIDATE --tools TOOLS --instance_folders_list INSTANCE --ref_opt_add_implementation TARGET_IMPLEMENTATION 
```

### All instances of the candidate

```
python3 toolchain-scripts/toolchain_script.py CANDIDATE --tools TOOLS --ref_opt_add_implementation TARGET_IMPLEMENTATION
```

### All instances of all candidates

```
python3 toolchain-scripts/toolchain_script.py -a  TOOLS OPTION1=VALUE1 OPTION2=VALUE2
```
where possible `OPTIONi` are: 
- number_measurements (for Dudect)
- timeout (for Dudect)
- depth (for binsec)
- ref_opt_add_implementation (for all tools)
- algorithms_patterns (for all tools)

and `TOOLS` are among the chosen tools of our toolchain.

`NOTE`: That option works only on the optimized implementation for now.
It could work on the additional and reference implementations, but some changes
need to be done in the script. We are working on it to make it automatic.


## Example

- 1 instance of the optimized implementation of mirith

````
python3 toolchain-scripts/toolchain_script.py mirith --tools binsec --instance_folders_list mirith_avx2_Ia_fast --ref_opt_add_implementation opt
````

- all instances of the optimized implementation of mirith


````
python3 toolchain-scripts/toolchain_script.py mirith --tools binsec --ref_opt_add_implementation opt
````

If we want to run the tests for the `sign()` function only:

````
python3 toolchain-scripts/toolchain_script.py mirith --tools binsec  --ref_opt_add_implementation opt --algorithms_patterns sign
````

- all instances of all candidates

Run dudect on the `Optimized implementation` of `crypto_sign()` algorithm for all instances of all integrated candidates with a timeout of `10` minutes (`600` s),
 with `100K` number of measurements.

```
python3 toolchain-scripts/toolchain_script.py -a  dudect ref_opt_add_implementation=opt number_measurements=1e5  timeout=600 algorithms_patterns=sign
```

## How to add/enable tests for a new candidate in the CLI

To be able to test a <new> candidate, in this project, proceed as follows:

1. `candidates_build.py`:
   - write a function that generates the `Makefile` or `CMakeLists` for the candidate.
     - cmake_CANDIDATE(path_to_cmake_lists,tool_type,candidate)
     - makefile_CANDIDATE(path_to_makefile_folder, subfolder, tool_name, candidate)
     - Call the function just written in the body of the function `makefile_candidate` or `cmake_candidate`
2. `toolchain_script.py`: 
   - Add the name of the candidate in one of the lists `candidates_to_build_with_makefile` 
      or `candidate_to_build_with_cmake` , local variables of the function `compile_run_candidate`
   - Add the candidate name to the list `list_of_integrated_candidates`. 
   - Add the candidate name to the dictionary `signature_type_based_candidates_dict` depending on its category. 
   - Add the candidate required data to the dictionary `candidates_api_sign_rng_path`
   - Define the candidate implementation folders, just like `mirith_implementations_folders`. Refer to the part `CANDIDATES IMPLEMENTATION FOLDERS`.


## Structure of the folders created with the scripts

```
type-based signature
└── candidate
    ├── Optimization folder
        ├── Tool name
            ├── Instance
                ├── candidate_keypair
                │   ├── required files for tests (.c file, .xml, .ini)
                │   ├── output file of the test (.txt)
                ├── candidate_sign
                │   ├── required files for tests (.c file, .xml, .ini)
                │   ├── output file of the test (.txt)
                ├── build
                │   ├── candidate_keypair
                │   │   ├── binary_file for crypto_sign_keypair
                │   │   ├── (if tool = binsec: gdb script, .snapshot file)
                │   ├── candidate_sign
                │   │   ├── binary_file for crypto_sign
                │   │   ├── (if tool = binsec: gdb script, .snapshot file)

```

### Example
- `tool`: binsec
- `type-based signature`: mpc-in-the-head
- `candidate`: mirith
- `Optimizated Implementation folder`: Optimized_Implementation
- `Instance`: mirith_avx2_Ia_fast

Note: For each candidate, the Optimized implementation folder has a 
default value: the one proposed by bidders.

As already mentioned above, to create required files for the tests and run the tests with a given tool:

```
python3 toolchain-scripts/toolchain_script.py mirith --tools binsec --instance_folders_list mirith_avx2_Ia_fast
```

Here's the structure of the generated files:


```
mpc-in-the-head
└── mirith
        ├── Optimized_Implementation
            ├── binsec
                ├── mirith_avx2_Ia_fast
                    ├── mirith_keypair
                    │    ├── cfg_keypair.ini, test_harness_crypto_sign_keypair.c
                    │    ├── (if binsec is run: crypto_sign_keypair_output.txt)
                    ├── candidate_sign
                    │    ├── cfg_sign.ini, test_harness_crypto_sign.c
                    │    ├── (if binsec is run: crypto_sign_output.txt)
                    ├── build
                    │    ├── mirith_keypair
                    │    │    ├── test_harness_crypto_sign_keypair (executable)
                    │    │    ├── test_harness_crypto_sign_keypair.gdb
                    │    │    ├── test_harness_crypto_sign_keypair.snapshot
                    │    ├── candidate_sign
                    │    │    ├── test_harness_crypto_sign (executable)
                    │    │    ├── test_harness_crypto_sign.gdb
                    │    │    ├── test_harness_crypto_sign.snapshot

```

## Special cases

For the following candidates, run the commands:

### Candidates with no instance

Candidates: `cross`, `less`, `pqsigrm`
```
python3 toolchain-scripts/toolchain_script.py CANDIDATE --tools TOOLS 
```

#### Vox

Actually, Vox has no instance. The optimized implementation folder is: `Reference_Implementation/vox_sign`.
We consider the instance of vox as: `vox_sign`
The default vox instance security level is 256. Use the option `--security_level` to run the tests the desired ones. 
```
python3 toolchain-scripts/toolchain_script.py vox --tools TOOLS  --security_level 128
```

### Mayo

Instances: `src/mayo_1`, `src/mayo_2`, `src/mayo_3`, `src/mayo_5`
```
python3 toolchain-scripts/toolchain_script.py mayo --tools TOOLS --instance_folders_list src/mayo_1
```

### Qr_uov

Instances: `qruov1q7L10v740m100`, `qruov1q31L3v165m60`, etc..

The List of instances can be found in the `Makefile` of the folder: `Optimized_Implementation`.

```
python3 toolchain-scripts/toolchain_script.py mayo --tools TOOLS --instance_folders_list qruov1q7L10v740m100
```

## Note

We have focused our work on the unbroken candidates (candidates with no security issues).
We didn't succeed to run our scripts on some of them. However, we are working on it.
We are also trying to improve the scripts, by enhancing the templates of each tool,  
