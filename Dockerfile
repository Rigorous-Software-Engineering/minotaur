FROM minotaur-base
USER root
WORKDIR /home/maze/workspace

# Get additional dependencies 
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install \
    software-properties-common \
&& rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install \
    python3.10 \
    python3.10-dev \
&& rm -rf /var/lib/apt/lists/*

USER maze
RUN sudo update-alternatives --install /usr/bin/python3 pyhton3 /usr/bin/python3.10 1

# Install pip
RUN wget https://bootstrap.pypa.io/get-pip.py &&  python3 get-pip.py && rm get-pip.py

# # Install requirements
ADD dockers/gen/requirements.txt /home/maze/workspace/requirements.txt
RUN /home/maze/.local/bin/pip3 install -r requirements.txt
RUN python3 -m pysmt install --confirm-agreement --z3
WORKDIR /home/maze/tools

WORKDIR /home/maze/workspace
ADD . /home/maze/workspace/Minotaur

WORKDIR /home/maze/workspace