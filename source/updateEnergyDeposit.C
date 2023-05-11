#include <iostream>
#include "TFile.h"
#include "TTree.h"

#include <vector>
#include <string>
#include <map>

#include "ROOT/RDataFrame.hxx"

std::string dir = "/media/argon/NVME2/Kevin/qpix/data/neutrinos_good_eng_cut/backup_sort_data/";
std::string ref_dir = "/home/argon/Projects/Kevin/neutAna/data_rtd/";

// keep track of the members that uniquely identify each ROOT event
struct filter_ob
{
  int ievt;     // ref event
  int ifileNo;  
  Float_t zpos;     // 5 pos
  Float_t theta[3]; // 5 angles
  double energy; // thing we're updating
  // equivalent to selecting ievt / ifileNo
  // int fsEnergy; // 100 energies
};

////////////////////////////////////////
// maps tp keep track
////////////////////////////////////////
std::map<int, std::string> pdg_map = {
  {12,"electron"},
  {-12,"aelectron"},
  {14,"muon"},
  {-14,"amuon"},
};

// total_eng_amuon_nu_fhc_files.root
std::map<std::pair<int,int>, std::string> ref_file_map = {
  {{12,1},"total_eng_electron_nu_fhc_files.root"},
  {{12,0},"total_eng_electron_nu_rhc_files.root"},
  {{-12,1},"total_eng_aelectron_nu_fhc_files.root"},
  {{-12,0},"total_eng_aelectron_nu_rhc_files.root"},
  {{14,1},"total_eng_muon_nu_fhc_files.root"},
  {{14,0},"total_eng_muon_nu_rhc_files.root"},
  {{-14,1},"total_eng_amuon_nu_fhc_files.root"},
  {{-14,0},"total_eng_amuon_nu_rhc_files.root"}
};

// defined in NeutrinoMac.sh in qpixg4 repo
void makeTheta(const int& t, Float_t* arr)
{
  if(t == 1){
    arr[0] = 1;
    arr[1] = 0;
    arr[2] = 0;
    return;
  }
  else if(t == 2){
    arr[0] = 10000;
    arr[1] = 0;
    arr[2] = 349;
    return;
  }
  else if(t == 3){
    arr[0] = 10000;
    arr[1] = 0;
    arr[2] = -349;
    return;
  }
  else if(t == 4){
    arr[0] = 0;
    arr[1] = 0;
    arr[2] = 1;
    return;
  }
  else if(t == 5){
    arr[0] = 0;
    arr[1] = 0;
    arr[2] = -1;
    return;
  }
  // error
  std::cout << "THETA ERROR!\n";
  exit(-1);
}
////////////////////////////////////////

std::string makeFile(bool fhc, int pdg, int evt, int energy, int theta, int zpos)
{
  std::string file;

  // pdg substring
  std::string particle = pdg_map[pdg];

  // fhc substring
  std::string s_fhc, s_fhc2;
  if(fhc){
    s_fhc = "_fhcpdg-";
    s_fhc2 = "_FHC-1";
  } else{
    s_fhc = "_rhcpdg-";
    s_fhc2 = "_FHC-0";
  }

  file = dir + "comb_" + particle + s_fhc + std::to_string(pdg) + "_E-" + std::to_string(energy) + "_evt-" + std::to_string(evt) + s_fhc2 + "_z-" + std::to_string(zpos) + "_seed-420_t-" + std::to_string(theta) + "_sorted.root";

  return file;
}


double getEnergyDeposit(std::string inputFile, int& ievt, int& ifileNo)
{
  auto rdf = ROOT::RDataFrame("event_tree", inputFile);
  double energy = rdf.Sum("hit_energy_deposit").GetValue();
  std::cout << "file: " << inputFile << ", has energy dep: " << energy << std::endl;
  TFile tf = TFile(inputFile.c_str(), "READ");
  TTree* tt = (TTree*)tf.Get("metadata");

  tt->SetBranchAddress("fsEvt", &ievt);
  tt->SetBranchAddress("fsFileNo", &ifileNo);
  tt->GetEntry(0);

  return energy;
}


void updateRefFile(std::string refFile, std::vector<filter_ob> filters)
{
  TFile tf = TFile(refFile.c_str(), "READ");
  TTree* tt = (TTree*)tf.Get("event_tree");
  int entries = tt->GetEntries();

  int fsFileNo, fsEvt;
  Float_t axis_x, axis_y, axis_z, zpos;
  tt->SetBranchAddress("fsFileNo", &fsFileNo);
  tt->SetBranchAddress("fsEvt", &fsEvt);
  tt->SetBranchAddress("axis_x", &axis_x);
  tt->SetBranchAddress("axis_y", &axis_y);
  tt->SetBranchAddress("axis_z", &axis_z);
  tt->SetBranchAddress("zpos", &zpos);

  std::cout << "tt has entires: " << entries << std::endl;
  for(auto filt : filters)
  {
    std::cout << "looking for ievt: " << filt.ievt << std::endl;
    std::cout << "looking for iFileNo: " << filt.ifileNo << std::endl;
    std::cout << "looking for zpos: " << filt.zpos << std::endl;
    for(int i=0; i<entries; ++i){
      // if(i%100 == 0) std::cout << "searching entry: " << i << std::endl;
      tt->GetEntry(i);
      if(zpos == filt.zpos && fsEvt == filt.ievt && fsFileNo == filt.ifileNo && axis_x == filt.theta[0] && axis_z == filt.theta[2]){
        std::cout << "found match at: " << i << std::endl;
        break;
      }
    }
  }
}

int main(int argc, char** argv)
{
  ROOT::EnableImplicitMT();
  std::cout << "running script.\n";
  std::cout << "looking into dir: " << dir << std::endl;

  // particle + pdg loop
  int fhc = 1;
  int pdg = 12;
  std::vector<Float_t> vzpos = {10};
  std::vector<filter_ob> filters;

  // build all of the energies and file entries here
  for(int energy=250; energy<500; energy+= 250){
    for(auto zpos : vzpos){
      for(Float_t theta=1; theta<3; theta+=1){
        for(int evt=0; evt<3; evt+=1){
          std::string file = makeFile(fhc, pdg, evt, energy, theta, zpos);
          int ievt, ifileno;
          double e = getEnergyDeposit(file, ievt, ifileno);
          filter_ob filt;
          filt.ievt = ievt;
          filt.ifileNo = ifileno;
          filt.zpos = zpos*10; // units are changed here!
          filt.energy = e;
          makeTheta(theta, filt.theta);
          filters.push_back(filt);
        }
      }
    }
  }
  // update the reference file here
  // std::cout << "looking for ref_file: " << ref_file_map[{12,1}]<< std::endl;
  std::string refFile = ref_dir + ref_file_map[{pdg,fhc}];
  updateRefFile(refFile, filters);
  return 0;
} 
