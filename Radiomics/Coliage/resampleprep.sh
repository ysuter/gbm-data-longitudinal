#!/bin/bash

export FREESURFER_HOME=/usr/local/freesurfer
source /usr/local/freesurfer/SetUpFreeSurfer.sh

# insert path to image root directory
basepath=[INSERT PATH]

for d in ${basepath}/*; do
	for sd in ${d}/*; do

		echo ${sd}
		
		mkdir ${sd}/collageprep

		# resample MRIs to 1mm isovoxels
		mri_convert -vs 1 1 1 ${sd}/CT1_r2s_bet_reg.nii.gz ${sd}/collageprep/CT1_bet_reg_resampled.nii.gz
		mri_convert -vs 1 1 1 ${sd}/T1_r2s_bet_reg.nii.gz ${sd}/collageprep/T1_bet_reg_resampled.nii.gz	
		mri_convert -vs 1 1 1 ${sd}/T2_r2s_bet_reg.nii.gz ${sd}/collageprep/T2_bet_reg_resampled.nii.gz
		mri_convert -vs 1 1 1 ${sd}/FLAIR_r2s_bet_reg.nii.gz ${sd}/collageprep/FLAIR_bet_reg_resampled.nii.gz
		
		# resample segmentation mask
		mri_convert -vs 1 1 1 -rt nearest ${sd}/segmentation.nii.gz ${sd}/collageprep/segmentation_resampled.nii.gz
		
		# invert the transforms and get the inverse of the orientation alignment
		convert_xfm -omat ${sd}/collageprep/CT1_r2s_bet_reg_inverse.mat -inverse ${sd}/CT1_r2s_bet_reg.mat
		convert_xfm -omat ${sd}/collageprep/T1_r2s_bet_reg_inverse.mat -inverse ${sd}/T1_r2s_bet_reg.mat
		convert_xfm -omat ${sd}/collageprep/T2_r2s_bet_reg_inverse.mat -inverse ${sd}/T2_r2s_bet_reg.mat
		convert_xfm -omat ${sd}/collageprep/FLAIR_r2s_bet_reg_inverse.mat -inverse ${sd}/FLAIR_r2s_bet_reg.mat
		
		fslreorient2std -m ${sd}/collageprep/CT1_stdorient.mat ${sd}/CT1.nii.gz ${sd}/collageprep/CT1_stdorient.nii.gz
		fslreorient2std -m ${sd}/collageprep/T1_stdorient.mat ${sd}/T1.nii.gz ${sd}/collageprep/T1_stdorient.nii.gz
		fslreorient2std -m ${sd}/collageprep/T2_stdorient.mat ${sd}/T2.nii.gz ${sd}/collageprep/T2_stdorient.nii.gz
		fslreorient2std -m ${sd}/collageprep/FLAIR_stdorient.mat ${sd}/FLAIR.nii.gz ${sd}/collageprep/FLAIR_stdorient.nii.gz
		
		convert_xfm -omat ${sd}/collageprep/CT1_stdorient_inverse.mat -inverse ${sd}/collageprep/CT1_stdorient.mat
		convert_xfm -omat ${sd}/collageprep/T1_stdorient_inverse.mat -inverse ${sd}/collageprep/T1_stdorient.mat
		convert_xfm -omat ${sd}/collageprep/T2_stdorient_inverse.mat -inverse ${sd}/collageprep/T2_stdorient.mat
		convert_xfm -omat ${sd}/collageprep/FLAIR_stdorient_inverse.mat -inverse ${sd}/collageprep/FLAIR_stdorient.mat
		
		# concatenate registration and standard-orientation transforms und apply them
		convert_xfm -omat ${sd}/collageprep/CT1_invreg_std.mat -concat ${sd}/collageprep/CT1_stdorient_inverse.mat ${sd}/collageprep/CT1_r2s_bet_reg_inverse.mat
		convert_xfm -omat ${sd}/collageprep/T1_invreg_std.mat -concat ${sd}/collageprep/T1_stdorient_inverse.mat ${sd}/collageprep/T1_r2s_bet_reg_inverse.mat
		convert_xfm -omat ${sd}/collageprep/T2_invreg_std.mat -concat ${sd}/collageprep/T2_stdorient_inverse.mat ${sd}/collageprep/T2_r2s_bet_reg_inverse.mat
		convert_xfm -omat ${sd}/collageprep/FLAIR_invreg_std.mat -concat ${sd}/collageprep/FLAIR_stdorient_inverse.mat ${sd}/collageprep/FLAIR_r2s_bet_reg_inverse.mat
		
		flirt -in ${sd}/segmentation.nii.gz -out ${sd}/collageprep/segmentation_CT1_origspace.nii.gz -ref ${sd}/CT1.nii.gz -applyxfm -init ${sd}/collageprep/CT1_invreg_std.mat -interp "nearestneighbour"
		flirt -in ${sd}/segmentation.nii.gz -out ${sd}/collageprep/segmentation_T1_origspace.nii.gz -ref ${sd}/T1.nii.gz -applyxfm -init ${sd}/collageprep/T1_invreg_std.mat -interp "nearestneighbour"
		flirt -in ${sd}/segmentation.nii.gz -out ${sd}/collageprep/segmentation_T2_origspace.nii.gz -ref ${sd}/T2.nii.gz -applyxfm -init ${sd}/collageprep/T2_invreg_std.mat -interp "nearestneighbour"
		flirt -in ${sd}/segmentation.nii.gz -out ${sd}/collageprep/segmentation_FLAIR_origspace.nii.gz -ref ${sd}/FLAIR.nii.gz -applyxfm -init ${sd}/collageprep/FLAIR_invreg_std.mat -interp "nearestneighbour"		

	done
	echo "processed $d"
done


