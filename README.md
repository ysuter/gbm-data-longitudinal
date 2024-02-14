This repository contains the code used to prepare the data in:

# The LUMIERE Dataset: Longitudinal Glioblastoma MRI with Expert RANO Evaluation

Please cite the following publication when using this dataset:

> Suter, Y., Knecht, U., Valenzuela, W., Notter, M., Hewer, E., Schucht, P., Wiest, R. and Reyes, M., 2022. The LUMIERE dataset: Longitudinal Glioblastoma MRI with expert RANO evaluation. Scientific data, 9(1), p.768. [https://doi.org/10.1038/s41597-022-01881-7](https://www.nature.com/articles/s41597-022-01881-7)

The dataset can be downloaded from [Figshare](https://springernature.figshare.com/collections/The_LUMIERE_Dataset_Longitudinal_Glioblastoma_MRI_with_Expert_RANO_Evaluation/5904905/1). Please note that the data is available for non-commercial use.
## Overview

This repository contains technical details and code so other researchers can reproduce and adapt to their specific research questions.

## Timepoint discretization

To add ambiguity for stronger anonymization but to retain the necessary time resolution, all timing information is provided relative to the first (pre-operative) MRI study date in weeks. The week was calculated by a floor division by 7 starting with the time span in days.

## Automated segmentation

Segmentation was performed with DeepBraTumIA [1] and HD-GLIO-AUTO [2]. The run.py file of HD-GLIO-AUTO was slightly modified to retain the transform matrices to allow back-transformation to the original image space. No other changes were made. The adapted run.py file is available in the Segmentation/HD-GLIO-AUTO folder.

## Skull-stripping

HD-BET [3] was used to remove the skull to ensure no conclusion is possible regarding the patient's head shape. Please note that while we provide skull-stripped MRIs, the input to the automated segmentation tools always was the original non-skull-stripped version.

Please note that both DeepBraTumIA and HD-GLIO-AUTO use HD-BET for skull-stripping, but results may differ to different pipelines (e.g., co-registration). We also provide skull-stripped MRIs for cases where not all four MR sequences were available.

## Acknowledgement

This project was funded by Swiss Cancer Research (Krebsliga Schweiz), grant KFS-3979-08-2016. The NVIDIA Corporation donated a Titan Xp GPU.



The dataset was curated with great care. Please do not hesitate to contact us if you still find an error or inconsistency.

## References

[1] DeepBraTumIA: https://www.nitrc.org/projects/deepbratumia

[2] HD-GLIO-AUTO: Please cite the publications listed on the author's repository https://github.com/NeuroAI-HD/HD-GLIO-AUTO

[3] HD-BET: https://github.com/MIC-DKFZ/HD-BET
