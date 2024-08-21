FROM minotaur-cpa-base

# Install
USER maze
RUN git pull
RUN git checkout 8aceff65  
RUN ant

RUN mv /home/maze/tools/run_cpa.sh /home/maze/tools/run_cpa-fixed4.sh

WORKDIR /home/maze/workspace