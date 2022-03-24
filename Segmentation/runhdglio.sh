#!/bin/bash

export FREESURFER_HOME=/usr/local/freesurfer
source /usr/local/freesurfer/SetUpFreeSurfer.sh

basepath=/Downloads/LUMIERE/Imaging
cd ${basepath}

for d in ${basepath}/*; do
	for sd in ${d}/*; do

		echo ${sd}

		docker run -ti --rm --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=0 --mount type=bind,source="${sd}",target=/input --mount type=bind,source="${sd}",target=/output hdglio/custom -v

	done
	echo "processed $d"
done
