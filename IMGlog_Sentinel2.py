import os
import time
import tkFileDialog
from Tkinter import *
# from glob import glob

print 'This program scans a tree for Sentinel 2 JP2 files'
print 'and creates a categorized list in CSV form.'
# Written by A. Anderson

os.chdir('C:\\')
root = Tk()
root.withdraw()
root.filename = tkFileDialog.askdirectory()

if root.filename == '':
    exit(5)

projectpath = root.filename.replace('/','\\')

print '\nSearching for JP2 files in:'
print projectpath
print '\nThis can take a while!\n'

# Traverse the tree and list the TIF files
listfile = projectpath + '\\Temp-Imagelogger.TMP'
os.system('dir "' + projectpath + '\\*.jp2" /s /b > "' + listfile + '"')
f = open(listfile)
tl = f.readlines()
f.close()
os.system('del "' + listfile + '"')
# make a list of lists, w/ possible newlines stripped out
r = [[i.split('\n')[0]] for i in tl]

print 'Analyzing List...'

fl = []
# sort out all files that don't look like they are Sentinel images
for i in r:
    filename = i[0].split('\\')[-1]
    if          filename[0]   == 'T'   \
            and filename[6:9] == '_20' \
            and filename[15]  == 'T'   \
            and filename[22]  == '_'   \
            or  filename[0:4] == 'MSK_':
        fl.append(i)

dates = []
# Parse file names and find attributes
for i in fl:
    # split the file name - full[0], file[1], path[2]
    filename = i[0].split('\\')[-1]
    i.append(filename)   # just the name of the file
    i.append(i[0].replace(filename, '')) #just the path of the file

    # scan for date [3]
    if len(filename) > 29 and filename[6:9] == '_20':
        d = filename[7:11] +'-' +filename[11:13] +'-' +filename[13:15]  # insert dashes into date
        # check if date is known and make sure it contains no letters
        if d not in dates and bool(re.search('[a-zA-Z]', d)) == False:
            dates.append(d)
        i.append(d)
    else:
        dpos =  i[2].rfind('_20')
        if dpos > 0:
            d = i[2][dpos +1:dpos +5] + '-' + i[2][dpos +5:dpos +7] + '-' + i[2][dpos +7:dpos +9]  # insert dashes into date
            i.append(d)# check if date is known and make sure it contains no letters
            if d not in dates and bool(re.search('[a-zA-Z]', d)) == False:
                dates.append(d)
        else:
            i.append('unknown')

    # check which Tile [4]
    if  filename[0] == 'T':
        d = filename[1 : 6]
        i.append(d)
    else:
        dpos =  i[2].rfind('_T')
        if dpos > 0:
            d = i[2][dpos +2:dpos +7]
            i.append(d)
        else:
            i.append('unknown')

    # check which Band [5]
    if len(filename) > 29 and filename[22] == '_':
        band = filename[23:26]
    elif filename[0:3] == 'MSK':
        band = 'Mask'
    else:
        band = 'unknown'
    i.append(band)

    # spell out Band [6]
    if band == 'B01':
        i.append(' - coastal aerosol')
    elif band == 'B02':
        i.append(' - blue')
    elif band == 'B03':
        i.append(' - green')
    elif band == 'B04':
        i.append(' - red')
    elif band == 'B05':
        i.append(' - red edge 1')
    elif band == 'B06':
        i.append(' - red edge 2')
    elif band == 'B07':
        i.append(' - red edge 3')
    elif band == 'B08':
        i.append(' - NIR')
    elif band == 'B8A':
        i.append(' - narrow NIR')
    elif band == 'B09':
        i.append(' - water vapor')
    elif band == 'B10':
        i.append(' - SWIR - cirrus')
    elif band == 'B11':
        i.append(' - SWIR 2')
    elif band == 'B12':
        i.append(' - SWIR 3')
    elif band == 'Mask':
        if filename[3:10] == '_CLDPRB':
            i.append(' - cloud prob')
        elif filename[3:10] == '_SNWPRB':
            i.append(' - snow prob')
        else:
            i.append('')
    else:
        i.append('')



    # check which satellite [7]
    dpos = i[0].rfind('\\S2')
    if dpos > 0:
        d = i[0][dpos+1:dpos +4]
        i.append(d)
    else:
        i.append('unknown')

    # check which processing level [8]
    dpos = i[0].rfind('_MSIL')
    if dpos > 0:
        d = i[0][dpos +5 : dpos +7]
        i.append(d)
    else:
        i.append('unknown')

    # check which processing baseline [9]
    dpos = i[0].find('_N')
    if dpos > 0:
        d = i[0][dpos +2 : dpos +4] + '.' + i[0][dpos +4 : dpos +6]
        i.append(d)
    else:
        i.append('unknown')

    # check which Relative Orbit [10]
    dpos = i[0].find('_R')
    if dpos > 0:
        d = i[0][dpos +2 : dpos +5]
        i.append(d)
    else:
        i.append('unknown')

    # check resolution [11]
    if band == 'Mask':
        i.append('20m')
    elif band == 'PVI':
        i.append('320m')
    elif len(filename) > 29:
        if filename[26] == '.':
            i.append('10m')
        elif  filename[26] == '_':
            i.append(filename[27:30])
    else:
        i.append('unknown')




# find day numbers [12]
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

csvtxt = ['Day,Date,Band,Res,ProcLvl,ProcBase,Sat,Tile,Orbit,Flag,Name,Path,Path including Name\n']
# build csv
for i in fl:
    csvtxt.append(str(i[12]) + ',' + i[3] + ',' + i[5] + i[6] + ',' + i[11] + ',' + i[8] + ',' + i[9] + ',' + i[7] + ',' + i[4] + ',' + i[10] + ',,' + i[1] + ',' + i[2] + ',' + i[0] + '\n')

f = open(outputfile, 'w')
f.writelines(csvtxt)
f.close()

print ''
print 'Done!'
time.sleep(3)
