FROM binsec/binsec
ARG NUM_PROCESSORS=8

#Since binsec image is not working root as user we need to specify it so that it can run the packages
USER root
# Intstall packages
RUN apt-get update   && \
    apt-get install -y --no-install-recommends graphviz  \
        bzip2 libc6-dbg gcc g++ wget xz-utils python  \
        git make wget build-essential libssl-dev sudo gpg-agent  \
        libffi-dev python3-pip cmake flex bison software-properties-common \
        ruby ruby-dev



# Flow Tracker
RUN wget -O /tmp/llvm.src.tar.xz "https://www.llvm.org/releases/3.7.1/llvm-3.7.1.src.tar.xz"
RUN tar -xf /tmp/llvm.src.tar.xz -C $HOME

RUN wget -O /tmp/cfe-3.7.1.src.tar.xz "http://www.llvm.org/releases/3.7.1/cfe-3.7.1.src.tar.xz"
RUN tar -xf /tmp/cfe-3.7.1.src.tar.xz -C $HOME/llvm-3.7.1.src/tools/
RUN mv $HOME/llvm-3.7.1.src/tools/cfe-3.7.1.src $HOME/llvm-3.7.1.src/tools/clang
RUN mkdir -p $HOME/llvm-3.7.1.src/build/lib/Transforms

RUN git clone https://github.com/dfaranha/FlowTracker.git /tmp/flowtracker && \
    cp -r /tmp/flowtracker/AliasSets $HOME/llvm-3.7.1.src/lib/Transforms && \
    cp -r /tmp/flowtracker/DepGraph $HOME/llvm-3.7.1.src/lib/Transforms && \
    cp -r /tmp/flowtracker/bSSA2 $HOME/llvm-3.7.1.src/lib/Transforms && \
    \
    cp -r /tmp/flowtracker/AliasSets $HOME/llvm-3.7.1.src/build/lib/Transforms && \
    cp -r /tmp/flowtracker/DepGraph $HOME/llvm-3.7.1.src/build/lib/Transforms && \
    cp -r /tmp/flowtracker/bSSA2 $HOME/llvm-3.7.1.src/build/lib/Transforms

RUN sed -i "s#bool hasMD() const { return MDMap; }#bool hasMD() const { return bool(MDMap); }#g" $HOME/llvm-3.7.1.src/include/llvm/IR/ValueMap.h

RUN cd $HOME/llvm-3.7.1.src/build && \
    ../configure --disable-bindings && \
    make -j${NUM_PROCESSORS}

ENV PATH="$PATH:/root/llvm-3.7.1.src/build/Release+Asserts/bin"

RUN cd $HOME/llvm-3.7.1.src/build/lib/Transforms/AliasSets && \
    make -j${NUM_PROCESSORS}
RUN cd $HOME/llvm-3.7.1.src/build/lib/Transforms/DepGraph && \
    make -j${NUM_PROCESSORS}
RUN cd $HOME/llvm-3.7.1.src/build/lib/Transforms/bSSA2 && \
    make -j${NUM_PROCESSORS}
RUN cd $HOME/llvm-3.7.1.src/build/lib/Transforms/bSSA2 && \
    g++ -shared -o parserXML.so -fPIC parserXML.cpp tinyxml2.cpp



# Install valgrind.
COPY valgrind /tmp/valgrind
RUN chmod u+x /tmp/valgrind/install.sh && \
    /tmp/valgrind/install.sh           && \
    rm -r /tmp/valgrind

# Install ctgrind.
COPY ctgrind /tmp/ctgrind
RUN chmod u+x /tmp/ctgrind/install.sh && \
    /tmp/ctgrind/install.sh           && \
    rm -r /tmp/ctgrind

# Install dudect.
COPY dudect /tmp/dudect
RUN chmod u+x /tmp/dudect/install.sh && \
    /tmp/dudect/install.sh           && \
    rm -r /tmp/dudect

# Install ctverif
# Install smack.
COPY ctverif /tmp/ctverif
RUN chmod u+x /tmp/ctverif/install.sh && \
    /tmp/ctverif/install.sh  && \
    rm -r /tmp/ctverif

ENV PATH="/usr/share/valgrind/bin:$PATH"


# RUN gem install bam-bam-boogieman
