#include "neutAna.hpp"
#include <iostream>

int main(int argc, char** argv){

    std::string input_name;
    std::string output_name;
    if(argc == 3){
        output_name = argv[2];
        std::cout << "saving arg name: " << output_name << std::endl;
    } else if(argc != 3){
        std::cout << "must provide input file and output file name.\n";
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

    // defines and filters here
    auto f = rdf.Define("tile_size", count_resets, {"pixel_reset", "pixel_x", "pixel_y"})
                // .Define("all_pixel_reset", all_pixel_resets, {"pixel_reset", "pixel_x", "pixel_y"})
                // .Define("max_pixel_reset", max_pixel_resets, {"all_pixel_reset"})
                .Define("asic_th2i", max_asic_resets, {"pixel_reset", "pixel_x", "pixel_y"});

    int sum = f.Sum("tile_size").GetValue();
    double mean = f.Mean("tile_size").GetValue();
    double Max = f.Max("tile_size").GetValue();
    double Min = f.Min("tile_size").GetValue();
    std::cout << "Found total tile hits: " << sum << std::endl;
    std::cout << "Found mean tile hits: " << mean << std::endl;
    std::cout << "Found max tile hits: " << Max << std::endl;
    std::cout << "Found min tile hits: " << Min << std::endl;

    // save an output and also save outputs that the python simulation can run
    std::cout << "Saving output event hists.\n";
    std::vector<std::string> cols = {"tile_size", "asic_th2i", "lepKE", "fsFHC", "fsFileNo",
                                    "fsEnergy", "nFS", "fsEvt", "fsPdg", "nEvt", "xpos", "ypos", "zpos", "axis_x", "axis_y", "axis_z",
                                    "hadTot", "hadPip", "hadPim", "hadPi0", "hadP", "hadN", "hadOther", "energy_deposit"};
    try{
        f.Snapshot("event_tree", output_name.c_str(), cols);
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }

    std::cout << "saving complete.\n";

    return 0;

}
