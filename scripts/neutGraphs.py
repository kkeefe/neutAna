import sys
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetStyle("Pub")

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# build the table headers here, the respective function calls in main fill and add
from texttable import Texttable
import latextable

# tabulate the integral graphs
table_neut_buf = Texttable()
table_neut_buf.set_cols_align(["c", "c", "c", "c", "c", "c", "c"])
table_neut_buf_data = [["lepton Pdg", "Horn Current Direction", "Z-Pos", "Theta", "95\% Capture", "99\% Capture"]]

# confidence intervals to relate local-remote buffer depths
table_digi_buf = Texttable()
table_digi_buf.set_cols_align(["c", "c", "c", "l", "r", "l", "r", "l", "r"])
table_digi_buf_data = [["Freq.", "Tile Size", "Local Hits", "95-S", "99-S", "95-L", "99-L", "95-T", "99-T"]]

# relate the number of remote transactions based on input hit size
table_digi_trans = Texttable()
table_digi_trans.set_cols_align(["c", "c", "c", "l", "r", "l", "r", "l", "r"])
table_digi_trans_data = [["Freq.", "Tile Size", "Avg. Local Hits", "S. Tot", "S. Per.", "L. Tot. ", "L. Per.", "T. Tot.", "T. Per."]]

# table to summarize the fitted line values for each of the parameters
table_fit_trans = Texttable()
table_fit_trans.set_cols_align(["l", "l", "c", "c", "c", "c"])
table_fit_trans_data = [["Freq.", "Tile Size", "Snake Fit", "Left Fit", "Trunk Fit", "Push Fit"]]

# don't warn when we update copys
pd.options.mode.chained_assignment = None

# neutrino globals
OUTPUT_FILE = "anaGraphs.root"
theta_dirs = [f"Theta{i}_const" for i in range(1, 6)]
theta_v = [0, 2, -2, 90, -90]
zpos_dirs = [f"zpos{i}" for i in range(1, 6)]
zpos_v = [10, 80, 180, 280, 350]
root_colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kYellow, ROOT.kOrange]
zpos_values = [10, 800, 1800, 2800, 3500]
theta_values = [0, 2, -2, 90, -90]
zpos_colors = {zp: color for zp, color in zip(zpos_dirs, root_colors)}
zpos_titles = {zp: "Z-Vertex: " + str(value) for zp, value in zip(zpos_dirs, zpos_values)}
theta_colors = {tp: color for tp, color in zip(theta_dirs, root_colors)}
theta_titles = {tp: "#theta_{z}: " + str(value) for tp, value in zip(theta_dirs, theta_values)}

zpos_values = {k:v for k,v in zip(zpos_dirs, zpos_v)}
theta_values = {k:v for k,v in zip(theta_dirs, theta_v)}

fhc_dirs = [
    "fhc_pdg12",
    "fhc_pdg-12",
    "fhc_pdg14",
    "fhc_pdg-14",
    "rhc_pdg12",
    "rhc_pdg-12",
    "rhc_pdg14",
    "rhc_pdg-14"
]

# digital globals
DIG_OUTPUT_FILE = "digAnaGraphs.root"
routeKeyColors = {"None":'red', 'trunk':'green', 'snake':'blue', 'left':'orange'}
routeColors = ['red', 'green', 'blue', 'orange']

# path relative from scripts directory?
OUTPUT_IMAGE_DIR = "./output_images"

# scripts
table_buffer_file = OUTPUT_IMAGE_DIR+"/buffer_data.tex"
table_trans_file = OUTPUT_IMAGE_DIR+"/transaction_data.tex"
table_fit_file = OUTPUT_IMAGE_DIR+"/fit_data.tex"
table_neut_buf_file =  OUTPUT_IMAGE_DIR+"/neut_buff_data.tex"

def saveTable(tab, fi):
    with open(fi, 'w') as f:
        f.write(tab)

class canvas_counter:
    """
    Manage creation of output graphs for neutAna into output_file
    """
    def __init__(self):
        self.cnt = 0
        self._obj = []
        self.tf = ROOT.TFile(OUTPUT_FILE, "RECREATE")
        self._canvas = ROOT.TCanvas(f"c", f"c", 1000, 1000)

    def Add(self, obj, output_dir, x_axis_title=None, y_axis_title=None, saveGraphs=None, legend_pos=None):
        """
        Add an object to the canvas, do some things with it, and save it to the
        output file
        """
        self.cnt += 1
        output_dir.cd()
        self._obj.append(obj)
        if isinstance(self._obj[-1], ROOT.TMultiGraph):
            self._obj[-1].Draw("APL")
        else:
            self._obj[-1].Draw()

        if legend_pos is not None and legend_pos == "tr":
            ROOT.gPad.BuildLegend(0.75, 0.75, 0.95, 0.95, "")
        if legend_pos is not None and legend_pos == "tl":
            ROOT.gPad.BuildLegend(0.15, 0.75, 0.35, 0.95, "")
        elif legend_pos is not None and legend_pos == "br":
            ROOT.gPad.BuildLegend(0.75, 0.15, 0.95, 0.35, "")

        if x_axis_title is not None:
            self._obj[-1].GetXaxis().SetTitle(x_axis_title)
        if y_axis_title is not None:
            self._obj[-1].GetYaxis().SetTitle(y_axis_title)

        self._canvas.Draw()
        if saveGraphs is not None:
            output_canv = f"{OUTPUT_IMAGE_DIR}/{saveGraphs}.pdf"
            self._canvas.SaveAs(output_canv)
        self._canvas.SetName(self._obj[-1].GetName())
        self._canvas.Write()
        self._canvas = ROOT.TCanvas(f"c", f"c", 1000, 1000)


root_canvas = canvas_counter()


def make_stack_hist(hist_list, output_name, x_axis_title=None, y_axis_title=None, title=None):
    """
    receive a list of histograms, stack them into a TStack
    """
    name = f"stack_{output_name}"

    thStack = ROOT.THStack(f"{name}", f"{name}")
    for hist in hist_list:
        thStack.Add(hist)
    if title is not None and isinstance(title, str):
        thStack.SetTitle(title)

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


def makeMultiGraph(graphs, output_name, x_axis_title, y_axis_title, title=None):
    name = f"multigraph_{output_name}"

    tmg = ROOT.TMultiGraph()
    tmg.SetName(f"{name}")

    for gr in graphs:
        tmg.Add(gr, "cp")

    if title is not None and isinstance(title, str):
        tmg.SetTitle(title)

    return tmg


def make_integral_hist(hists, output_name, tdirs, zdirs, lepPdg, isFHC, x_axis_title="Maximum ASIC Buffer Depth",
                    y_axis_title="Percent of Events Fully Captured", title=None):
    """
    create a running integral from a list of histograms passed here
    """
    assert isinstance(hists, list), "must receive a list of histograms"

    totalEntries = 0
    for hist in hists:
        totalEntries += hist.GetEntries()

    graphs = []
    points = hists[0].GetNcells()
    for i, asic in enumerate(hists):
        val = asic.GetIntegral()
        data = np.array([val[i] for i in range(points) if val[i] <= 0.99], dtype=np.double)
        ind = np.array([asic.GetBinCenter(i) for i in range(len(data))], dtype=np.double)
        tg = ROOT.TGraph(len(data), ind, data)
        tg.SetLineColor(asic.GetFillColor())
        tg.SetTitle(asic.GetTitle())
        graphs.append(tg)

        if lepPdg is not None and isFHC is not None:
            if not isinstance(zdirs, list):
                zpos = zdirs
                theta = tdirs[i]
            else:
                zpos = zdirs[i]
                theta = tdirs
            hornCurrent = "forward" if isFHC else "reverse"
            buf_data = [lepPdg, hornCurrent, zpos_values[zpos], theta_values[theta], ind[np.argwhere(data>=0.95)[0][0]], ind[-1]]
            table_neut_buf_data.append(buf_data)

    return makeMultiGraph(graphs, output_name, x_axis_title, y_axis_title, title)


def make_average_tmg(graphs, output_name, x_bins, title=None):
    """
    each graph represents an ASIC in this cut with the corresponding x, y value

    Create a TMultigraph of TGraphErrors for each graph
    """

    # we need to extract the x-axis and y-axis points for all graphs
    nGraphs = len(graphs)
    assert nGraphs > 0, "did not receive any graphs at make_average_tmg"

    def bin(x):
        prev_bin = 0
        for i, x_bin in enumerate(x_bins):
            if x < x_bin:
                return prev_bin
            else:
                prev_bin = x_bin
        return x_bin


    newGraphs = []
    for graph in graphs:
        nPoints = graph.GetN()

        data = [ graph.GetPointY(i) for i in range(nPoints) ]
        graph_bin = sorted([ bin(graph.GetPointX(i)) for i in range(nPoints) ])

        graph_ind, data = zip(*sorted(zip(graph_bin, data)))
        unique_ind = np.array(np.unique(graph_ind), dtype=np.double)
        mean_data = np.array([ np.mean([d for ind, d in zip(graph_ind, data) if ind == uid]) for uid in unique_ind], dtype=np.double)

        # errors
        ex = np.array([0]*len(unique_ind), dtype=np.double)
        std_data = np.array([np.std(d) for d in data], dtype=np.double)

        new_graph = ROOT.TGraphErrors(len(unique_ind), unique_ind, mean_data, ex, 0)
        new_graph.Fit("pol1", "Q")
        new_graph.SetLineColor(graph.GetLineColor())
        fit_line = new_graph.GetListOfFunctions().FindObject("pol1")
        fit_line.SetLineWidth(1)
        fit_line.SetLineColor(graph.GetLineColor())
        new_graph.SetTitle(graph.GetTitle())
        newGraphs.append(new_graph)

    tmg = makeMultiGraph(newGraphs, output_name, graphs[0].GetXaxis().GetTitle(), graphs[0].GetYaxis().GetTitle(), title)

    return tmg


def makeGraphs(tf_dict, tdirs, zdirs, output_dir, graph_name, output_name, x_axis_title=None, y_axis_title=None, lepPdg=None, isFHC=None, saveGraphs=None):

    asic_ints = get_graphs(tf_dict, tdirs, zdirs, graph_name)
    if len(asic_ints) == 0:
        print(f"found no graphs of {graph_name}")
        return 

    # manage output titles, if needed
    if saveGraphs is not None:
        title= "\\theta_{z} = "+f"{theta_values[tdirs]}" if isinstance(zdirs, list) else f"Z = {zpos_values[zdirs]} cm"
    else:
        title = None

    # manage THistograms
    sg = None
    fhc = "NA"
    if isFHC is not None and saveGraphs is not None:
        fhc = "fhc" if isFHC else "rhc" 
    if isinstance(asic_ints[0], ROOT.TH1):
        tmg = make_integral_hist(asic_ints, output_name, tdirs, zdirs, lepPdg, isFHC, title=title)
        if saveGraphs is not None:
            sg = saveGraphs+"_integral"+f"_pdg{lepPdg}"+f"_{fhc}"
        root_canvas.Add(tmg, output_dir, x_axis_title, y_axis_title, saveGraphs=sg ,legend_pos="br")

        stack = make_stack_hist(asic_ints, output_name, x_axis_title, y_axis_title, title=title)
        if saveGraphs is not None:
            sg = saveGraphs+"_stack_integral"+f"_pdg{lepPdg}"+f"_{fhc}"
        root_canvas.Add(stack, output_dir, x_axis_title, y_axis_title, saveGraphs=sg, legend_pos="tl")

    # manage TGraphs
    if isinstance(asic_ints[0], ROOT.TGraph):
        lepKEbins = list(range(250,10000,250))
        tmg = make_average_tmg(asic_ints, output_name, x_bins=lepKEbins, title=title)
        # tmg = make_average_tmg(asic_ints, output_name, title=title)
        if saveGraphs is not None:
            sg = saveGraphs+"_multigraph"+f"_pdg{lepPdg}"+f"_{fhc}"
        root_canvas.Add(tmg, output_dir, x_axis_title, y_axis_title, saveGraphs=sg, legend_pos="tl")


def readRootDataFile(infile, file_dir="test", lepPdg=None, isFHC=None):
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

    # top level dir
    fdir = root_canvas.tf.mkdir(file_dir)
    zdir = [fdir.mkdir(zp) for zp in zpos_dirs]
    tdir = [fdir.mkdir(tp) for tp in theta_dirs]

    # control for theta graphs
    for i, (theta_dir, td) in enumerate(zip(theta_dirs, tdir)):
        sg = True if i == 0 and lepPdg is not None else None
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "hTile",  "tile_cZpos", "Tile Resets", "Counts", lepPdg, isFHC, saveGraphs=f"Const_Theta{theta_values[theta_dirs[i]]}_Tile" if sg else None)
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "hAsic",  "asic_cZpos", "ASIC Resets", "Counts", lepPdg, isFHC, saveGraphs=f"Const_Theta{theta_values[theta_dirs[i]]}_ASIC" if sg else None)
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "hPixel", "pixel_cZpos",  "Pixel Resets", "Counts")
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "tgLepKEAsic", "LepKE_AsicResets_cZpos",  "LepKE", "Max ASIC Resets", lepPdg, isFHC, saveGraphs=f"Const_Theta{theta_values[theta_dirs[i]]}_ASIC_lepKE" if sg else None)
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "tgLepKETile", "LepKE_TileResets_cZpos",  "LepKE", "Max APA Resets", lepPdg, isFHC, saveGraphs=f"Const_Theta{theta_values[theta_dirs[i]]}_Tile_lepKE" if sg else None)
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "tgEnergyDepAsic", "EnergyDep_AsicResets_cZpos",  "Energy Deposit (MeV)", "Max ASIC Resets", lepPdg, isFHC, saveGraphs=f"Const_Theta{theta_values[theta_dirs[i]]}_ASIC_EnergyDep" if sg else None)
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "tgEnergyDepTile", "EnergyDep_TileResets_cZpos",  "Energy Deposit (MeV)", "Max APA Resets", lepPdg, isFHC, saveGraphs=f"Const_Theta{theta_values[theta_dirs[i]]}_Tile_EnergyDep" if sg else None)

    # control for zpos graphs
    for i, (zpos_dir, zd) in enumerate(zip(zpos_dirs, zdir)):
        sg = True if zpos_values[zpos_dirs[i]] == 180 and lepPdg is not None else None
        makeGraphs(tf_dict, theta_dirs, zpos_dir, zd, "hTile",  "tile_cTheta", "Tile Resets", "Counts", lepPdg, isFHC, saveGraphs=f"Const_Z{zpos_values[zpos_dirs[i]]}_Tile" if sg else None)
        makeGraphs(tf_dict, theta_dirs, zpos_dir, zd, "hAsic",  "asic_cTheta", "ASIC Resets", "Counts", lepPdg, isFHC, saveGraphs=f"Const_Z{zpos_values[zpos_dirs[i]]}_ASIC" if sg else None)
        makeGraphs(tf_dict, theta_dirs, zpos_dir, zd, "hPixel", "pixel_cTheta",  "Pixel Resets", "Counts")
        makeGraphs(tf_dict, theta_dirs, zpos_dir, zd, "tgLepKEAsic", "LepKE_AsicResets_cTheta",  "LepKE", "Max ASIC Resets", lepPdg, isFHC, saveGraphs=f"Const_Z{zpos_values[zpos_dirs[i]]}_ASIC_lepKE" if sg else None)
        makeGraphs(tf_dict, theta_dirs, zpos_dir, zd, "tgLepKETile", "LepKE_TileResets_cTheta",  "LepKE", "Max Tile Resets", lepPdg, isFHC, saveGraphs=f"Const_Z{zpos_values[zpos_dirs[i]]}_ASIC_lepKE" if sg else None)
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "tgEnergyDepAsic", "EnergyDep_AsicResets_cTheta",  "Energy Deposit (MeV)", "Max ASIC Resets", lepPdg, isFHC, saveGraphs=f"Const_Z{theta_values[theta_dirs[i]]}_ASIC_EnergyDep" if sg else None)
        makeGraphs(tf_dict, theta_dir, zpos_dirs, td, "tgEnergyDepTile", "EnergyDep_TileResets_cTheta",  "Energy Deposit (MeV)", "Max APA Resets", lepPdg, isFHC, saveGraphs=f"Const_Z{theta_values[theta_dirs[i]]}_Tile_EnergyDep" if sg else None)

    tf.Close()


###############################################################################
############################     Digital Ana     ##############################
###############################################################################

def readFeatherDataFile(output_name, input_file="./scripts/neutMP60k.feather", size=16):
    """
    read the input feather file, create output PDFs, and fill the texttables to print
    to LaTex
    """
    
    df = pd.read_feather(input_file)
    architectures = pd.unique(df["Architecture"])

    df = df[(df["Route"] != "None") and (df["Route"] == "Push")]
    df['size'] = df['AsicX'].map(len)
    sizes = pd.unique(df['size'])
    df = df[df['size'] == size]
    routes = ["snake", "left", "trunk"]
    df["Remote Transaction Average"] = df['Remote Transactions'].map(np.mean)

    remote_trans_avg = [0 for i in range(len(routes)+1)]
    conf95_intervals = [0 for i in range(len(routes)+1)]
    conf99_intervals = [0 for i in range(len(routes)+1)]
    maxSize = 0
    max_local_stack, max_remote_stack, stack_data = [], [], []
    for i, route in enumerate(routes):

        # add data to stacks
        route_df = df[df["Route"] == route]
        stack_data.append(route_df["Remote Transaction Average"])
        max_local_stack.append(route_df["Max Local"])
        max_remote_stack.append(route_df["Max Remote"])
        print(f'{route} has counts: {len(route_df["Max Local"])}')

        # find the 90% and 99% intervals here
        remote_data = sorted(route_df["Max Remote"])
        len_1p = int(0.01 * (len(remote_data)))
        len_10p = int(0.10 * (len(remote_data)))
        len_5p = int(0.05 * (len(remote_data)))
        maxSize = len(remote_data) if len(remote_data) > maxSize else maxSize
        conf99_intervals[i] = remote_data[-len_1p+1]
        conf95_intervals[i] = remote_data[-len_5p+1]

        local_data = sorted(route_df["Max Local"])
        len_1p = int(0.01 * (len(local_data)))
        len_10p = int(0.10 * (len(local_data)))
        len_5p = int(0.05 * (len(local_data)))
        maxSize = len(local_data) if len(local_data) > maxSize else maxSize
        conf99_intervals[-1] = local_data[-len_1p+1]
        
        remote_trans_avg[i] = np.mean(route_df["Remote Transaction Average"])
        remote_trans_avg[-1] = np.mean(route_df["Injected Size"])

    # save local data
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.hist(max_local_stack, bins=int(np.sqrt(maxSize)),  histtype='step', stacked=False, fill=False, range=(0, maxSize), density=False, cumulative=True)
    ax.set_xlabel("Local Buffer Depth")
    ax.set_ylabel("CDF of entries")
    plt.tight_layout()
    fig.savefig(OUTPUT_IMAGE_DIR+f"/{output_name}_local_stack.pdf")

    # scatter plot fits
    fig, ax = plt.subplots(figsize=(5, 5))
    fits = [0 for i in range(len(routes)+1)]
    for i, (maxL, maxR) in enumerate(zip(max_local_stack, max_remote_stack)):
        b, a = np.polyfit(maxL, maxR, deg=1)
        x = np.linspace(1, max(maxL), num=50)
        fits[i] = b
        ax.plot(x, b*x+a, c=routeColors[i], rasterized=True)
        ax.scatter(x=maxL, y=maxR, c=routeColors[i], label=f"{routes[i]} - {b:0.2f}", rasterized=True)
    ax.legend(loc="upper left")
    ax.set_xlabel("Local Buffer Depth")
    ax.set_ylabel("Remote Buffer Depth")
    plt.tight_layout()
    fig.savefig(OUTPUT_IMAGE_DIR+f"/{output_name}_route_fits.pdf")
    plt.close(fig)

    # save remote data
    fig, ax = plt.subplots(figsize=(5, 5))
    max_labels = [*routes, "local"]
    max_labels = [ f"{r} - {c}" for r, c in zip(max_labels, conf99_intervals)]
    max_remote_stack.append(max_local_stack[0])
    ax.hist(max_remote_stack, bins=100, histtype='step', stacked=False, fill=False, range=(0, 2000), density=False, cumulative=True, label=max_labels)
    ax.set_xlabel("Buffer Depth")
    ax.set_ylabel("CDF of entries")
    ax.legend(loc="lower right")
    plt.tight_layout()
    fig.savefig(OUTPUT_IMAGE_DIR+f"/{output_name}_remote_stack.pdf")
    plt.close(fig)

    # save remote transaction average data
    rng = (1, 3001)
    nbins = 200
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlabel("Average number of remote transactions")
    ax.hist(stack_data, bins=nbins, range=rng, histtype='bar', stacked=True, log=False, label=routes)
    ax.set_ylabel(f"{(rng[1]-rng[0])/nbins:.2f} events / remote trans avg.")
    ax.set_xlabel("Remote Transaction Average")
    ax.legend(loc="upper right")
    plt.tight_layout()
    fig.savefig(OUTPUT_IMAGE_DIR+f"/{output_name}_remote_transactions.pdf")
    plt.close(fig)

    frq = "0.5\%" if "low" in input_file.lower() else "5\%"
    buf_data = [frq, f"{size}", conf99_intervals[-1], conf95_intervals[0], conf99_intervals[0], conf95_intervals[1], conf99_intervals[1], conf95_intervals[2], conf99_intervals[2]]
    trans_data = [frq, f"{size}", remote_trans_avg[-1], remote_trans_avg[0], remote_trans_avg[0]/10, remote_trans_avg[1], remote_trans_avg[1]/10, remote_trans_avg[2], remote_trans_avg[2]/10]
    fit_data = [frq, f"{size}", fits[0], fits[1], fits[2], fits[3]]

    table_digi_trans_data.append(trans_data)
    table_digi_buf_data.append(buf_data)
    table_fit_trans_data.append(fit_data)


def main():

    # table_neut = Texttable()
    # table_neut.set_cols_align(["l", "r", "c"])
    # table_neut.set_cols_valign(["t", "m", "b"])
    # # full tile analysis
    readRootDataFile(infile="./test_graphs.root", file_dir="fhc_pdg12", lepPdg=12, isFHC=True)
    # readRootDataFile(infile=".\\pdfs\\full_graphs_pdg12_fhc-1.root", file_dir="fhc_pdg12", lepPdg=12, isFHC=True)
    # readRootDataFile(infile=".\\pdfs\\full_graphs_pdg-12_fhc-1.root", file_dir="fhc_pdg-12")
    # readRootDataFile(infile=".\\pdfs\\full_graphs_pdg14_fhc-1.root", file_dir="fhc_pdg14")
    # readRootDataFile(infile=".\\pdfs\\full_graphs_pdg-14_fhc-1.root", file_dir="fhc_pdg-14")
    # readRootDataFile(infile=".\\pdfs\\full_graphs_pdg12_fhc-rhc.root", file_dir="rhc_pdg12")
    # readRootDataFile(infile=".\\pdfs\\full_graphs_pdg-12_fhc-rhc.root", file_dir="rhc_pdg-12")
    # readRootDataFile(infile=".\\pdfs\\full_graphs_pdg14_fhc-rhc.root", file_dir="rhc_pdg14")
    # readRootDataFile(infile=".\\pdfs\\full_graphs_pdg-14_fhc-rhc.root", file_dir="rhc_pdg-14")
    # neut_buff_tab = latextable.draw_latex(table_neut_buf_data, caption="APA Integral Data", label="tab:apa_sum")
    # saveTable(neut_buff_tab, table_neut_buf_file)

    # # vertex analysis
    # readRootDataFile(infile=".\\pdfs\\electron_nu_fhc_graphs.root", file_dir="fhc_pdg12", lepPdg=12, isFHC=True)
    # readRootDataFile(infile=".\\pdfs\\aelectron_nu_fhc_graphs.root", file_dir="fhc_pdg-12")
    # readRootDataFile(infile=".\\pdfs\\muon_nu_fhc_graphs.root", file_dir="fhc_pdg14")
    # readRootDataFile(infile=".\\pdfs\\amuon_nu_fhc_graphs.root", file_dir="fhc_pdg-14")
    # readRootDataFile(infile=".\\pdfs\\electron_nu_rhc_graphs.root", file_dir="rhc_pdg12")
    # readRootDataFile(infile=".\\pdfs\\aelectron_nu_rhc_graphs.root", file_dir="rhc_pdg-12")
    # readRootDataFile(infile=".\\pdfs\\muon_nu_rhc_graphs.root", file_dir="rhc_pdg14")
    # readRootDataFile(infile=".\\pdfs\\amuon_nu_rhc_graphs.root", file_dir="rhc_pdg-14")

    # readFeatherDataFile("mp60_16_fast", input_file="./scripts/neutMP60k.feather", size=16)
    # readFeatherDataFile("mp60_16_slow", input_file="./scripts/neutMP60k_lowFrq.feather", size=16)
    # readFeatherDataFile("mp60_64_fast", input_file="./scripts/neutMP60k.feather", size=64)
    # readFeatherDataFile("mp60_64_slow", input_file="./scripts/neutMP60k_lowFrq.feather", size=64)
    # readFeatherDataFile("mp60_140_fast", input_file="./scripts/neutMP60k.feather", size=140)
    # readFeatherDataFile("mp60_140_slow", input_file="./scripts/neutMP60k_lowFrq.feather", size=140)
    # readFeatherDataFile("mp60_256_fast", input_file="./scripts/neutMP60k.feather", size=256)
    # readFeatherDataFile("mp60_256_slow", input_file="./scripts/neutMP60k_lowFrq.feather", size=256)
    # table_digi_trans.add_rows(table_digi_trans_data)
    # table_digi_buf.add_rows(table_digi_buf_data)
    # table_fit_trans.add_rows(table_fit_trans_data)
    # trans_tab = latextable.draw_latex(table_digi_trans, caption="Transaction Data", label="tab:transact")
    # buff_tab = latextable.draw_latex(table_digi_buf, caption="Buffer Data", label="tab:buffers")
    # fit_tab = latextable.draw_latex(table_fit_trans, caption="Transaction Fit Results", label="tab:fit")
    # saveTable(buff_tab, table_buffer_file)
    # saveTable(trans_tab, table_trans_file)
    # saveTable(fit_tab, table_fit_file)

    # readNeutrinoAnaFile("anaGraphsFull.root")

if __name__ == "__main__":
    # if len(sys.argv) != 1:
    #     print("only run, no args")
    #     sys.exit(-1)
    main()
