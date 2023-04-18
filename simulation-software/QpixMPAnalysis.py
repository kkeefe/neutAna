import multiprocessing as mp

import numpy as np
import QpixAsicArray as qparray
import pandas as pd
from datetime import datetime

# make sure we can find the script path
import sys
sys.path.append("../")
from scripts.neutMakeJson import main as MakeNeutJson

## This Script reads in the output of radiogenicNB.ipynb (which reads in output
## from radiogenic ROOT data) and then executes a parameter space search
## utilizing multiprocessing to speed things up

MAXTIME = 10 # time to integrate for, or time radiogenic data is based on
INPUT_FILE = "../jsons/1k_rtd_data_200-210.json"
INPUT_DATA_FILE = "../data_rtd/electron_nu_fhc_files.root"
SEED = 420

INT_PRD = 0.5
NHARDINT = 10

def makeData(tile, r):
    """
    Helper function which will extrct relevant data from a processed tile to a
    serialized, useful format to put onto the mp.queue

    This function must be useful to extract for comparative analysis based 
    on either a push or a pull architecture.
    """

    # memoize lists to input serialized data
    daqBytes = list([daqbyte for daqbyte in tile._daqNode._localFifo._data])
    asics = list([asic for asic in tile])

    data = {
        "Architecture":"Pull" if tile.push_state else "Push",
        "Route":str(tile.RouteState),
        "Injected Hits":np.asarray(tile.InjectedHits, dtype=np.double),
        "Injected Size":int(tile.totalInjectedHits),

        # asic data
        "AsicX":np.asarray([asic.col for asic in asics], dtype=np.short),
        "AsicY":np.asarray([asic.row for asic in asics], dtype=np.short),
        "Frq":np.asarray([asic.fOsc for asic in asics], dtype=np.single),
        "Start Time":np.asarray([asic._startTime for asic in asics], dtype=np.single),
        "Rel Time":np.asarray([asic.relTimeNow for asic in asics], dtype=np.single),
        "Rel Tick":np.asarray([asic.relTicksNow for asic in asics], dtype=np.intc),

        # local data
        "Local Hits":np.asarray([asic._localFifo._totalWrites for asic in asics], dtype=np.intc),
        "Local Max":np.asarray([asic._localFifo._maxSize for asic in asics], dtype=np.intc),
        "Local Remain":np.asarray([asic._localFifo._curSize for asic in asics], dtype=np.intc),
        "Max Local": np.max(np.asarray([asic._localFifo._maxSize for asic in asics], dtype=np.intc)),

        # remote data
        "Remote Transactions":np.asarray([asic._remoteFifo._totalWrites for asic in asics], dtype=np.intc),
        "Remote Max":np.asarray([asic._remoteFifo._maxSize for asic in asics], dtype=np.intc),
        "Remote Remain":np.asarray([asic._remoteFifo._curSize for asic in asics], dtype=np.intc),
        "Max Remote": np.max(np.asarray([asic._remoteFifo._maxSize for asic in asics], dtype=np.intc)),

        # daq data to be stored its own 
        "DaqAsicX":np.asarray([daqbyte.row for daqbyte in daqBytes], dtype=np.short),
        "DaqAsicY":np.asarray([daqbyte.col for daqbyte in daqBytes], dtype=np.short),
        "DaqWordType":np.asarray([daqbyte.wordType.value for daqbyte in daqBytes], dtype=np.short),
        "DaqTime":np.asarray([daqbyte.daqT for daqbyte in daqBytes], dtype=np.intc),
        "DaqTimestamp":np.asarray([daqbyte.qbyte.timeStamp for daqbyte in daqBytes], dtype=np.intc),
        "DaqSimTime":np.asarray([daqbyte.qbyte.data if daqbyte.qbyte.data is not None else -1 for daqbyte in daqBytes], dtype=np.double),
        "Daqchannels":np.asarray([int(daqbyte.qbyte.channelMask) if daqbyte.qbyte.channelMask is not None else -1 for daqbyte in daqBytes], dtype=np.intc)
    }

    return data

def GetOutputJsonFile(event_number, arrayXdim, arrayYdim):
    return f"../jsons/evt-{event_number}_x-{arrayXdim}_y-{arrayYdim}.json"

def getDF(input_file):
    import codecs, json
    if isinstance(input_file, tuple):
        input_file = GetOutputJsonFile(input_file[0], input_file[1], input_file[2])
    obj_text = codecs.open(input_file, 'r').read()
    return json.loads(obj_text)

def MakeNeutFile(event_number, arrayXdim, arrayYdim):
    """
    Running the scripted import file
    ARGS: input_file, event_number, output_file, arrayXdim, arrayYdim

    """
    input_file = INPUT_DATA_FILE

    output_file = GetOutputJsonFile(event_number, arrayXdim, arrayYdim)

    hits = MakeNeutJson(input_file, event_number, output_file, arrayXdim, arrayYdim)

    return output_file

def pushTile(queue, r, neutFile, int_time=MAXTIME):
    """
    Push script to run. should be based on QpixTest format
    """

    import numpy as np
    np.random.seed(SEED)

    neutDF = getDF(neutFile)
    tile = qparray.QpixAsicArray(0, 0, tiledf=neutDF, deltaT=10e-6, debug=0, offset=5.1)
    if neutDF["size"] == 0:
        queue.put(makeData(tile, r))
        return

    tile.SetSendRemote(enabled=True, transact=False)
    tile.Route(r, transact=False)
    tile.SetPushState(enabled=True, transact=False)

    # inject the radiogenic reference data
    readDF = getDF(INPUT_FILE)
    tile._InjectHits(readDF["hits"])

    # don't try to simulate egregiously large events
    if tile.totalInjectedHits > 800 * int(tile._ncols * tile._nrows):
        print(f"skipping large sim event size: {tile.totalInjectedHits}")
        queue.put(makeData(tile, r))
        return

    dT, nInt = 0, 0
    while dT < int_time + INT_PRD:
        dT += INT_PRD
        if nInt % NHARDINT == 0:
            tile.Interrogate(INT_PRD, hard=True)
        else:
            tile.Interrogate(INT_PRD, hard=False)
        nInt += 1

    queue.put(makeData(tile, r))

def pullTile(queue, r, neutFile, int_time=MAXTIME):
    """
    basic function to run a tile with an integration period, over a specified time

    store processed tile on output queue to send back to main thread.
    """

    import numpy as np
    np.random.seed(SEED)

    neutDF = getDF(neutFile)
    tile = qparray.QpixAsicArray(0, 0, tiledf=neutDF, deltaT=10e-6, debug=0, offset=5.1)
    if neutDF["size"] == 0:
        queue.put(makeData(tile, r))
        return

    # inject the radiogenic reference data
    readDF = getDF(INPUT_FILE)
    tile._InjectHits(readDF["hits"])

    # don't try to simulate egregiously large events
    if tile.totalInjectedHits > 800 * int(tile._ncols * tile._nrows):
        print(f"skipping large sim event size: {tile.totalInjectedHits}")
        queue.put(makeData(tile, r))
        return

    # configure other meta cases of the tile
    tile.SetSendRemote(enabled=True, transact=False)
    if r == "trunk":
        tile.Route(r, transact=False, pos=int(tile._nrows/2)) # route near middle
    else:
        tile.Route(r, transact=False)

    dT, nInt = 0, 0
    while dT < int_time + INT_PRD:
        dT += INT_PRD
        if nInt % NHARDINT == 0:
            tile.Interrogate(INT_PRD, hard=True)
        else:
            tile.Interrogate(INT_PRD, hard=False)
        nInt += 1

    queue.put(makeData(tile, r))

def makeBranches():
    """
    Return the dictionary of ROOT object types which are used to store
    the TTree values in the output ttree
    Keys should match those of the type in makeData.
    """
    branches = {}

    branches["Architecture"] = []
    branches["Route"] = []
    branches["Injected Hits"] = []
    branches["Injected Size"] = []
    # asic data
    branches["AsicX"] = []
    branches["AsicY"] = []
    branches["Frq"] = []
    branches["Start Time"] = []
    branches["Rel Time"] = []
    branches["Rel Tick"] = []
    # local data
    branches["Local Hits"] = []
    branches["Local Max"] = []
    branches["Local Remain"] = []
    branches["Max Local"] = []

    # remote data
    branches["Remote Transactions"] = []
    branches["Remote Max"] = []
    branches["Remote Remain"] = []
    branches["Max Remote"] = []

    # daq data to be stored its own
    branches["DaqAsicX"] = []
    branches["DaqAsicY"] = []
    branches["DaqWordType"] = []
    branches["DaqTime"] = []
    branches["DaqTimestamp"] = []
    branches["DaqSimTime"] = []
    branches["Daqchannels"] = []

    return branches

def fillData(data, branches):
    """
    read data from makeData, copy onto branches, and fill tt
    """
    branches["Architecture"].append(data["Architecture"])
    branches["Route"].append(data["Route"])
    branches["Injected Hits"].append(data["Injected Hits"])
    branches["Injected Size"].append(data["Injected Size"])

    # asic data
    branches["AsicX"].append(data["AsicX"])
    branches["AsicY"].append(data["AsicY"])
    branches["Frq"].append(data["Frq"])
    branches["Start Time"].append(data["Start Time"])
    branches["Rel Time"].append(data["Rel Time"])
    branches["Rel Tick"].append(data["Rel Tick"])

    # local data
    branches["Local Hits"].append(data["Local Hits"])
    branches["Local Max"].append(data["Local Max"])
    branches["Local Remain"].append(data["Local Remain"])
    branches["Max Local"].append(data["Max Local"])

    # remote data
    branches["Remote Transactions"].append(data["Remote Transactions"])
    branches["Remote Max"].append(data["Remote Max"])
    branches["Remote Remain"].append(data["Remote Remain"])
    branches["Max Remote"].append(data["Max Remote"])

    # daq data to be stored its own
    branches["DaqAsicX"].append(data["DaqAsicX"])
    branches["DaqAsicY"].append(data["DaqAsicY"])
    branches["DaqWordType"].append(data["DaqWordType"])
    branches["DaqTime"].append(data["DaqTime"])
    branches["DaqTimestamp"].append(data["DaqTimestamp"])
    branches["DaqSimTime"].append(data["DaqSimTime"])
    branches["Daqchannels"].append(data["Daqchannels"])

def main(seed=SEED):
    """
    This script should be called and run as an executable.
    """
    ncpu = 60
    branches = makeBranches()

    # define the ranges of pull parameters to test
    routes = ["left", "snake", "trunk"]
    dims = [(4,4), (8,8), (10,14), (16,16)]
    event_number = [i for i in range(1,5000)]
    neutFiles = [(evt, xd, yd) for evt in event_number for xd, yd in dims]

    # make the files on the pool
    msg = f"creating {len(neutFiles)} neutrino json files. continue?"
    print(msg)
    pool = mp.Pool()
    pool.starmap(MakeNeutFile, neutFiles)

    # place holder for the completed tiles
    tile_queue = mp.Queue()

    # create a list of all of the processes that need to run.
    pull_args = [(r, f) for r in routes for f in neutFiles]

    # only test snake for push routing on 8x8 tiles
    push_args = [("snake", f) for f in neutFiles if "x-4" in f] 

    # pull architecture procs
    procs = [mp.Process(target=pullTile, args=(tile_queue, *arg)) for arg in pull_args]

    # push archiecture procs
    procs.extend([mp.Process(target=pushTile, args=(tile_queue, *arg)) for arg in push_args])

    nProcs = len(procs)
    msg = f"begginning processing of {nProcs} tiles."
    print(msg)

    try:
        completeProcs = 0
        runningProcs, pTiles = [], []
        while completeProcs < nProcs:

            # fill running procs until we use all cpu cores
            while len(runningProcs) <= ncpu and len(procs) > 0:
                runningProcs.append(procs.pop())

            # ensure the running procs have started
            for ip, p in enumerate(runningProcs):
                if p.pid is None:
                    p.start()
                elif p.exitcode is not None:
                    runningProcs.pop(ip)

            # wait to get anything on the queue
            pTiles.append(tile_queue.get())
            for data in pTiles:
                completeProcs += 1
                fillData(data, branches)
            pTiles = []
            print(f"Completed tile {completeProcs}/{nProcs}: {completeProcs/nProcs*100:0.2f}% @ {datetime.now()}..")
    except Exception as ex:
        print("encountered exception in creating output mp data:", ex)
        print("attemping save..")

    finally:
        # save output file
        df = pd.DataFrame(branches)
        df.to_feather("neutMP.feather", compression="zstd")

if __name__ == "__main__":
    main()
