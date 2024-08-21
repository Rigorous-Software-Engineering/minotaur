#!/bin/bash
# ARG 1: Outdir
# ARG 2: Outfile
SEAHORN_DIR="/home/maze/tools/seahorn"
mkdir -p "$1"
python3 -m gcovr --gcov-executable "llvm-cov-14 gcov" -r "$SEAHORN_DIR/lib/seahorn" --filter "$SEAHORN_DIR/lib/seahorn" --filter "$SEAHORN_DIR/build/lib/seahorn" --merge-mode-functions=separate --json "$1/$2".json "$SEAHORN_DIR/build/lib/seahorn"