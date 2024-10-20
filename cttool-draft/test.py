#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from subprocess import Popen
import sys

import os

def test_sed(path_to_file: str, expression):
    file_directory = "/".join(path_to_file.split('/')[:-1])
    print("---file_directory: ", file_directory)
    os.chdir(file_directory)
    makefile = f'Makefile'
    # sed -i 's/^projdir .*$/projdir PacMan/' .ignore
    cmd = [f"sed -i 's/^TOOLS_FLAGS := .*$/TOOLS_FLAGS := {expression}/g' {makefile}"]
    subprocess.call(cmd, stdin=sys.stdin, shell=True)


path_to_file = 'candidates/mpc-in-the-head/perk/Optimized_Implementation/perk-128-fast-3/Makefile'
exp = '-g -Wall'
test_sed(path_to_file, exp)