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
	if [ ! -f "${ZIPDIR}${base}.zip" ] && [ -e "${base}/${base}.color_lab" ]; then
#		echo "! -f ${base} ??"
#		echo "! -f ${base}/${base}.mfcc ??"	
		echo "zip -rX ${base}.zip ${base} -x '*.mov' '.DS_Store' '*.wav' '*.mp4'"
		`zip -rX ${base}.zip ${base} -x '*.mov' '.DS_Store' '*.wav' '*.mp4'`
		echo "mv ${base}.zip ${ZIPDIR}${base}.zip"
        `mv ${base}.zip ${ZIPDIR}${base}.zip`
	fi
done
