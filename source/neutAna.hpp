#include <vector>
#include <string>
#include "ROOT/RDataFrame.hxx"
#include "TDirectory.h"
#include "TH2.h"
#include "TGraphErrors.h"

// encoder for the pixel
int encodePixel(const int& px, const int&py)
{
    int id;
    id = px + 576*py; // px max is 575
    return id;
}

// encoder for the asic, necessarily 4x4 but translational, as well
// int encodePixel(const int& px, const int&py)
// {
//     int id;
//     id = px + 576*py; // px max is 575
//     return id;
// }

// place helper define functions here to send to the RDFs to create new branches
int count_resets(const std::vector<double>& p_resets,
                 const std::vector<int>& px,
                 const std::vector<int>& py)
{
    return p_resets.size();
}

// return the maximum pixel hit here
int max_pixel_resets(const std::vector<double>& p_resets,
                 const std::vector<int>& px,
                 const std::vector<int>& py)
{
    int max=0;
    std::map<int, int> pixel_counts;

    for(int i=0; i<p_resets.size(); ++i){
        int id = encodePixel(px[i], py[i]);
        if(pixel_counts.find(id) != pixel_counts.end()){
            int count = ++pixel_counts[id];
            if(count > max){
                max = count;
            }
        }else{
            pixel_counts[id] = 1;
        }
    }
    return max;
}

// return the maximum asic hit here
TH2I max_asic_resets(const std::vector<double>& p_resets,
                    const std::vector<int>& px,
                    const std::vector<int>& py)
{
    TH2I asicBins = TH2I("", "", 128/4, 300-64, 300+64, 128/4, 800-64, 800+64);

    // build the pixel hit map
    for(int i=0; i<p_resets.size(); ++i){
        asicBins.Fill(px[i], py[i]);
    }

    return asicBins;
}
typedef ROOT::RDF::RInterface<ROOT::Detail::RDF::RJittedFilter,void> filtered_rdf;
void makeGraphs(filtered_rdf& rdf, std::string& cut, TDirectory* td)
{
    td->cd();
    auto f = rdf.Filter(cut);

    auto thTile = f.Histo1D({"hTile", "hTile", 100, 0, 10000}, "tile_size");
    thTile->Draw();
    thTile->Write();

    auto th2En = f.Histo2D({"he", "he", 39, 250, 10000, 40, 0, 4000}, "fsEnergy", "tile_size");
    th2En->Draw("colz");
    th2En->Write();

    auto thPixel = f.Histo1D({"hPixel", "hPixel", 256, 0, 512}, "max_pixel_reset");
    thPixel->Draw();
    thPixel->Write();

    auto nf = f.Define("max_asic_reset", "return asic_th2i.GetMaximum();");
    auto thAsic = nf.Histo1D({"hAsic", "hAsic", 256, 0, 1024}, "max_asic_reset");
    thAsic->Draw();
    thAsic->Write();

    // make a TGraphErrors here
    // int n=0;
    // std::vector<double> px, py, pex, pey;
    // TGraphErrors* tge = new TGraphErrors()
    // TGraphErrors* tge = new TGraphErrors(n, &px[0], &py[0], &pex[0], &pey[0]);
    // tge->Draw("AP");
    // tge->Write();

}