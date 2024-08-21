FROM minotaur-cpa-base

# Install
USER maze
RUN git checkout f3059648 
RUN ant

RUN mv /home/maze/tools/run_cpa.sh /home/maze/tools/run_cpa-bug3.sh

WORKDIR /home/maze/workspace