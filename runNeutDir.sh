#!/bin/bash

echo 'ni hao making the graphics from the raw data'

make_neutrino () {
  ./build/source/filtNeutrino "./comb_rtd/""$1" $2 $3;
  mv ./out.root "./filt_rtd/""$1";
  ./build/source/combNeutrinoRam "./filt_rtd/""$1" $2 $3;
  mv ./out_comb.root "./data_rtd/""$1";
  ./build/source/anaNeutrino "./data_rtd/""$1" "./pdfs/graphs.root";
  mv ./pdfs/graphs.root ./pdfs/"graphs_pdg""$2""_fhc-""$3"".root"
  mv ./saveRdf.root ./pdfs/"th2_pdg""$2""_fhc-""$3"".root"
}

# all (5/8/23) current RTD data needs at least a time filter
# create the data_rtd for the full neutrino comb data file
make_neutrino_full () {
  ./build/source/filtNeutrino "/comb_rtd/""$1" $2 $3;
  mv ./out.root "./filt_rtd/""$1";
  ./build/source/combNeutrinoRam "./comb_rtd/""$1" $2 $3;
  mv ./out_comb.root "./data_rtd/total_""$1";
  ./build/source/anaNeutrino "./data_rtd/total_""$1" "./pdfs/full_graphs.root";
  # skip making graphics right now
  # mv ./pdfs/full_graphs.root ./pdfs/"full_graphs_pdg""$2""_fhc-""$3"".root"
  mv ./saveRdf.root ./pdfs/"full_th2_pdg""$2""_fhc-""$3"".root"
}

# make the filtered neutrino files
# make_neutrino eng_aelectron_nu_fhc_files.root -12 1;
# make_neutrino eng_aelectron_nu_rhc_files.root -12 rhc;
# make_neutrino eng_amuon_nu_fhc_files.root -14 1;
# make_neutrino eng_amuon_nu_rhc_files.root -14 rhc;
# make_neutrino eng_electron_nu_fhc_files.root 12 1;
# make_neutrino eng_electron_nu_rhc_files.root 12 rhc;
# make_neutrino eng_muon_nu_fhc_files.root 14 1;
# make_neutrino eng_muon_nu_rhc_files.root 14 rhc;

# make the full neutrino files
make_neutrino_full simple_electron_nu_fhc_files.root 12 1;
make_neutrino_full simple_electron_nu_rhc_files.root 12 rhc;

# make_neutrino_full eng_aelectron_nu_fhc_files.root -12 1;
# make_neutrino_full eng_aelectron_nu_rhc_files.root -12 rhc;
# make_neutrino_full eng_amuon_nu_fhc_files.root -14 1;
# make_neutrino_full eng_amuon_nu_rhc_files.root -14 rhc;
# make_neutrino_full eng_electron_nu_fhc_files.root 12 1;
# make_neutrino_full eng_electron_nu_rhc_files.root 12 rhc;
# make_neutrino_full eng_muon_nu_fhc_files.root 14 1;
# make_neutrino_full eng_muon_nu_rhc_files.root 14 rhc;

# ./build/source/fixHadNeut ./pdfs/full_th2_pdg12_fhc-1.root ./neut_src_data/comb_electron_fhc.root 
# ./build/source/fixHadNeut ./pdfs/full_th2_pdg-12_fhc-1.root ./neut_src_data/comb_aelectron_fhc.root 
# ./build/source/fixHadNeut ./pdfs/full_th2_pdg14_fhc-1.root ./neut_src_data/comb_muon_fhc.root 
# ./build/source/fixHadNeut ./pdfs/full_th2_pdg-14_fhc-1.root ./neut_src_data/comb_amuon_fhc.root 
# ./build/source/fixHadNeut ./pdfs/full_th2_pdg12_fhc-rhc.root ./neut_src_data/comb_electron_rhc.root 
# ./build/source/fixHadNeut ./pdfs/full_th2_pdg-12_fhc-rhc.root ./neut_src_data/comb_aelectron_rhc.root 
# ./build/source/fixHadNeut ./pdfs/full_th2_pdg14_fhc-rhc.root ./neut_src_data/comb_muon_rhc.root 
# ./build/source/fixHadNeut ./pdfs/full_th2_pdg-14_fhc-rhc.root ./neut_src_data/comb_amuon_rhc.root 
