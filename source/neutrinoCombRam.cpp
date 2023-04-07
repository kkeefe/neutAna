// #include "RXX/RDataFrame.hxx"
#include "TFile.h"
#include "ROOT/RDataFrame.hxx"
#include "TTree.h"

#include <string>
#include <vector>
#include <iostream>

#include <unordered_map>

int encodeT(const int& axis_x, const int& axis_z) //
{
    if(axis_x == 1 && axis_z == 0)
        return 1;
    else if (axis_x == 10000 && axis_z == 349)
        return 2;
    else if (axis_x == 10000 && axis_z == -349)
        return 3;
    else if (axis_x == 0 && axis_z == 1)
        return 4;
    else if (axis_x == 0 && axis_z == -1)
        return 5;
    else
        return -10;
}

int encodeZ(const int& pos_z) //
{
    switch (pos_z)
    {
    case 100:
        return 1;
    case 800:
        return 2;
    case 1800:
        return 3;
    case 2800:
        return 4;
    case 3500:
        return 5;
    default:
        return -1;
        break;
    }
}

// 100 events, for each energy, at 5 positions, for 5 angles
// try reading in all of the event selection criteria here
int encode(const float_t& fsEnergy, const int& evt,
           const int& axis_x, const int& axis_z, const int& zpos)
{
    int i_en = fsEnergy; // 250 increments // max is 10000
    int i_evt = evt; // 100 increments
    int i_t = encodeT(axis_x, axis_z); // 5 increments
    int i_z = encodeZ(zpos); // 5 increments

    int id = i_en + i_evt + 100000*(i_t) + 1000000*(i_z);
    return id;
}

struct neutrinoEvent{
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
};

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

    TFile* tf = new TFile(name.c_str(), "READ");
    TTree* tt = (TTree*)tf->Get("event_tree");

    Int_t pdg = -42;
    Float_t energy = -42;
    Int_t event = -42;

    Int_t nEvent = -42;
    Float_t fsEnergy = -42;
    Int_t fsFileNo = -42;
    Int_t nFS = -42;
    Float_t lepKE = -42;

    Float_t xpos  = -42; // vertex position
    Float_t ypos  = -42;
    Float_t zpos  = -42;

    Float_t axis_x = -42; // rotation angle branches
    Float_t axis_y = -42;
    Float_t axis_z = -42;

    Int_t pixel_x;
    Int_t pixel_y;
    Double_t pixel_reset;
    tt->SetBranchAddress("axis_x", &axis_x);
    tt->SetBranchAddress("axis_y", &axis_y);
    tt->SetBranchAddress("axis_z", &axis_z);
    tt->SetBranchAddress("xpos", &xpos);
    tt->SetBranchAddress("ypos", &ypos);
    tt->SetBranchAddress("zpos", &zpos);
    tt->SetBranchAddress("fsFHC", &isFHC);
    // takes
    tt->SetBranchAddress("nEvt", &nEvent);
    tt->SetBranchAddress("fsPdg", &pdg);
    tt->SetBranchAddress("fsEnergy", &fsEnergy); // cut energy
    tt->SetBranchAddress("fsEvt", &event);
    tt->SetBranchAddress("fsFileNo", &fsFileNo);
    tt->SetBranchAddress("nFS", &nFS);
    tt->SetBranchAddress("lepKE", &lepKE);
    // vector takes
    tt->SetBranchAddress("pixel_x", &pixel_x);
    tt->SetBranchAddress("pixel_y", &pixel_y);
    tt->SetBranchAddress("pixel_reset", &pixel_reset);

    // pre-fill the map
    const std::vector<float> v_zpos = {100, 800, 1800, 2800, 3500};
    std::vector<std::vector<int>> v_axis = {{1,0,0}, {10000,0,349}, {10000, 0, -349}, {0,0,1}, {0,0,-1}};
    std::unordered_map<int, neutrinoEvent> mNeut;
    for(int i_en=250; i_en<10000; ){
        for(int i_evt=0; i_evt<100; i_evt++){
            for(const auto i_zpos : v_zpos){
                for(const auto i_th : v_axis){
                    int id = encode(i_en, i_evt, i_th[0], i_th[2], i_zpos);
                    mNeut[id] = neutrinoEvent();
                    mNeut[id].xpos  = 1200; // vertex position
                    mNeut[id].ypos  = 3200;
                    mNeut[id].zpos  = i_zpos;

                    mNeut[id].axis_x = i_th[0]; // rotation angle branches
                    mNeut[id].axis_y = i_th[1];
                    mNeut[id].axis_z = i_th[2];
                    mNeut[id].fsEnergy = i_en;
                    mNeut[id].event = i_evt;
                }
            }
        }
        i_en += 250;
    }
    std::cout << "built the storage map with size: " << mNeut.size() << "..\n";

    // fill map here
    std::cout << "building the map from entries: " << tt->GetEntries() << "..\n";
    for(int i=0; i<tt->GetEntries(); ++i){
        tt->GetEntry(i);
        const int id = encode(fsEnergy, nEvent, axis_x, axis_z, zpos);
        try
        {
            // update vals
            mNeut.at(id).nEvent = nEvent;
            mNeut.at(id).pdg = pdg;
            mNeut.at(id).nFS = nFS;
            mNeut.at(id).fsFileNo = fsFileNo;
            mNeut.at(id).event = event;
            mNeut.at(id).lepKE = lepKE;
            mNeut.at(id).isFHC = isFHC;
            mNeut.at(id).fsEnergy = fsEnergy;

            // update vectors
            mNeut.at(id).pixel_reset.push_back(pixel_reset);
            mNeut.at(id).pixel_x.push_back(pixel_x);
            mNeut.at(id).pixel_y.push_back(pixel_y);
            if(i%10000000 == 0) std::cout << "read entry: " << i << std::endl;
        }
        catch(const std::exception& e)
        {
            std::cerr << e.what() << '\n';
            std::cout << id << ", " << fsEnergy << ", " << nEvent << ", " << axis_x << ", " << axis_z << ", " << zpos << '\n';
            std::cout << id << ", " << fsEnergy << ", " << nEvent << ", " << encodeT(axis_x, axis_z) << ", " << encodeZ(zpos) << '\n';
            return -1;
        }
    }
    tf->Close();

    Int_t pdg_ = 0;
    Float_t energy_ = 0;
    Int_t event_ = 0;

    Int_t nEvent_ = 0;
    Float_t fsEnergy_ = 0;
    Int_t fsFileNo_ = 0;
    Int_t nFS_ = 0;
    Float_t lepKE_ = 0;

    Float_t xpos_  = 0; // vertex position
    Float_t ypos_  = 0;
    Float_t zpos_  = 0;

    Float_t axis_x_ = 0; // rotation angle branches
    Float_t axis_y_ = 0;
    Float_t axis_z_ = 0;
    // read through map, create new output file
    std::vector<Int_t> v_pixel_x_;
    std::vector<Int_t> v_pixel_y_;
    std::vector<Double_t> v_pixel_reset_;
    std::string outputTree = "out.root";
    TFile* ntf = new TFile(outputTree.c_str(), "RECREATE");
    TTree* ntt = new TTree("event_tree", "tt");
    ntt->Branch("axis_x", &axis_x_);
    ntt->Branch("axis_y", &axis_y_);
    ntt->Branch("axis_z", &axis_z_);
    ntt->Branch("xpos", &xpos_);
    ntt->Branch("ypos", &ypos_);
    ntt->Branch("zpos", &zpos_);
    ntt->Branch("fsFHC", &isFHC);
    
    ntt->Branch("nEvt", &nEvent_);
    ntt->Branch("fsPdg", &pdg_); // is the lepPdg
    ntt->Branch("fsEnergy", &fsEnergy_); // cut energy
    ntt->Branch("fsEvt", &event_);
    ntt->Branch("fsFileNo", &fsFileNo_);
    ntt->Branch("nFS", &nFS_);
    ntt->Branch("lepKE", &lepKE_);
    
    ntt->Branch("pixel_x", &v_pixel_x_);
    ntt->Branch("pixel_y", &v_pixel_y_);
    ntt->Branch("pixel_reset", &v_pixel_reset_);

    std::cout << "map complete creating new output file..\n";
    int i=0;
    int cnt = mNeut.size();
    for(auto& [k, neutEvt]: mNeut){
        axis_x_ = neutEvt.axis_x;
        axis_y_ = neutEvt.axis_y;
        axis_z_ = neutEvt.axis_z;
        xpos_ = neutEvt.xpos;
        ypos_ = neutEvt.ypos;
        zpos_ = neutEvt.zpos;
        isFHC = neutEvt.isFHC;
        nEvent_ = neutEvt.nEvent;
        pdg_ = neutEvt.pdg;
        fsEnergy_ = neutEvt.fsEnergy; // cut energ.fsEnergy;
        event_ = neutEvt.event;
        fsFileNo_ = neutEvt.fsFileNo;
        nFS_ = neutEvt.nFS;
        lepKE_ = neutEvt.lepKE;
        v_pixel_x_ = neutEvt.pixel_x;
        v_pixel_y_ = neutEvt.pixel_y;
        v_pixel_reset_ = neutEvt.pixel_reset;

        ntt->Fill();
        if(++i%5000==0)std::cout << "filling hit: " << i << ", out of: " << cnt << std::endl;
    }
    ntf->Write();
    ntf->Close();
    return 1;
}