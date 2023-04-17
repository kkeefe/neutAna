import sys
import ROOT
ROOT.gROOT.SetBatch(True)
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# neutrino globals
OUTPUT_FILE = "anaGraphs.root"
theta_dirs = [f"Theta{i}_const" for i in range(1, 6)]
zpos_dirs = [f"zpos{i}" for i in range(1, 6)]
root_colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kYellow, ROOT.kOrange]
zpos_values = [10, 800, 1800, 2800, 3500]
theta_values = [0, 2, -2, 90, -90]
zpos_colors = {zp: color for zp, color in zip(zpos_dirs, root_colors)}
zpos_titles = {zp: "Z-Vertex: " + str(value) for zp, value in zip(zpos_dirs, zpos_values)}
theta_colors = {tp: color for tp, color in zip(theta_dirs, root_colors)}
theta_titles = {tp: "#theta_{z}: " + str(value) for tp, value in zip(theta_dirs, theta_values)}


# digital globals
DIG_OUTPUT_FILE = "digAnaGraphs.root"
routeColors = {"None":'red', 'trunk':'green', 'snake':'blue', 'left':'orange'}


class canvas_counter:
    """
    Manage creation of output graphs for neutAna into output_file
    """
    def __init__(self):
        self.cnt = 0
        self._obj = []
        self._tf = ROOT.TFile(OUTPUT_FILE, "RECREATE")
        self._canvas = ROOT.TCanvas(f"c", f"c", 1000, 1000)

    def Add(self, obj, x_axis_title=None, y_axis_title=None, legend_pos=None):
        """
        Add an object to the canvas, do some things with it, and save it to the
        output file
        """
        self.cnt += 1
        self._tf.cd()
        self._obj.append(obj)
        self._obj[-1].Draw()

        if legend_pos is not None and legend_pos == "tr":
            ROOT.gPad.BuildLegend(0.75, 0.75, 0.95, 0.95, "")
        elif legend_pos is not None and legend_pos == "br":
            ROOT.gPad.BuildLegend(0.75, 0.15, 0.95, 0.35, "")

        if x_axis_title is not None:
            self._obj[-1].GetXaxis().SetTitle(x_axis_title)
        if y_axis_title is not None:
            self._obj[-1].GetYaxis().SetTitle(y_axis_title)

        self._canvas.SetName(self._obj[-1].GetName())
        self._canvas.Draw()
        self._canvas.Write()
        self._canvas = ROOT.TCanvas(f"c", f"c", 1000, 1000)


root_canvas = canvas_counter()


def make_stack_hist(hist_list, output_name, x_axis_title=None, y_axis_title=None):
    """
    receive a list of histograms, stack them into a TStack
    """
    name = f"stack_{output_name}"

    thStack = ROOT.THStack(f"{name}", f"{name}")
    for hist in hist_list:
        thStack.Add(hist)

    return thStack


def get_graphs(data_dict, theta_key, z_key, name):
    graphs = []
    vary_z = True
    vary_t = True

    if not isinstance(theta_key, list):
        theta_key = [theta_key]
        vary_t = False

    if not isinstance(z_key, list):
        z_key = [z_key]
        vary_z = False

    assert vary_z ^ vary_t, f"get_graphs expections are variation in z XOR theta"

    for tk in theta_key:
        for zk in z_key:
            if name not in data_dict[tk][zk].keys():
                print(f"warning {name} not found at", tk, zk)
                continue
            data = data_dict[tk][zk][name]
            if isinstance(data, ROOT.TH1):
                if vary_z:
                    data.SetFillColor(zpos_colors[zk])
                    data.SetTitle(zpos_titles[zk])
                else:
                    data.SetFillColor(theta_colors[tk])
                    data.SetTitle(theta_titles[tk])
            elif isinstance(data, ROOT.TGraph):
                if vary_z:
                    data.SetLineColor(zpos_colors[zk])
                    data.SetTitle(zpos_titles[zk])
                else:
                    data.SetLineColor(theta_colors[tk])
                    data.SetTitle(theta_titles[tk])
            graphs.append(data)

    return graphs


def makeMultiGraph(graphs, output_name, x_axis_title, y_axis_title):
    name = f"multigraph_{output_name}"

    tmg = ROOT.TMultiGraph()
    tmg.SetName(f"{name}")

    for gr in graphs:
        tmg.Add(gr, "cp")

    return tmg


def make_integral_hist(hists, output_name, x_axis_title="Maximum ASIC Buffer Depth",
                    y_axis_title="Percent of Events Fully Captured"):
    """
    create a running integral from a list of histograms passed here
    """
    assert isinstance(hists, list), "must receive a list of histograms"

    totalEntries = 0
    for hist in hists:
        totalEntries += hist.GetEntries()
    print("found total entries", totalEntries)

    graphs = []
    points = hists[0].GetNcells()
    for asic in hists:
        val = asic.GetIntegral()
        data = np.array([val[i] for i in range(points) if val[i] <= 0.99], dtype=np.double)
        ind = np.array([asic.GetBinCenter(i) for i in range(len(data))], dtype=np.double)
        tg = ROOT.TGraph(len(data), ind, data)
        tg.SetLineColor(asic.GetFillColor())
        tg.SetTitle(asic.GetTitle())
        graphs.append(tg)

    return makeMultiGraph(graphs, output_name, x_axis_title, y_axis_title)


def make_average_tmg(graphs, output_name, x_bins=None):
    """
    each graph represents an ASIC in this cut with the corresponding x, y value

    Create a TMultigraph of TGraphErrors for each graph
    """

    # we need to extract the x-axis and y-axis points for all graphs
    nGraphs = len(graphs)
    assert nGraphs > 0, "did not receive any graphs at make_average_tmg"

    newGraphs = []
    for graph in graphs:
        nPoints = graph.GetN()
        xpoints = graph.GetX()
        ydata = graph.GetY()

        # raw points
        graph_ind = np.array([graph.GetPointX(i) for i in range(nPoints)], dtype=np.double)
        if x_bins is not None:
            ind = []
            for i, gi in enumerate(graph_ind):
                for j, xi in enumerate(x_bins):
                    if xi > gi:
                        ind.append(x_bins[j-1])
                        break
                    elif i == len(graph_ind) - 1 or j == len(x_bins) - 1:
                        ind.append(x_bins[-1])
                        break
            graph_ind = ind

        unique_ind = np.array(np.unique(graph_ind), dtype=np.double)
        unique_ind_id = 0
        cur_unique_ind = unique_ind[unique_ind_id]

        # build the means and unique index
        data = [[]]
        for i in range(nPoints):
            if graph_ind[i] == cur_unique_ind:
                data[-1].append(graph.GetPointY(i))
            else:
                unique_ind_id += 1
                cur_unique_ind = unique_ind[unique_ind_id]
                data.append([])
                data[-1].append(graph.GetPointY(i)) 

        mean_data = np.array([np.mean(d) for d in data], dtype=np.double)

        # errors
        ex = np.array([0]*len(unique_ind), dtype=np.double)
        std_data = np.array([np.std(d) for d in data], dtype=np.double)

        new_graph = ROOT.TGraphErrors(len(unique_ind), unique_ind, mean_data, ex, std_data)
        new_graph.SetLineColor(graph.GetLineColor())
        new_graph.SetTitle(graph.GetTitle())
        newGraphs.append(new_graph)

    tmg = makeMultiGraph(newGraphs, output_name, graphs[0].GetXaxis().GetTitle(), graphs[0].GetYaxis().GetTitle())

    return tmg



def makeGraphs(tf_dict, tdirs, zdirs, graph_name, output_name, x_axis_title=None, y_axis_title=None):

    asic_ints = get_graphs(tf_dict, tdirs, zdirs, graph_name)
    if len(asic_ints) == 0:
        print(f"found no graphs of {graph_name}")
        return 

    # manage THistograms
    if isinstance(asic_ints[0], ROOT.TH1):
        tmg = make_integral_hist(asic_ints, output_name)
        root_canvas.Add(tmg, x_axis_title, y_axis_title, legend_pos="br")

        stack = make_stack_hist(asic_ints, output_name, x_axis_title, y_axis_title)
        root_canvas.Add(stack, x_axis_title, y_axis_title, legend_pos="tr")

    # manage TGraphs
    if isinstance(asic_ints[0], ROOT.TGraph):
        lepKEbins = list(range(250,10000,250))
        tmg = make_average_tmg(asic_ints, output_name, x_bins=lepKEbins)
        root_canvas.Add(tmg, x_axis_title, y_axis_title, legend_pos="tr")


def readRootDataFile(infile):
    """
    how to parse the output data graph of neutAna.cpp
    """

    tf = ROOT.TFile(infile, "read")
    if tf.IsZombie():
        print("unable to find root file")
        sys.exit(-1)

    tf_dict = {
        theta_dir: {zdir: {f.GetName(): f.ReadObj() for f in getattr(getattr(tf, theta_dir), zdir).GetListOfKeys()} for
                    zdir in zpos_dirs} for theta_dir in theta_dirs}


    # control for theta graphs
    makeGraphs(tf_dict, theta_dirs[0], zpos_dirs, "hTile",  "tile_cZpos", "Tile Resets", "Counts")
    makeGraphs(tf_dict, theta_dirs[0], zpos_dirs, "hAsic",  "asic_cZpos", "ASIC Resets", "Counts")
    makeGraphs(tf_dict, theta_dirs[0], zpos_dirs, "hPixel", "pixel_cZpos",  "Pixel Resets", "Counts")
    makeGraphs(tf_dict, theta_dirs[0], zpos_dirs, "tgLepKEAsic", "LepKE_AsicResets_cZpos",  "LepKE", "Max ASIC Resets")
    makeGraphs(tf_dict, theta_dirs[0], zpos_dirs, "tgLepKETile", "LepKE_TileResets_cZpos",  "LepKE", "Max Tile Resets")

    # control for zpos graphs
    makeGraphs(tf_dict, theta_dirs, zpos_dirs[0], "hTile",  "tile_cTheta", "Tile Resets", "Counts")
    makeGraphs(tf_dict, theta_dirs, zpos_dirs[0], "hAsic",  "asic_cTheta", "ASIC Resets", "Counts")
    makeGraphs(tf_dict, theta_dirs, zpos_dirs[0], "hPixel", "pixel_cTheta",  "Pixel Resets", "Counts")
    makeGraphs(tf_dict, theta_dirs, zpos_dirs[0], "tgLepKEAsic", "LepKE_AsicResets_cTheta",  "LepKE", "Max ASIC Resets")
    makeGraphs(tf_dict, theta_dirs, zpos_dirs[0], "tgLepKETile", "LepKE_TileResets_cTheta",  "LepKE", "Max Tile Resets")

    tf.Close()


def readFeatherDataFile():
    df = pd.read_feather("./scripts/neutMP.feather")

    df['size'] = df['AsicX'].map(len)
    df = df[df['size'] == 64]

    architectures = pd.unique(df["Architecture"])
    routes = pd.unique(df['Route'])

    df["Remote Transaction Average"] = df['Remote Transactions'].map(np.mean)

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))
    max_local_stack, max_remote_stack, stack_data = [], [], []
    for route in routes:
        if route == "None":
            continue
        route_df = df[df["Route"] == route]

        ax[0][1].scatter(x=route_df["Max Local"], y=route_df["Max Remote"], c=routeColors[route], label=route)

        # scatter plot fits
        b, a = np.polyfit(route_df["Max Local"], route_df["Max Remote"], deg=1)
        x = np.linspace(1, ax[0][1].get_xlim(), num=50)
        ax[0][1].plot(x, b*x+a, c=routeColors[route])

        # add data to stacks
        stack_data.append(route_df["Remote Transaction Average"])
        max_local_stack.append(route_df["Max Local"])
        max_remote_stack.append(route_df["Max Remote"])

    ax[0][0].hist(max_local_stack, bins=100,  histtype='step', stacked=False, fill=False, range=(0, 2000), density=False, cumulative=True, label=routes[1:])
    max_remote_stack.append(max_local_stack[0])
    max_labels = [*routes[1:], "local"]
    ax[1][0].hist(max_remote_stack, bins=100, histtype='step', stacked=False, fill=False, range=(0, 2000), density=False, cumulative=True, label=max_labels)

    ax[1][1].hist(stack_data, bins=200, range=(1, 3001), histtype='bar', stacked=True, log=False, label=routes[1:])
    ax[1][1].set_ylabel("10 events / remote trans avg.")
    ax[1][1].set_xlabel("Remote Transaction Average")

    ax[0][0].legend(loc="lower right")
    ax[0][0].set_xlabel("Local Buffer Depth")
    ax[0][0].set_ylabel("CDF of entries")

    ax[0][1].legend(loc="lower right", numpoints=1)
    ax[0][1].set_xlabel("Max Local Buffer Depth")
    ax[0][1].set_ylabel("Max Remote Buffer Depth")

    ax[1][0].legend(loc="lower right")
    ax[1][0].set_xlabel("Max Remote Buffer Depth")
    ax[1][0].set_ylabel("Cumulative Events")

    ax[1][1].legend()


    fig.savefig("df_histos.png")


def main(infile):

    print("running main")

    # readRootDataFile(infile=infile)

    readFeatherDataFile()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("need input file arg to read")
        sys.exit(-1)


    input_file = sys.argv [1]
    if not os.path.isfile(input_file):
        print("could not find file at:", input_file)
        sys.exit(-1)

    main(input_file)
