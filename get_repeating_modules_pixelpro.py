import sys,time,os,re
import argparse
from datetime import datetime, timezone
import glob
import csv
import subprocess

#Created by Muti Wulansatiti. Email: meutia.wulansatiti@cern.ch
#Compares automasked channels lists and returns the repeating, recovered, and new modules. option -r/--timerange plots the number of masked channels overtim
#Run $python3 get_repeating_modules.py --help for details and list of arguments

path_automask = '/nfspixelraid/nfspixelraid/users/masks/automasked_channels/'
#csvpng_outpath = ''

def get_module_list(fil):
    m = []
    with open(fil) as f:
        for line in f.readlines():
            bpix = re.search('BPix_B[pm][IO]_SEC\d_LYR\d_LDR\d+[FH]_MOD\d', line)
            if bpix:
                m.append(bpix.group(0))
            fpix = re.search('FPix_B[pm][IO]_D\d_BLD\d+_PNL\d_RNG\d', line)
            if fpix:
                m.append(fpix.group(0))

        ch = m
        ch.sort()

        m = list(set(m))
        m.sort()

    return m, ch

def return_recover(lafter, lbefore):

    recover = []

    for i in lbefore:
        if i not in lafter:
            recover.append(i)

    len_recover.append(len(recover))

    return recover


def compare_list(modlist):

    nmasked = []

    for i in range(len(modlist)):
        globals()[f"set{i}"] = set(modlist[i])
        nmasked.append(len(modlist[i]))

    print("Number of masked channels in each file:")
    print(nmasked)

    same = set0
    new = []

    for i in range(len(modlist)-1):
        same = same.intersection(globals()[f"set{i+1}"])
        diff = list(globals()[f"set{i+1}"])
        for j in diff:
            if j not in list(same):
                new.append(j)

    same = list(set(same))

    len_stuck.append(len(same))

    recover = return_recover(list(same), list(set0))

    same.sort()
    recover.sort()
    new = list(set(new))
    new.sort()

    return same, recover, new, nmasked


def find_file_timestamp(ser_time, start=0, stop=0):

    if args.timestamp is not None:
        ser_datetime_object = datetime.strptime(ser_time , '%Y-%m-%d_%H:%M:%S')
        ser_unix_time = ser_datetime_object.replace(tzinfo=timezone.utc).timestamp()

    elif args.timerange is not None:
        tmp_datetime_start = datetime.strptime(start , '%Y-%m-%d_%H:%M:%S')
        unix_start = tmp_datetime_start.replace(tzinfo=timezone.utc).timestamp()
        tmp_datetime_stop = datetime.strptime(stop , '%Y-%m-%d_%H:%M:%S')
        unix_stop = tmp_datetime_stop.replace(tzinfo=timezone.utc).timestamp()

    creation_time_list = []
    fils = []

    for f in(glob.glob(path_automask+'/automasked_*')):
        creation_datetime = os.path.basename(f).split("_")[1]
        creation_time_list.append(int(creation_datetime))

    creation_time_list = sorted(creation_time_list)
    filesFound = False

    if args.timestamp is not None:

        for i in range(len(creation_time_list)-1):
            if ser_unix_time > creation_time_list[i] and ser_unix_time < creation_time_list[i+1]:
                before = creation_time_list[i]
                after = creation_time_list[i+1]
                filesFound = True
            elif ser_unix_time == creation_time_list[i] :
                if i == 0:
                    print("No automasked list found before the time provided")
                    print("Exiting")
                    exit()
                before = creation_time_list[i-1]
                after = creation_time_list[i+1]
                filesFound = True

        if filesFound == False:
            print("No automasked list found either before or after the time provided")
            print("Exiting")
            exit()

        fileBefore = glob.glob(path_automask+'/automasked_*'+str(before)+'*.txt')
        fileAfter = glob.glob(path_automask+'/automasked_*'+str(after)+'*.txt')

        fils.append(fileBefore[0])
        fils.append(fileAfter[0])

        print("Files to be compared:")
        print(*fils, sep="\n")

        return fils


    elif args.timerange is not None:
    
        trange = [x for x in creation_time_list if x >= unix_start and x <= unix_stop]
        fils = [glob.glob(path_automask+'/automasked_*'+str(x)+'*.txt')[0] for x in trange]
        trange_datetime = [str(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d_%H:%M:%S')) for x in trange]

        if args.verbose:
            print("Files within time range:")
            print(*fils, sep="\n")

        return(fils, trange_datetime)


def print_repeating_module(fl, ts=str(datetime.now())):
    modules = []
    for f in fl:
        modules.append(get_module_list(f)[0])

    repeating_module, recovered_module, new_module, n_masked = compare_list(modules)

    write_modules(repeating_module, ts)
    write_modules(recovered_module, ts, "recovered")
    write_modules(new_module, ts, "new")

    return repeating_module, recovered_module, new_module, n_masked


def get_nmasked(fl):

    modules = []
    for f in fl:
        modules.append(get_module_list(f)[1])

    nmasked = []
    nbpix = [[],[],[],[]]
    nfpix = [[],[],[]]
 
    for i in range(len(modules)):
        nmasked.append(len(modules[i]))

        lyr1 = [j for j in modules[i] if j.split('_')[0] == 'BPix' and j.split('_')[3] == 'LYR1']
        lyr2 = [j for j in modules[i] if j.split('_')[0] == 'BPix' and j.split('_')[3] == 'LYR2']
        lyr3 = [j for j in modules[i] if j.split('_')[0] == 'BPix' and j.split('_')[3] == 'LYR3']
        lyr4 = [j for j in modules[i] if j.split('_')[0] == 'BPix' and j.split('_')[3] == 'LYR4']

        nbpix[0].append(len(lyr1))
        nbpix[1].append(len(lyr2))
        nbpix[2].append(len(lyr3))
        nbpix[3].append(len(lyr4))

        d1 = [j for j in modules[i] if j.split('_')[0] == 'FPix' and j.split('_')[2] == 'D1']
        d2 = [j for j in modules[i] if j.split('_')[0] == 'FPix' and j.split('_')[2] == 'D2']
        d3 = [j for j in modules[i] if j.split('_')[0] == 'FPix' and j.split('_')[2] == 'D3']

        nfpix[0].append(len(d1))
        nfpix[1].append(len(d2))
        nfpix[2].append(len(d3))


    if args.verbose :

        print("Number of total masked modules in each file:")
        print(nmasked)
        print("Number of bpix masked modules in each file [[lyr1],[lyr2],[lyr3],[lyr4]]:")
        print(nbpix)
        print("Number of fpix masked modules in each file [[d1],[d2],[d3]]:")
        print(nfpix)

    return nmasked, nbpix, nfpix


def write_modules(modlist, occ, modtype = "repeating"):
    modWrite = ["{}\n".format(i+" "+occ) for i in modlist]
    with open(path_automask+'tmp_'+modtype+'_modules.txt', 'a') as fil:
        fil.writelines(modWrite)


def write_csv(tstamp, nmasked, bpix, fpix):
#    out = path_automask+"N_masked_channels_"+tstamp[0]+"to"+tstamp[-1]+".csv"
#    out = csvpng_outpath+"N_masked_channels_"+tstamp[0]+"to"+tstamp[-1]+".csv"
    out = "N_masked_channels_"+tstamp[0]+"to"+tstamp[-1]+".csv"

    csvFile = open(out, "w", newline = "")
    header = ['File_timestamp','Masked_Total','LYR1','LYR2','LYR3','LYR4','D1','D2','D3']
    writer = csv.DictWriter(csvFile, delimiter=' ', fieldnames = header)
 
    writer.writeheader()
    for i,j in enumerate(tstamp):
        writer.writerow( {header[0] : j,
                          header[1] : nmasked[i],
                          header[2] : bpix[0][i],
                          header[3] : bpix[1][i],
                          header[4] : bpix[2][i],
                          header[5] : bpix[3][i],
                          header[6] : fpix[0][i],
                          header[7] : fpix[1][i],
                          header[8] : fpix[2][i] 
                      } )
        
    print_separator()
    print("Output csv file:")
    print(out)

    return out


def make_hist(filname,st,opt="--all"):

    print("Running dump script...")

    if args.full : opt="--full"
    if args.all : opt="--all"
    if args.bpix : opt="--bpix"
    if args.fpix : opt="--fpix"

    run = []
    run.append("python")
    run.append("/nfshome0/pixelpro/opstools/masked/dump_masked_channels.py")
    run.append("-i")
    run.append(filname)
    run.append("-st")
    run.append(st)
    run.append(opt)

    if args.verbose:
        print("Command to run dump script:")
        print(run)

    proc = subprocess.Popen(run)
    

def print_separator():
    print("-------------------------")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Compares auto-masked channels lists and returns the repeating, recovered, and new modules. option -r/--timerange plots the number of masked channels overtime")
    requiredName = parser.add_argument_group('Required argument (choose one)')
    requiredName.add_argument("-i", "--inputfile", nargs="+", type=str, help="Compares automasked modules between the given textfiles")
    requiredName.add_argument("-l", "--listOfFiles", type=str, help="Compares automasked modules between the textfiles in the given list")
    requiredName.add_argument("-t", "--timestamp", nargs="+", type=str, help="Compares automasked modules before and after the listed timestamps. Can give one or more timestamps, Format: YYYY-MM-DD_HH:MM:SS")
    requiredName.add_argument("-f", "--fill", type=int, help="Compares automasked modules before and after SER times queried from the given fill number. DOES NOT WORK IN PIXEL MACHINE YET")

    requiredName.add_argument("-r", "--timerange", nargs=2, type=str, help="Start and End time to compare lists. Format: -r YYYY-MM-DD_HH:MM:SS YYYY-MM-DD_HH:MM:SS")

    parser.add_argument("--full", action="store_true", help="Plot total masked channels. To be used with -r/--timerange")
    parser.add_argument("--bpix", action="store_true", help="Plot bpix masked channels. To be used with -r/--timerange")
    parser.add_argument("--fpix", action="store_true", help="Plot fpix masked channels. To be used with -r/--timerange")
    parser.add_argument("--all", action="store_true", help="Overlay total, bpix, fpix. To be used with -r/--timerange")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose Output")
    
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    len_stuck = []
    len_recover = []
    len_new = []

    if args.inputfile is not None:
        openList = args.inputfile
        fileList = [path_automask+i for i in openList]
        rep, rec, ne, nmasked = print_repeating_module(fileList)

    elif args.listOfFiles is not None:
        openList = open(args.listOfFiles).read().splitlines()
        fileList = [path_automask+i for i in openList]
        rep, rec, ne, nmasked = print_repeating_module(fileList)

    elif args.timestamp is not None:
        for stamp in args.timestamp:
            fileList = find_file_timestamp(stamp)
            rep, rec, ne, nmasked = print_repeating_module(fileList, stamp)

            print_separator()
            print("Repeating Modules:")
            print(*rep, sep="\n")
            print("Number:", len(rep))
            print_separator()
            print("Recovered Modules:")
            print(*rec, sep="\n")
            print("Number:", len(rec))
            print_separator()
            print("New Modules:")
            print(*ne, sep="\n")
            print("Number:", len(ne))

        exit()

    elif args.timerange is not None:
        fileList, tlist = find_file_timestamp(0, args.timerange[0], args.timerange[1])
        nmasked, nbpix, nfpix = get_nmasked(fileList)

        out = write_csv(tlist, nmasked, nbpix, nfpix)

        make_hist(out, tlist[0])

        exit()

    else:
        print("Please provide module lists or timestamp")
        print("Exiting")
        exit()

    if len(fileList) < 2 : 
        print("Please provide more than one module lists")
        print("Exiting")
        exit()

        
    print_separator()
    print("Repeating Modules:")
    print(*rep, sep="\n")
    print("Number:", len(rep))
    print_separator()
    print("Recovered Modules:")
    print(*rec, sep="\n")
    print("Number:", len(rec))
    print_separator()
    print("New Modules:")
    print(*ne, sep="\n")
    print("Number:", len(ne))

    exit()
