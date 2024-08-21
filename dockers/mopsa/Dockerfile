FROM minotaur-base
ARG CORE_COUNT
RUN sudo dpkg --add-architecture i386 

RUN apt-get update && apt-get install -y \
    zlib1g-dev \
    libc6-i386 \
    opam \
    llvm \
    clang \
    llvm-dev \
    libclang-dev \
    libclang-cpp10-dev \
    libgmp-dev \
    libmpfr-dev \
    autoconf \
    pkg-config \
&& rm -rf /var/lib/apt/lists/*

USER maze
WORKDIR /home/maze/tools/
RUN git clone https://github.com/antoinemine/apron.git apron
WORKDIR /home/maze/tools/apron
RUN git checkout 66fa6a4
RUN \
    opam init --disable-sandboxing -y && \
    eval $(opam env) && \
    opam switch create 4.14.0 && \
    eval $(opam env) && \
    opam update -y && \
    opam install -j${CORE_COUNT} -y ocamlfind camlidl mlgmpidl 
RUN opam config exec ./configure
RUN make
RUN sudo make install

WORKDIR /home/maze/tools
RUN git clone https://gitlab.com/mopsa/mopsa-analyzer.git
WORKDIR /home/maze/tools/mopsa-analyzer
RUN git checkout 2429b5d0
RUN \
    eval $(opam env) && \
    opam update -y && \
    opam install -j${CORE_COUNT} -y dune zarith menhir yojson
RUN opam config exec ./configure
RUN make
RUN make install
    
ADD svcomp.c /home/maze/tools/mopsa-analyzer/share/mopsa/stubs/c/mopsa/svcomp.c

WORKDIR /home/maze/tools
ADD run_mopsa.sh /home/maze/tools/run_mopsa.sh
RUN sudo chmod +x run_mopsa.sh 

ADD get_tcs.py /home/maze/tools/get_tcs.py

USER root
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install \
    software-properties-common \
    cvise \
&& rm -rf /var/lib/apt/lists/*

ENV PATH=$PATH:/home/maze/tools/mopsa-analyzer/bin
USER maze

WORKDIR /home/maze/workspace/
