#!/bin/bash

set -e

if [ "$1" == "" ]; then
    CORE_COUNT="1"
else
    CORE_COUNT=$1
fi

DOCKERDIR=$(readlink -f $(dirname "$0")/..)/dockers
for tool in base cpa-base cpa esbmc-base esbmc cbmc seahorn ultimate 2ls mopsa symbiotic;
    do echo "[*] Build minotaur-$tool Docker image..."; cd "$DOCKERDIR/$tool"; docker build --network=host --ulimit nofile=1024 --rm --build-arg="CORE_COUNT=$CORE_COUNT" -t minotaur-$tool .; echo "[*] Done!";
done; 
echo "[*] Build minotaur-gen Docker image..."; cd "$DOCKERDIR/.."; docker build --ulimit nofile=1024 --network=host --rm -t minotaur-gen .; echo "[*] Done!";
