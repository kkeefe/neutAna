#!/bin/bash

echo 'ni hao'

make_neutrino () {
  ./build/source/filtNeutino "./comb_rtd/""$1" $2 $3;
  mv ./out.root "./filt_rtd/""$1";
  ./build/source/combNeutrinoRam "./filt_rtd/""$1" $2 $3;
  mv ./out_comb.root "./data_rtd/""$1";
  ./build/source/anaNeutrino "./data_rtd/""$1";
  mv ./pdfs/graphs.root ./pdfs/"graphs_pdg""$2""_fhc-""$3"".root"
}

make_neutrino aelectron_nu_fhc_files.root -12 1;
make_neutrino aelectron_nu_rhc_files.root -12 0;
make_neutrino amuon_nu_fhc_files.root -14 1;
make_neutrino amuon_nu_rhc_files.root -14 0;
make_neutrino electron_nu_fhc_files.root 12 1;
make_neutrino electron_nu_rhc_files.root 12 0;
make_neutrino muon_nu_fhc_files.root 14 1;
make_neutrino muon_nu_rhc_files.root 14 0;
