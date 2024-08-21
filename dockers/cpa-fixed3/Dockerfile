FROM minotaur-cpa-base

# Install
USER maze
RUN git checkout e675a9cd 
RUN ant

RUN mv /home/maze/tools/run_cpa.sh /home/maze/tools/run_cpa-fixed3.sh

WORKDIR /home/maze/workspace