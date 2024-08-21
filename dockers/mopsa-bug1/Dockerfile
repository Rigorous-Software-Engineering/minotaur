FROM minotaur-base
ARG CORE_COUNT

RUN sudo dpkg --add-architecture i386 
RUN apt-get update && apt-get install -y \
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
    zlib1g-dev \
    libc6-i386 \
&& rm -rf /var/lib/apt/lists/*

USER maze
WORKDIR /home/maze/tools/
RUN git clone https://gitlab.com/mopsa/mopsa-analyzer.git
WORKDIR /home/maze/tools/mopsa-analyzer
RUN git checkout a7964f3f
RUN opam init --yes --disable-sandboxing
RUN opam switch create 4.14.1
RUN eval $(opam env)


RUN opam install -j${CORE_COUNT} --deps-only --with-doc --with-test --yes .
RUN opam config exec ./configure
RUN make
RUN make install

ADD svcomp.c /home/maze/tools/mopsa-analyzer/share/mopsa/stubs/c/mopsa/svcomp.c

WORKDIR /home/maze/tools
ADD run_mopsa.sh /home/maze/tools/run_mopsa-bug1.sh
RUN sudo chmod +x run_mopsa-bug1.sh 

ADD get_tcs.py /home/maze/tools/get_tcs.py

WORKDIR /home/maze/workspace/
