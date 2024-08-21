#!/bin/bash

# Arg1: File containing targets
# Arg2: Timeout (in minutes)
# Arg3: Variant

# 

WORKDIR=/home/maze/workspace

OUTDIR=$WORKDIR/outputs
mkdir -p $OUTDIR

for maze in $(cat $1)
do
    name=$(basename $maze)
    OUTFILE=$OUTDIR/res$name
    # Create dummy file to indicate running start
    touch $WORKDIR/.start$name
    timeout -k 2s $2s  /home/maze/tools/mopsa-analyzer/bin/mopsa -c-check-unsigned-implicit-cast-overflow false -no-color -config c/$3.json -additional-stubs c/mopsa/svcomp.c -ccopt -fbracket-depth=2048 $maze >  $OUTFILE 
    touch $WORKDIR/.end$name
done
