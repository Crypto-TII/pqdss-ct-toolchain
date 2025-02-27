#!/bin/bash
#
# This script installs and configures binsec.

# Make sure the script is being executed with superuser privileges.
if [[ "${UID}" -ne 0 ]]
then
  echo 'Please, run with sudo or as root.'
  exit 1
fi


#BINSEC_INSTALL_DIR=binsec_install_dir
#BINSEC_DIR=binsec
#UNISIM_ARCHISEC_DIR=unisim_archisec
#GMP_INSTALL_DIR=gmp-6.1.2

BINSEC_INSTALL_DIR=pqdss-toolchain
BINSEC_DIR=binsec
UNISIM_ARCHISEC_DIR=unisim_archisec
GMP_INSTALL_DIR=gmp-6.1.2
# Download binsec.
#if ! git clone https://github.com/binsec/binsec.git
#then
#  echo 'Binsec could not be downloaded.'
#  exit 1
#fi

# Download unisim_archisec.
#if ! git clone git@github.com:binsec/unisim_archisec.git
#then
#  echo 'unisim_archisec could not be downloaded.'
#  exit 1
#fi


#if ! cp div.patch $BINSEC_DIR/div.patch
#  then
#    echo "Could not find div.patch"
#    exit 1
#fi
#
#
#if ! cp diff.patch $UNISIM_ARCHISEC_DIR/diff.patch
#  then
#    echo "Could not find diff.patch"
#    exit 1
#fi


# Build gmp.
cd $GMP_INSTALL_DIR || exit

if ! ./configure --prefix=/usr --enable-cxx
then
  echo 'gmp could not be configured.'
  exit 1
fi


if ! make -j$NUM_PROCESSORS
then
  echo 'gmp could not be built.'
  exit 1
fi


if ! make check
then
  echo 'gmp could not be checked.'
  exit 1
fi



if ! sudo make install
then
  echo 'gmp could not be installed.'
  exit 1
fi

cd ..

cd $BINSEC_DIR || exit
if ! git apply < div.patch
then
  echo 'div.patch could not be applied.'
  exit 1
fi

if ! opam install dune
then
  echo 'dune could not be installed.'
  exit 1
fi

if ! eval $(opam env)
then
  echo 'eval opam failed.'
  exit 1
fi

cd ..

cd $UNISIM_ARCHISEC_DIR || exit
if ! git apply < diff.patch
then
  echo 'diff.patch could not be applied.'
  exit 1
fi

if ! dune build @install
then
  echo 'unisim_archisec could not be build.'
  exit 1
fi

if ! dune install
then
  echo 'unisim_archisec could not be installed.'
  exit 1
fi

cd ..

cd $BINSEC_DIR || exit
if ! opam install menhir grain_dypgen ocamlgraph zarith toml bitwuzla-cxx
then
  echo 'menhir grain_dypgen ocamlgraph zarith toml could not be installed.'
  exit 1
fi


if ! opam install bitwuzla dune-site
then
  echo 'bitwuzla dune-site could not be installed.'
  exit 1
fi


# opam install curses
opam depext -i curses

#if ! make
#then
#  echo 'binsec could not be build.'
#  exit 1
#fi
#
#if ! make install
#then
#  echo 'binsec could not be installed.'
#  exit 1
#fi

if ! dune build @install
then
  echo 'binsec could not be build.'
  exit 1
fi

if ! dune install
then
  echo 'binsec could not be installed.'
  exit 1
fi

cd ..

echo "===================== CWD ====================="
pwd
echo "===================== CONTENT OF CWD ====================="
ls

exit 0

