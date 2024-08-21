FROM minotaur-base as build 

# Install dependencies
RUN apt-get update && apt-get install -y \
    make \
    clang \
    maven \
    openjdk-11-jdk \
    zip \
    g++ \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /home/maze/tools/

USER maze

# Add scripts
RUN git clone https://github.com/ultimate-pa/ultimate.git
WORKDIR /home/maze/tools/ultimate
RUN git checkout c5dabf3
RUN sudo update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java 

WORKDIR /home/maze/tools/ultimate/releaseScripts/default
RUN ./makeFresh.sh
RUN mv *-linux /home/maze/tools

FROM minotaur-base
USER maze
RUN sudo update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java 
RUN sudo apt-get update && sudo apt-get install -y \
    build-essential \
&& sudo rm -rf /var/lib/apt/lists/*


WORKDIR /home/maze/tools/
COPY --from=build /home/maze/tools/UAutomizer-linux /home/maze/tools/UAutomizer-linux
COPY --from=build /home/maze/tools/UTaipan-linux /home/maze/tools/UTaipan-linux
COPY --from=build /home/maze/tools/UGemCutter-linux /home/maze/tools/UGemCutter-linux
COPY --from=build /home/maze/tools/UKojak-linux /home/maze/tools/UKojak-linux

ADD run_ultimate.sh /home/maze/tools/run_ultimate.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD unreach.prp /home/maze/workspace/unreach.prp

RUN sudo chmod +x *.sh

ENV PATH=$PATH:/home/maze/tools/UAutomizer-linux/

USER maze
WORKDIR /home/maze/workspace