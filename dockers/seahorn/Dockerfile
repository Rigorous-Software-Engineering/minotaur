ARG BASE_IMAGE=jammy-scm 
ARG CORE_COUNT=4
# Base image with usual build dependencies
FROM buildpack-deps:$BASE_IMAGE

# Install dependencies
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
  apt-get install -yqq software-properties-common && \
  apt-get update && \
  apt-get upgrade -yqq && \
  apt-get install -yqq unzip \
      zlib1g-dev \
      ninja-build libgraphviz-dev \
      libgmp-dev libmpfr-dev \
      libboost1.74-dev \
      python3-pip \
      less vim \
      gcc-multilib \
      sudo \
      graphviz libgraphviz-dev python3-pygraphviz \
      lcov gcovr rsync \
      clang-14 lldb-14 lld-14 clang-format-14 && \
  pip3 install lit OutputCheck && \
  pip3 install networkx && \
  mkdir seahorn

# Install z3 v4.8.9 since bionic comes with much older version
WORKDIR /tmp
RUN wget https://github.com/Z3Prover/z3/releases/download/z3-4.8.9/z3-4.8.9-x64-ubuntu-16.04.zip && \
  unzip z3-4.8.9-x64-ubuntu-16.04.zip && \
  mv z3-4.8.9-x64-ubuntu-16.04 /opt/z3-4.8.9

# Install yices 2.6.1
RUN curl -sSOL https://yices.csl.sri.com/releases/2.6.1/yices-2.6.1-x86_64-pc-linux-gnu-static-gmp.tar.gz && \
  tar xf yices-2.6.1-x86_64-pc-linux-gnu-static-gmp.tar.gz && \
  cd /tmp/yices-2.6.1/ && \
  ./install-yices /opt/yices-2.6.1

# Install cmake manually for newer version
RUN wget https://github.com/Kitware/CMake/releases/download/v3.27.2/cmake-3.27.2-linux-x86_64.tar.gz
RUN tar xf cmake-3.27.2-linux-x86_64.tar.gz
RUN mv cmake-3.27.2-linux-x86_64 /opt/cmake
ENV PATH=$PATH:/opt/cmake/bin

RUN groupadd --gid 1000 maze \ 
    && useradd --uid 1000 --gid maze --shell /bin/bash --create-home maze
RUN echo 'maze  ALL=(root) NOPASSWD: ALL' >> /etc/sudoers

### Set up directory structure
USER maze
RUN mkdir -p /home/maze/tools
RUN mkdir -p /home/maze/workspace

# Assume that docker-build is ran in the top-level SeaHorn directory
WORKDIR /home/maze/tools
RUN git clone https://github.com/seahorn/seahorn.git  seahorn
# Re-create the build directory that might have been present in the source tree
WORKDIR /home/maze/tools/seahorn
RUN git checkout 36a3081
WORKDIR /home/maze/tools
RUN rm -rf seahorn/build seahorn/debug seahorn/release && \
  mkdir seahorn/build && \
# Remove any third-party dependencies that build process clones
  rm -rf seahorn/clam seahorn/sea-dsa seahorn/llvm-seahorn
  WORKDIR /home/maze/tools/seahorn/build

ARG BUILD_TYPE=Coverage

# Build configuration
RUN cmake .. -GNinja \
  -DCMAKE_BUILD_TYPE=Coverage \
  -DZ3_ROOT=/opt/z3-4.8.9 \
  -DYICES2_HOME=/opt/yices-2.6.1 \
  -DCMAKE_INSTALL_PREFIX=run \
  -DCMAKE_CXX_COMPILER=clang++-14 \
  -DCMAKE_C_COMPILER=clang-14 \
  -DSEA_ENABLE_LLD=ON \
  -DCPACK_GENERATOR="TGZ" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_CXX_OUTPUT_EXTENSION_REPLACE=ON  && \
  cmake --build . -j${CORE_COUNT} --target extra  && cmake .. && \
  cmake --build . -j${CORE_COUNT} --target crab  && cmake .. && \
  cmake --build . -j${CORE_COUNT} --target install && \
  cmake --build . -j${CORE_COUNT} --target units_z3 && \
  cmake --build . -j${CORE_COUNT} --target units_yices2 && \
  cmake --build . -j${CORE_COUNT} --target test_type_checker && \
  cmake --build . -j${CORE_COUNT} --target test_hex_dump && \
  cmake --build . -j${CORE_COUNT} --target package && \
  units/units_z3 && \
  units/units_yices2

RUN pip3 install --upgrade gcovr

ENV PATH "/home/maze/tools/seahorn/build/run/bin:$PATH"

USER maze
WORKDIR /home/maze/tools
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD get_coverage.sh /home/maze/tools/get_coverage.sh
ADD run_seahorn.sh /home/maze/tools/run_seahorn.sh
RUN sudo  chmod +x /home/maze/tools/*.sh
WORKDIR /home/maze/workspace