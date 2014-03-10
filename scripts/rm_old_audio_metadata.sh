#!/bin/bash
# invoke: ./rm_old_audio_metadata ACTION_DIR
#
# ANALYSIS METADATA written to same folder as MOV and WAV files! Be careful.

DIR=$( cd "$( dirname "$0" )" && pwd )
echo $DIR
echo 'starting...'
MOVDIR=$1
cd $MOVDIR
ls */*.mov | while read m
do
    filename=$(basename "$m")
    filename="${filename%.*}"
    echo " >>> $filename"

	echo `rm ${filename}/${filename}.cqft_*`
	echo `rm ${filename}/${filename}.mfcc_*`
	echo `rm ${filename}/${filename}.chrom_*`
	echo `rm ${filename}/${filename}.power_*`	

    done
echo 'done!'
cd $DIR
