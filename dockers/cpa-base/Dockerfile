FROM minotaur-base

# Install
WORKDIR /home/maze/tools/

RUN apt-get update && apt-get install -y \
    ant \
    openjdk-17-jdk \
    openjdk-17-jre \
&& rm -rf /var/lib/apt/lists/*

### Add scripts
USER maze

WORKDIR /home/maze/tools/
RUN git clone https://gitlab.com/sosy-lab/software/cpachecker.git cpa
ADD run_cpa.sh /home/maze/tools/run_cpa.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD svcompNotl.properties /home/maze/tools/cpa/config/svcompNotl.properties

WORKDIR /home/maze/tools/cpa