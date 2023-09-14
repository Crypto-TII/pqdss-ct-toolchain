
#FROM ubuntu:16.04
#FROM ubuntu:22.04
#FROM ubuntu:20.04
#Binsec-latest
FROM binsec/binsec
ARG NUM_PROCESSORS=8

#Since binsec image is not working root as user we need to specify it so that it can run the packages
USER root
# Valgrind
RUN apt-get update && \
    apt-get install -y bzip2 libc6-dbg gcc wget git make build-essential libssl-dev libffi-dev python3-pip cmake flex bison

RUN wget -O /tmp/valgrind.tar.bz2 "https://sourceware.org/pub/valgrind/valgrind-3.16.1.tar.bz2" && \
    tar -xf /tmp/valgrind.tar.bz2 -C /tmp/

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

# Patch with ctgrind
COPY valgrind_need/valgrind.patch /tmp/valgrind.patch
RUN cd /tmp/ && \
    patch -p0 < /tmp/valgrind.patch

RUN cd /tmp/valgrind-3.16.1 && \
    ./configure --prefix=/usr/share/valgrind && \
    make -j${NUM_PROCESSORS} && \
    make install

ENV PATH="/usr/share/valgrind/bin:$PATH"
#Exiting root privilege
USER binsec

#Script to execute test

#COPY test.c /usr/share/ctgrind/test.c

#RUN cd /usr/share/ctgrind && \
#    gcc test.c libctgrind.so -o test.o -ggdb -std=c99 -Wall -Wextra -lm && \
#    valgrind ./test.o

#RUN rm -rf /var/lib/apt/lists/*

CMD ["bash"]