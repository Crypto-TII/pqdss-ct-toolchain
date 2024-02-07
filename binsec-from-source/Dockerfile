FROM ocaml/opam:ubuntu-22.04-ocaml-4.14
ARG NUM_PROCESSORS=8

#USER root

# Install common packages.
RUN sudo apt-get update           && \
    sudo apt-get install -y --no-install-recommends  \
        git make wget build-essential libssl-dev \
        libffi-dev cmake clang python python3-pip xz-utils gdb \
        texinfo g++ m4 zlib1g-dev p7zip flex bison   && \
    sudo apt-get clean && sudo  rm -rf /var/lib/apt/lists/*
