#dockerfile for constant-time checking tools: binsec/valgrind/ctgrind/dudect/Flow Tracker AND fuzzing tool: libfuzzer
#FROM ubuntu:16.04
#FROM ubuntu:22.04
#FROM ubuntu:20.04
#Binsec-latest
FROM binsec/binsec
ARG NUM_PROCESSORS=8

#Since binsec image is not working root as user we need to specify it so that it can run the packages
USER root
########################################
#Install required packages for all the tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz bzip2 libc6-dbg gcc wget git make clang g++ build-essential libssl-dev libffi-dev python cmake flex bison xz-utils python3-pip llvm libgmp3-dev
#For libfuzzer the only requirement is to install llvm and clang
########################################
# Valgrind
RUN wget -O /tmp/valgrind.tar.bz2 "https://sourceware.org/pub/valgrind/valgrind-3.16.1.tar.bz2" && \
    tar -xf /tmp/valgrind.tar.bz2 -C /tmp/
########################################
# Libraries for ctgrind
RUN mkdir /usr/share/ctgrind
COPY valgrind_need/ctgrind.h /usr/share/ctgrind/
COPY valgrind_need/ctgrind.c /usr/share/ctgrind/
COPY valgrind_need/ctgrind.h /usr/include/ctgrind.h
RUN cd /usr/share/ctgrind && \
    gcc -o libctgrind.so -shared ctgrind.c -Wall -std=c99 -fPIC -Wl,-soname,libctgrind.so.1 && \
    cp libctgrind.so /usr/lib/ && \
    cd /usr/lib/ && \
    ln -s libctgrind.so libctgrind.so.1
########################################
# Patch with ctgrind
COPY valgrind_need/valgrind.patch /tmp/valgrind.patch
RUN cd /tmp/ && \
    patch -p0 < /tmp/valgrind.patch

RUN cd /tmp/valgrind-3.16.1 && \
    ./configure --prefix=/usr/share/valgrind && \
    make -j${NUM_PROCESSORS} && \
    make install

ENV PATH="/usr/share/valgrind/bin:$PATH"
########################################
# Dudect
RUN git clone https://github.com/oreparaz/dudect.git /usr/share/dudect
RUN cd /usr/share/dudect && make
# Replace all occurences of function randombytes in dudect.h by randombytes_dudect
#RUN sed -i "s/randombytes/randombytes_dudect/g" "/usr/share/dudect"/src/dudect.h
# If this step is not done you might not find dudect.h
RUN cp /usr/share/dudect/src/dudect.h /usr/include/dudect.h
########################################
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
########################################
#Exiting root privilege
USER binsec

CMD ["bash"]