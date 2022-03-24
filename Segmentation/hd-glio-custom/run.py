#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

:AUTHOR: Jens Petersen
:ORGANIZATION: Heidelberg University Hospital; German Cancer Research Center
:CONTACT: jens.petersen@dkfz.de
:VERSION: 0.1
:THIS VERSION WAS ADAPTED TO RETAIN THE REGISTRATION MATRICES

"""
# =============================================================================
# IMPORT STATEMENTS
# =============================================================================

import argparse
from datetime import datetime
import os
import re
import shutil
import subprocess as subp
import time
import traceback
import multiprocessing as mp
from functools import partial
import nibabel as nib
import numpy as np

# =============================================================================
# METHODS & CLASSES
# =============================================================================


def reorient2std(file_, overwrite=False):
    out_file = file_.replace(".nii.gz", "_r2s.nii.gz")
    if not os.path.exists(out_file) or overwrite:
        cmd = ["fslreorient2std", file_, out_file]
        output = subp.check_output(cmd)
    else:
        output = "{} already exists and overwrite=False.".format(out_file)
    return out_file, output


def register_to_t1(file_, reference_file, overwrite=False):
    out_file = file_.replace(".nii.gz", "_reg.nii.gz")
    mat_file = file_.replace(".nii.gz", "_reg.mat")
    if not os.path.exists(out_file) or overwrite:
        cmd = [
            "flirt",
            "-in",
            file_,
            "-ref",
            reference_file,
            "-out",
            out_file,
            "-dof",
            "6",
            "-interp",
            "spline",
            "-omat",
            mat_file,
        ]
        output = subp.check_output(cmd)
    else:
        output = "{} already exists and overwrite=False.".format(out_file)
    return out_file, output


def run(
    t1,
    ct1,
    t2,
    flair,
    output_dir,
    make_t1sub=False,
    verbose=False,
    overwrite=False,
    necrosis_to_background=False,
    copy_permissions=True,
):

    # switch to output dir to do work and create temporary working dir
    old_wd = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)
    existing_files = os.listdir(output_dir)
    files_to_remove = [
        "T1.nii",
        "T1.nii.gz",
        "T1_r2s.nii.gz",
        "T1_r2s_bet.nii.gz",
        "T1_r2s_bet_mask.nii.gz",
        # "T1_r2s_bet_reg.mat",
        "T1_info.txt",
        "CT1.nii",
        "CT1.nii.gz",
        "CT1_r2s.nii.gz",
        "CT1_r2s_bet.nii.gz",
        "CT1_r2s_bet_mask.nii.gz",
        # "CT1_r2s_bet_reg.mat",
        "CT1_info.txt",
        "T2.nii",
        "T2.nii.gz",
        "T2_r2s.nii.gz",
        "T2_r2s_bet.nii.gz",
        "T2_r2s_bet_mask.nii.gz",
        # "T2_r2s_bet_reg.mat",
        "T2_info.txt",
        "FLAIR.nii",
        "FLAIR.nii.gz",
        "FLAIR_r2s.nii.gz",
        "FLAIR_r2s_bet.nii.gz",
        "FLAIR_r2s_bet_mask.nii.gz",
        # "FLAIR_r2s_bet_reg.mat",
        "FLAIR_info.txt",
        "plans.pkl",
        "segmentation_0000.nii.gz",
        "segmentation_0001.nii.gz",
        "segmentation_0002.nii.gz",
        "segmentation_0003.nii.gz",
        "T1_r2s_bet_reg_norm.nii.gz",
        "CT1_r2s_bet_reg_norm.nii.gz",
    ]
    files_to_keep = [
        # "mask.nii.gz",
        "T1_r2s_bet_reg.nii.gz",
        "CT1_r2s_bet_reg.nii.gz",
        "T2_r2s_bet_reg.nii.gz",
        "FLAIR_r2s_bet_reg.nii.gz",
        "segmentation.nii.gz",
        "volumes.txt",
        "postprocessing.json",
        "T1_r2s_bet_reg.mat",
        "CT1_r2s_bet_reg.mat",
        "T2_r2s_bet_reg.mat",
        "FLAIR_r2s_bet_reg.mat",
    ]
    if make_t1sub:
        files_to_keep.append("T1sub_r2s_bet_reg.nii.gz")

    files = [t1, ct1, t2, flair]
    names = ["T1w", "T1wCE", "T2w", "FLAIR"]
    filenames_after_preprocessing = [
        "T1_r2s_bet_reg.nii.gz",
        "CT1_r2s_bet_reg.nii.gz",
        "T2_r2s_bet_reg.nii.gz",
        "FLAIR_r2s_bet_reg.nii.gz",
    ]

    # check if all preprocessed files are already there, if so, skip all of it
    need_preprocess = False
    for f in filenames_after_preprocessing:
        if f not in existing_files:
            need_preprocess = True
    if overwrite:
        need_preprocess = True

    if not need_preprocess:
        files = [os.path.join(output_dir, f) for f in filenames_after_preprocessing]
        if verbose:
            print(
                "All preprocessed inputs for segmentation are available, skipping preprocessing."
            )
    else:

        # convert to NIfTI if necessary, otherwise copy to output_dir
        for f, file_ in enumerate(files):
            if not overwrite:
                if names[f] + ".nii" in existing_files:
                    files[f] = os.path.join(output_dir, names[f] + ".nii")
                    if verbose:
                        print(names[f] + ".nii already exists, continuing.")
                    continue
                elif names[f] + ".nii.gz" in existing_files:
                    files[f] = os.path.join(output_dir, names[f] + ".nii.gz")
                    if verbose:
                        print(names[f] + ".nii.gz already exists, continuing.")
                    continue
            if os.path.isdir(file_):
                # cmd = [
                #     "mcverter",
                #     "-o",
                #     output_dir,
                #     "-f",
                #     "nifti",
                #     "-v",
                #     "-n",
                #     "-F",
                #     names[f],
                #     file_,
                # ]

                cmd = [
                    "dcm2niix",
                    "-o",
                    output_dir,
                    "-b",
                    "n",
                    "-f",
                    names[f],
                    file_,
                ]

                output = subp.check_output(cmd)
                if verbose:
                    print(
                        "Converted {} to NIfTI with the following output:".format(
                            os.path.basename(file_)
                        )
                    )
                    print(output)
                files[f] = os.path.join(output_dir, names[f] + ".nii")
            else:
                new_file = os.path.join(output_dir, os.path.basename(file_))
                shutil.copy(file_, new_file)
                files[f] = new_file
                if verbose:
                    print(
                        "Copied {} to output directory.".format(os.path.basename(file_))
                    )

        # zip if necessary
        for f, file_ in enumerate(files):
            if not file_.endswith(".gz"):
                if (
                    not overwrite
                    and os.path.basename(file_.replace(".nii", ".nii.gz"))
                    in existing_files
                ):
                    files[f] = file_.replace(".nii", ".nii.gz")
                    if verbose:
                        print(
                            os.path.basename(file_.replace(".nii", ".nii.gz"))
                            + " already exists, not zipping .nii file."
                        )
                    continue
                output = subp.check_output(["gzip", file_])
                if verbose:
                    print(
                        "Zipped {} with the following output:".format(
                            os.path.basename(file_)
                        )
                    )
                    print(output)
                files[f] = file_.replace(".nii", ".nii.gz")

        # Reorient to standard
        p = mp.Pool(min(len(files), mp.cpu_count()))
        results = p.map(partial(reorient2std, overwrite=overwrite), files)
        files, outputs = list(zip(*results))
        files = list(files)
        if verbose:
            print(
                "Reoriented all files to standard orientation with the following outputs:"
            )
            for output in outputs:
                print(output)

        # save the current files, we will use the transformations from
        # the registrations AFTER BET to register them to a reference space
        # and then apply the BET mask!
        files_r2s = [f for f in files]

        # check the spacing for all files to determine which one will be our
        # reference. Default is T1
        ref_index = 0
        min_spacing = 1e9
        for f, file_ in enumerate(files):
            try:
                file_ = nib.load(file_)
                spacing = int(np.product(file_.header.get_zooms()))
                if spacing < min_spacing:
                    min_spacing = spacing
                    ref_index = f
            except Exception as e:
                continue
        print("Using contrast {} as reference".format(names[ref_index]))

        # Brain extraction (do not parallelize because we run on gpu)
        mask_files = []
        for f, file_ in enumerate(files):
            mask_file = file_.replace(".nii.gz", "_bet_mask.nii.gz")
            mask_files.append(mask_file)
            new_file = file_.replace(".nii.gz", "_bet.nii.gz")
            if (
                not overwrite
                and os.path.basename(new_file) in existing_files
                and os.path.basename(mask_file) in existing_files
            ):
                files[f] = new_file
                print(
                    "{} and {} already exist, continuing.".format(
                        os.path.basename(new_file), os.path.basename(mask_file)
                    )
                )
                continue
            # output1 = subp.check_output(["hd-bet", "-i", file_, "-device", "0"])
            # print("File:")
            # print(file_)
            # print("New File:")
            # print(new_file)
            cmd = ["cp", file_, new_file]
            # cmd = ["fslmaths", new_file, "-mas", mask_file, new_file]
            output2 = subp.check_output(cmd)
            files[f] = new_file
            if verbose:
                print(
                    "Applied brain extraction for {} with the following output:".format(
                        os.path.basename(file_)
                    )
                )
                print(output)

        # Copy reference mask to a new file to keep later
        # shutil.copyfile(
        #     mask_files[ref_index],
        #     os.path.join(os.path.dirname(mask_files[ref_index]), "mask.nii.gz"),
        # )

        # Register to reference
        results = p.map(
            partial(
                register_to_t1, reference_file=files[ref_index], overwrite=overwrite
            ),
            files,
        )
        files, outputs = list(zip(*results))
        if verbose:
            print("Registered all sequences to T1 with the following outputs:")
            for output in outputs:
                print(output)

        # Transform original files (after r2s) to reference space with .mat files
        # from previous step, then apply reference BET mask.
        for f, file_ in enumerate(files_r2s):
            name = files[f]
            ref_file = files[ref_index]
            mat_file = files[f].replace(".nii.gz", ".mat")
            mat_file_inv = files[f].replace(".nii.gz", "_inv.mat")
            # mask_file = mask_files[ref_index]  # reference BET mask
            cmd = [
                "flirt",
                "-in",
                file_,
                "-out",
                name,
                "-ref",
                ref_file,
                "-applyxfm",
                "-init",
                mat_file,
                "-interp",
                "spline",
            ]
            output = subp.check_output(cmd)
            cmd = [
                "convert_xfm",
                "-omat",
                mat_file_inv,
                "-inverse",
                mat_file,
            ]
            output = subp.check_output(cmd)
            # cmd = ["fslmaths", name, "-mas", mask_file, name]
            # output2 = subp.check_output(cmd)
            if verbose:
                print("Re-applied masks to registered files with outputs:")
                print(output)
                print(output2)

    # T1 subtraction map
    if make_t1sub and (overwrite or "T1sub_r2s_bet.nii.gz" not in existing_files):
        t1_file = files[0]
        ct1_file = files[1]
        sub_file = files[0].replace("T1", "T1sub")
        for f in (t1_file, ct1_file):
            nifti = nib.load(f)
            data = nifti.get_data()
            data = data - np.mean(data)
            data = data / np.std(data)
            new = nib.Nifti1Image(data, nifti.affine, nifti.header)
            outname = f.replace(".nii.gz", "_norm.nii.gz")
            nib.save(new, outname)
        cmd = [
            "fslmaths",
            ct1_file.replace(".nii.gz", "_norm.nii.gz"),
            "-sub",
            t1_file.replace(".nii.gz", "_norm.nii.gz"),
            sub_file,
        ]
        output = subp.check_output(cmd)
        if verbose:
            print("Made T1 subtraction map with output:")
            print(output)

    # prepare Decathlon format for nnU-Net and run segmentation
    if overwrite or "segmentation.nii.gz" not in existing_files:
        cmd = [
            "hd_glio_predict",
            "-t1",
            files[0],
            "-t1c",
            files[1],
            "-t2",
            files[2],
            "-flair",
            files[3],
            "-o",
            "segmentation.nii.gz",
        ]
        output = subp.check_output(cmd)
        if necrosis_to_background:
            seg_file = os.path.join(output_dir, "segmentation.nii.gz")
            img = nib.load(seg_file)
            data = img.get_data()
            data[data == 3] = 0  # necrosis to background
            nib.save(img, seg_file)
        if verbose:
            print("Created segmentation.nii.gz with the following output:")
            print(output)
    elif verbose:
        print("segmentation.nii.gz already exists, continuing.")

    # transform segmentation mask back to the original (re-oriented images)
    seg_file = os.path.join(output_dir, "segmentation.nii.gz")
    for fidx_, file_ in enumerate(files):
        segoutname = file_.replace(".nii.gz", "_seg.nii.gz")
        cmd = [
            "flirt",
            "-in",
            seg_file,
            "-ref",
            files_r2s[fidx_],
            "-applyxfm",
            "-init",
            mat_file_inv[fidx_],
            "-interp",
            "nearestneighbour",
            "-o",
            segoutname,
        ]
        output = subp.check_output(cmd)

    # get volumes
    if overwrite or "volumes.txt" not in existing_files:
        seg_file = os.path.join(output_dir, "segmentation.nii.gz")
        img = nib.load(seg_file)
        data = img.get_data()
        vol_edema = np.sum(data == 1)
        vol_enhancing = np.sum(data == 2)
        with open(os.path.join(output_dir, "volumes.txt"), "w") as out_file:
            out_file.write(
                "volume_non_enhancing_T2_FLAIR_signal_abnormality_mm3: {:.2f}".format(
                    vol_edema
                )
            )
            out_file.write("\n")
            out_file.write(
                "volume_contrast_enhancing_tumor_mm3: {:.2f}".format(vol_enhancing)
            )
        if verbose:
            print("Created volumes.txt")
    else:
        if verbose:
            print("volumes.txt already exists, continuing.")

    # Remove all files we created and don't want to keep
    for file_ in files_to_remove:
        if file_ in existing_files:
            continue
        else:
            try:
                os.remove(os.path.join(output_dir, file_))
                if verbose:
                    print("Removed {}".format(file_))
            except FileNotFoundError:
                continue

    # Set permissions of files we created
    if copy_permissions:
        for file_ in files_to_keep:
            if file_ in existing_files:
                continue
            else:
                shutil.copymode(t1, os.path.join(output_dir, file_))
                shutil.chown(
                    os.path.join(output_dir, file_),
                    user=os.stat(t1).st_uid,
                    group=os.stat(t1).st_gid,
                )
                if verbose:
                    print("Set permissions for {}".format(file_))

    os.chdir(old_wd)


# =============================================================================
# MAIN METHOD
# =============================================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Glioblastoma Segmentation")
    parser.add_argument(
        "-i", "--input_dir", type=str, required=True, help="Input directory"
    )
    parser.add_argument(
        "-o", "--output_dir", type=str, default=None, help="Output directory"
    )
    parser.add_argument("-t1sub", action="store_true", help="Create T1 subtraction map")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Toggle verbose output"
    )
    parser.add_argument(
        "-ow", "--overwrite", action="store_true", help="Overwrite existing files"
    )
    parser.add_argument(
        "-d", "--device", type=str, default="0", help="Select GPU (integer, default=0)"
    )
    parser.add_argument("-kn", "--keep_necrosis", action="store_true", help="Do not remove necrosis from segmentation")
    parser.add_argument(
        "-np",
        "--no_permissions",
        action="store_true",
        help="Do not adjust permissions of created files (meaning they will be owned by root)",
    )
    args = parser.parse_args()

    if args.output_dir is None:
        output_dir = args.input_dir
    else:
        output_dir = args.output_dir

    inputs = os.listdir(args.input_dir)
    inputs_resolved = []
    for identifier in ("T1w", "T1wCE", "T2w", "FLAIR"):
        identifier_options = (identifier + ".nii.gz", identifier + ".nii", identifier)
        for option in identifier_options:
            if option in inputs:
                inputs_resolved.append(option)
                break
        else:
            raise IOError("Could not find input for {}".format(identifier))
    for i in range(4):
        inputs_resolved[i] = os.path.join(args.input_dir, inputs_resolved[i])

    os.environ["CUDA_VISIBLE_DEVICES"] = args.device

    run(
        *inputs_resolved,
        output_dir,
        args.t1sub,
        args.verbose,
        args.overwrite,
        False,
        not args.no_permissions
    )

# -*- coding: utf-8 -*-
