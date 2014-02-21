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
	echo "=== checking for analysis files..."
	echo " (if all the audio analysis files exist, no WAV file is generated...) "
	echo ""
	if [ ! -f "$OUTDIR/${filename}/${filename}.cqft" ] || [ ! -f "$OUTDIR/${filename}/${filename}.chrom" ] || [ ! -f "$OUTDIR/${filename}/${filename}.mfcc" ] || [ ! -f "$OUTDIR/${filename}/${filename}.power" ]; then
		WAVFLAG=1
		echo '***********WAV ANALYSIS NEEDED*************'
		echo ''
		tmpfile=`mktemp $OUTDIR/${filename}/${filename}.wav`
		echo ">>> $tmpfile"
	fi
	echo "flag: $WAVFLAG"
	if [ $WAVFLAG == 1 ]; then
		echo '===========================MPLAYER=========================='
		echo ''
		mplayer -ao pcm:file=$tmpfile "${MOVDIR}/${m}" -benchmark -vc dummy -vo null & # -ss -endpos SECONDS
		echo ">>> mplayer -ao pcm:waveheader pcm:file=$tmpfile $MOVDIR/$m -benchmark -vc dummy -vo null & "
		
		echo '===========================WAIT=========================='
		echo ''
		wait
	fi
	# echo '===========================@FFT_EXTRACT@=========================='
	# echo ''
	if [ ! -f "$OUTDIR/${filename}/${filename}.power" ] && [ $WAVFLAG == 1 ]; then
		echo '=== begin Power extraction...'
		echo ">>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -P -l 62.5 -i 16000 -C 2 $tmpfile $OUTDIR/${filename}/${filename}.power"
		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -P -l 62.5 -i 16000 -C 2 $tmpfile "$OUTDIR/${filename}/${filename}.power"
	fi
	if [ ! -f "$OUTDIR/${filename}/${filename}.cqft" ] && [ $WAVFLAG == 1 ] ; then
		echo '=== begin CQFT extraction...'
		echo ">>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -q 12 -l 62.5 -i 16000 -C 2 $tmpfile $OUTDIR/${filename}/${filename}.cqft"
		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -q 12 -l 62.5 -i 16000 -C 2 $tmpfile "$OUTDIR/${filename}/${filename}.cqft"
	fi
	if [ ! -f "$OUTDIR/${filename}/${filename}.mfcc" ] && [ $WAVFLAG == 1 ]; then
		echo '=== begin MFCC extraction...'
		echo ">>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -m 13 -l 62.5 -i 16000 -C 2 $tmpfile $OUTDIR/${filename}/${filename}.mfcc"
		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -m 13 -l 62.5 -i 16000 -C 2 $tmpfile "$OUTDIR/${filename}/${filename}.mfcc"
	fi
	if [ ! -f "$OUTDIR/${filename}/${filename}.chrom" ] && [ $WAVFLAG == 1 ]; then
		echo '=== begin Chroma extraction...'
		echo ">>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -c 12 -l 62.5 -i 16000 -C 2 $tmpfile $OUTDIR/${filename}/${filename}.chrom"
		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -c 12 -l 62.5 -i 16000 -C 2 $tmpfile "$OUTDIR/${filename}/${filename}.chrom"
	fi
# comment  rm wav file
#	if [ $WAVFLAG == 1 ]; then
# 		echo '===========================@RMDIR@========================='
# 		echo ''
# 		rm $tmpfile
#	fi
done
echo 'done!'
cd $DIR