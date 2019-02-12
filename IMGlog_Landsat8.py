import os
import time
import tkFileDialog
from Tkinter import *
from glob import glob

print 'This program scans a tree for Landsat 8 OLI/TRS TIF files'
print 'and creates a categorized list in CSV form.'
# Written by A. Anderson

os.chdir('C:\\')
root = Tk()
root.withdraw()
root.filename = tkFileDialog.askdirectory()

if root.filename == '':
    exit(5)

projectpath = root.filename.replace('/','\\')

print '\nSearching for TIF files in:'
print projectpath
print '\nThis can take a while!\n'

# Traverse the tree and list the TIF files
tl = []
for x in os.walk(projectpath):
    for y in glob(os.path.join(x[0], '*.TIF')):
        tl.append(y)

# make a list of lists, w/ possible newlines stripped out
r = [[i.split('\n')[0]] for i in tl]

print 'Analyzing List...'

fl = []
# sort out all files that don't look like they are Landsat 8 OLI/TRS images
for i in r:
    filename = i[0].split('\\')[-1]
    if filename[0:5]    == 'LC08_':
        fl.append(i)

dates = []
# Parse file names and find attributes
for i in fl:
    # split the file name - full[0], file[1], path[2]
    filename = i[0].split('\\')[-1]
    i.append(filename)   # just the name of the file
    i.append(i[0].replace(filename, '')) #just the path of the file
    if filename[0:8] =='LC08_CU_':
        filename = filename[0:8] + 'XX' + filename[8:33] + filename[34:38] + filename[39:]  # for experimental files to be parseable
    # scan for date [3]
    if len(filename) > 46 and filename[16:19] == '_20':
        d = filename[17:21] +'-' +filename[21:23] +'-' +filename[23:25]  # insert dashes into date
        # check if date is known and make sure it contains no letters
        if d not in dates and bool(re.search('[a-zA-Z]', d)) == False:
            dates.append(d)
        i.append(d)
    else:
        dpos = i[2].rfind('_20')
        dpos = i[2].rfind('\\',0,dpos)
        dpos = i[2].find('_20',dpos)
        if dpos > 0:
            d = i[2][dpos +1:dpos +5] + '-' + i[2][dpos +5:dpos +7] + '-' + i[2][dpos +7:dpos +9]  # insert dashes into date
            i.append(d)# check if date is known and make sure it contains no letters
            if d not in dates and bool(re.search('[a-zA-Z]', d)) == False:
                dates.append(d)
        else:
            i.append('unknown')

    # check which Path [4]
    if len(filename) > 46:
        d = filename[10 : 13]
        i.append(d)
    else:
        found = False
        p = i[2].split('\\')
        for j in reversed(p):
            if len(j) > 39 and j[9] == '_':
                i.append(j[10:13])
                found = True
                break
        if not found:
            i.append('unknown')

    # check which Row [5]
    if len(filename) > 46:
        d = filename[13 : 16]
        i.append(d)
    else:
        found = False
        p = i[2].split('\\')
        for j in reversed(p):
            if len(j) > 39 and j[9] == '_':
                i.append(j[13:16])
                found = True
                break
        if not found:
            i.append('unknown')

    # check which Band [6]
    proc = 'ToA'
    if filename[0:8] == 'LC08_CU_':
        proc = 'Srf'
    if len(filename) > 46:
        band = filename[41:44]
        if band.isupper():
            band = band.replace('.','')
            if len(band) == 2 and band[0] == 'B':
                band = band[0] + '0' + band[1]
            elif band == 'BQA':
                band = 'QA'
                qa = ' - pre-collection'
        else:
            proc = 'Srf'
            dpos = filename.rfind('_')
            epos = filename.rfind('.')
            band = filename[dpos+1 : epos]
            if band[0:4] == 'band':
                band = 'B0' + filename[epos-1]
            elif band == 'aerosol':
                band = 'Mask'
            elif band == 'qa':
                band = 'QA'
                epos = filename.rfind('_',0,dpos-1)
                qa = ' - ' + filename[epos+1:dpos]
    else:
        band = 'Mask'
    i.append(band)

    # spell out Band [7]
    if band == 'B01':
        i.append(' - coastal aerosol')
    elif band == 'B02':
        i.append(' - blue')
    elif band == 'B03':
        i.append(' - green')
    elif band == 'B04':
        i.append(' - red')
    elif band == 'B05':
        i.append(' - NIR')
    elif band == 'B06':
        i.append(' - SWIR 1')
    elif band == 'B07':
        i.append(' - SWIR 2')
    elif band == 'B08':
        i.append(' - panchromatic')
    elif band == 'B09':
        i.append(' - SWIR - cirrus')
    elif band == 'B10':
        i.append(' - Thermal IR 1')
    elif band == 'B11':
        i.append(' - Thermal IR 2')
    elif band == 'CLO':
        i.append(' - clouds')
    elif band == 'QA':
        i.append(qa)
    elif band == 'Mask':
        d = filename.rfind('_')
        e = filename.find('.')
        i.append(' - ' + filename[d+1:e])
    else:
        i.append(' - unknown')

    # check which category [8]
    if  len(filename) > 46:
        d = filename[38:40]
        i.append(d)
    else:
        i.append('')

    # check which collection # [9]
    if  len(filename) > 46:
        d = filename[35:37]
        i.append(d)
    else:
        i.append('')

    # check resolution [10]
    if len(band) == 3 and band[2] == '8':
        i.append('15m')
    else:
        i.append('30m')

    # check Proc Lvl [11]
    i.append(proc)

    # check which correction Lvl [12]
    if  len(filename) > 46:
        d = filename[5:9]
        if d[0:3] == 'CU_':
            d = 'CU'
        i.append(d)
    else:
        i.append('')

# find day numbers [13]
dates.sort()
for i in fl:
    if i[3] in dates:
        i.append(dates.index(i[3])+1)
    else:
        i.append(0)
    





print ''
print 'Writing results to:'
root.filename = tkFileDialog.asksaveasfilename(initialdir=projectpath, title="Save CSV", defaultextension='.csv',
                                               filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))
if root.filename == '':
    exit(5)

outputfile = root.filename.replace('/','\\')

print outputfile

csvtxt = ['Day,Date,Band,Proc,Res,Path,Row,CorrLvl,Category,Collection,Flag,Name,Path,Path including Name\n']
# build csv
for i in fl:
    csvtxt.append(str(i[13]) + ',' + i[3] + ',' + i[6]  + i[7] + ',' + i[11] + ',' + i[10] + ',' + i[4] + ',' + i[5] + ',' + i[12] + ',' + i[8] + ',' + i[9] + ',,' + i[1] + ',' + i[2] + ',' + i[0] + '\n')

f = open(outputfile, 'w')
f.writelines(csvtxt)
f.close()

print ''
print 'Done!'
time.sleep(3)
