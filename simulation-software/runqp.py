#!/usr/bin/env python3
#
import os
import sys

# qparray things
import QpixAsicArray as qparray
from QpixMPAnalysis import makeData, DAQ_KEY, saveData

# python imports
import pandas as pd

def main(int_time=1010, int_prd=0.25, nHardInt=20):

    import numpy as np
    np.random.seed(2)

    import codecs, json
    obj_text = codecs.open("1k_rtd_data.json", 'r').read()
    readDF = json.loads(obj_text)

    r = 'left'
    tile = qparray.QpixAsicArray(0, 0, tiledf=readDF, deltaT=1e-6)
    tile.SetSendRemote(enabled=True, transact=False)
    tile.Route(r, transact=False)

    dT, nInt = 0, 0
    while dT < int_time + int_prd:
        dT += int_prd
        if nInt % nHardInt == 0:
            print(f"hard interrogate at {dT}")
            tile.Interrogate(int_prd, hard=True)
        else:
            print(f"soft interrogate at {dT}")
            tile.Interrogate(int_prd, hard=False)
        nInt += 1

    data = makeData(tile, r, int_time, int_prd, nHardInt)
    daq_data, data = saveData(data)

    # create the dataframe from from these dictionaries
    df = pd.DataFrame.from_dict(data)
    daq_df = pd.DataFrame.from_dict(daq_data)

    # save the dataframe into a json for safe keeping
    df.to_csv("output_df.csv")
    daq_df.to_csv("output_daq_df.csv")

if __name__ == "__main__":
    print("running")
    main()
