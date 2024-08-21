FROM minotaur-cpa-base

# Install
USER maze
RUN git checkout 9a29873a 
RUN ant

RUN mv /home/maze/tools/run_cpa.sh /home/maze/tools/run_cpa-bug1.sh

WORKDIR /home/maze/workspace