// #include "RXX/RDataFrame.hxx"
#include "TFile.h"
#include "ROOT/RDataFrame.hxx"
#include "TTree.h"

#include <string>
#include <vector>
#include <iostream>

#include "neutAna.hpp"

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
    // std::vector<std::string> colNames = {"axis_x", "axis_y", "axis_z",
    //                                      "xpos", "ypos", "zpos",
    //                                      "fsFHC", "nEvt", "lepKE",
    //                                      "fsPdg", "fsEnergy", "fsEvt",
    //                                      "fsFileNo", "nFS", "pixel_x",
    //                                      "pixel_y", "pixel_reset"};

    // std::string tile_set = "pixel_x < " + std::to_string(XMAX) + " && pixel_x >= "+ std::to_string(XMIN) + " && "
    //                        "pixel_y < " + std::to_string(YMAX) + " && pixel_y >= "+ std::to_string(YMIN);
    ROOT::EnableImplicitMT();
    ROOT::RDataFrame rdf = ROOT::RDataFrame("event_tree", name.c_str());
    auto fdf = rdf.Filter("pixel_reset < 1e-1");
    std::string outputTree = "out.root";
    std::cout << "saving snapshot!\n";
    fdf.Snapshot("event_tree", outputTree.c_str());

    // notes about how this performs comparatively on different timestamp cuts
    // auto time_df = rdf.Filter("pixel_reset < 2e-2");
    // auto tile_df = rdf.Filter(tile_set.c_str());
    // auto both_df = tile_df.Filter("pixel_reset < 2e-2");
    // float max = rdf.Count().GetValue() ;
    // float time_cnt = time_df.Count().GetValue();
    // float tile_cnt = tile_df.Count().GetValue();
    // float both_cnt = both_df.Count().GetValue();
    // std::cout << "filtering for none leaves: " << max << std::endl;
    // std::cout << "filtering for time leaves: " <<  time_cnt << ", " << time_cnt / max  << std::endl;
    // std::cout << "filtering for tile leaves: " <<  tile_cnt << ", " << tile_cnt / max  << std::endl;
    // std::cout << "filtering for both leaves: " <<  both_cnt << ", " << both_cnt / max  << std::endl;
    // 100 ms cut
    // filtering for none leaves: 9.95972e+08
    // filtering for time leaves: 5.26862e+08, 0.528993
    // filtering for tile leaves: 3.03296e+08, 0.304522
    // filtering for both leaves: 1.93029e+08, 0.193809
    // 20 ms cut
    // filtering for time leaves: 5.26859e+08, 0.528989
    // filtering for tile leaves: 3.03296e+08, 0.304522 // same
    // filtering for both leaves: 1.93027e+08, 0.193808
    // 500 ms cut .003% more resets than 20ms cut
    // filtering for time leaves: 5.26874e+08, 0.529004
    // filtering for tile leaves: 3.03296e+08, 0.304522
    // filtering for both leaves: 1.93033e+08, 0.193814
    // std::string outputTree = "out.root";
    // std::cout << "saving snapshot!\n";
    // fdf.Snapshot("event_tree", outputTree.c_str());

    return 0;
}
