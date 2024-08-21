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

# Get old version 
WORKDIR /home/maze/tools/ultimate
RUN git checkout  8a44606 

RUN sudo update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java 

WORKDIR /home/maze/tools/ultimate/releaseScripts/default
RUN ./makeFresh.sh
RUN mv *-linux /home/maze/tools

WORKDIR /home/maze/tools/

RUN mv UAutomizer-linux ua
RUN mv UGemCutter-linux ugc
RUN mv UTaipan-linux ut
RUN mv UKojak-linux uk

FROM minotaur-base
USER maze
WORKDIR /home/maze/tools/
COPY --from=build /home/maze/tools/ua /home/maze/tools/ua
COPY --from=build /home/maze/tools/ut /home/maze/tools/ut
COPY --from=build /home/maze/tools/ugc /home/maze/tools/ugc
COPY --from=build /home/maze/tools/uk /home/maze/tools/uk
RUN sudo update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java 

ADD run_ultimate.sh /home/maze/tools/run_ultimate-fixed3.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD unreach.prp /home/maze/workspace/unreach.prp
ENV PATH=$PATH:/home/maze/tools/ua/

WORKDIR /home/maze/workspace