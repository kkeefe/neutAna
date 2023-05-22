void makeResetVsE(){
    ROOT::EnableImplicitMT();
    auto rdf = ROOT::RDataFrame("event_tree", "single_electron_nu_fhc_files.root");
    std::cout << rdf.Count().GetValue();
    auto f = rdf.Define("hits", "return pixel_reset.size();");
    std::cout << "made the defin.. now saving..\n";
    f.Snapshot("event_tree", "single_electron_fhc_hits.root");
}