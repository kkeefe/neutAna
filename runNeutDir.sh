#!/bin/bash

echo 'ni hao making the graphics from the raw data'

make_neutrino () {
  ./build/source/filtNeutrino "./comb_rtd/""$1" $2 $3;
  mv ./out.root "./filt_rtd/""$1";
  ./build/source/combNeutrinoRam "./filt_rtd/""$1" $2 $3;
  mv ./out_comb.root "./data_rtd/""$1";
  ./build/source/anaNeutrino "./data_rtd/""$1";
  mv ./pdfs/graphs.root ./pdfs/"graphs_pdg""$2""_fhc-""$3"".root"
  mv ./saveRdf.root ./pdfs/"th2_pdg""$2""_fhc-""$3"".root"
}

# create the data_rtd for the full neutrino comb data file
make_neutrino_full () {
  ./build/source/combNeutrinoRam "./comb_rtd/""$1" $2 $3;
  mv ./out_comb.root "./data_rtd/total_""$1";
  ./build/source/anaNeutrino "./data_rtd/total_""$1" "./pdfs/full_graphs.root";
  mv ./pdfs/full_graphs.root ./pdfs/"full_graphs_pdg""$2""_fhc-""$3"".root"
  mv ./saveRdf.root ./pdfs/"full_th2_pdg""$2""_fhc-""$3"".root"
}

# make the filtered neutrino files
# make_neutrino aelectron_nu_fhc_files.root -12 1;
# make_neutrino aelectron_nu_rhc_files.root -12 rhc;
# make_neutrino amuon_nu_fhc_files.root -14 1;
# make_neutrino amuon_nu_rhc_files.root -14 rhc;
# make_neutrino electron_nu_fhc_files.root 12 1;
# make_neutrino electron_nu_rhc_files.root 12 rhc;
# make_neutrino muon_nu_fhc_files.root 14 1;
# make_neutrino muon_nu_rhc_files.root 14 rhc;

# make the full neutrino files
make_neutrino_full aelectron_nu_rhc_files.root -12 rhc;
make_neutrino_full amuon_nu_fhc_files.root -14 1;
make_neutrino_full amuon_nu_rhc_files.root -14 rhc;
make_neutrino_full electron_nu_fhc_files.root 12 1;
make_neutrino_full electron_nu_rhc_files.root 12 rhc;
make_neutrino_full muon_nu_fhc_files.root 14 1;
make_neutrino_full muon_nu_rhc_files.root 14 rhc;
make_neutrino_full aelectron_nu_fhc_files.root -12 1;
