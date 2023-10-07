# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact

## Help
```
python3 toolchain_script.py -h
```


### To see the list of arguments of function, type:
```
python3 toolchain_script.py CANDIDATE_NAME -h
```

### Example
```
python3 toolchain_script.py mirith -h
```
### Command-Line-Interface (CLI) Flags

1. `tools`: list of tools that a given candidate will be tested with. Ex: binsec, ctgrind, dudect etc.. The tools are white space-separated
2. `signature_type`: type-based signature. Ex: code, isogeny, lattice etc.
3. `candidate`: NIST candidate. Ex: mirith, sqisign, perk, mira etc.
4. `optimization_folder`: the Optimized Implementation folder. For most of the candidates, this 
    folder is named ***Optimized_Implementation***
5. `instance_folders_list`: the list of the different parameters set based folders. 
    Ex: mirith_avx2_Ia_fast  mirith_hypercube_avx2_IIIb_shortest etc.. The instance folders are white space-separated.
6. `rel_path_to_api`: the relative path to api.h from 
   TOOL_TYPE/INSTANCE_FOLDER/CANDIDATE_keypair(or sign). 
   Ex: From the folder mpc-in-the-head/mirith/Optimized_Implementation/ctgrind/mirith_avx2_Ia_fast/mirith_keypair, the real
   relative path to api.h would be: rel_path_to_api ="../../../mirith_avx2_Ia_fast/api.h". But the script would add automatically the 
   name of the instance. So rel_path_to_api ="../../../api.h".
   If the file api.h doesn't contain the declaration of the crypto_sign_keypair and crypto_sign functions, then
   rel_path_to_api = "".
7. `rel_path_to_sign`: Similar to rel_path_to_api.
8. `compile`: by default, its value is 'yes'. If the targeted executable has already been generated in a previous execution, and if 
   we just want to run the test, then the value of the flag is 'no'.
9. `run`: by default, its value is 'yes'. If we just want to compile, then the value of this flag is 'no'.
10. `depth`: this flag is meant for the use of binsec tool. The default value in our implementation is 1000000. But the default value
    set by the authors of binsec tool is 1000.
11. `build`: the default value is 'build'.
12. `algorithms_patterns`: the patterns of the algorithm to be tested. default value: keypair sign

## Compile and/or Run a candidate

To test a candidate by a targeted tool, run:

```
python3 toolchain_script.py CANDIDATE --tools TOOLS --instance_folders_list PARAMETER_SET_FOLDER --algorithms_patterns PATTERN
```

### Example

````
python3 toolchain_script.py mirith --tools ctgrind --instance_folders_list mirith_avx2_Ia_fast --algorithms_patterns sign
````

## To contribute to the project

### Add a new candidate in the CLI

1. `candidates_build.py`: write a function that generates the `Makefile` or `CMakeLists` for the candidate. 
   - cmake_CANDIDATE(path_to_cmake_lists,tool_type,candidate)
   - makefile_CANDIDATE(path_to_makefile,tool_type,candidate)
2. `generic_functions.py`: add the function just created above. 
3. `toolchain_script.py`: write a function`compile_run_CANDIDATE` as in function `compile_run_cross`.
   - compile_with_cmake = 'yes' if the candidate is to be compiled with a CMakeLists.tx
   - compile_with_cmake = 'yes' otherwise (with a Makefile)
4. `toolchain_script.py`: add `generic.add_cli_arguments`: See the part: `# Create a parser for every function in the sub-parser namespace`
