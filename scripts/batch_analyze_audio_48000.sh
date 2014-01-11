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
	echo " >>> $MOVDIR/$m"
	echo " >>> $filename"
	WAVFLAG=0
	echo '==========================checking for analysis files======='
	echo ''
	if [ ! -f "$OUTDIR/${filename}/${filename}.cqft_12_a0_C2_g0_i16000" ] || [ ! -f "$OUTDIR/${filename}/${filename}.chrom_12_a0_C2_g0_i16000" ] || [ ! -f "$OUTDIR/${filename}/${filename}.mfcc_13_M2_a0_C2_g0_i16000" ] || [ ! -f "$OUTDIR/${filename}/${filename}.power_C2_i16000" ]; then
		WAVFLAG=1
		echo '***********WAV ANALYSIS NEEDED*************'
		echo ''
		tmpfile=`mktemp $OUTDIR/${filename}/${filename}.wav`
		echo " >>> $tmpfile"
	fi
	echo "flag: $WAVFLAG"
	if [ $WAVFLAG == 1 ]; then
		echo '===========================MPLAYER=========================='
		echo ''
		mplayer -ao pcm:file=$tmpfile "${MOVDIR}/${m}" -benchmark -vc dummy -vo null & # -ss -endpos SECONDS
		echo " >>> mplayer -ao pcm:file=$tmpfile $MOVDIR/$m -benchmark -vc dummy -vo null & "
		echo '===========================WAIT=========================='
		echo ''
		wait
	fi
	# echo '===========================MKDIR=========================='
	# echo ''
	# mkdir -p $OUTDIR
	# echo '===========================@FFT_EXTRACT@=========================='
	# echo ''
	# fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -f 0 -C 2 -g 0 -a 0 $tmpfile "$OUTDIR/${filename}/${filename}.stft_0_a0_C2_g0"
	if [ ! -f "$OUTDIR/${filename}/${filename}.cqft_12_a0_C2_g0_i16000" ] && [ $WAVFLAG == 1 ] ; then
		echo '===========================@CQFT@=========================='
		echo " >>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -q 12 -i 16000 -C 2 -g 0 -a 0 $tmpfile $OUTDIR/${filename}/${filename}.cqft_12_a0_C2_g0_i16000"
		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -q 12 -i 16000 -C 2 -g 0 -a 0 $tmpfile "$OUTDIR/${filename}/${filename}.cqft_12_a0_C2_g0_i16000"
	fi
	if [ ! -f "$OUTDIR/${filename}/${filename}.chrom_12_a0_C2_g0_i16000" ] && [ $WAVFLAG == 1 ]; then
		echo '===========================@CHROMA@=========================='
		echo " >>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -c 12 -i 16000 -C 2 -g 0 -a 0 $tmpfile $OUTDIR/${filename}/${filename}.chrom_12_a0_C2_g0_i16000"
		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -c 12 -i 16000 -C 2 -g 0 -a 0 $tmpfile "$OUTDIR/${filename}/${filename}.chrom_12_a0_C2_g0_i16000"
	fi
	if [ ! -f "$OUTDIR/${filename}/${filename}.mfcc_13_M2_a0_C2_g0_i16000" ] && [ $WAVFLAG == 1 ]; then
		echo '===========================@MFCC@=========================='
		echo " >>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -m 13 -M 2 -i 16000 -C 2 -g 0 -a 0 $tmpfile $OUTDIR/${filename}/${filename}.mfcc_13_M2_a0_C2_g0_i16000"
		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -m 13 -M 2 -i 16000 -C 2 -g 0 -a 0 $tmpfile "$OUTDIR/${filename}/${filename}.mfcc_13_M2_a0_C2_g0_i16000"
	fi
	if [ ! -f "$OUTDIR/${filename}/${filename}.power_C2_i16000" ] && [ $WAVFLAG == 1 ]; then
		echo '===========================@POWAH!@=========================='
		echo " >>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -P -i 16000 -C 2 $tmpfile $OUTDIR/${filename}/${filename}.power_C2_i16000"
		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -P -i 16000 -C 2 $tmpfile "$OUTDIR/${filename}/${filename}.power_C2_i16000"
	fi
	if [ $WAVFLAG == 1 ]; then
		echo '===========================@RMDIR@========================='
		echo ''
		rm $tmpfile
	fi
done
echo 'done!'
cd $DIR