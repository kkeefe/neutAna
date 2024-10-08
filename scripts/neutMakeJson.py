import os
import sys
import numpy as np
import pandas as pd
import ROOT
from array import array

channelXdim = 4
channelYdim = 4
xMAX = 575
yMAX = 1500

def findMax(pixel_x, pixel_y, pixel_reset, arrayXdim, arrayYdim):
    """
    find the range of pixels within Xdim and Ydim that give the most resets
    and create the
    """
    if len(pixel_x) == 0:
        pixel_x = [-1]
        pixel_y = [-1]
        pixel_reset = [-1]

    pixel_x = np.asarray(pixel_x)
    pixel_y = np.asarray(pixel_y)
    pixel_reset = np.asarray(pixel_reset)

    xPixRange = channelXdim * arrayXdim
    yPixRange = channelYdim * arrayYdim

    min_x = np.min(pixel_x)
    min_y = np.min(pixel_y)
    max_x = np.max(pixel_x)
    max_y = np.max(pixel_y)

    # print(f"found asic hit range, x:{min_x}-{max_x} - y: {min_y}-{max_y}")

    def getBestSlice(x, pix_x, y, pix_y):
        x_hits = np.logical_and(pix_x >= x, pix_x < x + xPixRange)
        y_hits = np.logical_and(pix_y >= y, pix_y < y + yPixRange)
        asic_hits = np.logical_and(x_hits, y_hits)
        return asic_hits

    # use steps of 1, which slides across every pixel to find the pixel-based max
    x_itr = range(min_x, max_x-xPixRange+1)
    y_itr = range(min_y, max_y-yPixRange+1)
    xBest, yBest, maxCount = 0, 0, 0 
    for x in x_itr:
        for y in y_itr:
            asic_hits = getBestSlice(x, pixel_x, y, pixel_y)
            counts = asic_hits.sum()
            if counts > maxCount:
                maxCount = counts
                xBest = x
                yBest = y

    asic_hits = getBestSlice(xBest, pixel_x, yBest, pixel_y)
    pixel_x = pixel_x[asic_hits]
    pixel_y = pixel_y[asic_hits]
    pixel_reset = pixel_reset[asic_hits]

    # print("found max hits:", asic_hits.sum())
    assert len(pixel_x) == len(pixel_y), f"uneven pixel lengths: {len(pixel_x)} != {len(pixel_y)}"
    assert len(pixel_x) == len(pixel_reset), f"uneven data lengths: {len(pixel_x)} != {len(pixel_reset)}"

    # re-order these pixels to 1
    if len(pixel_x) > 0:
        pixel_x = pixel_x - np.min(pixel_x) + 1
        pixel_y = pixel_y - np.min(pixel_y) + 1

    return pixel_x, pixel_y, pixel_reset

def makeDF(pixel_x, pixel_y, pixel_reset, arrayXdim, arrayYdim):
    from math import ceil

    xDIM = arrayXdim * channelXdim
    yDIM = arrayYdim * channelYdim

    pixel_x, pixel_y, pixel_reset = findMax(pixel_x, pixel_y, pixel_reset, arrayXdim, arrayYdim)

    pd_data = {}
    pd_data["pX"] = pixel_x
    pd_data["pY"] = pixel_y
    pd_data["Reset"] = pixel_reset

    df = pd.DataFrame(pd_data)
    # count these as done in Simulation "Top Left" Asic is (0,0) : (row, col)
    # create X, Y asic associations
    df["AsicX"] = ((df["pX"] - 1) / channelXdim).map(int)
    df["AsicY"] = ((df["pY"] - 1) / channelYdim).map(int)

    # for each asic, it should only number a nPix within it's dimensions channelXdim *channelYdim
    # we chose X-dim as the "row" and Y-dim as the "column", to be consistent with the 
    # coordinates for the tile / simulation dimensions
    npx = ((df["pX"]) - channelXdim*df["AsicX"] - 1).map(int)
    npy = ((df["pY"]) - channelYdim*df["AsicY"] - 1).map(int)
    df["nPix"] = npx + channelYdim*npy

    return df

def makeJson(pixel_x, pixel_y, pixel_reset, arrayXdim, arrayYdim, evt_e, lep_recon, axis_x, axis_z, zpos, outf):
    """
    args: filtered_pd_df - filtered RDataFrame
    """
    fdf = makeDF(pixel_x, pixel_y, pixel_reset, arrayXdim, arrayYdim)
    
    # create the tile's dataframe to send into the QPixAsicArray
    tiledf = {}
    tiledf["nrows"] = arrayXdim
    tiledf["ncols"] = arrayYdim
    tiledf["energy_deposit"] = evt_e
    tiledf["lep_recon"] = lep_recon
    tiledf["axis_x"] = axis_x
    tiledf["axis_z"] = axis_z
    tiledf["zpos"] = zpos

    tiledf["hits"] = []

    # normalize asic numbers: this is for the simulation input which "0 numbers" the asic's within it's rows / cols
    hitX = fdf["AsicX"].unique()
    hitY = fdf["AsicY"].unique()

    # build the hits tuple for each asic within the tile
    nHits = 0
    for x in hitX:
        for y in hitY:
            asicResets = fdf[ (fdf["AsicX"] == x) & (fdf["AsicY"] == y) ][["Reset","nPix"]].values.tolist()
            arrayX = int(x)
            arrayY = int(y)
            tiledf["hits"].append([arrayX, arrayY, asicResets])
            nHits += len(asicResets)

    tiledf["size"] = nHits

    print(f"stored a total of {nHits} hits")
    # store the values within a json file
    import json
    with open(outf, "w") as outputFile:
        json.dump(tiledf, outputFile, indent=4)

    return nHits

def setup_tree(input_file, event_number):
    pix_x = ROOT.std.vector('Int_t')()
    pix_y = ROOT.std.vector('Int_t')()
    pix_r = ROOT.std.vector('Double_t')()
    evt_e = array('f', [ 0. ])
    lep_e = array('f', [ 0. ])
    hadtot_e = array('f', [ 0. ])
    hadother_e = array('f', [ 0. ])
    axis_x = array('f', [ 0. ])
    axis_z = array('f', [ 0. ])
    zpos = array('f', [ 0. ])

    tf = ROOT.TFile(input_file, "READ")
    if tf.IsZombie():
        print("warning, unable to open root file at:", input_file)
        sys.exit(-1)
    if not hasattr(tf, "event_tree"):
        print("warning event tree not found!")
        sys.exit(-1)

    t = tf.event_tree
    t.SetBranchAddress('pixel_x', pix_x)
    t.SetBranchAddress('pixel_y', pix_y)
    t.SetBranchAddress('pixel_reset', pix_r)
    t.SetBranchAddress('energy_deposit', evt_e)
    t.SetBranchAddress('lepKE', lep_e)
    t.SetBranchAddress('hadTot', hadtot_e)
    t.SetBranchAddress('hadOther', hadother_e)
    # position information
    t.SetBranchAddress('zpos', zpos)
    t.SetBranchAddress('axis_x', axis_x)
    t.SetBranchAddress('axis_z', axis_z)
    if event_number > t.GetEntries():
        print("warning, not enough entries in tree:", event_number, " > ", t.GetEntries())
        sys.exit(-1)
    t.GetEntry(event_number)

    assert pix_x.size() == pix_y.size(), f"uneven pixel lengths: {pix_x.size()} != {pix_y.size()}"
    assert pix_x.size() == pix_r.size(), f"uneven data lengths: {pix_x.size()} != {pix_r.size()}"

    lep_recon = lep_e[0] + hadtot_e[0] + hadother_e[0]

    return pix_x, pix_y, pix_r, evt_e[0], lep_recon, axis_x[0], axis_z[0], zpos[0]

def main(input_file, event_number, output_file, arrayXdim, arrayYdim):
    """
    ARGS:
        input_file - root file of neutrino data
        event_number - number in the event to get from the tree
        output_file - output json name
        arrayXdim - number of ASICs in the x-dim
        arrayYdim - number of ASICs in the y-dim
    """

    # get the stl vectors from the input ttree
    pixel_x, pixel_y, pixel_reset, evt_e, lep_recon, axis_x, axis_z, zpos = setup_tree(input_file, event_number)

    # filter and create the flattened output json file to send to the python sim
    hits = makeJson(pixel_x, pixel_y, pixel_reset, arrayXdim, arrayYdim, evt_e, lep_recon, axis_x, axis_z, zpos, output_file)

    return hits

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(f"need 6 args: received: {len(sys.argv)}")
        msg = """
        input_file = sys.argv[1]
        event_number = int(sys.argv[2])
        output_file = sys.argv[3]
        arrayXdim = int(sys.argv[4])
        arrayYdim = int(sys.argv[5])
        """
        print("give args:", msg)
    else:
        input_file = sys.argv[1]
        event_number = int(sys.argv[2])
        output_file = sys.argv[3]
        arrayXdim = int(sys.argv[4])
        arrayYdim = int(sys.argv[5])
        main(input_file, event_number, output_file, arrayXdim, arrayYdim)
