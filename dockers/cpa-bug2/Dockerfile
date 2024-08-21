FROM minotaur-cpa-base

# Install
USER maze
RUN git checkout ec8f159a  
RUN ant

RUN mv /home/maze/tools/run_cpa.sh /home/maze/tools/run_cpa-bug2.sh

WORKDIR /home/maze/workspace