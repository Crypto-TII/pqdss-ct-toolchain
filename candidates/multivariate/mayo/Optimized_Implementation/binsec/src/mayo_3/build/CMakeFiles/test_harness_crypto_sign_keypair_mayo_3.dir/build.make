# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/build

# Include any dependencies generated for this target.
include CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/flags.make

CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.o: CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/flags.make
CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.o: ../mayo_keypair/test_harness_crypto_sign_keypair.c
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.o"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -o CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.o   -c /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/mayo_keypair/test_harness_crypto_sign_keypair.c

CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.i"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/mayo_keypair/test_harness_crypto_sign_keypair.c > CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.i

CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.s"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/mayo_keypair/test_harness_crypto_sign_keypair.c -o CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.s

# Object files for target test_harness_crypto_sign_keypair_mayo_3
test_harness_crypto_sign_keypair_mayo_3_OBJECTS = \
"CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.o"

# External object files for target test_harness_crypto_sign_keypair_mayo_3
test_harness_crypto_sign_keypair_mayo_3_EXTERNAL_OBJECTS =

mayo_keypair/test_harness_crypto_sign_keypair_mayo_3: CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/mayo_keypair/test_harness_crypto_sign_keypair.c.o
mayo_keypair/test_harness_crypto_sign_keypair_mayo_3: CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/build.make
mayo_keypair/test_harness_crypto_sign_keypair_mayo_3: libmayo_3_nistapi.a
mayo_keypair/test_harness_crypto_sign_keypair_mayo_3: libmayo_3.a
mayo_keypair/test_harness_crypto_sign_keypair_mayo_3: libmayo_common_sys.a
mayo_keypair/test_harness_crypto_sign_keypair_mayo_3: CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking C executable mayo_keypair/test_harness_crypto_sign_keypair_mayo_3"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/build: mayo_keypair/test_harness_crypto_sign_keypair_mayo_3

.PHONY : CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/build

CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/cmake_clean.cmake
.PHONY : CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/clean

CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/depend:
	cd /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3 /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3 /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/build /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/build /tmp/binsec_new_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_3/build/CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/test_harness_crypto_sign_keypair_mayo_3.dir/depend
