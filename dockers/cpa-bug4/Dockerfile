FROM minotaur-cpa-base

# Install
USER maze
RUN git checkout 413c89ea 
RUN ant

RUN mv /home/maze/tools/run_cpa.sh /home/maze/tools/run_cpa-bug4.sh

WORKDIR /home/maze/workspace