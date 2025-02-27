#!/bin/bash
#
# This script installs and configures timecop.

# Make sure the script is being executed with superuser privileges.
if [[ "${UID}" -ne 0 ]]
then
  echo 'Please, run with sudo or as root.'
  exit 1
fi

# Copy poison.h into /usr/include
if ! cp /tmp/timecop/src/poison.h /usr/include/poison.h
  then
    echo "Could not find poison.h"
    exit 1
fi

# Copy toolchain_randombytes.h into /usr/include
if ! cp /tmp/timecop/src/toolchain_randombytes.h /usr/include/toolchain_randombytes.h
  then
    echo "Could not find toolchain_randombytes.h"
    exit 1
fi