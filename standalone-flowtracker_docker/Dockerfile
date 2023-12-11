FROM binsec/binsec
ARG NUM_PROCESSORS=8

#Since binsec image is not working root as user we need to specify it so that it can run the packages
USER root
RUN apt-get update                                   && \
    apt-get install -y --no-install-recommends graphviz          \
        bzip2 libc6-dbg gcc g++ wget xz-utils python    \
        git make wget build-essential libssl-dev        \
        libffi-dev python3-pip cmake flex bison



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
