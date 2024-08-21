#!/bin/bash
# ARGS: $1 Number of cores
set -e

if [ "$1" == "" ]; then
    CORE_COUNT="1"
else
    CORE_COUNT=$1
fi

DOCKERDIR=$(readlink -f $(dirname "$0")/..)/dockers
for tool in base \
    cpa-base cpa-bug1 cpa-fixed1 cpa-bug2 cpa-fixed2 cpa-bug3 cpa-fixed3 cpa-bug4 cpa-fixed4  \
    ultimate-bug1 ultimate-bug2 ultimate-bug3 ultimate-bug4 \
    ultimate-fixed1 ultimate-fixed2 ultimate-fixed3 ultimate-fixed4 \
    esbmc-base esbmc-bug1 esbmc-fixed1 esbmc-bug2 esbmc-fixed2 esbmc-bug3 esbmc-fixed3 esbmc-bug4 esbmc-fixed4 \
    mopsa-bug1 mopsa-fixed1 mopsa-bug2 mopsa-fixed2;
    do echo "[*] Build minotaur-$tool Docker image..."; cd "$DOCKERDIR/$tool"; docker build --rm --network=host --ulimit nofile=1024 -t minotaur-$tool . --build-arg CORE_COUNT=$CORE_COUNT; echo "[*] Done!";
done; 
echo "[*] Build minotaur-gen Docker image..."; cd "$DOCKERDIR/.."; docker build --rm --network=host --ulimit nofile=1024 -t minotaur-gen .; echo "[*] Done!";
