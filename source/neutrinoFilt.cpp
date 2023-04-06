// #include "RXX/RDataFrame.hxx"
#include "TFile.h"
#include "ROOT/RDataFrame.hxx"
#include "TTree.h"

#include <string>
#include <vector>
#include <iostream>

int main(int argc, char** argv){

    if(argc != 4){
        std::cout << "must provide input file, lepPdg, and FHC as params.\n";
        std::cout << "nArgs: " << argc << std::endl;
        return -1;
    }

    std::string name = argv[1];
    std::string s_rhc = argv[3];

    // from file type
    Int_t lepPdg = std::stoi(argv[2]);
    if(!(lepPdg == 12 || lepPdg == 14 || lepPdg == -12 || lepPdg == -14)){
        std::cout << "error, lepPdg not an acceptable value: " << lepPdg << std::endl;
        return -1;
    }

    Int_t isFHC = 0;
    if(s_rhc == "rhc"){
        isFHC = 0;
    }else{
        isFHC = 1;
    }

    std::cout << "read FHC: " << isFHC << std::endl;
    std::cout << "read pdg: " << lepPdg << std::endl;

    // use colNames to avoid loading in pixel_reset_truth and pixel_reset_track_id for these filters
    // as the buffer analysis largely doesn't care about the source of the electrons
    std::vector<std::string> colNames = {"axis_x", "axis_y", "axis_z",
                                         "xpos", "ypos", "zpos",
                                         "fsFHC", "nEvt", "lepKE",
                                         "fsPdg", "fsEnergy", "fsEvt",
                                         "fsFileNo", "nFS", "pixel_x",
                                         "pixel_y", "pixel_reset"};

    std::string tile_set = "pixel_x < 300 + 64 && pixel_x > 300 - 64 && pixel_y < 800 + 64 && pixel_y > 800 - 64";
    ROOT::EnableImplicitMT();
    ROOT::RDataFrame rdf = ROOT::RDataFrame("event_tree", name.c_str(), colNames);
    auto fdf = rdf.Filter("pixel_reset < 1e-1").Filter(tile_set.c_str());
    std::string outputTree = "out.root";
    std::cout << "saving snapshot!\n";
    fdf.Snapshot("event_tree", outputTree.c_str());

    return 0;
}
