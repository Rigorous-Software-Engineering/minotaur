#!/bin/bash

# Arg1: File containing targets
# Arg2: Timeout (in minutes)
# Arg3: Variant


WORKDIR=/home/maze/workspace

OUTDIR=$WORKDIR/outputs
mkdir -p $OUTDIR

for maze in $(cat $1)
do
    name=$(basename $maze)
    OUTFILE=$OUTDIR/res$name
    # Create dummy file to indicate running start
    touch $WORKDIR/.start$name
    timeout -k 2s $2s  /home/maze/tools/symbiotic/scripts/symbiotic --exit-on-error $maze &> $OUTFILE 
    touch $WORKDIR/.end$name
done