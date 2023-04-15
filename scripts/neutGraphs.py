import ROOT
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


OUTPUT_FILE = "anaGraphs.root"
theta_dirs = [f"Theta{i}_const" for i in range(1, 6)]
zpos_dirs = [f"zpos{i}" for i in range(1, 6)]
root_colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kYellow, ROOT.kOrange]
zpos_values = [10, 800, 1800, 2800, 3500]
theta_values = [0, 2, -2, 90, -90]
zpos_colors = {zp: color for zp, color in zip(zpos_dirs, root_colors)}
zpos_titles = {zp: "Z-Vertex: " + str(value) for zp, value in zip(zpos_dirs, zpos_values)}
theta_colors = {tp: color for tp, color in zip(theta_dirs, root_colors)}
theta_titles = {tp: "\\theta_{z}: " + str(value) for tp, value in zip(theta_dirs, theta_values)}

output_file = "tmp.root"


class canvas_counter:
    cnt = 0
    self._canvases = []
    self._tf = ROOT.TFile(output_file, "RECREATE")

    def Add(self, canvas):
        self.cnt += 1
        self._tf.cd()
        canvas.Write()
        self._canvases.append(canvas)



root_canvas = canvas_counter()


def make_multi_graph(graph_list):
    """
    receive a list of graphs, stack them into a TMultigraph
    """
    tgMulti = ROOT.TMultiGraph()
    for graph in graph_list:
        tgMulti.Add(graph, "cp")
    return tgMulti


def draw_stack_hist(hist_list, x_axis_title=None, y_axis_title=None):
    """
    receive a list of histograms, stack them into a TStack
    """
    thStack = ROOT.THStack("hs", "")
    for hist in hist_list:
        thStack.Add(hist)
    thStack.Draw()
    if x_axis_title is not None:
        thStack.GetXaxis().SetTitle(x_axis_title)
    if y_axis_title is not None:
        thStack.GetYaxis().SetTitle(y_axis_title)
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
            graphs.append(data)

    return graphs


def makeMultiGraph(graphs, output_name, x_axis_title, y_axis_title):
    tmg = ROOT.TMultiGraph()
    for gr in graphs:
        tmg.Add(gr, "cp")
    root_canvas.cnt += 1
    canvas = ROOT.TCanvas(f"c{root_canvas.cnt}", f"c{root_canvas.cnt}", 1000, 1000)
    tmg.Draw("apl")
    tmg.GetXaxis().SetTitle(x_axis_title)
    tmg.GetYaxis().SetTitle(y_axis_title)
    # ROOT.gPad.BuildLegend(0.65, 0.25, 0.9, 0.50, "")
    canvas.SaveAs(output_name)
    canvas.Close()


def integrate_hists(hists, output_name, x_axis_title="Maximum ASIC Buffer Depth",
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

    makeMultiGraph(graphs, output_name, x_axis_title=x_axis_title, y_axis_title=y_axis_title)


def makeGraphs(tf_dict, tdirs, zdirs, graph_name="hAsic", hist_file="test_hASic_zpos.png",
               integral_file="test_tmg_zpos.png", x_axis_title=None, y_axis_title=None):

    asic_ints = get_graphs(tf_dict, tdirs, zdirs, graph_name)
    root_canvas.Add(ROOT.TCanvas(f"c{root_canvas.cnt}", f"c{root_canvas.cnt}", 1000, 1000))
    draw_stack_hist(asic_ints, x_axis_title, y_axis_title)
    # ROOT.gPad.BuildLegend(0.75, 0.75, 0.95, 0.95, "")
    canvas.SaveAs(hist_file)
    canvas.Close()
    integrate_hists(asic_ints, integral_file)


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

    outf = ROOT.TFile(output_file, "RECREATE")

    asic_ints = get_graphs(tf_dict, theta_dirs[0], zpos_dirs, "hAsic")
    root_canvas.cnt += 1
    integrate_hists(asic_ints, "test_tmg_zpos.png")
    canvas = ROOT.TCanvas(f"c{root_canvas.cnt}", f"c{root_canvas.cnt}", 1000, 1000)
    asic_stack = draw_stack_hist(asic_ints, "Asic Resets")
    ROOT.gPad.BuildLegend(0.75, 0.75, 0.95, 0.95, "")
    canvas.SaveAs("test_hASic_zpos.png")
    canvas.Close()

    pixel_ints = get_graphs(tf_dict, theta_dirs[0], zpos_dirs, "hPixel")
    root_canvas.cnt += 1
    integrate_hists(pixel_ints, "test_tmg_zpos_pixel.png", x_axis_title="Maximum Pixel Resets")
    pix_canvas = ROOT.TCanvas(f"c{root_canvas.cnt}", f"c{root_canvas.cnt}", 1000, 1000)
    pixel_stack = draw_stack_hist(pixel_ints, "Asic Resets")
    ROOT.gPad.BuildLegend(0.75, 0.75, 0.95, 0.95, "")
    pix_canvas.SaveAs("test_hPixel_zpos.png")
    pix_canvas.Close()

    # asic_ints = get_graphs(tf_dict, theta_dirs, zpos_dirs[0], "hPixel")
    # root_canvas.cnt += 1
    # canvas = ROOT.TCanvas(f"c{root_canvas.cnt}", f"c{root_canvas.cnt}", 1000, 1000)
    # stack = draw_stack_hist(asic_ints, "Asic Resets")
    # ROOT.gPad.BuildLegend(0.75, 0.75, 0.95, 0.95, "")
    # canvas.SaveAs("test_hPixel_theta.png")
    # canvas.Close()
    # integrate_hists(asic_ints, "test_tmg_theta_pixel.png", x_axis_title="Maximum Pixel Resets")

    # asic_theta = get_graphs(tf_dict, theta_dirs, zpos_dirs[0], "hAsic")
    # root_canvas.cnt += 1
    # newcanv = ROOT.TCanvas(f"c{root_canvas.cnt}", f"c{root_canvas.cnt}", 1000, 1000)
    # newcanv.cd()
    # tstack = draw_stack_hist(asic_theta, "Asic Resets")
    # ROOT.gPad.BuildLegend(0.75, 0.75, 0.95, 0.95, "")
    # newcanv.SaveAs("test_hASic_theta.png")
    # integrate_hists(asic_theta, "test_tmg_theta.png")


def readFeatherDataFile():
    df = pd.read_feather("neutMP.feather")

    df['size'] = df['AsicX'].map(len)
    df = df[df['size'] == 64]

    print(df)
    # print(df.columns, df.size)

    df["Remote Transaction Average"] = df['Remote Transactions'].map(np.mean)

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))
    df.hist('Max Local', bins=30, ax=ax[0][0])
    df.hist('Max Remote', bins=30, ax=ax[1][0])
    df.plot.scatter(x='Max Local', y='Max Remote', ax=ax[0][1])
    df.hist('Remote Transaction Average', bins=30)

    fig.savefig("df_histos.png")


def main(infile):

    print("running main")

    readRootDataFile(infile=infile)

    # readFeatherDataFile()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("need input file arg to read")
        sys.exit(-1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print("could not find file at:", input_file)
        sys.exit(-1)

    main(input_file)
