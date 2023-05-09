#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"

#include <iostream>

int main(int argc, char** argv)
{
    std::string input_file, ref_file;
    if(argc != 3){
        std::cout << "must supply only input th2 file and neutrino source file.\n";
        return -1;
    }

    input_file = argv[1];
    ref_file = argv[2];

    Float_t hadTot_ref = 0;
    Float_t hadPip_ref = 0;
    Float_t hadPim_ref = 0;
    Float_t hadPi0_ref = 0;
    Float_t hadP_ref = 0;
    Float_t hadN_ref = 0;
    Float_t hadOther_ref = 0;

    Int_t ievt_ref = 0;
    Int_t ifileNo_ref = 0;

    TFile ref_tf(ref_file.c_str(), "READ");
    TTree* ref_tt = (TTree*)ref_tf.Get("tree");
    ref_tt->SetBranchAddress("hadTot", &hadTot_ref);
    ref_tt->SetBranchAddress("hadPip", &hadPip_ref);
    ref_tt->SetBranchAddress("hadPim", &hadPim_ref);
    ref_tt->SetBranchAddress("hadPi0", &hadPi0_ref);
    ref_tt->SetBranchAddress("hadP", &hadP_ref);
    ref_tt->SetBranchAddress("hadN", &hadN_ref);
    ref_tt->SetBranchAddress("hadOther", &hadOther_ref);
    ref_tt->SetBranchAddress("ievt", &ievt_ref);
    ref_tt->SetBranchAddress("ifileNo", &ifileNo_ref);

    std::cout << "set branches for reference file\n";

    Float_t hadTot_up = 0;
    Float_t hadPip_up = 0;
    Float_t hadPim_up = 0;
    Float_t hadPi0_up = 0;
    Float_t hadP_up = 0;
    Float_t hadN_up = 0;
    Float_t hadOther_up = 0;

    Int_t ievt_up = 0;
    Int_t ifileno_up = 0;

    TFile had_tf(input_file.c_str(), "UPDATE");
    if(had_tf.IsZombie()){
        std::cout << "unable to read the input file.\n";
        return -1;
    }
    TTree* had_tt = (TTree*)had_tf.Get("event_tree");
    had_tt->SetBranchAddress("fsEvt", &ievt_up);
    had_tt->SetBranchAddress("fsFileNo", &ifileno_up);

    TBranch* tot_tb = had_tt->Branch("newHadTot", &hadTot_up);
    TBranch* pip_tb = had_tt->Branch("newHadPip", &hadPip_up);
    TBranch* pim_tb = had_tt->Branch("newHadPim", &hadPim_up);
    TBranch* pi0_tb = had_tt->Branch("newHadPi0", &hadPi0_up);
    TBranch* p_tb = had_tt->Branch("newHadP", &hadP_up);
    TBranch* n_tb = had_tt->Branch("newHadN", &hadN_up);
    TBranch* other_tb = had_tt->Branch("newHadOther", &hadOther_up);

    int entries_found = 0;
    for(int i=0; i<had_tt->GetEntries(); ++i){
        had_tt->GetEntry(i);
        bool found_evt = false;
        int nu_evt = 0;
        while(!found_evt){
            ref_tt->GetEntry(nu_evt);
            if(ievt_ref == ievt_up && ifileno_up == ifileNo_ref)
            {
                if(++entries_found%1000==0)
                    std::cout << "found new entry: " << entries_found << std::endl;
                hadTot_up = hadTot_ref;
                hadPip_up = hadPip_ref;
                hadPim_up = hadPim_ref;
                hadPi0_up = hadPi0_ref;
                hadP_up = hadP_ref;
                hadN_up = hadN_ref;
                hadOther_up = hadOther_ref;
                tot_tb->Fill();
                pip_tb->Fill();
                pim_tb->Fill();
                pi0_tb->Fill();
                p_tb->Fill();
                n_tb->Fill();
                other_tb->Fill();
                found_evt = true;
            }
            ++nu_evt;
            if(nu_evt > ref_tt->GetEntries())
            {
                std::cout << "ERROR: unable to find reference neutrino event.\n";
                return -1;
            }
        }
    }
    had_tt->Write();

    return 0;
}