#!/bin/bash
# invoke: ./batch_analyze_audio_48000 path/to/folder/of/movs/to/extract path/from/there/to/folder/for/analysis/data
# *OR*
#         ./batch_analyze_audio_48000 path/to/folder/of/movs/to/extract path/to/folder/for/analysis/data

OUTDIR=$2
DIR=$( cd "$( dirname "$0" )" && pwd )
echo $DIR
echo 'starting...'
MOVDIR=$1
cd $MOVDIR
ls */*.mov | while read m
do
	cd $DIR
	filename=$(basename "$m")
	filename="${filename%.*}"
 	tmpfile=`mktemp $OUTDIR/${filename}/${filename}.wav`
	echo " >>> $MOVDIR/$m"
	echo " >>> $filename"
	echo " >>> $tmpfile"
    echo '===========================MPLAYER=========================='
    echo ''
    mplayer -ao pcm:file=$tmpfile "$MOVDIR/$m" -benchmark -vc dummy -vo null & # -ss -endpos SECONDS
    echo '===========================WAIT=========================='
    echo ''
    wait
    echo '===========================MKDIR=========================='
    echo ''
    mkdir -p $OUTDIR
    echo '===========================@FFT_EXTRACT@=========================='
    echo ''
    #fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -f 0 -C 2 -g 0 -a 0 $tmpfile "$OUTDIR/${filename}/${filename}.stft_0_a0_C2_g0"
    echo '===========================@CQFT@=========================='
    if [ ! -f "$OUTDIR/${filename}/${filename}.cqft_12_a0_C2_g0_i16000" ];
    then
        echo " >>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -q 12 -i 16000 -C 2 -g 0 -a 0 $tmpfile $OUTDIR/${filename}/${filename}.cqft_12_a0_C2_g0_i16000"
        fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -q 12 -i 16000 -C 2 -g 0 -a 0 $tmpfile "$OUTDIR/${filename}/${filename}.cqft_12_a0_C2_g0_i16000"
    fi
    echo '===========================@CHROMA@=========================='
    if [ ! -f "$OUTDIR/${filename}/${filename}.chrom_12_a0_C2_g0_i16000" ];
    then
        echo " >>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -c 12 -i 16000 -C 2 -g 0 -a 0 $tmpfile $OUTDIR/${filename}/${filename}.chrom_12_a0_C2_g0_i16000"
        fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -c 12 -i 16000 -C 2 -g 0 -a 0 $tmpfile "$OUTDIR/${filename}/${filename}.chrom_12_a0_C2_g0_i16000"
    fi
    echo '===========================@MFCC@=========================='
    if [ ! -f "$OUTDIR/${filename}/${filename}.mfcc_13_M2_a0_C2_g0_i16000" ];
    then
        echo " >>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -m 13 -M 2 -i 16000 -C 2 -g 0 -a 0 $tmpfile $OUTDIR/${filename}/${filename}.mfcc_13_M2_a0_C2_g0_i16000"
        fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -m 13 -M 2 -i 16000 -C 2 -g 0 -a 0 $tmpfile "$OUTDIR/${filename}/${filename}.mfcc_13_M2_a0_C2_g0_i16000"
    fi
    echo '===========================@POWAH!@=========================='
    if [ ! -f "$OUTDIR/${filename}/${filename}.power_C2_i16000" ];
    then
        echo " >>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -P -i 16000 -C 2 $tmpfile $OUTDIR/${filename}/${filename}.power_C2_i16000"
        fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -P -i 16000 -C 2 $tmpfile "$OUTDIR/${filename}/${filename}.power_C2_i16000"
    fi
    # echo '===========================@RMDIR@========================='
    # echo ''
    # rm $tmpfile
done
echo 'done!'
done
cd $DIR