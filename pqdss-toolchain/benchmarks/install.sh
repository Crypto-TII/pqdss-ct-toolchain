#!/bin/bash
#
# This script to copy cycle.h into /usr/include

# Make sure the script is being executed with superuser privileges.
if [[ "${UID}" -ne 0 ]]
then
  echo 'Please, run with sudo or as root.'
  exit 1
fi

BENCHMARKS_TMP_DIR=/tmp/benchmarks


if ! cp $BENCHMARKS_TMP_DIR/cycle.h /usr/include/cycle.h
  then
    echo "Could not find $BENCHMARKS_TMP_DIR/cycle.h"
    exit 1
fi

exit 0
