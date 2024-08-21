#!/bin/bash
# ARG 1: Outdir
# ARG 2: Outfile
CBMC_DIR="/home/maze/tools/cbmc"
mkdir -p "$1"
python3 -m gcovr -r "$CBMC_DIR/src" --filter="$CBMC_DIR/src/" --filter="$CBMC_DIR/build/src" --json "$1/$2".json "$CBMC_DIR/build/src/cbmc"