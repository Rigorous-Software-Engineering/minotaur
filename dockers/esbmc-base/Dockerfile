FROM ubuntu:20.04
ARG CORE_COUNT=4
RUN groupadd --gid 1000 maze \ 
    && useradd --uid 1000 --gid maze --shell /bin/bash --create-home maze

### Set up directory structure
USER maze
RUN mkdir -p /home/maze/tools
RUN mkdir -p /home/maze/workspace

USER root 

### Install Dependencies
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    gperf \
    libgmp-dev \
    bison \
    curl \
    flex \
    gcc-multilib \
    linux-libc-dev \
    libboost-all-dev \
    libtinfo-dev \
    ninja-build \
    python3-setuptools \
    unzip \
    python3-pip \
    openjdk-8-jre \
    lld \
    pkg-config \
    lcov \
&& rm -rf /var/lib/apt/lists/*

USER maze
WORKDIR /home/maze/tools

### Get CMAKE manually, as we need version >= 3.18
RUN wget https://github.com/Kitware/CMake/releases/download/v3.27.2/cmake-3.27.2-linux-x86_64.tar.gz
RUN tar xf cmake-3.27.2-linux-x86_64.tar.gz
RUN mv cmake-3.27.2-linux-x86_64 cmake
ENV PATH=$PATH:/home/maze/tools/cmake/bin

### Install ESBMC
WORKDIR /home/maze/tools
RUN ls
RUN git clone https://github.com/esbmc/esbmc

## Set up SMT solvers
# Boolector
RUN git clone --depth=1 --branch=3.2.1 https://github.com/boolector/boolector
WORKDIR /home/maze/tools/boolector
RUN ./contrib/setup-lingeling.sh
RUN ./contrib/setup-btor2tools.sh
RUN ./configure.sh --prefix $PWD/../boolector-release
WORKDIR /home/maze/tools/boolector/build
RUN make -j${CORE_COUNT} && make install

# CVC4
WORKDIR /home/maze/tools
RUN pip3 install toml
RUN git clone https://github.com/CVC4/CVC4.git 
WORKDIR /home/maze/tools/CVC4
RUN git reset --hard b826fc8ae95fc && ./contrib/get-antlr-3.4 && ./configure.sh --optimized --prefix=../cvc4 --static --no-static-binary 
WORKDIR /home/maze/tools/CVC4/build
RUN make -j${CORE_COUNT} && make install 

# MathSAT
WORKDIR /home/maze/tools
RUN wget http://mathsat.fbk.eu/download.php?file=mathsat-5.5.4-linux-x86_64.tar.gz -O mathsat.tar.gz && tar xf mathsat.tar.gz && mv mathsat-5.5.4-linux-x86_64 mathsat

# Yices
RUN wget https://gmplib.org/download/gmp/gmp-6.1.2.tar.xz && tar xf gmp-6.1.2.tar.xz && rm gmp-6.1.2.tar.xz
WORKDIR /home/maze/tools/gmp-6.1.2
RUN ./configure --prefix $PWD/../gmp --disable-shared ABI=64 CFLAGS=-fPIC CPPFLAGS=-DPIC && make -j${CORE_COUNT} && make install
WORKDIR /home/maze/tools
RUN git clone https://github.com/SRI-CSL/yices2.git
WORKDIR /home/maze/tools/yices2
RUN git checkout Yices-2.6.1 && autoreconf -fi && ./configure --prefix $PWD/../yices --with-static-gmp=$PWD/../gmp/lib/libgmp.a && make -j${CORE_COUNT} && make static-lib && make install && cp ./build/x86_64-pc-linux-gnu-release/static_lib/libyices.a ../yices/lib

# Z3
WORKDIR /home/maze/tools
RUN wget https://github.com/Z3Prover/z3/releases/download/z3-4.8.9/z3-4.8.9-x64-ubuntu-16.04.zip && unzip z3-4.8.9-x64-ubuntu-16.04.zip && mv z3-4.8.9-x64-ubuntu-16.04 z3

WORKDIR /home/maze/tools
ADD run_esbmc.sh /home/maze/tools/run_esbmc.sh
ADD get_coverage.sh /home/maze/tools/get_coverage.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py


WORKDIR /home/maze/tools/esbmc 
ENV PATH=/home/maze/tools/cvc4/bin:/home/maze/tools/z3/bin:/home/maze/tools/yices/bin:/home/maze/tools/boolector-release/bin:/home/maze/tools/mathsat/bin:$PATH
