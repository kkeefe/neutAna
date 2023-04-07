#include "neutAna.hpp"
#include <iostream>

// root testing
#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TStyle.h"

int main(int argc, char** argv){

    if(argc != 2){
        std::cout << "must provide only input file.\n";
        std::cout << "nArgs: " << argc << std::endl;
        return -1;
    }

    std::string input_name = argv[1];
    TFile* tf = new TFile(input_name.c_str(), "READ");
    if(tf->IsZombie()){std::cout << "warning unable to open file!\n";return -1;};
    tf->Close();

    ROOT::EnableImplicitMT();
    ROOT::RDataFrame rdf = ROOT::RDataFrame("event_tree", input_name.c_str());
    std::cout << "found tree with entries: " << rdf.Count().GetValue() << std::endl;

    // filtering here
    auto r = rdf.Define("tile_size", count_resets, {"pixel_reset", "pixel_x", "pixel_y"})
                .Define("all_pixel_reset", all_pixel_resets, {"pixel_reset", "pixel_x", "pixel_y"})
                .Define("max_pixel_reset", max_pixel_resets, {"all_pixel_reset"})
                .Define("asic_th2i", max_asic_resets, {"pixel_reset", "pixel_x", "pixel_y"})
                .Define("max_pixel_rtd", max_pixel_rtds, {"pixel_reset", "pixel_x", "pixel_y"});
    auto f = r.Filter("tile_size > 0");

    int sum = f.Sum("tile_size").GetValue();
    double mean = f.Mean("tile_size").GetValue();
    double Max = f.Max("tile_size").GetValue();
    double Min = f.Min("tile_size").GetValue();
    std::cout << "Found total pixel hits: " << sum << std::endl;
    std::cout << "Found mean pixel hits: " << mean << std::endl;
    std::cout << "Found max pixel hits: " << Max << std::endl;
    std::cout << "Found min pixel hits: " << Min << std::endl;

    TFile* otf = new TFile("./pdfs/graphs.root", "RECREATE");

    // z-pos, defined in Neutrino.sh in qpixg4 and in neutrinoCombRam
    std::string zpCut100 = "zpos == 100";
    std::string zpCut800 = "zpos == 800";
    std::string zpCut1800 = "zpos == 1800";
    std::string zpCut2800 = "zpos == 2800";
    std::string zpCut3500 = "zpos == 3500";

    auto z1 = f.Filter(zpCut100);
    auto z8 = f.Filter(zpCut800);
    auto z18 = f.Filter(zpCut1800);
    auto z28 = f.Filter(zpCut2800);
    auto z38 = f.Filter(zpCut3500);

    // theta, defined in Neutrino.sh in qpixg4 and in neutrinoCombRam
    std::string thCut1 = "axis_x == 1 && axis_z == 0";
    std::string thCut2 = "axis_x == 10000 && axis_z == 349";
    std::string thCut3 = "axis_x == 10000 && axis_z == -349";
    std::string thCut4 = "axis_x == 0 && axis_z == 1";
    std::string thCut5 = "axis_x == 0 && axis_z == -1";

    try
    {
        auto t1 = f.Filter(thCut1);
        auto tdZ1 = otf->mkdir("zpos1");
        auto tdZ2 = otf->mkdir("zpos2");
        auto tdZ3 = otf->mkdir("zpos3");
        auto tdZ4 = otf->mkdir("zpos4");
        auto tdZ5 = otf->mkdir("zpos5");
        makeGraphs(t1, zpCut100, tdZ1);
        makeGraphs(t1, zpCut800, tdZ2);
        makeGraphs(t1, zpCut1800, tdZ3);
        makeGraphs(t1, zpCut2800, tdZ4);
        makeGraphs(t1, zpCut3500, tdZ5);
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }
    

    // theta graphs
    auto tdTh1 = otf->mkdir("theta1");
    auto tdTh2 = otf->mkdir("theta2");
    auto tdTh3 = otf->mkdir("theta3");
    auto tdTh4 = otf->mkdir("theta4");
    auto tdTh5 = otf->mkdir("theta5");
    makeGraphs(z18, thCut1, tdTh1);
    makeGraphs(z18, thCut2, tdTh2);
    makeGraphs(z18, thCut3, tdTh3);
    makeGraphs(z18, thCut4, tdTh4);
    makeGraphs(z18, thCut5, tdTh5);

    otf->Write();
    otf->Close();

    // save an output and also save outputs that the python simulation can run
    // f.Snapshot("event_tree", "./pdfs/saveRdf.root", {"asic_th2i"});
    // std::cout << "Saving output event hists.\n";

    return 0;
}