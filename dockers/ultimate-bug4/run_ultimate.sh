#!/bin/bash

# Arg1: File containing targets
# Arg2: Timeout (in minutes)
# Arg3: Variant 
# Arg4: Config



WORKDIR=/home/maze/workspace

OUTDIR=$WORKDIR/outputs
mkdir -p $OUTDIR

UDIR="/home/maze/tools/U${3}-linux"
sudo chown -R maze:maze $UDIR
export PATH=$PATH:$UDIR 

for maze in $(cat $1)
do
    name=$(basename $maze)
    OUTFILE=$OUTDIR/res$name
    # Create dummy file to indicate running start
    touch $WORKDIR/.start$name
    timeout -k 2s $2s  $UDIR/Ultimate -tc $UDIR/config/${3}Reach.xml -s $UDIR/config/svcomp-Reach-64bit-${3}_$4.epf -i $maze &> $OUTFILE
    touch $WORKDIR/.end$name
done