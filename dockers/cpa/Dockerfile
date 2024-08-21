FROM minotaur-cpa-base as build
# Install
RUN git checkout 0a0997b
RUN ant

### Add scripts
FROM minotaur-base
COPY --from=build /home/maze/tools /home/maze/tools
USER maze

RUN /home/maze/tools/cpa/scripts/cpa.sh
RUN sudo chmod +x /home/maze/tools/*.sh

WORKDIR /home/maze/workspace