#!/bin/bash
# invoke: ./batch_analyze_audio_48000 path/to/folder/of/movs/to/extract
#
# ANALYSIS METADATA written to same folder as MOV and WAV files!

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

    #echo "=== convert MP4 -> MOV MJPEG..."
    #echo "rm ${filename}/${filename}.mov"
    #echo "ffmpeg -i ${filename}/${filename}.mp4 -vcodec mjpeg -y -r 24 -acodec pcm_s16le ${filename}/${filename}.mov &"
    #rm "${filename}/${filename}.mov"
    #ffmpeg -i "${filename}/${filename}.mp4" -vcodec mjpeg -y -r 24 -acodec pcm_s16le "${filename}/${filename}.mov" &
    #wait

    WAVFLAG=1
    echo "=== checking for analysis files..."
    echo " (if all the audio analysis files exist, no WAV file is generated...) "
    echo ""
#    if ([ ! -f "${filename}/${filename}.cqft" ] || [ ! -f "${filename}/${filename}.chrom" ] || [ ! -f "${filename}/${filename}.mfcc" ] || [ ! -f "${filename}/${filename}.power" ]) && [ ! -f "${filename}/${filename}.wav" ]; then
#		WAVFLAG=1
		echo '***********WAV ANALYSIS NEEDED*************'
		echo ''
#		rm "${filename}/${filename}.wav"
#		tmpfile=`mktemp ${filename}/${filename}.wav`
#    fi
    echo "flag: $WAVFLAG"
    if [ $WAVFLAG == 1 ]; then
		echo '===========================MPLAYER=========================='
		echo ''
		mplayer -ao pcm:waveheader -ao pcm:file=$tmpfile "${filename}/${filename}.mov" -benchmark -vc dummy -vo null & # -ss -endpos SECONDS
		echo ">>> mplayer -ao pcm:waveheader -ao pcm:file=${tmpfile} ${filename}/${filename}.mov -benchmark -vc dummy -vo null & "

		echo '===========================WAIT=========================='
		echo ''
		wait
	else
		tmpfile="${filename}/${filename}.wav"
		WAVFLAG=0
    fi
    echo '===========================@FFT_EXTRACT@=========================='
    echo ''
    echo ">>> $tmpfile"
	
#    if [ ! -f "${filename}/${filename}.power" ] && [ $WAVFLAG == 1 ]; then
#		echo '=== begin Power extraction...'
#		echo ">>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -P -l 62.5 -i 16000 -C 2 $tmpfile ${filename}/${filename}.power"
#		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -P -l 62.5 -i 16000 -C 2 $tmpfile "${filename}/${filename}.power"
#	fi
#	if [ ! -f "${filename}/${filename}.cqft" ] && [ $WAVFLAG == 1 ] ; then
#		echo '=== begin CQFT extraction...'
#		echo ">>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -q 12 -l 62.5 -i 16000 -C 2 $tmpfile ${filename}/${filename}.cqft"
#		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -q 12 -l 62.5 -i 16000 -C 2 $tmpfile "${filename}/${filename}.cqft"
#	fi
#	if [ ! -f "${filename}/${filename}.mfcc" ] && [ $WAVFLAG == 1 ]; then
#		echo '=== begin MFCC extraction...'
#		echo ">>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -m 13 -l 62.5 -i 16000 -C 2 $tmpfile ${filename}/${filename}.mfcc"
#		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -m 13 -l 62.5 -i 16000 -C 2 $tmpfile "${filename}/${filename}.mfcc"
#	fi
#	if [ ! -f "${filename}/${filename}.chrom" ] && [ $WAVFLAG == 1 ]; then
#		echo '=== begin Chroma extraction...'
#		echo ">>> fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -c 12 -l 62.5 -i 16000 -C 2 $tmpfile ${filename}/${filename}.chrom"
#		fftExtract -p action.wis -n 48000 -w 48000 -h 12000 -c 12 -l 62.5 -i 16000 -C 2 $tmpfile "${filename}/${filename}.chrom"
#	fi

# comment  rm wav file
#	if [ $WAVFLAG == 1 ]; then
# 		echo '===========================@RMDIR@========================='
# 		echo ''
# 		rm $tmpfile
#	fi
done
echo 'done!'
cd $DIR
