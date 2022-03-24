#!/usr/bin/env python3

import pandas as pd
import numpy as np

fulldata = "/LUMIERE/ExpertRating.csv"
methylationinfo = pd.read_csv("./LUMIERE/Demographics_Pathology.csv")

overall = pd.read_csv(fulldata)
overall["Rating"] = [e if "Op" not in e else "OP" for e in overall["Rating"]]
overall = overall[overall["Rating"].str.contains("None") == False]

patients_methylated = methylationinfo.loc[methylationinfo["MGMT qualitative"] == "methylated", "Patient"].values
patients_unmethylated = methylationinfo.loc[methylationinfo["MGMT qualitative"] == "not methylated", "Patient"].values

df_methylated = overall.loc[overall["Patient"].isin(patients_methylated)]
df_unmethylated = overall.loc[overall["Patient"].isin(patients_unmethylated)]

statelist = ['OP', 'CR', 'PR', 'SD', 'PD', 'Death']
deathobj = pd.Series({"Rating": "Death"})

transitions_methylated = pd.DataFrame(data=np.zeros((6, 6)), columns=statelist, index=statelist)
transitions_unmethylated = pd.DataFrame(data=np.zeros((6, 6)), columns=statelist, index=statelist)

# methylated
for patient in patients_methylated:
    currdf = df_methylated.loc[df_methylated["Patient"] == patient, "Rating"]
    currdf = pd.concat((currdf, deathobj), ignore_index=True)

    for idx in np.arange(1, currdf.shape[0]):
        transitions_methylated.at[currdf.values[idx - 1], currdf.values[idx]] += 1

transitions_methylated_norm = transitions_methylated.div(transitions_methylated.sum(axis=1), axis=0)

# not methylated
for patient in patients_unmethylated:
    currdf = df_unmethylated.loc[df_unmethylated["Patient"] == patient, "Rating"]
    currdf = pd.concat((currdf, deathobj), ignore_index=True)

    for idx in np.arange(1, currdf.shape[0]):
        transitions_unmethylated.at[currdf.values[idx - 1], currdf.values[idx]] += 1

transitions_unmethylated_norm = transitions_unmethylated.div(transitions_unmethylated.sum(axis=1), axis=0)
transitions_unmethylated_norm.to_csv("./statespace/unmethylated.csv")
transitions_methylated_norm.to_csv("./statespace/methylated.csv")
