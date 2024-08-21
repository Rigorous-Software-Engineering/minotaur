FROM minotaur-cpa-base

# Install
USER maze
RUN git checkout cdee5c75 
RUN ant

RUN mv /home/maze/tools/run_cpa.sh /home/maze/tools/run_cpa-fixed1.sh

WORKDIR /home/maze/workspace