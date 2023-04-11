#!/usr/bin/env python3
bestX = 281
bestY = 561
bestPos = 205640

fdf = rdf.Filter(f"pixel_x >= {bestX} && pixel_x < {bestX+xDIM}")\
         .Filter(f"pixel_y >= {bestY} && pixel_y < {bestY+yDIM}")
def makeNumpy(filtered_df, time_start=0, time_end=None):
    from math import ceil

    rd_data = filtered_df.AsNumpy(["pixel_x", "pixel_y", "pixel_reset"])

    pixel_x = rd_data["pixel_x"]
    pixel_y = rd_data["pixel_y"]
    pixel_reset = rd_data["pixel_reset"]

    if time_end is not None:
        good_times = np.logical_and(pixel_reset > time_start, pixel_reset <= time_end)
        pixel_x = pixel_x[good_times]
        pixel_y = pixel_y[good_times]
        pixel_reset = pixel_reset[good_times]

    pd_data = {}
    pd_data["pX"] = pixel_x
    pd_data["pY"] = pixel_y
    pd_data["Reset"] = pixel_reset

    df = pd.DataFrame(pd_data)
    # count these as done in Simulation "Top Left" Asic is (0,0) : (row, col)
    # create X
    df['tileX'] = ((df['pX'] - 1) / xDIM).map(int)
    df["AsicX"] = ((df["pX"] - 1) / channelXdim).map(int)

    # create Y
    df['tileY'] = ((df['pY'] - 1) / yDIM).map(int)
    df["AsicY"] = ((df["pY"] - 1) / channelYdim).map(int)

    # create N, unique ASIC / Tile numbers to easily histogram
    df['tileN'] = df['tileX'] + df['tileY'] * ceil(xMAX / xDIM)
    df['AsicN'] = df['AsicX'] + df['AsicY'] * ceil(xMAX / channelXdim)

    # for each asic, it should only number a nPix within it's dimensions channelXdim *channelYdim
    # we chose X-dim as the "row" and Y-dim as the "column", to be consistent with the
    # coordinates for the tile / simulation dimensions
    npx = ((df["pX"]) - channelXdim*df["AsicX"] - 1).map(int)
    npy = ((df["pY"]) - channelYdim*df["AsicY"] - 1).map(int)
    df["nPix"] = npx + channelYdim*npy
    df["PixN"] = df['pX'] + (df['pY'] ) * xMAX # include -1 since pY is one counted

    return df

out_file = "/mnt/c/Users/keefe/OneDrive/Documents/qpix-digital/simulation-rtd/hits/1k_rtd_data.json"

def makeJson(filtered_df, arrayXdim=16, arrayYdim=16, outf=out_file, time_start=0, time_end=None):
    """
    args: filtered_pd_df - filtered RDataFrame
    """
    fdf = makeNumpy(filtered_df, time_start, time_end)

    # create the tile's dataframe to send into the QPixAsicArray
    tiledf = {}
    tiledf["nrows"] = arrayXdim
    tiledf["ncols"] = arrayYdim
    tiledf["hits"] = []

    # normalize asic numbers: this is for the simulation input which "0 numbers" the asic's within it's rows / cols
    hitX = fdf["AsicX"].unique()
    hitY = fdf["AsicY"].unique()
    minX = min(hitX)
    minY = min(hitY)

    # build the hits tuple for each asic within the tile
    for x in hitX:
        for y in hitY:
            asicResets = fdf[ (fdf["AsicX"] == x) & (fdf["AsicY"] == y) ][["Reset","nPix"]].values.tolist()
            arrayX = x if minX == 0 else int(x%minX)
            arrayY = y if minY == 0 else int(y%minY)
            if time_end is not None:
                asicResets = np.array(asicResets) - time_start
                asicResets = asicResets.tolist()
            tiledf["hits"].append([arrayX, arrayY, list(asicResets)])

    # store the values within a json file
    import json
    with open(outf, "w") as outputFile:
        json.dump(tiledf, outputFile, indent=4)
        print("saved file", outputFile)
        outputFile.close()

makeJson(fdf, outf="./1k_rtd_data_200-210.json", time_start=200, time_end=210)
