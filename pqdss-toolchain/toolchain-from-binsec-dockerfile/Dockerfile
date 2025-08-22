FROM binsec/binsec:latest
ARG NUM_PROCESSORS=8

USER root

ARG DEBIAN_FRONTEND=noninteractive

# Intstall packages
RUN apt-get update   && \
    apt-get install -y --no-install-recommends opam graphviz sudo  \
        bzip2 libc6-dbg gcc g++ texinfo m4 wget xz-utils  python3  \
        git make wget build-essential libssl-dev gpg-agent  \
        libffi-dev python3-pip cmake flex bison software-properties-common \
        zlib1g-dev p7zip pkg-config gdb z3 libgmp3-dev time


ENV PQDSSDIR /tmp/pqdss-toolchain
WORKDIR $PQDSSDIR


# Install valgrind.
COPY ../ct-tools/valgrind /tmp/valgrind
RUN chmod u+x /tmp/valgrind/install.sh && \
    /tmp/valgrind/install.sh           && \
    rm -r /tmp/valgrind


# Install timecop.
COPY ../ct-tools/timecop /tmp/timecop
RUN chmod u+x /tmp/timecop/install.sh && \
    /tmp/timecop/install.sh           && \
    rm -r /tmp/timecop

# Install dudect.
COPY ../ct-tools/dudect /tmp/dudect
RUN chmod u+x /tmp/dudect/install.sh && \
    /tmp/dudect/install.sh           && \
    rm -r /tmp/dudect


# Copy cycle.h into /usr/include.
COPY ../benchmarks /tmp/benchmarks
RUN chmod u+x /tmp/benchmarks/install.sh && \
    /tmp/benchmarks/install.sh           && \
    rm -r /tmp/benchmarks

ENV PATH="/usr/share/valgrind/bin:$PATH"