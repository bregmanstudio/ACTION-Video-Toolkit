#!/bin/bash

ACTIONDIR=$1
ZIPDIR=$2
echo "using:"
echo $ACTIONDIR
echo ""
echo $ZIPDIR
echo ""
mkdir $ZIPDIR
cd $ACTIONDIR
find . -mindepth 1 -maxdepth 1 -type d | while read f
do
	base=$(basename "$f")
	echo "---"
	echo "! -f ${ZIPDIR}${base}.zip ??"
if [ ! -f "${ZIPDIR}${base}.zip" ];
	then
		echo "zip -rX ${base}.zip ${base} -x '*.mov' '.DS_Store' '*.wav'"
        `zip -rX ${base}.zip ${base} -x '*.mov' '.DS_Store' '*.wav'`
		echo "mv ${base}.zip ${ZIPDIR}${base}.zip"
        `mv ${base}.zip ${ZIPDIR}${base}.zip`
	fi
done
