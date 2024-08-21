#!/bin/bash

while getopts a:w:h:o:r:n:c:g:s:e:b:m:t:uEWID option
do
    case "${option}"
    in
    a) ALGORITHM=${OPTARG};;
    w) WIDTH=${OPTARG};;
    h) HEIGHT=${OPTARG};;
    o) OUTPUT_DIR=${OPTARG};;
    r) SEED=${OPTARG};;
    n) NUMB=${OPTARG};;
    c) CYCLE=${OPTARG};;
    g) GEN=${OPTARG};;
    s) SMT_PATH=${OPTARG};;
    e) EXIT=${OPTARG};;
    b) BUGTYPE=${OPTARG};;
    m) T_NUMB=${OPTARG};;
    t) T_TYPE=${OPTARG};;
    u) UNIT=1;;
    E) LOG='E';;
    W) LOG='W';;
    I) LOG='I';;
    D) LOG='D'
    esac
done

if [ -z ${ALGORITHM+x} ]; then
    echo "NOTE: No algorithm selected. Backtracking will be used."
    ALGORITHM="Backtracking"
fi

if [ -z ${UNIT+x} ]; then
    UNIT=0
else
    echo "NOTE: Generating unit maze"
    WIDTH=1
    HEIGHT=1
fi

if [[ -z ${WIDTH+x} || -z ${HEIGHT+x} ]]; then
    echo "Size of maze was not specified. Exiting..."
    exit 1
fi

case "${WIDTH#[-+]}" in
    *[!0-9]* | '')
        echo "Invalid size input: width should be a positive integer"
        exit 1;;
esac

case "${HEIGHT#[-+]}" in
    *[!0-9]* | '')
        echo "Invalid size input: height should be a positive integer"
        exit 1;;
esac

#(($WIDTH < 5)) && { echo "Invalid size input: width should be greater than 4"; exit 1; }
#(($HEIGHT < 5)) && { echo "Invalid size input: height should be greater than 4"; exit 1; }

if [ -z ${OUTPUT_DIR+x} ]; then
    echo "Output directory not specified. Exiting..."
    exit 1
fi

if [ -z ${NUMB+x} ]; then
    echo "NOTE: The number of mazes to chain was not specified. Default value of 1 will be used."
    NUMB=1
fi

case "${NUMB#[-+]}" in
    *[!0-9]* | '')
        echo "Invalid input: Id of mazes should be a positive integer"
        exit 1;;
esac

(($NUMB < 1)) && { echo "Invalid input: number of mazes should be greater than 0"; exit 1; }

if [ -z ${SEED+x} ]; then
    echo "NOTE: The seed was not specified. Default value of 1 will be used."
    SEED=1
fi

if [ -z ${CYCLE+x} ]; then
    echo "NOTE: The percentage of cycles was not specified. Default value of 0 will be used."
    CYCLE="0"
fi

if [ -z ${BUGTYPE} ]; then
    echo "NOTE: The bugtype was not specified. Default function __VERIFIER_ERROR() will be used."
    BUGTYPE="ve"
fi

if [ -z ${EXIT+x} ]; then
    EXIT="default"
fi

if [ -z ${GEN+x} ]; then
    echo "NOTE: The program generator was not specified. CVE generator will be used."
    GEN="CVE_gen"
fi

if [ -z ${T_TYPE} ]; then
    echo "NOTE: No transformations where specified. No transformations will be performed"
    T_TYPE="keepId"
    T_NUMB=0
fi

if [ -z ${T_NUMB} ]; then
    echo "NOTE: The number of transformed mazes was not specified. One transformation will be performed"
    T_NUMB=1
fi

if [ -z ${LOG+x} ]; then
    LOG="D"
fi

echo "Generating mazes..."
echo "##############################################"
echo "Algorithm: "$ALGORITHM
echo "Size: "$WIDTH" by "$HEIGHT
echo "Maze exit: "$EXIT
echo "Pseudo-random seed: "$SEED
echo "Remaining cycles: "$CYCLE"%"
echo "Number of mazes: "$NUMB
echo "Types of transformations used: "$T_TYPE
echo "Number of transformations per maze: "$T_NUMB
echo "Bugtype: "$BUGTYPE
echo "Generator used: "$GEN
echo "Output directory: "$OUTPUT_DIR
echo "##############################################"

MAZEGEN_DIR=$(readlink -f $(dirname "$0")/..)/src/maze_gen
mkdir -p $OUTPUT_DIR/src $OUTPUT_DIR/bin $OUTPUT_DIR/png $OUTPUT_DIR/txt $OUTPUT_DIR/sln $OUTPUT_DIR/smt $OUTPUT_DIR/smt/$SEED

NAME=$ALGORITHM"_"$WIDTH"x"$HEIGHT"_"$SEED"_"
if [ $UNIT -eq 0 ]; then
    python3 $MAZEGEN_DIR/array_gen.py $ALGORITHM $WIDTH $HEIGHT $SEED $EXIT $NUMB $T_TYPE $T_NUMB 
    if [ $? -eq 1 ]; then
        echo "Select one of the following algorithms: Backtracking, Kruskal, Prims, Wilsons, Sidewinder"
        exit 1
    fi
fi

MAZES=""
for (( INDEX=0; INDEX < $NUMB; INDEX++ ))
do
    MAZES=$MAZES$NAME$INDEX"_"$T_TYPE" "$WIDTH" "$HEIGHT" "
done
if [[ "$GEN" == *"CVE"* ]]; then
    SMT_NAME=$(basename $SMT_PATH .smt2)
    NAME_EXT="_"$CYCLE"percent_"$SMT_NAME"_gen_"$BUGTYPE
    python3 $MAZEGEN_DIR/array_to_code.py $LOG $SEED $BUGTYPE $T_TYPE $T_NUMB $OUTPUT_DIR $CYCLE $UNIT $GEN $SMT_PATH $MAZES
else
    NAME_EXT="_"$CYCLE"percent_"$GEN"_"$BUGTYPE
    python3 $MAZEGEN_DIR/array_to_code.py $LOG $SEED $BUGTYPE $T_TYPE $T_NUMB $OUTPUT_DIR $CYCLE $UNIT $GEN $MAZES
fi

MIN=1
if [[ "$T_TYPE" == *"keepId"* ]]; then
    MIN=0
fi
for (( T_INDEX=$MIN; T_INDEX<=$T_NUMB; T_INDEX++ ))
do
    NAME_P=$NAME"0_"$T_TYPE"_t"$T_INDEX$NAME_EXT;
    #gcc -O3 -w -o $NAME_P".bin" $NAME_P".c"
    for (( INDEX = 0; INDEX < $NUMB; INDEX++ ))
    do
        if [ $UNIT -eq 0 ]; then
            mv $NAME$INDEX"_"$T_TYPE"_t"$T_INDEX".png" $OUTPUT_DIR/png
            mv $NAME$INDEX"_"$T_TYPE"_t"$T_INDEX".txt" $OUTPUT_DIR/txt
        fi
    done
    if [[ "$T_TYPE" == *"last"* ]]; then
        if [[ $T_INDEX == $T_NUMB ]]; then
            mv $NAME_P".c" $OUTPUT_DIR/src
        fi
    else
        mv $NAME_P".c" $OUTPUT_DIR/src
    fi
done
for (( INDEX = 0; INDEX < $NUMB; INDEX++ ))
do
    if [ $UNIT -eq 0 ]; then
        mv $NAME$INDEX"_"$T_TYPE"_solution.txt" $OUTPUT_DIR/sln
    fi
done
echo "Done!"