#include <vector>
#include <string>
#include "ROOT/RDataFrame.hxx"
#include "TDirectory.h"
#include "TH2.h"

#include <algorithm>

#define TILE_WIDTH 64;
const int YMIN = 800 - TILE_WIDTH;
const int YMAX = 800 + TILE_WIDTH;
const int XMIN = 300 - TILE_WIDTH;
const int XMAX = 300 + TILE_WIDTH;

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

// return the maximum asic hit here
TH2I max_asic_resets(const std::vector<double>& p_resets,
                     const std::vector<int>& px,
                     const std::vector<int>& py)
{
    TH2I asicBins = TH2I("", "", 128/4, XMIN, XMAX, 128/4, YMIN, YMAX);

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

    auto thAllPixel = f.Histo1D({"hAllPixel", "hAllPixel", 128, 0, 128}, "all_pixel_reset");
    thAllPixel->Draw();
    thAllPixel->Write();

    auto thPixel = f.Histo1D({"hPixel", "hPixel", 256, 0, 512}, "max_pixel_reset");
    thPixel->Draw();
    thPixel->Write();

    auto thPixelRTD = f.Histo1D({"hPixelRTD", "hPixelRTD", 512, 0, 10e-6}, "max_pixel_rtd");
    thPixelRTD->Draw();
    thPixelRTD->Write();

    auto thPixelRTDns = f.Histo1D({"hPixelRTDns", "hPixelRTDns", 512, 0, 100e-9}, "max_pixel_rtd");
    thPixelRTDns->Draw();
    thPixelRTDns->Write();

    auto nf = f.Define("max_asic_reset", "return asic_th2i.GetMaximum();");
    auto thAsic = nf.Histo1D({"hAsic", "hAsic", 256, 0, 1024}, "max_asic_reset");
    thAsic->Draw();
    thAsic->Write();

    TGraph tgPixel = *nf.Graph("tile_size", "max_pixel_reset");
    tgPixel.Sort();
    tgPixel.Draw();
    tgPixel.SetName("tgMaxPixel");
    tgPixel.SetTitle("tgMaxPixel");
    tgPixel.Write();

    TGraph tgAsic = *nf.Graph("tile_size", "max_asic_reset");
    tgAsic.Sort();
    tgAsic.Draw();
    tgAsic.SetName("tgMaxAsic");
    tgAsic.SetTitle("tgMaxAsic");
    tgAsic.Write();

    TGraph tgLepKEAsic = *nf.Graph("lepKE", "max_asic_reset");
    tgLepKEAsic.Sort();
    tgLepKEAsic.Draw();
    tgLepKEAsic.SetName("tgLepKEAsic");
    tgLepKEAsic.SetTitle("tgLepKEAsic");
    tgLepKEAsic.Write();

    TGraph tgLepKETile = *nf.Graph("lepKE", "hTile");
    tgLepKETile.Sort();
    tgLepKETile.Draw();
    tgLepKETile.SetName("tgLepKETile");
    tgLepKETile.SetTitle("tgLepKETile");
    tgLepKETile.Write();

    TGraph tgnFSAsic = *nf.Graph("nFS", "max_asic_reset");
    tgnFSAsic.Sort();
    tgnFSAsic.Draw();
    tgnFSAsic.SetName("tgnFSAsic");
    tgnFSAsic.SetTitle("tgnFSAsic");
    tgnFSAsic.Write();

    TGraph tgnFSTile = *nf.Graph("nFS", "hTile");
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

}