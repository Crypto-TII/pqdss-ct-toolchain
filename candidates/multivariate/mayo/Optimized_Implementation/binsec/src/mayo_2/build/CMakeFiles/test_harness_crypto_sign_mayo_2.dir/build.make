# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
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
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/build

# Include any dependencies generated for this target.
include CMakeFiles/test_harness_crypto_sign_mayo_2.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/test_harness_crypto_sign_mayo_2.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/test_harness_crypto_sign_mayo_2.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/test_harness_crypto_sign_mayo_2.dir/flags.make

CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o: CMakeFiles/test_harness_crypto_sign_mayo_2.dir/flags.make
CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o: ../mayo_sign/test_harness_crypto_sign.c
CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o: CMakeFiles/test_harness_crypto_sign_mayo_2.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o -MF CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o.d -o CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o -c /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/mayo_sign/test_harness_crypto_sign.c

CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.i"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/mayo_sign/test_harness_crypto_sign.c > CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.i

CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.s"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/mayo_sign/test_harness_crypto_sign.c -o CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.s

# Object files for target test_harness_crypto_sign_mayo_2
test_harness_crypto_sign_mayo_2_OBJECTS = \
"CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o"

# External object files for target test_harness_crypto_sign_mayo_2
test_harness_crypto_sign_mayo_2_EXTERNAL_OBJECTS =

mayo_sign/test_harness_crypto_sign_mayo_2: CMakeFiles/test_harness_crypto_sign_mayo_2.dir/mayo_sign/test_harness_crypto_sign.c.o
mayo_sign/test_harness_crypto_sign_mayo_2: CMakeFiles/test_harness_crypto_sign_mayo_2.dir/build.make
mayo_sign/test_harness_crypto_sign_mayo_2: libmayo_2_nistapi.a
mayo_sign/test_harness_crypto_sign_mayo_2: libmayo_2.a
mayo_sign/test_harness_crypto_sign_mayo_2: libmayo_common_sys.a
mayo_sign/test_harness_crypto_sign_mayo_2: CMakeFiles/test_harness_crypto_sign_mayo_2.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking C executable mayo_sign/test_harness_crypto_sign_mayo_2"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/test_harness_crypto_sign_mayo_2.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/test_harness_crypto_sign_mayo_2.dir/build: mayo_sign/test_harness_crypto_sign_mayo_2
.PHONY : CMakeFiles/test_harness_crypto_sign_mayo_2.dir/build

CMakeFiles/test_harness_crypto_sign_mayo_2.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/test_harness_crypto_sign_mayo_2.dir/cmake_clean.cmake
.PHONY : CMakeFiles/test_harness_crypto_sign_mayo_2.dir/clean

CMakeFiles/test_harness_crypto_sign_mayo_2.dir/depend:
	cd /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2 /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2 /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/build /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/build /home/old_image/multivariate/mayo/Optimized_Implementation/binsec/src/mayo_2/build/CMakeFiles/test_harness_crypto_sign_mayo_2.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/test_harness_crypto_sign_mayo_2.dir/depend
