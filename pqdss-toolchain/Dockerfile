FROM ocaml/opam:ubuntu-22.04-ocaml-4.14
ARG NUM_PROCESSORS=8

USER root

ARG DEBIAN_FRONTEND=noninteractive

# Intstall packages
RUN apt-get update   && \
    apt-get install -y --no-install-recommends graphviz sudo  \
        bzip2 libc6-dbg gcc g++ texinfo m4 wget xz-utils  python3  \
        git make wget build-essential libssl-dev gpg-agent  \
        libffi-dev python3-pip cmake flex bison software-properties-common \
        zlib1g-dev p7zip pkg-config gdb z3


ENV PQDSSDIR /tmp/pqdss-toolchain
WORKDIR $PQDSSDIR


COPY binsec $PQDSSDIR
RUN chmod u+x $PQDSSDIR/install.sh && \
    $PQDSSDIR/install.sh           && \
    rm -r $PQDSSDIR
    # rm -r $PQDSSDIR/binsec

# FlowTracker
#RUN wget -O /tmp/llvm.src.tar.xz "https://www.llvm.org/releases/3.7.1/llvm-3.7.1.src.tar.xz"
#RUN tar -xf /tmp/llvm.src.tar.xz -C $HOME
#
#RUN wget -O /tmp/cfe-3.7.1.src.tar.xz "http://www.llvm.org/releases/3.7.1/cfe-3.7.1.src.tar.xz"
#RUN tar -xf /tmp/cfe-3.7.1.src.tar.xz -C $HOME/llvm-3.7.1.src/tools/
#RUN mv $HOME/llvm-3.7.1.src/tools/cfe-3.7.1.src $HOME/llvm-3.7.1.src/tools/clang
#RUN mkdir -p $HOME/llvm-3.7.1.src/build/lib/Transforms
#
#RUN git clone https://github.com/dfaranha/FlowTracker.git /tmp/flowtracker && \
#    cp -r /tmp/flowtracker/AliasSets $HOME/llvm-3.7.1.src/lib/Transforms && \
#    cp -r /tmp/flowtracker/DepGraph $HOME/llvm-3.7.1.src/lib/Transforms && \
#    cp -r /tmp/flowtracker/bSSA2 $HOME/llvm-3.7.1.src/lib/Transforms && \
#    \
#    cp -r /tmp/flowtracker/AliasSets $HOME/llvm-3.7.1.src/build/lib/Transforms && \
#    cp -r /tmp/flowtracker/DepGraph $HOME/llvm-3.7.1.src/build/lib/Transforms && \
#    cp -r /tmp/flowtracker/bSSA2 $HOME/llvm-3.7.1.src/build/lib/Transforms
#
#RUN sed -i "s#bool hasMD() const { return MDMap; }#bool hasMD() const { return bool(MDMap); }#g" $HOME/llvm-3.7.1.src/include/llvm/IR/ValueMap.h
#
#RUN cd $HOME/llvm-3.7.1.src/build && \
#    ../configure --disable-bindings && \
#    make -j${NUM_PROCESSORS}
#
#ENV PATH="$PATH:/root/llvm-3.7.1.src/build/Release+Asserts/bin"
#
#RUN cd $HOME/llvm-3.7.1.src/build/lib/Transforms/AliasSets && \
#    make -j${NUM_PROCESSORS}
#RUN cd $HOME/llvm-3.7.1.src/build/lib/Transforms/DepGraph && \
#    make -j${NUM_PROCESSORS}
#RUN cd $HOME/llvm-3.7.1.src/build/lib/Transforms/bSSA2 && \
#    make -j${NUM_PROCESSORS}
#RUN cd $HOME/llvm-3.7.1.src/build/lib/Transforms/bSSA2 && \
#    g++ -shared -o parserXML.so -fPIC parserXML.cpp tinyxml2.cpp
#


# Install valgrind.
COPY valgrind /tmp/valgrind
RUN chmod u+x /tmp/valgrind/install.sh && \
    /tmp/valgrind/install.sh           && \
    rm -r /tmp/valgrind


# Install timecop.
COPY timecop /tmp/timecop
RUN chmod u+x /tmp/timecop/install.sh && \
    /tmp/timecop/install.sh           && \
    rm -r /tmp/timecop

# Install dudect.
COPY dudect /tmp/dudect
RUN chmod u+x /tmp/dudect/install.sh && \
    /tmp/dudect/install.sh           && \
    rm -r /tmp/dudect


# Copy cycle.h into /usr/include.
COPY benchmarks /tmp/benchmarks
RUN chmod u+x /tmp/benchmarks/install.sh && \
    /tmp/benchmarks/install.sh           && \
    rm -r /tmp/benchmarks

ENV PATH="/usr/share/valgrind/bin:$PATH"






## ===========================================================================================
## ===========================================================================================
## ============================ ctverif ============================
#FROM ocaml/opam:ubuntu-20.04-ocaml-4.13
#ARG NUM_PROCESSORS=8
#
#
#
#USER root
#ARG DEBIAN_FRONTEND=noninteractive
#
## Install common packages.
#RUN apt-get update \
#    && apt-get install -y --no-install-recommends sudo  \
#        git wget build-essential libssl-dev \
#        libffi-dev curl \
#        texinfo && \
#    sudo apt-get clean #&& sudo rm -rf /var/lib/apt/lists/*
#
#
#ENV PQDSSDIR /tmp/pqdss-toolchain
#
#
## Set the work directory
#WORKDIR $PQDSSDIR
#
#COPY ctverif $PQDSSDIR
#RUN chmod u+x $PQDSSDIR/install.sh && \
#    $PQDSSDIR/install.sh           && \
#    rm -rf $PQDSSDIR
