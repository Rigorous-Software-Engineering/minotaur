#!/bin/bash

# Arg1: File containing targets
# Arg2: Timeout (in minutes)
# Arg3: Variant 


sudo chown -R maze:maze /home/maze/tools/$3

WORKDIR=/home/maze/workspace

OUTDIR=$WORKDIR/outputs
mkdir -p $OUTDIR

for maze in $(cat $1)
do
    name=$(basename $maze)
    OUTFILE=$OUTDIR/res$name
    # Create dummy file to indicate running start
    touch $WORKDIR/.start$name
    timeout -k 2s $2s  /home/maze/tools/$3/Ultimate.py --spec unreach.prp --witness-dir $OUTDIR --architecture 64bit --file $maze &> $OUTFILE
    touch $WORKDIR/.end$name
done
