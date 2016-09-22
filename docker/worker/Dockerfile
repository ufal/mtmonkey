FROM ubuntu:16.04

ARG CPU_CORES=4

RUN \
  apt-get update \
  && apt-get install -y \
    git \
    libxmlrpc-c++8-dev \
    python-pip \
    build-essential \
    pkg-config \
    automake \
    libtool \
    wget \
    zlib1g-dev \
    python-dev \
    libbz2-dev \
    libcmph-dev

RUN \
  git clone https://github.com/moses-smt/mosesdecoder.git \
  && cd mosesdecoder \
  && ./bjam -j $CPU_CORES \
  && cd ..

RUN \
  pip install --upgrade pip \
  && pip install flask validictory regex configobj requests

RUN \
  git clone https://github.com/ufal/mtmonkey

VOLUME /mt-model

EXPOSE 8080

COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
