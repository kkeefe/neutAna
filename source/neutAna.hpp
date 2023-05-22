#include <vector>
#include <string>
#include "ROOT/RDataFrame.hxx"
#include "TDirectory.h"
#include "TH2.h"

#include <algorithm>

#define TILE_WIDTH 64;
// const int YMIN = 800 - TILE_WIDTH;
// const int YMAX = 800 + TILE_WIDTH;
// const int XMIN = 300 - TILE_WIDTH;
// const int XMAX = 300 + TILE_WIDTH;

// if using the entire APA range, use these constants
// #define TILE_WIDTH 64;
const int YMIN = 1;
const int YMAX = 1500;
const int XMIN = 1;
const int XMAX = 575;

// encoder for the pixel
int encodePixel(const int& px, const int&py)
{
    int id;
    id = px + 576*py; // px max is 575
    return id;
}

void decodePixel(const int& id, int& px, int& py)
{
    py = id/576;
    px = id%576;    
}

// place helper define functions here to send to the RDFs to create new branches
int count_resets(const std::vector<double>& p_resets,
                 const std::vector<int>& px,
                 const std::vector<int>& py)
{
    return p_resets.size();
}

// return the maximum pixel hit here
int max_pixel_resets(std::vector<int>& m_resets)
{
    int max=0;

    for(auto reset : m_resets)
        if(reset > max)
            max = reset;

    return max;
}

// return a vector which show the sizes of the pixels hit
std::vector<int> all_pixel_resets(const std::vector<double>& p_resets,
                                  const std::vector<int>& px,
                                  const std::vector<int>& py)
{
    std::map<int, int> pixel_counts;
    for(int ix=XMIN; ix<XMAX; ix++) // count all of the zeros too
        for(int iy=YMIN; iy<YMAX; iy++){
            pixel_counts[encodePixel(ix, iy)] = 0;
        }

    for(int i=0; i<p_resets.size(); ++i){
        int id = encodePixel(px[i], py[i]);
        if(pixel_counts.find(id) != pixel_counts.end()){
            int count = ++pixel_counts[id];
        }else{
            pixel_counts[id] = 1;
        }
    }
    std::vector<int> resets;
    for(auto& [id, count] : pixel_counts){
        resets.push_back(count);
    }
    return resets;
}

std::vector<double> max_pixel_rtds(const std::vector<double>& p_resets,
                                   const std::vector<int>& px,
                                   const std::vector<int>& py)
{
    std::map<int, int> pixel_counts;

    for(int i=0; i<p_resets.size(); ++i){
        int id = encodePixel(px[i], py[i]);
        if(pixel_counts.find(id) != pixel_counts.end()){
            int count = ++pixel_counts[id];
        }else{
            pixel_counts[id] = 1;
        }
    }
    int bestId = 0; int resetCnt = 0;
    for(auto& [id, resets] : pixel_counts){
        if(resets > resetCnt){
            bestId = id;
            resetCnt = resets;
        }
    }

    int idX, idY;
    decodePixel(bestId, idX, idY);

    // build the vector of interest and ensure it's sorted
    std::vector<double> resets;
    for(int i=0; i<p_resets.size(); ++i){
        if(px[i] == idX && py[i] == idY){
            resets.push_back(p_resets[i]);
        }
    }
    std::sort(resets.begin(), resets.end());

    std::vector<double> max_rtds;
    double curT = resets[0];
    for(int i=1; i<resets.size(); ++i){
        double rtd = resets[i] - curT;
        max_rtds.push_back(rtd);
        curT = resets[i];
    }

    return max_rtds;
}

// define the ASIC weight based on the energy deposit or the 
double make_weight(const double& energy_range)
{
    double weight;
    // values read off of the TDR
    // ve apperance
    // 14.8, // 500
    // 25,   // 750
    // 26,   // 1G
    // 35,   // 1.25G
    // 57,   // 1.5G
    // 89,   // 1.75
    // 110,  // 2
    // 130,  // 2.25
    // 135,  // 2.5
    // 133,  // 2.75
    // 123,  // 3
    // 111,  // 3.25
    // 92,  // 3.5
    // 73,  // 3.75
    // 58,  // 4
    // 42,  // 4.25
    // 30,  // 4.5
    // 22,  // 4.75
    // 17,  // 5
    // 15,  // 5.25
    // 12, // 5.5
    // 10.5, // 5.75
    // 10, // 6
    // 7.5, // 6.25
    // 7.25, // 6.5
    // 6.5, // 6.75
    // 6.4 // 7
    // 6.0, // 7.25
    // 6.0, // 7.5
    // 6.0, // 7.75
    // otherwise 0 for neutrino oscillation


    return weight;
}

// return the maximum asic hit here
TH2I max_asic_resets(const std::vector<double>& p_resets,
                     const std::vector<int>& px,
                     const std::vector<int>& py)
{
    TH2I asicBins = TH2I("", "", 144, 0.5, 0.5+144*4, 375, 0.5, 1500.5);

    // build the pixel hit map
    for(int i=0; i<p_resets.size(); ++i){
        asicBins.Fill(px[i], py[i]);
    }

    return asicBins;
}
// typedef ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager> cached_rdf;
// typedef ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager filtered_rdf;
typedef ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager> defined_rdf;
typedef ROOT::RDF::RInterface<ROOT::Detail::RDF::RJittedFilter,void> filtered_rdf;
void makeGraphs(filtered_rdf& rdf, const std::string& cut, TDirectory* td)
{
    td->cd();
    auto f = rdf.Filter(cut);

    std::cout << "creating graphics in dir: " << td->GetName() << ".. ";

    auto thTile = f.Histo1D({"hTile", "hTile", 200, 0, 10000}, "tile_size");
    thTile->Draw();
    thTile->Write();

    auto th2En = f.Histo2D({"he", "he", 39, 250, 10000, 40, 0, 4000}, "fsEnergy", "tile_size");
    th2En->Draw("colz");
    th2En->Write();

    // auto thPixel = f.Histo1D({"hPixel", "hPixel", 512, 0, 1024}, "max_pixel_reset");
    // thPixel->Draw();
    // thPixel->Write();

    // auto thPixelRTD = f.Histo1D({"hPixelRTD", "hPixelRTD", 512, 0, 10e-6}, "max_pixel_rtd");
    // thPixelRTD->Draw();
    // thPixelRTD->Write();

    // auto thPixelRTDns = f.Histo1D({"hPixelRTDns", "hPixelRTDns", 512, 0, 100e-9}, "max_pixel_rtd");
    // thPixelRTDns->Draw();
    // thPixelRTDns->Write();

    auto thAsic = f.Histo1D({"hAsic", "hAsic", 512, 0, 2048}, "max_asic_reset");
    thAsic->Draw();
    thAsic->Write();

    // TGraph tgPixel = *f.Graph("tile_size", "max_pixel_reset");
    // tgPixel.Sort();
    // tgPixel.Draw();
    // tgPixel.SetName("tgMaxPixel");
    // tgPixel.SetTitle("tgMaxPixel");
    // tgPixel.Write();

    TGraph tgAsic = *f.Graph("tile_size", "max_asic_reset");
    tgAsic.Sort();
    tgAsic.Draw();
    tgAsic.SetName("tgMaxAsic");
    tgAsic.SetTitle("tgMaxAsic");
    tgAsic.Write();

    TGraph tgLepKEAsic = *f.Graph("neutEnergy", "max_asic_reset");
    tgLepKEAsic.Sort();
    tgLepKEAsic.Draw();
    tgLepKEAsic.SetName("tgLepKEAsic");
    tgLepKEAsic.SetTitle("tgLepKEAsic");
    tgLepKEAsic.Write();

    TGraph tgLepKETile = *f.Graph("neutEnergy", "tile_size");
    tgLepKETile.Sort();
    tgLepKETile.Draw();
    tgLepKETile.SetName("tgLepKETile");
    tgLepKETile.SetTitle("tgLepKETile");
    tgLepKETile.Write();

    TGraph tgEnergyDepAsic = *f.Graph("energy_deposit", "max_asic_reset");
    tgEnergyDepAsic.Sort();
    tgEnergyDepAsic.Draw();
    tgEnergyDepAsic.SetName("tgEnergyDepAsic");
    tgEnergyDepAsic.SetTitle("tgEnergyDepAsic");
    tgEnergyDepAsic.Write();

    TGraph tgEnergyDepTile = *f.Graph("energy_deposit", "tile_size");
    tgEnergyDepTile.Sort();
    tgEnergyDepTile.Draw();
    tgEnergyDepTile.SetName("tgEnergyDepTile");
    tgEnergyDepTile.SetTitle("tgEnergyDepTile");
    tgEnergyDepTile.Write();

    TGraph tgnFSAsic = *f.Graph("nFS", "max_asic_reset");
    tgnFSAsic.Sort();
    tgnFSAsic.Draw();
    tgnFSAsic.SetName("tgnFSAsic");
    tgnFSAsic.SetTitle("tgnFSAsic");
    tgnFSAsic.Write();

    TGraph tgnFSTile = *f.Graph("nFS", "tile_size");
    tgnFSTile.Sort();
    tgnFSTile.Draw();
    tgnFSTile.SetName("tgnFSTile");
    tgnFSTile.SetTitle("tgnFSTile");
    tgnFSTile.Write();

    // make a TGraphErrors here
    // int n=0;
    // std::vector<double> px, py, pex, pey;
    // TGraphErrors* tge = new TGraphErrors()
    // TGraphErrors* tge = new TGraphErrors(n, &px[0], &py[0], &pex[0], &pey[0]);
    // tge->Draw("AP");
    // tge->Write();
    //
    //
    std::cout << "graphics complete.\n";
}
