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
CMAKE_SOURCE_DIR = /home/lattice/haetae/Optimized_Implementation/ctgrind

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/lattice/haetae/Optimized_Implementation/ctgrind/build

# Include any dependencies generated for this target.
include CMakeFiles/taint_2.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/taint_2.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/taint_2.dir/flags.make

CMakeFiles/taint_2.dir/haetae_keypair/taint.c.o: CMakeFiles/taint_2.dir/flags.make
CMakeFiles/taint_2.dir/haetae_keypair/taint.c.o: ../haetae_keypair/taint.c
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/lattice/haetae/Optimized_Implementation/ctgrind/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object CMakeFiles/taint_2.dir/haetae_keypair/taint.c.o"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -o CMakeFiles/taint_2.dir/haetae_keypair/taint.c.o   -c /home/lattice/haetae/Optimized_Implementation/ctgrind/haetae_keypair/taint.c

CMakeFiles/taint_2.dir/haetae_keypair/taint.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/taint_2.dir/haetae_keypair/taint.c.i"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/lattice/haetae/Optimized_Implementation/ctgrind/haetae_keypair/taint.c > CMakeFiles/taint_2.dir/haetae_keypair/taint.c.i

CMakeFiles/taint_2.dir/haetae_keypair/taint.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/taint_2.dir/haetae_keypair/taint.c.s"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/lattice/haetae/Optimized_Implementation/ctgrind/haetae_keypair/taint.c -o CMakeFiles/taint_2.dir/haetae_keypair/taint.c.s

# Object files for target taint_2
taint_2_OBJECTS = \
"CMakeFiles/taint_2.dir/haetae_keypair/taint.c.o"

# External object files for target taint_2
taint_2_EXTERNAL_OBJECTS =

haetae_keypair/taint_2: CMakeFiles/taint_2.dir/haetae_keypair/taint.c.o
haetae_keypair/taint_2: CMakeFiles/taint_2.dir/build.make
haetae_keypair/taint_2: libs/lib2.so
haetae_keypair/taint_2: /usr/lib/libctgrind.so
haetae_keypair/taint_2: /usr/lib/x86_64-linux-gnu/libcrypto.so
haetae_keypair/taint_2: libs/libfips202.so
haetae_keypair/taint_2: libs/libRNG.so
haetae_keypair/taint_2: /usr/lib/x86_64-linux-gnu/libcrypto.so
haetae_keypair/taint_2: CMakeFiles/taint_2.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/lattice/haetae/Optimized_Implementation/ctgrind/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking C executable haetae_keypair/taint_2"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/taint_2.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/taint_2.dir/build: haetae_keypair/taint_2

.PHONY : CMakeFiles/taint_2.dir/build

CMakeFiles/taint_2.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/taint_2.dir/cmake_clean.cmake
.PHONY : CMakeFiles/taint_2.dir/clean

CMakeFiles/taint_2.dir/depend:
	cd /home/lattice/haetae/Optimized_Implementation/ctgrind/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/lattice/haetae/Optimized_Implementation/ctgrind /home/lattice/haetae/Optimized_Implementation/ctgrind /home/lattice/haetae/Optimized_Implementation/ctgrind/build /home/lattice/haetae/Optimized_Implementation/ctgrind/build /home/lattice/haetae/Optimized_Implementation/ctgrind/build/CMakeFiles/taint_2.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/taint_2.dir/depend
