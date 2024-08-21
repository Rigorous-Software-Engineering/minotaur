FROM minotaur-esbmc-base as build

USER root
RUN apt-get update && apt-get install -y \
    g++ \
    flex \
    bison \
    curl \
    patch \
    cmake \
    lcov \
&& rm -rf /var/lib/apt/lists/*

USER maze
WORKDIR /home/maze/tools
RUN git clone http://github.com/diffblue/2ls
WORKDIR /home/maze/tools/2ls
RUN git checkout c572aa1
RUN ./build.sh  

FROM minotaur-base
USER maze 
COPY --from=build /home/maze/tools/2ls /home/maze/tools/2ls

ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD run_2ls.sh /home/maze/tools/run_2ls.sh
RUN sudo chmod +x /home/maze/tools/*.sh

WORKDIR /home/maze/workspace

