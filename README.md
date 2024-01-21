# Toolchain consisting of binsec - ctgrind - dudect - flowtracker




## What is in this repository ? 
This repository contains the following folders: 
* `candidates`: contains the Post-Quantum Digital Signatures Schemes (PQDSS) implementations, submitted in the context of NIST Call 
for proposals for PQC-based signature schemes. The candidates are classified according to the type-based signature scheme. Here 
are the different folders: `code`, `lattice`, `mpc-in-the-head`, `symmetric`, `isogeny`, `mutlivariate` and `other`.

* `toolchain`: contains required files (Dockerfile, .sh files) to build a Docker image consisting of the required packages
and requirements to compile and run candidates with the following constant-time check tools: binsec - ctgrind - dudect and flowtracker

* `toolchain-scripts`: consist of the following files 
  * `candidates_build.py`:  contains the functions that generate the CMakeLists.txt/Makefile of the candidates. For almost each candidate, the 
  content of the CMakeLists.txt/Makefile is a copie, except the targets for tests and kat files generation, of the one proposed in the candidate implementation.
  * `generic_functions.py`: contains generic functions for tools templates and other required files generation, functions to compile and run tools on the targets candidates 
  * `toolchain_script.py`: contains the functions `compile_run_candidate` 
  that allows to compile targets and run tests with a given tool. The scripts that create main parser and subparsers 
  for candidates are also part of this file.


## Benefits of using our toolchain

- Tools libraries/packages: each of the tools above-mentioned has its requirements, necessary packages/libraries for 
compilation and execution of a given target. Our Dockerfile allows to not worry about 
 all those requirements as "everything" is already taken into account.
- Tools required files to test a candidate: each of the tools need a specific file, related to the candidate
  to test. Our scripts allow to generate all needed files (.c, .xml, .ini, etc.).
- Tools commands to run a candidate: each tool has its own commands (including necessary flags for compilation and commands for execution). 
Those requirements are also taken into account by our scripts.
- Test many instances of a (many) candidate(s):  generating required files, compiling and running a given candidate for all tools
 could take a non-negligible amount of time, especially when the tests must be performed on 
many instances of many candidates. Our scripts allow to gain a significant amount of time to achieve that goal.
- With our scripts, one can generate templates, improve them manually, compile and run tests. 



## Help

To see the list of all candidates, type:

```
python3 toolchain-scripts/toolchain_script.py -h
```

## List of options to test a candidate

To see the list of all options for test of a given target (candidate), type:

```
python3 toolchain-scripts/toolchain_script.py CANDIDATE_NAME -h
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
   TOOL_TYPE/INSTANCE_FOLDER/CANDIDATE_keypair(or sign). 
   Ex: From the folder mpc-in-the-head/mirith/Optimized_Implementation/ctgrind/mirith_avx2_Ia_fast/mirith_keypair, the real
   relative path to api.h would be: rel_path_to_api ="../../../mirith_avx2_Ia_fast/api.h". But the script would add automatically the 
   name of the instance. So rel_path_to_api ="../../../api.h".
   If the file api.h doesn't contain the declaration of the crypto_sign_keypair and crypto_sign functions, then
   rel_path_to_api = "".
- `rel_path_to_sign`: Similar to *rel_path_to_api*.
- `compile`: by default, its value is ***yes***. If the targeted executable has already been generated in a previous execution, and if 
   we just want to run the test, then set this option to ***no***.
- `run`: by default, its value is ***yes***. If we just want to compile, then set this option to ***no***.
- `depth`: this flag is meant for the use of binsec tool. The default value in our implementation is ***1000000***. But the default value
    set by the authors of binsec tool is ***1000***.
- `build`: the default value is *build*.
- `algorithms_patterns`: the patterns of the algorithm to be tested. default value: ***keypair***, ***sign***
- `is_rng_outside_folder`: for some of the candidates, the folder containing the header file, (rng.h, randombytes, etc.), in which is defined
the function that generates random data.
- `with_core_dump`: option to run binsec from core dump. By default, it's ***yes***.

## Compile and/or Run a candidate

To test a candidate by a targeted tool, run:

```
python3 toolchain-scripts/toolchain_script.py CANDIDATE --tools TOOLS --instance_folders_list PARAMETER_SET_FOLDER --algorithms_patterns PATTERN
```

## Example

````
python3 toolchain-scripts/toolchain_script.py mirith --tools ctgrind --instance_folders_list mirith_avx2_Ia_fast --algorithms_patterns sign
````




## How to add/enable tests for a new candidate in the CLI

To be able to test a <new> candidate, in this project, proceed as follows:

1. `candidates_build.py`: write a function that generates the `Makefile` or `CMakeLists` for the candidate. 
   - cmake_CANDIDATE(path_to_cmake_lists,tool_type,candidate)
   - makefile_CANDIDATE(path_to_makefile_folder, subfolder, tool_name, candidate)
   - Call the function just written in the body of the function `makefile_candidate` or `cmake_candidate`
3. `toolchain_script.py`: Add the name of the candidate in one of the lists `candidates_to_build_with_makefile` 
   or `candidate_to_build_with_cmake` , local variables of the function `compile_run_candidate`
4. `toolchain_script.py`: add `generic.add_cli_arguments`: See the part: `# Create a parser for every function in the sub-parser name


## Structure of the folders created with the scripts

```
type-based signature
    candidate
        Optimization folder
            Tool name
                Instance
                    candidate_keypair
                        required files for tests (.c file, .xml, .ini)
                        output file of the test (.txt)
                    candidate_sign
                        required files for tests (.c file, .xml, .ini)
                        output file of the test (.txt)
                    build
                        candidate_keypair
                            binary_file for crypto_sign_keypair
                            (if tool = binsec: gdb script, .snapshot file)
                        candidate_sign
                            binary_file for crypto_sign
                            (if tool = binsec: gdb script, .snapshot file)

```

### Example
- tool: binsec
- type-based signature: mpc-in-the-head
- candidate: mirith
- Optimizated Implementation folder: Optimized_Implementation
- Instance: mirith_avx2_Ia_fast

Note: For each candidate, the Optimized implementation folder has a 
default value: the one proposed by bidders.

As already mentioned above, to create required files for the tests and run the tests with a given tool:

```
python3 toolchain-scripts/toolchain_script.py mirith --tools binsec --instance_folders_list mirith_avx2_Ia_fast
```

Here's the result:


```
mpc-in-the-head
    mirith
        Optimized_Implementation
            binsec
                mirith_avx2_Ia_fast
                    mirith_keypair
                        cfg_keypair.ini, test_harness_crypto_sign_keypair.c
                        (if binsec is run: crypto_sign_keypair_output.txt)
                    candidate_sign
                        cfg_sign.ini, test_harness_crypto_sign.c
                        (if binsec is run: crypto_sign_output.txt)
                    build
                        mirith_keypair
                            test_harness_crypto_sign_keypair (executable)
                            test_harness_crypto_sign_keypair.gdb
                            test_harness_crypto_sign_keypair.snapshot
                        candidate_sign
                            test_harness_crypto_sign (executable)
                            test_harness_crypto_sign.gdb
                            test_harness_crypto_sign.snapshot

```

## Especial cases

For the following candidates, run the commands:

### Candidates with no instance

Candidates: `cross`, `less`, `pqsigrm`
```
python3 toolchain-scripts/toolchain_script.py CANDIDATE --tools TOOLS 
```

#### Vox

Actually, Vox has no instance. The optimized implementation folder is: `Reference_Implementation/vox_sign`.
We consider the instance of vox as: `vox_sign`

```
python3 toolchain-scripts/toolchain_script.py vox --tools TOOLS --instance_folders_list vox_sign
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
