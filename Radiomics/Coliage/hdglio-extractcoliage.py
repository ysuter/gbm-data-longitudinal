#!/usr/bin/env python3

import os
import SimpleITK as sitk
import collageradiomics
from tqdm import tqdm

rootdir = "./LUMIERE/Imaging"

filelist = ["CT1_bet_reg_resampled.nii.gz", "T1_bet_reg_resampled.nii.gz",
            "T2_bet_reg_resampled.nii.gz", "FLAIR_bet_reg_resampled.nii.gz"]
filenames = ["T1c", "T1", "T2", "FLAIR"]
segmentation = "segmentation.nii.gz"

patientlist = sorted([elem for elem in os.listdir(rootdir) if os.path.isdir(os.path.join(rootdir, elem))])

runningidx = 0

for patient in tqdm(patientlist):
    patdir = os.path.join(rootdir, patient)
    tplist = [elem for elem in os.listdir(patdir) if os.path.isdir(os.path.join(patdir, elem))]

    for tp in tplist:
        tpdir = os.path.join(patdir, tp)
        currsegpath = os.path.join(tpdir, segmentation)

        if os.path.isfile(currsegpath):
            seg = sitk.ReadImage(currsegpath)
            segarr = sitk.GetArrayFromImage(seg)
        else:
            continue

        for idx, f in enumerate(filelist):
            currimgpath = os.path.join(tpdir, f)

            primaryname = "collage_hdglio_" + filenames[idx] + "_primary.nii.gz"
            secondaryname = "collage_hdglio" + filenames[idx] + "_secondary.nii.gz"

            # skip if it already exists
            if os.path.isfile(os.path.join(tpdir, secondaryname)):
                continue

            if os.path.isfile(currimgpath) and os.path.isfile(currsegpath):
                img = sitk.ReadImage(currimgpath)

                try:
                    collage = collageradiomics.Collage(
                        sitk.GetArrayFromImage(img),
                        segarr,
                        svd_radius=5,
                        verbose_logging=True,
                        num_unique_angles=64
                    )

                    full_images = collage.execute()

                    # split dominant and non-dominant angles to separate images
                    feat_primary = full_images[:, :, :, :, 0]
                    feat_secondary = full_images[:, :, :, :, 1]

                    feat_primary_sitk = sitk.GetImageFromArray(feat_primary, isVector=True)
                    feat_secondary_sitk = sitk.GetImageFromArray(feat_secondary, isVector=True)

                    feat_primary_sitk.CopyInformation(img)
                    feat_secondary_sitk.CopyInformation(img)

                    sitk.WriteImage(feat_primary_sitk, os.path.join(tpdir, primaryname))
                    sitk.WriteImage(feat_secondary_sitk, os.path.join(tpdir, secondaryname))

                    print('- ' + str(runningidx))
                    runningidx += 1
                except:
                    print(patient)
                    print(tp)
                    continue
