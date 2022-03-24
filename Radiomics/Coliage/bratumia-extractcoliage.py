#!/usr/bin/env python3

import os
import SimpleITK as sitk
import collageradiomics
from tqdm import tqdm

rootdir = "./LUMIERE/Imaging"

filelist = ["_t1c_accurate_skull_stripped.nii.gz", "_t1_accurate_skull_stripped.nii.gz",
            "_t2_accurate_skull_stripped.nii.gz", "_flair_accurate_skull_stripped.nii.gz"]
filenames = ["T1c", "T1", "T2", "FLAIR"]
segmentationpostfix = "_accurate_seg_mask.nii.gz"

patientlist = sorted([elem for elem in os.listdir(rootdir) if os.path.isdir(os.path.join(rootdir, elem))])

runningidx = 0

failedlist = []

for patient in tqdm(patientlist):
    patdir = os.path.join(rootdir, patient)

    currsegpath = os.path.join(patdir, 'Segmentation', patient + segmentationpostfix)

    if os.path.isfile(currsegpath):
        seg = sitk.ReadImage(currsegpath)
        segarr = sitk.GetArrayFromImage(seg)
    else:
        continue

    for idx, f in enumerate(filelist):
        currimgpath = os.path.join(patdir, "Skull_stripped", patient + f)

        primaryname = "collage_" + filenames[idx] + "_primary.nii.gz"
        secondaryname = "collage_" + filenames[idx] + "_secondary.nii.gz"

        if os.path.isfile(os.path.join(patdir, secondaryname)):
            continue

        if os.path.isfile(currimgpath) and os.path.isfile(currsegpath):
            img = sitk.ReadImage(currimgpath)

            try:
                collage = collageradiomicscustom.Collage(
                    sitk.GetArrayFromImage(img),
                    segarr,
                    svd_radius=5,
                    verbose_logging=True,
                    num_unique_angles=64
                )

                full_images = collage.execute()

                # split dominant and non-dominant angles to separate images?
                feat_primary = full_images[:, :, :, :, 0]
                feat_secondary = full_images[:, :, :, :, 1]

                feat_primary_sitk = sitk.GetImageFromArray(feat_primary, isVector=True)
                feat_secondary_sitk = sitk.GetImageFromArray(feat_secondary, isVector=True)

                feat_primary_sitk.CopyInformation(img)
                feat_secondary_sitk.CopyInformation(img)

                sitk.WriteImage(feat_primary_sitk, os.path.join(patdir, primaryname))
                sitk.WriteImage(feat_secondary_sitk, os.path.join(patdir, secondaryname))

                print('- ' + str(runningidx))
                runningidx += 1
            except:
                failedlist.append(patient)
                continue
print(failedlist)
