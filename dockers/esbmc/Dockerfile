FROM minotaur-esbmc-base
ARG CORE_COUNT=4

USER maze
WORKDIR /home/maze/tools/esbmc
RUN git checkout c2728f2

RUN mkdir build 
WORKDIR /home/maze/tools/esbmc/build
RUN cmake .. -GNinja -DENABLE_COVERAGE=On -DDOWNLOAD_DEPENDENCIES=On -DBUILD_STATIC=On -DBoolector_DIR=$PWD/../../boolector-release -DZ3_DIR=$PWD/../../z3 -DENABLE_MATHSAT=ON -DMathsat_DIR=$PWD/../../mathsat -DENABLE_YICES=On -DYices_DIR=$PWD/../../yices -DCVC4_DIR=$PWD/../../cvc4 -DGMP_DIR=$PWD/../../gmp -DCMAKE_INSTALL_PREFIX:PATH=$PWD/../../release
RUN cmake --build . -j${CORE_COUNT}
RUN ninja install

RUN pip3 install gcovr

WORKDIR /home/maze/tools
USER maze
ADD run_esbmc.sh /home/maze/tools/run_esbmc.sh

USER root
RUN chmod +rwx *.sh
USER maze
### Cleanup
WORKDIR /home/maze/workspace