#include <string>
#include <vector>

// refactor of neutAna here to make the pdfs
#include "neutAna.hpp"

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

void fillZposDir(TDirectory* otf, defined_rdf& f, const std::string& cut){
    otf->cd();
    auto t1 = f.Filter(cut);
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


int main(int argc, char** argv){

    std::string input_name;
    input_name = argv[1];
    std::string output_name;
    if(argc == 3){
        output_name = argv[2];
        std::cout << "saving arg name: " << output_name << std::endl;
    } else if(argc != 3){
        std::cout << "must provide input file and output file name.\n";
        std::cout << "nArgs: " << argc << std::endl;
        return -1;
    }

    TFile* otf = new TFile(output_name.c_str(), "RECREATE");

    ROOT::EnableImplicitMT();
    ROOT::RDataFrame rdf = ROOT::RDataFrame("event_tree", input_name.c_str());
    std::cout << "found tree with entries: " << rdf.Count().GetValue() << std::endl;

    // defines and filters here
    auto f = rdf.Define("tile_size", "return asic_th2i.GetSum();")
                .Define("neutEnergy", "return hadTot+lepKE+hadOther;")
                .Define("max_asic_reset", "return asic_th2i.GetMaximum()");

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
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }

    otf->Write();
    otf->Close();

 return 0;
}