#!/bin/bash
## Get outdir
if ["$1" -eq ""]; then
    OUTDIR="smt_comp_benchmarks"
else
    OUTDIR=$1
fi 

## Download everything
echo "[*] Cloning into directory $OUTDIR"
for logic in BV ABV UFBV AUFBV LIA ALIA UFLIA AUFLIA; do
    wget "https://zenodo.org/records/11061097/files/QF_$logic.tar.zst";
    tar xf "QF_$logic.tar.zst";
    rm "QF_$logic.tar.zst";
done

## Cleanup
mv non-incremental $OUTDIR
mkdir $OUTDIR/bv
mkdir $OUTDIR/int
for logic in BV ABV UFBV AUFBV; do
    mv $OUTDIR/QF_$logic $OUTDIR/bv;
done
for logic in  LIA ALIA UFLIA AUFLIA; do
    mv $OUTDIR/QF_$logic $OUTDIR/int;
done
