# Pull binsec docker to be able to use the tool
Run in the root of the project:nist-pqc-first-round-signatures
- `docker pull binsec/binsec:rel-2023-02-14`(this docker contain the binsec tool)
- `docker run -it -v $(pwd):/tii_binsec --name binsec_pqdss_rel-2023-02-14 binsec/binsec:rel-2023-02-14 /bin/bash`

Or the following for the latest binsec release:
- `docker pull binsec/binsec:0.8.0`(this docker contain the binsec tool)
- `docker run -it -v $(pwd):/tii_binsec --name binsec_pqdss binsec/binsec:0.8.0 /bin/bash`

## Requirements
- `sudo apt-get update`
- `sudo apt-get install make cmake flex bison libgmp3-dev`

## Commands to build with binsec and run binsec
- `cd ../../tii_binsec/isogeny/sqisign/Additional_Implementations/broadwell`
- `cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_DOC_TARGET=OFF -DSQISIGN_BUILD_TYPE=broadwell -Bcmake-build-broadwell`("-DSQISIGN_BUILD_TYPE=broadwell" is on broadwell by default in this folder)
- `cd cmake-build-broadwell/`
- `make -j`
- `cd binsec/sqisign_keypair/`
- `binsec -checkct -checkct-depth 1000000 -checkct-script ../../../binsec/sqisign_keypair/cfg_file.cfg binsec_sqisign_keypair_lvl1`
- `cd ../sqisign_sign/`
- `binsec -checkct -checkct-depth 1000000 -checkct-script ../../../binsec/sqisign_sign/cfg_file.cfg binsec_sqisign_lvl1`

## Modifications added to the initial project
- Add folder binsec in folder Additional_Implementations/broadwell
- add the instruction `add_subdirectory(binsec)#add binsec folder` to the following CMakeLists.txt:
  "nist-pqc-first-round-signatures/isogeny/sqisign/Additional_Implementations/broadwell/CMakeLists.txt".
  This instruction is for adding the folder binsec when compiling.
- add the following instructions to the cmake file located at "nist-pqc-first-round-signatures/isogeny/sqisign/Additional_Implementations/broadwell/.cmake/flags.cmake":
  `#construct static lib for binsec`
  `set(CMAKE_FIND_LIBRARY_SUFFIXES  ".a")`
  `set(BUILD_SHARED_LIBS OFF)`
  `set(CMAKE_EXE_LINKER_FLAGS "-static")`
  These instructions are here to build the library as static, without which binsec cannot be executed.