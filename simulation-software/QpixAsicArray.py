from QpixAsic import QPByte, QPixAsic, ProcQueue, DaqNode, AsicWord, AsicState, \
                     AsicConfig, AsicDirMask, QPException
import matplotlib.pyplot as plt
import random
import math
import time
import numpy as np

## helper functions
def OrderAsics(qparray, ordering="Normal"):
    asics = []
    # normal ordering
    if ordering == "Normal":
        for asic in qparray:
            asics.append(asic)
    # order main column on bottom followed by other rows
    elif ordering.lower() == "left":
        colAsics = [a for a in qparray if a.col == 0]
        rowAsics = [a for a in qparray if a.col != 0]
        asics.extend(colAsics)
        asics.extend(rowAsics)
    elif ordering.lower() == "snake":
        for i in range(qparray._nrows):
            for j in range(qparray._ncols):
                if i%2 == 0:
                    asics.append(qparray[i][j])
                else:
                    asics.append(qparray[i][(qparray._ncols - 1) - j])
    # attempt to order in the perceived shortest broadcast distance
    else:
        r, c = qparray._nrows, qparray._ncols
        for i in range(r+c):
            dAsics = sorted([a for a in qparray if a.row+a.col == i], reverse=True)
            asics.extend(dAsics)
    return asics

def MakeFifoBars(qparray):
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    
    ColorWheelOfFun = ["#"+''.join([random.choice('0123456789ABCDEF') for i in range(6)])
        for j in range(qparray._nrows * qparray._ncols)]

    LocalFifoMax = np.zeros((qparray._nrows * qparray._ncols))
    Names = []
    for i, asic in enumerate(qparray):
        LocalFifoMax[i] = asic._localFifo._maxSize
        Names.append(f'({asic.row}, {asic.col})')
        if asic._localFifo._full:
            print(f'asic ({asic.row}, {asic.col}) local fifo was full')

    plt.bar(Names, LocalFifoMax, color=ColorWheelOfFun)
    plt.title('Local Fifo Maximum Sizes')
    plt.ylabel('Max Sizes')
    plt.show()

    ## remote fifo current sizes
    ColorWheelOfFun = ["#"+''.join([random.choice('0123456789ABCDEF') for i in range(6)])
        for j in range(qparray._nrows * qparray._ncols)]

    remoteFifoCur = np.zeros((qparray._nrows * qparray._ncols))
    Names = []
    for i, asic in enumerate(qparray):
        remoteFifoCur[i] = asic._remoteFifo._curSize
        Names.append(f'({asic.row}, {asic.col})')
        if asic._localFifo._full:
            print(f'asic ({asic.row}, {asic.col}) local fifo was full')

    plt.bar(Names, remoteFifoCur, color=ColorWheelOfFun)
    plt.title('Remote Fifo Current Sizes')
    plt.ylabel('Cur Sizes')
    plt.show()

    fig, ax = plt.subplots(figsize = (8,8))

    RemoteFifoMax = np.zeros(qparray._nrows * qparray._ncols)
    patches = []

    plt.xticks(
        rotation=45, 
        horizontalalignment='right',
        fontweight='light',
    )
    for i, asic in enumerate(qparray):
        locals() [f'patch{i}'] = mpatches.Patch(color=ColorWheelOfFun[i], label=f'Asic ({asic.row}, {asic.col})')
        patches.append(locals() [f'patch{i}'])
        RemoteFifoMax[i] = asic._remoteFifo._maxSize
        if asic._remoteFifo._full:
            print(f'asic ({asic.row}, {asic.col}) remote fifo full')
        Nem = f'({asic.row}, {asic.col})'        
        ax.bar(Nem, RemoteFifoMax[i], color=ColorWheelOfFun[i])
    ax.set(ylabel='Max Sizes', title='Remote Fifo Maximum Sizes')
    if len(patches) < 10:
        ax.legend(handles=[*patches])
    plt.tight_layout()
    plt.show()

def heatMap(data, rows, cols, header="", ax=None, cbarlabel="", cbar_kw={}, **kwargs):
    """
    modified heatmap function based on matplotlib docs
    """

    if ax is None:
        print("getting ax")
        ax = plt.gca()

    im = ax.imshow(data, **kwargs)

    # color bar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    ax.set_xticks(np.arange(cols))
    ax.set_yticks(np.arange(rows))

    ax.tick_params(top=True, bottom=False,
                    labeltop=True, labelbottom=False)

    # Loop over data dimensions and create text annotations.
    for i in range(rows):
        for j in range(cols):
            text = ax.text(j, i, data[i][j],
                        ha="center", va="center", color="w")

    ax.set_title(f"{header}")

    return im, cbar

def viewAsicState(qparray, time_begin=-100e-9, time_end=300e-6, ordering="Normal"):
    """
    viewing function to take in a processed QpixArray class.

    This function will plot all of the ASIC states in a broken_barh graph
    with different colors based on AsicState enum class.

    The inspection range of times are controlled with time_begin and time_end.
    """

    color_mapping = {}
    for state in AsicState:
        color_mapping[state] = f"C{state.value}"

    asics = OrderAsics(qparray, ordering)

    # unpack the data into arrays of states and times
    states = [[] for i in range(len(asics))]
    absTimes = [[] for i in range(len(asics))]
    for i, asic in enumerate(asics):
        for (state, _, absTime, *_) in asic.state_times:
            states[i].append(state)
            absTimes[i].append(absTime)

    # make the graph 
    # fig, ax = plt.subplots(figsize=(15, 0.2*(qparray._ncols * qparray._nrows)))
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_ylim(0.5, len(asics)+3)

    # repack the data into a viewable format for barh
    i = 1
    for asic_states, asic_relTimes in zip(states[:], absTimes[:]):
        asic_state_widths = []
        state_colors = []
        cur_state = asic_states[0]
        cur_time = asic_relTimes[0]
        for state, time in list(zip(asic_states, asic_relTimes))[1:]:
            asic_state_widths.append([cur_time, time-cur_time])
            state_colors.append(color_mapping[cur_state])
            cur_state = state
            cur_time = time
        # make sure we extend the final state to the end of the graph
        if len(asic_state_widths) < 1:
            asic_state_widths.append([cur_time, time_end])
            state_colors.append(color_mapping[cur_state])
        if asic_state_widths[-1][1] < time_end:
            asic_state_widths.append([cur_time, time_end - cur_time])
            state_colors.append(color_mapping[cur_state])
        ax.broken_barh(asic_state_widths, (i, 0.50),
                        facecolors=state_colors)
        i += 1

    ax.grid(True)
    df = qparray._daqNode.fOsc
    ax.set_yticks([i+1.15 for i in range(len(asics))], labels=[f"{asic.fOsc/df:.2f}({asic.row}, {asic.col})" for asic in asics])
    ax.set_xlim(time_begin, time_end)
    plt.tight_layout()

    # fake legend points
    markers = [plt.Line2D([0,0],[0,0],color=color, marker='o', linestyle='') for color in color_mapping.values()]
    plt.legend(markers, color_mapping.keys(), numpoints=1)
    plt.show()

    return fig, ax

def viewAsicBuffers(qparray):
    """
    Helper function to go through the ASIC states.
    Create two plots. One for all of the local fifo sizes as a function of time,
    and the other for the remote fifos as a function of time.
    """
    color_mapping = {}
    for state in AsicState:
        color_mapping[state] = f"C{state.value}"

    asics = OrderAsics(qparray)
    # unpack the data into arrays of states and times
    states = [[] for i in range(len(asics))]
    absTimes = [[] for i in range(len(asics))]
    for i, asic in enumerate(asics):
        for (state, _, absTime, *_) in asic.state_times:
            states[i].append(state)
            absTimes[i].append(absTime)

    fig, ax = plt.subplots(1,2)

    return fig, ax

def PrintTsMap(qparray):
    """
    boiler plate code for printing interesting data about each asic
    """
    for i, asic in enumerate(qparray):
        print(asic.lastTsDir, end=" ")
        if (i+1)%qparray._nrows == 0:
            print()

def PrintTimeMap(qparray):
    for i, asic in enumerate(qparray):
        print(asic.relTimeNow, end=" ")
        if (i+1)%qparray._nrows == 0:
            print()

def PrintTicksMap(qparray):
    print("Total Ticks")
    for i, asic in enumerate(qparray):
        print(asic.relTicksNow, end=" ")
        if (i+1)%qparray._nrows == 0:
            print()

def PrintMeasureMap(qparray):
    print("Measured Transmissions:")
    for i, asic in enumerate(qparray):
        print(asic._measurements, end=" ")
        if (i+1)%qparray._nrows == 0:
            print()

def PrintReceiveMap(qparray):
    print("Received Transmissions:")
    for i, asic in enumerate(qparray):
        print(asic._hitReceptions, end=" ")
        if (i+1)%qparray._nrows == 0:
            print()

def PrintTimes(qparray):
    print("Tick Values :")
    for i, asic in enumerate(qparray):
        print(f"{asic.relTicksNow:1.2E}", end=" ")
        if (i+1)%qparray._nrows == 0:
            print()
    print("Rel Time Values (us):")
    for i, asic in enumerate(qparray):
        print(f"{(asic.relTimeNow)*1e6:1.2E}", end=" ")
        if (i+1)%qparray._nrows == 0:
            print()
    print("Abs Time Values (us):")
    for i, asic in enumerate(qparray):
        print(f"{(asic._absTimeNow - qparray._targNode._absTimeNow)*1e6:1.2E}", end=" ")
        if (i+1)%qparray._nrows == 0:
            print()
    print("Measured Time Values (us):")
    for i, asic in enumerate(qparray):
        print(f"{(asic._measuredTime[-1] - qparray._targNode._measuredTime[-1])*1e6:3.2f}", end=" ")
        if (i+1)%qparray._nrows == 0:
            print()

def PrintTransactMap(qparray, silent=False):
    """
    Helper function which iterates through a QPixArray and returns a dictionary of information
    for the QPFifos for each asic within the Array.
    """
    dMap = {}
    localT, remoteT, remoteMax = [], [], []

    if not silent:
        print(f"tile with route {qparray.RouteState} Transmission map:")
        print("Local Transmissions:")
    for i, asic in enumerate(qparray):
        localWrites = asic._localFifo._totalWrites
        localT.append((asic.row, asic.col, localWrites))
        if not silent:
            print(localWrites, end=" ")
            if (i+1)%qparray._nrows == 0:
                print()
    dMap["LocalT"] = localT

    if not silent:
        print("Remote Transmissions:")
    for i, asic in enumerate(qparray):
        remoteTransacts = asic._remoteFifo._totalWrites
        remoteT.append((asic.row, asic.col, remoteTransacts))
        if not silent:
            print(remoteTransacts, end=" ")
            if (i+1)%qparray._nrows == 0:
                print()
    dMap["RemoteT"] = remoteT

    if not silent:
        print("Remote Max Sizes:")
    for i, asic in enumerate(qparray):
        rMax = asic._remoteFifo._maxSize
        remoteMax.append((asic.row, asic.col, rMax))
        if not silent:
            print(rMax, end=" ")
            if (i+1)%qparray._nrows == 0:
                print()
    dMap["RemoteMax"] = remoteMax

    return dMap

def AnalyzeArray(qparray, silent=False):
    """
    Function tests to ensure that the array has emptied all of the injected hits,
    and looks at the daqNode to ensure that each ASIC has all of its data within the daq node
    args:
        qpixasicarray : array which should be empty
        silent : flag to indicate whether or not printing should occur during ASIC checks.

    returns:
        bool : true if daqNode has all correct injected hits from each asic, false otherwise
    """
    daqNode = qparray._daqNode
    if daqNode._localFifo._curSize == 0:
        print("Analyze: no data in the DAQ Node!")
        return False
    recv, injected = daqNode._localFifo._dataWords, qparray.totalInjectedHits
    msg = f"Analyze: missing injected data recv {recv} != injected {injected}"
    if recv != injected:
        print(msg)
        return False

    # check all of the ASICs
    for asic in qparray:
        data, end = AnalyzeASIC(qparray, asic.row, asic.col, silent=silent)
        if len(data) != asic.totalInjected:
            print(f"Analyze: Asic data failure at ({asic.row},{asic.col})", end=" ")
            print(f"recv: {len(data)} expected {asic.totalInjected}")
            return False
    return True


def AnalyzeASIC(qparray, row, col, silent=False):
    """
    This function should perform a full analysis for a specific ASIC within qparray.

    This means that the DAQ node is expected to be full of data. if not, this will return None,
    indicating a failure.

    Return tuple of (asicData, asicEnd) within the daqNode on success.
    """
    # get a list of all of the data within the DAQNode, and filter
    # for the specific ASIC we want
    daqNode = qparray._daqNode
    fifoData = daqNode._localFifo._data
    asicData = [d for d in fifoData if d.row==row and d.col == col and d.wordType==AsicWord.DATA]
    asicEnd = [d for d in fifoData if d.row==row and d.col == col and d.wordType==AsicWord.EVTEND]

    if not silent:
        print(f"found {len(asicData)} hits for ASIC ({row},{col})")
        print(f"found {len(asicEnd)} end words for ASIC ({row},{col})")

    return asicData, asicEnd

## end helper functions

class QpixAsicArray():
    """
    Class purpose is to streamline creation of a digital asic array tile for the
    QPix project. Controls main sequencing of spread of asic clock cycles
    VARS:
      nrows       - rows within the array
      ncols       - columns within the array
      nPixs=16    - number of channels for each ASIC
      fNominal    - Default clock frequency (default ~50 MHz)
      pctSpread   - std distribution of ASIC clocks (default 5%)
      deltaT      - stepping interval for the simulation
      timeEpsilon - stepping time interval for simulation (default 1e-6)
      debug       - debug level, values >= 0 produce text output (default 0)
      tiledf      - tuple of asic hits to load into the array, tile dataframe is created from radiogenicNB
      RouteState  - string or None type member to define current routing method of Array
      push_state  - enable flag that is sent to ASICs within the array enabling push
      seed        - seed value to send to random module
      offset      - float value to set to injected hits method
    """
    def __init__(self, nrows, ncols, nPixs=16, fNominal=30e6, pctSpread=0.05, deltaT=1e-5, timeEpsilon=1e-6,
                 timeout=1.5e4, hitsPerSec = 20./1., debug=0.0, tiledf=None, seed=2, offset=None):

        # if we have a tiledf to construct an array, then the size is determined by the tile
        if tiledf is not None:
            self._nrows = tiledf["nrows"]
            self._ncols = tiledf["ncols"]
        else:
            self._nrows = nrows
            self._ncols = ncols

        # array parameters
        self._tickNow = 0
        self._timeNow = 0
        self._debugLevel = debug
        self._nPixs = nPixs
        self.fNominal = fNominal
        self.pctSpread = pctSpread
        self.RouteState = None
        self.push_state = False
        self.send_remote = False

        # keep track of which seed was used for this array
        self._seed = seed
        random.seed(seed)

        # the array also manages all of the processing queue times to use
        self._queue = ProcQueue()
        self._timeEpsilon = timeEpsilon
        self._deltaT = deltaT
        self._deltaTick = self.fNominal * self._deltaT

         # Make the array and connections
        self._asics = self._makeArray(timeout=timeout, randomRate=hitsPerSec)
        self._daqNode = DaqNode(fOsc=self.fNominal, nPixels=0, debugLevel=self._debugLevel, timeout=timeout, randomRate=hitsPerSec)

        # which node should receive the information from the daqNode
        self._targNode = self[0][0]
        self._targNode.connections[AsicDirMask.West.value].asic = self._daqNode
        self._targDir = AsicDirMask(3)

        self._alert = 0
        self.totalInjectedHits = 0
        self.totalTimes = 0

        # load in hits if we're creating an array based on tiledf data
        if tiledf is not None:
            self._InjectHits(tiledf["hits"], offset=offset)
   
    def __iter__(self):
        '''returns iterable through the asics within the array'''
        for asic_row in self._asics:
            for asic in asic_row:
                yield asic

    def __getitem__(self, row):
        '''
        make the array subscriptable to get whichever item we want
        '''
        assert row <= self._nrows - 1, "not enough rows in that array" 
        return self._asics[int(row)]

    def _makeArray(self, timeout, randomRate):
        """
        helper function designed to construct QPix asic values within array type
        """
        matrix = [[] for j in range(self._nrows)]

        for i in range(self._nrows):
            for j in range(self._ncols):
                frq = random.gauss(self.fNominal,self.fNominal*self.pctSpread)
                matrix[i].append(QPixAsic(frq, self._nPixs, row=i, col=j, debugLevel=self._debugLevel, timeout=timeout, randomRate=randomRate))
                
                if self._debugLevel > 0:
                    print(f"Created ASIC at row {i} col {j} with frq: {frq:.2f}")

        # fully connect the asics within the array
        for i in range(self._nrows):
            for j in range(self._ncols):
                if i > 0:
                    matrix[i][j].connections[AsicDirMask.North.value].asic = matrix[i-1][j]
                if i < self._nrows-1:
                    matrix[i][j].connections[AsicDirMask.South.value].asic = matrix[i+1][j]
                if j > 0:
                    matrix[i][j].connections[AsicDirMask.West.value].asic = matrix[i][j-1]
                if j < self._ncols-1:
                    matrix[i][j].connections[AsicDirMask.East.value].asic = matrix[i][j+1]    

        return matrix

    def readData(self):
        """
        function call to issue a command to read data from the full array
        """
        data = []
        readTime = time.perf_counter()

        for asic in self:
            data += asic.Process(readTime)

        stopTime = time.perf_counter()
        self._processTime = stopTime - readTime

        if self._debugLevel >= 5:
            print(f"processing time was: {self._processTime:.4f}")

        return data

    def Calibrate(self, interval=1.0):
        """
        function used to calibrate timing interval of all underlying asics, assuiming
        no current knowledge of underlying times / frequencies
        ARGS:
            interval - time in seconds to issue two different commands and to read time value pairs back from asics
        """
        self._alert = 0
        t1 = self._timeNow + interval
        calibrateSteps = self._Command(t1, command="Calibrate")

        t2 = self._timeNow + interval
        calibrateSteps = self._Command(t2, command="Calibrate")

    def Interrogate(self, interval=0.1, hard=False):
        """
        Function for issueing command to base node from daq node, and beginning
        a full readout sequence of timestamp data.
        The ratio duration/interval gives the number of interrogations
        VARS:
            interval - how often the daq interrogates the asics
            duration - how long the simulation will run for
            hard     - bool: if true, force remote ASICs to enter into transmit local state no matter what
        """
        
        self._alert=0
        time = self._timeNow + interval
        if hard:
            readoutSteps = self._Command(time, command="HardInterrogate")
        else:
            readoutSteps = self._Command(time, command="Interrogate")

    def WriteAsicRegister(self, row, col, config, timeEnd=1e-3):
        """
        Function sends a destination register read or write to the located asic

        ARGS:
            row    - XDest
            col    - YDest
            config - configuration type to be written to specific ASIC
            timeEnd - how long to process the array forward till, default ~1 ms
        """
        assert isinstance(config, AsicConfig), "unsuitable configuration type to write to register"
        assert row < self._nrows and row >= 0, f"row {row} unable for this array"
        assert col < self._ncols and col >= 0, f"col {col} unable for this array"

        # build the DaqNode register request
        byte = self._daqNode.RegWrite(row, col, config)

        # issue the byte command, and move forward in time
        timeProc = self._timeNow + timeEnd
        self._Command(timeProc, byte=byte)

    def _Command(self, timeEnd, command=None, byte=None):
        """
        Refactor TODO: This function should be able to remove the command option, since
        the QPByte member should be sufficienty to determine how a ASIC behaves.

        Function for issueing command to base node from daq node, and beginning
        a full readout sequence
        VARS:
            timeEnd - how long the array should be processed until
            command - string argument that the asics receive to tell them what readout is coming in from DAQnode.
            byte    - pre-generated QPByte from the DAQNode which is used to start the simulation process.

        NOTE Basic Unit of simulation:
            ASIC      - Node which receives incoming QPByte, Rx
            Direction - QpixAsicDir, direction of incoming QPByte
            QPByte    - source data, represents 64 bit word sent over Tx/Rx
            hitTime   - true transaction complete time defined by sending ASIC
            Command   - optional argument passed to receive data to tell
                        receiving ASIC to behave differently, this functionality
                        mirrors packet headers
        """

        # add the initial broadcast to the queue
        if byte is None:
            request = self._daqNode.GetTimestamp()
        # the only kinds of bytes that go this else through here are register writes
        elif byte.wordType == AsicWord.REGREQ:
            request = byte
        else:
            raise Excpetion("Unknown word type being sent via command")
        assert self._targNode is not None, "warning no targ node to send to"
        self._queue.AddQueueItem(self._targNode, self._targDir, request, self._timeNow, command=command)

        # move the Array forward in time
        self.Process(timeEnd)

        return self._queue.processed

    def _ProcessArray(self, nextTime):
        """
        move all processing of the array up to absTime
        """
        processed = 0
        somethingToDo = True
        while somethingToDo:
            somethingToDo = False
            for asic in self:
                newProcessItems = asic.Process(nextTime)
                if newProcessItems:
                    somethingToDo = True
                    for item in newProcessItems:
                        processed += 1
                        self._queue.AddQueueItem(*item)
        return processed

    def Process(self, timeEnd):
        """
        Main logic function to move the all ASICs within the Array forward in
        time to timeEnd.

        ARGS:
        timeEnd - 'absolute' time to move Array to. If Array is already at this
                   time, this function will do nothing
        """
        steps = 0
        PROCITEM = 0
        self._procAsics = [asic for asic in self]
        while(self._timeNow < timeEnd):

            dT = self._timeNow - self._timeEpsilon
            for asic in self._procAsics:
                newProcessItems = asic.Process(dT)
                if newProcessItems:
                    self._alert = 1 # this is not really a problem
                    for item in newProcessItems:
                        self._queue.AddQueueItem(*item)

            # process transactions
            while(self._queue.Length() > 0):

                if self._debugLevel > 0:
                    print(f"step-{steps} | time-{self._timeNow} | process size-{self._queue.Length()}")
                    for asic in self:
                        print(f"\t({asic.row}, {asic.col}): {asic.state} - {asic.relTicksNow}")

                # pop the next simulation unit
                steps += 1
                nextItem = self._queue.PopQueue()
                asic = nextItem.asic
                hitTime = nextItem.inTime

                p1 = self._ProcessArray(hitTime-self._timeEpsilon)

                newProcessItems = asic.ReceiveByte(nextItem)
                if newProcessItems:
                    for item in newProcessItems:
                        self._queue.AddQueueItem(*item)

                # ASICs to catch up to this time, and to send data
                p1 = self._ProcessArray(hitTime)

                # Speed up logic! What kinds of ASIC configuration can generate a 
                # byte transfer via processing only
                if self._queue.Length() == 0:
                    if self.push_state == True:
                        self._procAsics = [asic for asic in self if len(asic._times) != 0]
                    else:
                        self._procAsics = [asic for asic in self if (
                                    asic.state != AsicState.Idle or
                                    (asic._remoteFifo._curSize > 0 and
                                        (asic.state == AsicState.TransmitRemote or
                                         asic.state == asic.config.SendRemote)
                                     ))]

            self._timeNow += self._deltaT
            self._tickNow = int(self._timeNow * self.fNominal) + 1

        return

    def SetPushState(self, enabled=True, transact=False):
        """
        This function will send a ASIC configuration write to all ASICs
        enabling the PushState
        """
        assert isinstance(enabled, bool), "must supply boolean state to enable to ASICs"

        self.push_state = enabled

        for asic in self:
            config = asic.config
            config.EnablePush = enabled
            if transact:
                self.WriteAsicRegister(asic.row, asic.col, config)
            else:
                asic.config = config

        # a pushed ASIC should be in the send remote state
        self.SetSendRemote(enabled, transact)

    def SetSendRemote(self, enabled=True, transact=False):
        """
        This function will send a ASIC configuration write to all ASICs
        enabling the PushState
        """
        assert isinstance(enabled, bool), "must supply boolean state to enable to ASICs"

        self.send_remote = enabled

        for asic in self:
            config = asic.config
            config.SendRemote = enabled
            if transact:
                self.WriteAsicRegister(asic.row, asic.col, config)
            else:
                asic.config = config

    def IdleFor(self, interval=0.5):
        """
        Function will move the array forward by this time. This is meant
        to be a replacement for the Interrogate method while the ASICs are
        in a push state.

        ARGS:
        interval - time in seconds to move the array forward
        """
        timeEnd = self._timeNow + interval
        self.Process(timeEnd)

    def Route(self, route=None, timeout=None, transact=True, pos=None):
        '''
        Defines the routing of the asics manually
        ARGS:
        -- 
        Route: string->
            left  - routes all of the remote information to the left most asics
                    then moves all data to (0,0)
            snake - serpentine style, snakes through all asics before
                    remote data origin until (0,0)
            trunk - single column down from where the daq node is, and sets the daqNode
                    to the north position for this ASIC
            transact: bool, if true (default) will simulate daq node transactions
                            if false, will automagically update asic configs
        '''
        self.RouteState = route
        if timeout is None:
            timeout = self._targNode.config.timeout
        if route == None:
            return
        elif route.lower() == 'left':
            for asic in self:
                if asic.row == 0: 
                    config = AsicConfig(AsicDirMask.West, timeout)
                elif not(asic.col == 0):
                    config = AsicConfig(AsicDirMask.West, timeout)
                else:
                    config = AsicConfig(AsicDirMask.North, timeout)
                config.ManRoute = True
                if transact:
                    self.WriteAsicRegister(asic.row, asic.col, config)
                else:
                    asic.config = config
        elif route.lower() == 'snake':
            for asic in self:
                if not(asic.row%2 == 0) and asic.col == self._ncols-1:
                    config = AsicConfig(AsicDirMask.North, timeout)
                elif asic.row%2 == 0:
                    if asic.col == 0 and not(asic.row == 0):
                        config = AsicConfig(AsicDirMask.North, timeout)
                    else:
                        config = AsicConfig(AsicDirMask.West, timeout)
                else:
                    config = AsicConfig(AsicDirMask.East, timeout)
                config.ManRoute = True
                if transact:
                    self.WriteAsicRegister(asic.row, asic.col, config)
                else:
                    asic.config = config
        elif route.lower() == 'trunk':
            assert isinstance(pos, int), "must supply daq-node pos with trunk"
            if pos > 0:
                assert transact==False, "moving the Daqnode location is not transactable"
            assert pos < self._ncols-1, "can't move daqNode further than n cols"
            for asic in self:
                if asic.col < pos:
                    config = AsicConfig(AsicDirMask.East, timeout)
                elif asic.col > pos:
                    config = AsicConfig(AsicDirMask.West, timeout)
                else:
                    config = AsicConfig(AsicDirMask.North, timeout)
                config.ManRoute = True
                asic.config = config

            # route the DaqNode to aggregator in the north, and remove it from the 0,0 west spot
            self._targNode = self[0][pos]
            self._targNode.connections[AsicDirMask.North.value].asic = self._daqNode
            self._targDir = AsicDirMask(0)

            # disconnect the old corner node
            self[0][0].connections[AsicDirMask.West.value].asic = None
        else:
            print("WARNING: unknown route state passed!", self.RouteState)

    def _InjectHits(self, dataframeHits, offset=None):
        """
        InjectHits reads in output from tiledf created in radiogenicNB.ipynb. 
        Values that are read in

        This function should be
        ARGS:
            dataframeHits - tuple of:
                    asicX  :int
                    asicY  :int
                    resets :list (time, channel)
            offset - time, of when to set the earliest injected reset value to
        """
        # store the asic times into the correct asic
        self.InjectedHits = []
        self.totalTimes = 0
        for asicX, asicY, resets in dataframeHits:

            if asicX >= self._nrows or asicY >= self._ncols:
                continue

            times = np.asarray([time for time, _ in resets])
            channels = np.asarray([int(channel) for _, channel in resets])

            if offset is not None:
                times = times + offset

            self._asics[asicX][asicY].InjectHits(times, channels)

            self.InjectedHits.extend(self._asics[asicX][asicY]._times)
            self.totalTimes += len(times)
        self.totalInjectedHits = len(self.InjectedHits)



if __name__ == "__main__":
    array = QpixAsicArray(2,2)
    array.Calibrate()
    data = array.readData()
    print("read the following data:\n", data)
