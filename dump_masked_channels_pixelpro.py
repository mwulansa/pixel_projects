import sys, os
import csv
import argparse

sys.path.append('/pixel/users/Calibrations/')
from modules.JMTROOTTools import *

#Created by Muti Wulansatiti. Email: meutia.wulansatiti@cern.ch
#Creates masked modules histograms from csv files outputted by get_repeating_modules.py
#Executed by get_repeating_modules.py if option --timerange is used for get_repeating_modules.py
#Run $python dump_masked_channels.py --help for list of arguments
#Example:
#$python dump_masked_channels.py -i <csv_file> -st <start_time (according to the csv file)> --all/--full/--bpix/--fpix

def get_masked_lists():
    filename = open(args.inputfile, 'r')

    file = list(csv.reader(filename, delimiter=" "))

    nMasked = [row[1] for row in file]

    lyr1 = lyr2 = lyr3 = lyr4 = d1 = d2 = d3 = []

    if args.bpix or args.all :

        lyr1 = [row[2] for row in file]
        lyr2 = [row[3] for row in file]
        lyr3 = [row[4] for row in file]
        lyr4 = [row[5] for row in file]

    if args.fpix or args.all :

        d1 = [row[6] for row in file]
        d2 = [row[7] for row in file]
        d3 = [row[8] for row in file]

    return nMasked, lyr1, lyr2, lyr3, lyr4, d1, d2, d3

def book_histograms():
    
    if args.full or args.all :

        h['hist_tot'] = ROOT.TH1F("NMasked_tot", "Number of Masked Modules Overtime. Start: "+args.starttime+"; minutes ; N Channels", len(nMasked)-1 , 0, len(nMasked)-1)

    if args.bpix or args.all :

        h['hist_lyr1'] = ROOT.TH1F("NMasked_lyr1", "Number of Masked Modules Overtime (BPix). Start: "+args.starttime+"; minutes ; N Channels", len(nMasked)-1 , 0, len(nMasked)-1)
        h['hist_lyr2'] = ROOT.TH1F("NMasked_lyr2", "Number of Masked Modules Overtime (LYR2). Start: "+args.starttime+"; minutes ; N Channels", len(nMasked)-1 , 0, len(nMasked)-1)
        h['hist_lyr3'] = ROOT.TH1F("NMasked_lyr3", "Number of Masked Modules Overtime (LYR3). Start: "+args.starttime+"; minutes ; N Channels", len(nMasked)-1 , 0, len(nMasked)-1)
        h['hist_lyr4'] = ROOT.TH1F("NMasked_lyr4", "Number of Masked Modules Overtime (LYR4). Start: "+args.starttime+"; minutes ; N Channels", len(nMasked)-1 , 0, len(nMasked)-1)

    if args.fpix or args.all :

        h['hist_d1'] = ROOT.TH1F("NMasked_d1", "Number of Masked Modules Overtime (FPix). Start: "+args.starttime+"; minutes ; N Channels", len(nMasked)-1 , 0, len(nMasked)-1)
        h['hist_d2'] = ROOT.TH1F("NMasked_d2", "Number of Masked Modules Overtime (D2). Start: "+args.starttime+"; minutes ; N Channels", len(nMasked)-1 , 0, len(nMasked)-1)
        h['hist_d3'] = ROOT.TH1F("NMasked_d3", "Number of Masked Modules Overtime (D3). Start: "+args.starttime+"; minutes ; N Channels", len(nMasked)-1 , 0, len(nMasked)-1)


def set_bin_content():
    
    for i in range(len(nMasked)-1):

        if args.full or args.all :
            h['hist_tot'].SetBinContent(i,int(nMasked[i+1]))

        if args.full or args.all :
            opt = "full"

        if args.bpix or args.all :
            opt = "bpix"
            h['hist_lyr1'].SetBinContent(i,int(lyr1[i+1]))
            h['hist_lyr2'].SetBinContent(i,int(lyr2[i+1]))
            h['hist_lyr3'].SetBinContent(i,int(lyr3[i+1]))
            h['hist_lyr4'].SetBinContent(i,int(lyr4[i+1]))

        if args.fpix or args.all :
            opt = "fpix"
            h['hist_d1'].SetBinContent(i,int(d1[i+1]))
            h['hist_d2'].SetBinContent(i,int(d2[i+1]))
            h['hist_d3'].SetBinContent(i,int(d3[i+1]))

        if args.all :
            opt = "all"

    return opt


def set_style():

    colour = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen+2, ROOT.kMagenta, ROOT.kCyan+1, ROOT.kOrange+9, ROOT.kViolet+1, ROOT.kBlack]

    hmax = [h[key].GetMaximum() for key in h.keys()]

    for i,key in enumerate(h.keys()):
        h[key].SetLineColor(colour[i])
        h[key].SetLineWidth(2)
        h[key].SetMaximum(max(hmax)+20)

def make_legend():

    ld = ROOT.TLegend(0.35,0.725,0.83,0.88)
    ld.SetLineWidth(0)
    ld.SetNColumns(4)

    for key in h.keys():
        if args.verbose :
            ld.AddEntry(h[key], str(key.split("_")[-1])+": "+str(int(h[key].Integral())), "f")
        else :
            ld.AddEntry(h[key], str(key.split("_")[-1]), "f")


    return ld

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="To plot histogram from csv file given by get_repeating_modules.py")
    parser.add_argument("-i", "--inputfile", type=str, help="csv file to plot")
    parser.add_argument("-st", "--starttime", type=str, help="start time")

    parser.add_argument("--full", action="store_true", help="Plot total masked channels")
    parser.add_argument("--bpix", action="store_true", help="Plot bpix masked channels")
    parser.add_argument("--fpix", action="store_true", help="Plot fpix masked channels")
    parser.add_argument("--all", action="store_true", help="Overlays histograms from --total, --bpix, and --fpix")

    parser.add_argument("--verbose", action="store_true", help="Print integrals on the plots")

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    print("Running dump script...")

    nMasked, lyr1, lyr2, lyr3, lyr4, d1, d2, d3 = get_masked_lists()

    h = {}

    book_histograms()

    for key in h.keys():
        h[key].SetStats(0)

    opt = set_bin_content()

    set_style()

    c1 = ROOT.TCanvas("c1","c1",850, 850)
    c1.cd()

    ld = make_legend()

    if args.full or args.all :
        h['hist_tot'].Draw("same")

    if args.bpix or args.all :
        h['hist_lyr1'].Draw("same")
        h['hist_lyr2'].Draw("same")
        h['hist_lyr3'].Draw("same")
        h['hist_lyr4'].Draw("same")

    if args.fpix or args.all :
        h['hist_d1'].Draw("same")
        h['hist_d2'].Draw("same")
        h['hist_d3'].Draw("same")

    ld.Draw("same")

    out = args.inputfile.strip('.csv')+"_"+opt+".png"

    c1.SaveAs(out)

    print("Histogram:")
    print(out)

    print("Press Return to exit")
