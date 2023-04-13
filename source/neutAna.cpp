#include "neutAna.hpp"
#include <iostream>

// root testing
#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TStyle.h"

// z-pos, defined in Neutrino.sh in qpixg4 and in neutrinoCombRam
const std::string zpCut100 = "zpos == 100";
const std::string zpCut800 = "zpos == 800";
const std::string zpCut1800 = "zpos == 1800";
const std::string zpCut2800 = "zpos == 2800";
const std::string zpCut3500 = "zpos == 3500";

// theta, defined in Neutrino.sh in qpixg4 and in neutrinoCombRam
const std::string thCut1 = "axis_x == 1 && axis_z == 0";
const std::string thCut2 = "axis_x == 10000 && axis_z == 349";
const std::string thCut3 = "axis_x == 10000 && axis_z == -349";
const std::string thCut4 = "axis_x == 0 && axis_z == 1";
const std::string thCut5 = "axis_x == 0 && axis_z == -1";

void fillZposDir(TDirectory* otf, cached_rdf& f, const std::string& cut){
    otf->cd();
    auto t1 = f.Filter(cut).Cache();
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

void fillThetaDir(TDirectory* otf, cached_rdf& f, const std::string& cut){
    otf->cd();
    auto zp = f.Filter(cut).Cache();
    auto tdTh1 = otf->mkdir("theta1");
    auto tdTh2 = otf->mkdir("theta2");
    auto tdTh3 = otf->mkdir("theta3");
    auto tdTh4 = otf->mkdir("theta4");
    auto tdTh5 = otf->mkdir("theta5");
    makeGraphs(zp, thCut1, tdTh1);
    makeGraphs(zp, thCut2, tdTh2);
    makeGraphs(zp, thCut3, tdTh3);
    makeGraphs(zp, thCut4, tdTh4);
    makeGraphs(zp, thCut5, tdTh5);
}

int main(int argc, char** argv){

    std::string input_name;
    std::string output_name;
    if(argc == 3){
        output_name = argv[2];
        std::cout << "saving arg name: " << output_name << std::endl;
    } else if(argc != 2){
        std::cout << "must provide only input file.\n";
        std::cout << "nArgs: " << argc << std::endl;
        return -1;
    }

    input_name = argv[1];
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
    auto f = r.Filter("tile_size > 0").Cache();

    int sum = f.Sum("tile_size").GetValue();
    double mean = f.Mean("tile_size").GetValue();
    double Max = f.Max("tile_size").GetValue();
    double Min = f.Min("tile_size").GetValue();
    std::cout << "Found total pixel hits: " << sum << std::endl;
    std::cout << "Found mean pixel hits: " << mean << std::endl;
    std::cout << "Found max pixel hits: " << Max << std::endl;
    std::cout << "Found min pixel hits: " << Min << std::endl;

    TFile* otf = new TFile(output_name.c_str(), "RECREATE");

    try
    {
        TDirectory* theta1Dir = otf->mkdir("Theta1_const");
        TDirectory* theta2Dir = otf->mkdir("Theta2_const");
        TDirectory* theta3Dir = otf->mkdir("Theta3_const");
        TDirectory* theta4Dir = otf->mkdir("Theta4_const");
        TDirectory* theta5Dir = otf->mkdir("Theta5_const");
        fillZposDir(theta1Dir, f, thCut1);
        fillZposDir(theta2Dir, f, thCut2);
        fillZposDir(theta3Dir, f, thCut3);
        fillZposDir(theta4Dir, f, thCut4);
        fillZposDir(theta5Dir, f, thCut5);

        TDirectory* z1Dir = otf->mkdir("Zpos1_const");
        TDirectory* z2Dir = otf->mkdir("Zpos8_const");
        TDirectory* z3Dir = otf->mkdir("Zpos18_const");
        TDirectory* z4Dir = otf->mkdir("Zpos28_const");
        TDirectory* z5Dir = otf->mkdir("Zpos35_const");
        fillThetaDir(z1Dir, f, zpCut100);
        fillThetaDir(z2Dir, f, zpCut800);
        fillThetaDir(z3Dir, f, zpCut1800);
        fillThetaDir(z4Dir, f, zpCut2800);
        fillThetaDir(z5Dir, f, zpCut3500);
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }

    otf->Write();
    otf->Close();

    // save an output and also save outputs that the python simulation can run
    // f.Snapshot("event_tree", "./saveRdf.root", {"asic_th2i"});
    // std::cout << "Saving output event hists.\n";

    return 0;
}