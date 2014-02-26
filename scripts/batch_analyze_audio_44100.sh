#!/bin/bash
# invoke: ./batch_analyze_audio_44100 path/to/folder/of/movs/to/extract path/from/there/to/folder/for/analysis/data
# *OR*
#         ./batch_analyze_audio_44100 path/to/folder/of/movs/to/extract path/to/folder/for/analysis/data

MOVDIR=$1
cd $MOVDIR
ls */*.mp4 | while read m
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

	WAVFLAG=0
	echo "=== checking for analysis files..."
	echo " (if all the audio analysis files exist, no WAV file is generated...) "
	echo ""
	if [ ! -f "${filename}/${filename}.cqft" ] || [ ! -f "${filename}/${filename}.chrom" ] || [ ! -f "${filename}/${filename}.mfcc" ] || [ ! -f "${filename}/${filename}.power" ]; then
		WAVFLAG=1
		echo '***********WAV ANALYSIS NEEDED*************'
		echo ''
		rm "${filename}/${filename}.wav"
		tmpfile=`mktemp ${filename}/${filename}.wav`
		#tmpfile="${filename}/${filename}.wav"	
		echo ">>> $tmpfile"
	fi
	echo "flag: $WAVFLAG"
# 	if [ $WAVFLAG == 1 ]; then
		echo '===========================MPLAYER=========================='
		echo ''
		rm $tmpfile
		mplayer -ao pcm:file=$tmpfile "${filename}/${filename}.mov" -benchmark -vc dummy -vo null & # -ss -endpos SECONDS
		echo ">>> mplayer pcm:file=${tmpfile} ${filename}/${filename}.mov -benchmark -vc dummy -vo null & "
		
		#echo '===========================WAIT=========================='
		#echo ''
		#wait
# 	fi
	# echo '===========================@FFT_EXTRACT@=========================='
	# echo ''
	if [ ! -f "${filename}.powe" ] && [ $WAVFLAG == 1 ]; then
		echo '=== begin Power extraction...'
		rm "${filename}/${filename}.power"
		echo ">>> fftExtract -p action.wis -n 44100 -w 44100 -h 1837.5 -P -l 62.5 -i 16000 -C 2 ${tmpfile} ${filename}/${filename}.power"
		fftExtract -p action.wis -n 44100 -w 44100 -h 8192 -P -l 62.5 -i 16000 -C 2 $tmpfile "${filename}/${filename}.power"
	fi
	if [ ! -f "${filename}.cqf" ] && [ $WAVFLAG == 1 ] ; then
		echo '=== begin CQFT extraction...'
		rm "${filename}/${filename}.cqft"
		echo ">>> fftExtract -p action.wis -n 44100 -w 44100 -h 1837.5 -q 12 -l 62.5 -i 16000 -C 2 ${tmpfile} ${filename}/${filename}.cqft"
		fftExtract -p action.wis -n 44100 -w 44100 -h 8192 -q 12 -l 62.5 -i 16000 -C 2 $tmpfile "${filename}/${filename}.cqft"
	fi
	if [ ! -f "${filename}.mfc" ] && [ $WAVFLAG == 1 ]; then
		echo '=== begin MFCC extraction...'
		rm "${filename}/${filename}.mfcc"
		echo ">>> fftExtract -p action.wis -n 44100 -w 44100 -h 1837.5 -m 13 -l 62.5 -i 16000 -C 2 ${tmpfile} ${filename}/${filename}.mfcc"
		fftExtract -p action.wis -n 44100 -w 44100 -h 8192 -m 13 -l 62.5 -i 16000 -C 2 $tmpfile "${filename}/${filename}.mfcc"
	fi
	if [ ! -f "${filename}.chro" ] && [ $WAVFLAG == 1 ]; then
		echo '=== begin Chroma extraction...'
		rm "${filename}/${filename}.chrom"
		echo ">>> fftExtract -p action.wis -n 44100 -w 44100 -h 1837.5 -c 12 -l 62.5 -i 16000 -C 2 ${tmpfile} ${filename}/${filename}.chrom"
		fftExtract -p action.wis -n 44100 -w 44100 -h 8192 -c 12 -l 62.5 -i 16000 -C 2 $tmpfile "${filename}/${filename}.chrom"
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
