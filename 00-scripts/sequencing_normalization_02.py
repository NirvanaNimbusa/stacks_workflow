#!/usr/bin/env python
"""Calculate new volumes needed to normalize the sequencing depth per sample
and then create a DNA plate template with these volumes for a new library.

Usage:
    ./00-scripts/sequencing_normalization_02.py targetNumReads minimumReads totalVolume

Where:
    targetNumReads = desired total number of sequenced reads [int]
"""

# Modules
# Excel support
from xlrd import open_workbook
from xlutils.copy import copy

# Other modules
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import sys
import os

# Classes

# Functions
def _getOutCell(outSheet, colIndex, rowIndex):
    """ HACK: Extract the internal xlwt cell representation. """
    row = outSheet._Worksheet__rows.get(rowIndex)
    if not row: return None

    cell = row._Row__cells.get(colIndex)
    return cell

def setOutCell(outSheet, col, row, value):
    """ Change cell value without changing formatting. """
    # HACK to retain cell style.
    previousCell = _getOutCell(outSheet, col, row)
    # END HACK, PART I

    outSheet.write(row, col, value)

    # HACK, PART II
    if previousCell:
        newCell = _getOutCell(outSheet, col, row)
        if newCell:
            newCell.xf_idx = previousCell.xf_idx
    # END HACK


# Parsing user input
try:
    targetNumReads = int(sys.argv[1])
    minimumReads = int(sys.argv[2])
    totalVolume = float(sys.argv[3])
except:
    print __doc__
    sys.exit(1)

# Main

# Global variables
folder="03-samples"

chips = [x.replace(".infos", "") for x in os.listdir(folder) if x.endswith(".infos")]

# Iterate over the chips
for chip in chips:

    # File names
    info_file = os.path.join(folder, chip + ".infos")
    numseq_file = os.path.join(folder, chip + ".numseq")

    # Load data into pandas data frame
    info_df = pd.read_csv(info_file, sep="\t", header=None)
    info_df = info_df.ix[:,0:5]
    info_df.columns = ["Chip", "Barcode", "Population", "Individual", "PopID", "Well"]

    numseq_df = pd.read_csv(numseq_file, sep=" ", header=None)
    numseq_df.columns = ["Barcode", "NumReads"]

    # Merge infos and number of reads into one dataframe
    data = pd.merge(info_df, numseq_df, on="Barcode")

    # Computations
    sum_reads = sum(data["NumReads"])
    data["Missing"] = targetNumReads - data["NumReads"]
    data.loc[data["NumReads"] > targetNumReads, "Missing"] = 0
    data.loc[data["NumReads"] < minimumReads, "Missing"] = 0

    data["Correction"] = data["Missing"].astype(float) / data["NumReads"]

    data["Volume"] = data["Correction"] / sum(data["Correction"]) * totalVolume
    data.loc[(data["Volume"] < 1) & (data["Missing"] > 0), "Volume"] = 1.0
    data.loc[(data["Missing"] == 0) & (data["NumReads"] < minimumReads), "Volume"] = 0.0

    # Create output csv file
    rows = list("ABCDEFGH")
    columns = range(1, 13)

    # Open Excel template, get link to first sheet and print name of chip
    rb = open_workbook("01-info_files/normalization_template.xls", formatting_info=True)
    wb = copy(rb)
    s = wb.get_sheet(0)

    # Print some useful informations (chip name, some stats...)
    print chip
    print "  {0:.2f} million usable reads produced".format(sum_reads / 1000000.)
    print "  {0:.1f} million reads still needed to reach {1:.1f} million reads per sample".format(
        float(data.shape[0]) * (float(targetNumReads) - sum_reads /
            float(data.shape[0])) / 1000000.0,
        targetNumReads / 1000000.0)
    print "  {0:.2f} more chips needed".format(
        (float(data.shape[0]) * targetNumReads - sum_reads) / float(sum_reads))

    setOutCell(s, 6, 0, chip + "(" + totalVolume + "ul to resequence)")
    setOutCell(s, 2, 10, "{0:.2f} million usable reads produced".format(
        sum_reads / 1000000.))
    setOutCell(s, 2, 11, "{0:.1f} million reads still needed to reach {1:.1f} million reads per sample".format(
        float(data.shape[0]) * (float(targetNumReads) - sum_reads / float(data.shape[0])) / 1000000.0,
        targetNumReads / 1000000.0))
    setOutCell(s, 2, 12, "{0:.2f} more chips needed".format(
        (float(data.shape[0]) * targetNumReads - sum_reads) / float(sum_reads)))

    # Create empty plate
    plate = pd.DataFrame(np.zeros([8, 12]))
    plate.columns = columns
    plate.index = rows

    # Fill plate with data
    for well in data["Well"]:
        row = well[0]
        column = int(well[1:])
        volume = float(data.loc[data["Well"] == well, "Volume"])
        volume = "{0:.1f}".format(round(volume, 1))
        plate.loc[row, column] = volume

    # Output data array for debugging purposes
    data.to_csv(os.path.join(folder, chip + "_data.csv"), sep="\t", index=False)

    # Fill Excel template
    nrow, ncol = plate.shape
    for row in range(nrow):
        for col in range(ncol):
            setOutCell(s, col+1, row+2, float(plate.iloc[row, col]))

    # Write CSV file
    plate.to_csv(os.path.join(folder, chip + "_normalization.csv"), sep="\t")

    # Write filled Excel template
    wb.save(chip + "_normalization.xls")
