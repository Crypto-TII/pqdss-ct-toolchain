#!/bin/bash
#
# This script installs and configures dudect.

# Make sure the script is being executed with superuser privileges.
if [[ "${UID}" -ne 0 ]]
then
  echo 'Please, run with sudo or as root.'
  exit 1
fi

DUDECT_SHARE_DIR=/usr/share/dudect

# Download dudect.
if ! git clone https://github.com/oreparaz/dudect.git $DUDECT_SHARE_DIR
then
  echo 'Dudect could not be downloaded.'
  exit 1
fi

# Build dudect.
cd $DUDECT_SHARE_DIR || exit

if ! make
then
  echo 'Dudect could not be built.'
  exit 1
fi

exit 0
