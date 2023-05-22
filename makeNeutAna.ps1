# .\build\source\Release\anaNeutrino.exe .\data_rtd\single_electron_nu_fhc_files.root ana_electron_fhc.root


## make the source files
# .\build\source\Release\anaNeutrino.exe .\data_rtd\single_electron_nu_rhc_files.root ana_electron_rhc.root
# .\build\source\Release\anaNeutrino.exe .\data_rtd\single_aelectron_nu_fhc_files.root ana_aelectron_fhc.root
# .\build\source\Release\anaNeutrino.exe .\data_rtd\single_aelectron_nu_rhc_files.root ana_aelectron_rhc.root
# .\build\source\Release\anaNeutrino.exe .\data_rtd\single_muon_nu_fhc_files.root ana_muon_fhc.root
# .\build\source\Release\anaNeutrino.exe .\data_rtd\single_muon_nu_rhc_files.root ./pdfs/ana_muon_rhc.root
# .\build\source\Release\anaNeutrino.exe .\data_rtd\single_amuon_nu_fhc_files.root ana_amuon_fhc.root
# .\build\source\Release\anaNeutrino.exe .\data_rtd\single_amuon_nu_rhc_files.root ana_amuon_rhc.root

## make the graphs
.\build\source\Release\graphsNeutrino.exe .\pdfs\ana_aelectron_fhc.root .\pdfs\ana_aelectron_fhc_graphs.root
.\build\source\Release\graphsNeutrino.exe .\pdfs\ana_aelectron_rhc.root .\pdfs\ana_aelectron_rhc_graphs.root
.\build\source\Release\graphsNeutrino.exe .\pdfs\ana_muon_fhc.root .\pdfs\ana_muon_fhc_graphs.root
.\build\source\Release\graphsNeutrino.exe .\pdfs\ana_muon_rhc.root .\pdfs\ana_muon_rhc_graphs.root
.\build\source\Release\graphsNeutrino.exe .\pdfs\ana_amuon_fhc.root .\pdfs\ana_amuon_fhc_graphs.root
.\build\source\Release\graphsNeutrino.exe .\pdfs\ana_amuon_rhc.root .\pdfs\ana_amuon_rhc_graphs.root
.\build\source\Release\graphsNeutrino.exe .\pdfs\ana_electron_fhc.root .\pdfs\ana_electron_fhc_graphs.root
.\build\source\Release\graphsNeutrino.exe .\pdfs\ana_electron_rhc.root .\pdfs\ana_electron_rhc_graphs.root