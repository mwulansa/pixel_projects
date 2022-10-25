import sys,time,os,re
import argparse
from datetime import datetime, timezone, timedelta
import glob
import pandas as pd
from omsapi import OMSAPI
import matplotlib.pyplot as plt

path_automask = '/Users/muti/Documents/Pixel/automask_muti_test/'

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
        m = list(set(m))
        m.sort()

    return m

def return_recover(lafter, lbefore):

    recover = []
    
    for i in lbefore:
        if i not in lafter:
            recover.append(i)

    len_recover.append(len(recover))
            
    return recover

def plot_hist(x):
    plt.hist(x, bins=range(min(x), max(x) + 1, 1))
    plt.show() 


def compare_list(modlist):
    for i in range(len(modlist)):
        globals()[f"set{i}"] = set(modlist[i])

    same = set0

    for i in range(len(modlist)-1):
        same = same.intersection(globals()[f"set{i+1}"])

    same = list(set(same))
    same.sort()

    len_stuck.append(len(same))

    recover = return_recover(list(same), list(set0))

    return same, recover

def find_file_timestamp(ser_time):
    ser_datetime_object = datetime.strptime(ser_time , '%Y-%m-%d_%H:%M:%S')
    ser_unix_time = ser_datetime_object.replace(tzinfo=timezone.utc).timestamp()

    creation_time_list = []
    fils = []

    for f in(glob.glob(path_automask+'/automasked_*')):
        creation_datetime = os.path.basename(f).split("_")[1]
        creation_time_list.append(int(creation_datetime))

    creation_time_list = sorted(creation_time_list)
    filesFound = False

    for i in range(len(creation_time_list)-1):
        if ser_unix_time > creation_time_list[i] and ser_unix_time < creation_time_list[i+1] :
            before = creation_time_list[i]
            after = creation_time_list[i+1]
            filesFound = True
        elif ser_unix_time == creation_time_list[i]:
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

    fileBefore = glob.glob(path_automask+'/automasked_*'+str(datetime.utcfromtimestamp(before).strftime('%Y-%m-%d_%H:%M:%S'))+'*.txt')
    fileAfter = glob.glob(path_automask+'/automasked_*'+str(datetime.utcfromtimestamp(after).strftime('%Y-%m-%d_%H:%M:%S'))+'*.txt')

    fils.append(fileBefore[0])
    fils.append(fileAfter[0])

    print("SER Time:", ser_time)
    print("Files to be compared:")
    print(*fils, sep="\n")

    return fils


def print_repeating_module(fl, ts=str(datetime.now())):
    modules = []
    for f in fl:
        modules.append(get_module_list(f))

    repeating_module, recovered_module = compare_list(modules)

    # print("Repeating Modules:") 
    # print(*repeating_module, sep="\n")

    write_modules(repeating_module, ts)
    write_modules(recovered_module, ts, "recovered")

    return repeating_module, recovered_module


def write_modules(modlist, occ, modtype = "repeating"):
    modWrite = ["{}\n".format(i+" "+occ) for i in modlist]
    with open(path_automask+'tmp_'+modtype+'_modules.txt', 'a') as fil:
        fil.writelines(modWrite)


def make_table(fn):
    if os.path.exists(path_automask+str(fn)+'_raw_table.csv'):
        os.remove(path_automask+str(fn)+'_raw_table.csv')
    if os.path.exists(path_automask+str(fn)+'_pivot_table.csv'):    
        os.remove(path_automask+str(fn)+'_pivot_table.csv')
    if os.path.exists(path_automask+str(fn)+'_occurences_table.csv'):
        os.remove(path_automask+str(fn)+'_occurences_table.csv')


    table = pd.read_csv(path_automask+'tmp_repeating_modules.txt', sep=' ', header=None, names=["Modules", "SER Time"])
    table.sort_values(by=["Modules", "SER Time"], inplace=True)

    # table_rec = pd.read_csv(path_automask+'tmp_recovered_modules.txt', sep=' ', header=None, names=["Modules", "SER Time"])
    # table_rec.sort_values(by=["Modules", "SER Time"], inplace=True)

    table.to_csv(path_automask+str(fn)+'_raw_table.csv')
    # table_rec.to_csv(path_automask+str(fn)+'_raw_table_recovered.csv')

    pivot_table = table.pivot_table(index=['Modules'],columns=['SER Time'], aggfunc='size')
    pivot_table.to_csv(path_automask+str(fn)+'_pivot_table.csv')

    dups_module = table.pivot_table(columns=['Modules'], aggfunc='size')
    dups_module.to_csv(path_automask+str(fn)+'_occurences_table.csv')
    
    print(table)
    print(pivot_table)
    print("***Occurences:")
    print(dups_module)

    # print(pivot_table.iloc[:,-1:] == 1.0)


def query_downtime(fll):
    my_app_id='test-pixel-ser'
    my_app_secret='c048a40d-b056-47dd-8943-048c3d8eefd7'

    omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
    omsapi.auth_oidc(my_app_id,my_app_secret)

    f = omsapi.query("downtimesrun3")
    f.per_page = 100

    f.attrs(['stop_time'])
    f.filter('start_fill_number', fll).filter('stable_beams','True').filter('subsystem', 'PIXEL').filter('category','SOFT_ERROR_RECOVERY')
    f.sort('stop_time')

    response = f.data()
    oms = response.json()
    data = oms['data']

    stop_time = []

    delta = timedelta(minutes = 10)

    for row in data:
        attr = row['attributes']
        stime = attr['stop_time'].strip('Z').replace('T','_')

        stime_datetime_object = datetime.strptime(stime , '%Y-%m-%d_%H:%M:%S')
    
        stop_time.append(stime)

    print("SER Occurences: ",len(stop_time))
    print(stop_time)

    nlist = [datetime.strptime(stime , '%Y-%m-%d_%H:%M:%S') for stime in stop_time]

    for i in range(len(nlist)-1):

        if nlist[i+1]-nlist[i] < delta :
            stop_time.remove(nlist[i].strftime("%Y-%m-%d_%H:%M:%S"))

    print("SER Occurences after removing SERs within 10 minutes: ", len(stop_time))
    print(stop_time)

    return stop_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comparing auto-masked channels lists")
    parser.add_argument("-i", "--inputfile", nargs="+", type=str, help="Compares automasked modules between the given textfiles")
    parser.add_argument("-l", "--listOfFiles", type=str, help="Compares automasked modules between the textfiles in the given list")
    parser.add_argument("-t", "--timestamp", type=str, help="Compares automasked modules before and after the given timestamp")
    parser.add_argument("-s", "--ser", nargs="+", type=str, help="Compares automasked modules before and after the listed timestamps")
    parser.add_argument("-f", "--fill", type=int, help="Compares automasked modules before and after SER times queried from the given fill number")
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    len_recover = []
    len_stuck = []

    if args.inputfile is not None:
        openList = args.inputfile
        fileList = [path_automask+i for i in openList]
        rep, rec = print_repeating_module(fileList, args.timestamp)

        print("--------------------")
        print("Repeating Modules:")
        print(*rep, sep="\n")

        print("--------------------")
        print("Recovered Modules:")
        print(*rec, sep="\n")
        exit()

    elif args.listOfFiles is not None:
        openList = open(args.listOfFiles).read().splitlines()
        fileList = [path_automask+i for i in openList]
        rep, rec = print_repeating_module(fileList, args.timestamp)

        print("--------------------")
        print("Repeating Modules:")
        print(*rep, sep="\n")
        
        print("--------------------")
        print("Recovered Modules:")
        print(*rec, sep="\n")
        exit()

    elif args.timestamp is not None:
        fileList = find_file_timestamp(args.timestamp)

        rep, rec = print_repeating_module(fileList, args.timestamp)

        print("--------------------")
        print("Repeating Modules:")
        print(*rep, sep="\n")

        print("--------------------")
        print("Recovered Modules:")
        print(*rec, sep="\n")
        exit()

    elif args.ser is not None:
        os.remove(path_automask+'tmp_repeating_modules.txt')
        for stamp in args.ser:
            fileList = find_file_timestamp(stamp)
            print_repeating_module(fileList, stamp)
        make_table()
        exit()

    elif args.fill is not None:
        if os.path.exists(path_automask+'tmp_repeating_modules.txt'):
            os.remove(path_automask+'tmp_repeating_modules.txt')
        ser_time_fill = query_downtime(args.fill)
        for stamp in ser_time_fill:
            fileList = find_file_timestamp(stamp)
            print_repeating_module(fileList, stamp)
        make_table(args.fill)
        print(len_recover)
        print(len_stuck)
        plot_hist(len_recover)
        exit()

    else:
        print("Please Provide module lists or timestamp")
        print("Exiting")
        exit()

    if len(fileList) < 2 : 
        print("Please provide more than one module lists")
        print("Exiting")
        exit()

    print_repeating_module(fileList)
