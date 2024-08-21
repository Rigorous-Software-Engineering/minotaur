FROM minotaur-esbmc-base as build
ARG CORE_COUNT=4

### Build esbmc
USER maze
WORKDIR /home/maze/tools/esbmc
RUN git checkout 5001667
RUN mkdir build 
WORKDIR /home/maze/tools/esbmc/build
RUN cmake .. -GNinja -DDOWNLOAD_DEPENDENCIES=On -DBUILD_STATIC=On -DBoolector_DIR=$PWD/../../boolector-release -DZ3_DIR=$PWD/../../z3 -DENABLE_MATHSAT=ON -DMathsat_DIR=$PWD/../../mathsat -DENABLE_YICES=On -DYices_DIR=$PWD/../../yices -DCVC4_DIR=$PWD/../../cvc4 -DGMP_DIR=$PWD/../../gmp -DCMAKE_INSTALL_PREFIX:PATH=$PWD/../../release
RUN cmake --build . -j${CORE_COUNT}
RUN ninja install

FROM minotaur-base
USER maze

COPY --from=build /home/maze/tools/cvc4 /home/maze/tools/cvc4 
COPY --from=build /home/maze/tools/z3 /home/maze/tools/z3
COPY --from=build /home/maze/tools/yices /home/maze/tools/yices
COPY --from=build /home/maze/tools/boolector-release/ /home/maze/tools/boolector-release/ 
COPY --from=build /home/maze/tools/mathsat /home/maze/tools/mathsat
COPY --from=build /home/maze/tools/release /home/maze/tools/release
ENV PATH=/home/maze/tools/cvc4/bin:/home/maze/tools/z3/bin:/home/maze/tools/yices/bin:/home/maze/tools/boolector-release/bin:/home/maze/tools/mathsat/bin:$PATH

COPY --from=build /home/maze/tools/run_esbmc.sh /home/maze/tools/
COPY --from=build /home/maze/tools/get_tcs.py /home/maze/tools/


WORKDIR /home/maze/tools
RUN mv /home/maze/tools/run_esbmc.sh /home/maze/tools/run_esbmc-fixed1.sh 
RUN sudo chmod +x /home/maze/tools/run_esbmc-fixed1.sh

### Cleanup
WORKDIR /home/maze/workspace