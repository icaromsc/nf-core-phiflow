#!/usr/bin/python

#Adapted from https://github.com/signalbash/how_are_we_stranded_here

import argparse
import numpy as np
import pandas as pd
import csv
import os
import sys
import re
#from statistics import median
#from statistics import stdev

#print python version
#print(sys.version_info) 


#### continue from here inputs

#Parse arguments from command line 

parser = argparse.ArgumentParser(description='Check if bam files are stranded')
parser.add_argument('-s', '--strand', type=str, help='.txt output file from infer_experiment.py', required = True)
parser.add_argument('library',type=str, help='Library type: single-end or paired-end data',choices=['single','paired'])

args = parser.parse_args()

library = args.library
#Check library type choosed
if library == 'single':
    single_strand = True
else:
    single_strand = False

result = pd.read_csv(args.strand, sep="\r\n", header=None, engine='python')

failed = float(result.iloc[1,0].replace('Fraction of reads failed to determine: ', ''))

if single_strand:
    fwd = float(result.iloc[2,0].replace('Fraction of reads explained by "++,--": ', ''))
    rev = float(result.iloc[3,0].replace('Fraction of reads explained by "+-,-+": ', ''))
else:
    fwd = float(result.iloc[2,0].replace('Fraction of reads explained by "1++,1--,2+-,2-+": ', ''))
    rev = float(result.iloc[3,0].replace('Fraction of reads explained by "1+-,1-+,2++,2--": ', ''))
fwd_percent = fwd/(fwd+rev)
rev_percent = rev/(fwd+rev)

#strandness option for featurecounts
strandness = False

print(result.iloc[0,0])
print(result.iloc[1,0])
print(result.iloc[2,0] + " (" + str(round(fwd_percent*100, 1)) + "% of explainable reads)")
print(result.iloc[3,0] + " (" + str(round(rev_percent*100, 1)) + "% of explainable reads)")


if float(result.iloc[1,0].replace('Fraction of reads failed to determine: ', '')) > 0.50:
    print('Failed to determine strandedness of > 50% of reads.')
    print('If this is unexpected, try running again with a higher --nreads value')
if fwd_percent > 0.9:
    if single_strand:
        print('Over 90% of reads explained by "++,--"')
        print('Data is likely FR/fr-stranded')
    else:
        print('Over 90% of reads explained by "1++,1--,2+-,2-+"')
        print('Data is likely FR/fr-secondstrand')
    strandedness = 1
    print('FeatureCounts parameter will be:\n -s 1')
elif rev_percent > 0.9:
    if single_strand:
        print('Over 90% of reads explained by "+-,-+"')
        print('Data is likely RF/rf-stranded')
    else:
        print('Over 90% of reads explained by "1+-,1-+,2++,2--"')
        print('Data is likely RF/fr-firststrand')
    strandedness = 2
    print('FeatureCounts parameter will be:\n -s 2')
elif max(fwd_percent, rev_percent) < 0.6:
    print('Under 60% of reads explained by one direction')
    print('Data is likely unstranded')
    strandedness = 0
    print('FeatureCounts parameter will be:\n -s 0')
else:
    print('Data does not fall into a likely stranded (max percent explained > 0.9) or unstranded layout (max percent explained < 0.6)')
    print('Please check your data for low quality and contaminating reads before proceeding')
    sys.exit(1)

with open("check_strandness_result.txt", "wt") as fhout:
    fhout.write("{}\n".format(strandedness))