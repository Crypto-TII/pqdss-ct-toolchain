FROM ubuntu:22.04

LABEL maintainer="Eduardo Fernández <eduardo.fernandez@tii.ae>"

RUN apt update                         && \
    apt install -y python3 python3-pip && \
    pip3 install pylint

WORKDIR /tmp
