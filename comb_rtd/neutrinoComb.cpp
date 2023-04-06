// #include "RXX/RDataFrame.hxx"
#include "TFile.h"

#include <string>
#include <vector>
#include <iostream>

int neutrinoComb(std::string name){

    std::string tile_set = "pixel_x < 300 + 64 && pixel_x > 300 - 64 && pixel_y < 800 + 64 && pixel_y > 800 - 64";
    ROOT::EnableImplicitMT();
    ROOT::RDataFrame rdf = ROOT::RDataFrame("event_tree", name.c_str());
    auto fdf = rdf.Filter("pixel_reset < 1e-1").Filter(tile_set.c_str()).Cache();
    std::cout << "working with counts: " << fdf.Count().GetValue();
    std::string outputTree = "out.root";

    TFile* tf = new TFile(outputTree.c_str(), "RECREATE");
    TTree* tt = new TTree("event_tree", "tt");
    Int_t pdg = 0;
    Float_t energy = 0;
    Int_t event = 0;
    Int_t isFHC = 0;

    Int_t nEvent = 0;
    Float_t fsEnergy = 0;
    Int_t fsFileNo = 0;
    Int_t nFS = 0;
    Float_t lepKE = 0;

    Float_t xpos  = 0; // vertex position
    Float_t ypos  = 0;
    Float_t zpos  = 0;

    Float_t axis_x = 0; // rotation angle branches
    Float_t axis_y = 0;
    Float_t axis_z = 0;

    std::vector<Int_t> pixel_x;
    std::vector<Int_t> pixel_y;
    std::vector<Double_t> pixel_reset;
    tt->Branch("axis_x", &axis_x);
    tt->Branch("axis_y", &axis_y);
    tt->Branch("axis_z", &axis_z);
    tt->Branch("xpos", &xpos);
    tt->Branch("ypos", &ypos);
    tt->Branch("zpos", &zpos);
    tt->Branch("fsFHC", &isFHC);
    tt->Branch("nEvt", &nEvent);
    tt->Branch("fsPdg", &pdg);
    tt->Branch("fsEnergy", &fsEnergy);
    tt->Branch("fsEvt", &event);
    tt->Branch("fsFileNo", &fsFileNo);
    tt->Branch("nFS", &nFS);
    tt->Branch("pixel_x", &pixel_x);
    tt->Branch("pixel_y", &pixel_y);
    tt->Branch("pixel_reset", &pixel_reset);

    // depends on file
    int fhc = 1;
    isFHC = fhc;
    int lepPdg = 12;

    // iters
    std::vector<float> v_zpos = {100, 800, 1800, 2800, 3500};
    std::vector<std::vector<int>> v_axis = {{1,0,0}, {10000,0,349}, {10000, 0, -349}, {0,0,1}, {0,0,-1}};
    std::vector<float> v_energies;
    for(float f=250; f<10000; ) {
        v_energies.push_back(f);
        f += 250;
    }

    // // filter and fill here
    for(float z : v_zpos){

        std::string zf = "zpos == " + std::to_string(z);
        auto z_df = rdf.Filter(zf.c_str());

        std::cout << "filters for: " << zf << std::endl;

        for(auto xyz : v_axis){

            std::string tf = "axis_x == "+ std::to_string(axis_x)+" && axis_y == "+ std::to_string(axis_y)+" && axis_z == "+ std::to_string(axis_z);
            auto t_df = z_df.Filter(tf.c_str());

            for(float en : v_energies){

                std::string ef = "fsEnergy == "+ std::to_string(en);
                auto df = t_df.Filter(ef.c_str());

                pixel_x.clear();
                pixel_y.clear();
                pixel_reset.clear();

                // assign
                xpos  = 1200; // vertex position
                ypos  = 3200;
                zpos  = z;

                axis_x = xyz[0]; // rotation angle branches
                axis_y = xyz[1];
                axis_z = xyz[2];

                fsEnergy = en;

                // takes
                auto px = df.Take<Int_t>("pixel_x");
                auto py = df.Take<Int_t>("pixel_y");
                auto pr = df.Take<Double_t>("pixel_reset");

                for(auto x : px){
                    pixel_x.push_back(x);
                }
                for(auto y : py){
                    pixel_y.push_back(y);
                }
                for(auto r : pr){
                    pixel_reset.push_back(r);
                }

                // take the values and fill
                tt->Fill();

            }
        }
    }

    tf->Write();
    return 1;
}
