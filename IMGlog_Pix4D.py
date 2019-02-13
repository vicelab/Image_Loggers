import os
import time
import tkFileDialog
from Tkinter import *
from glob import glob

print 'This program scans a tree for TIF files created with Pix4D'
print 'and creates a categorized list in CSV form.'
# Written by A. Anderson

os.chdir('C:/')
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
listfile = projectpath + '\\Temp-Imagelogger.TMP'
os.system('dir "' + projectpath + '\\*.TIF" /s /b > "' + listfile + '"')
f = open(listfile)
tl = f.readlines()
f.close()
os.system('del "' + listfile + '"')

# make a list of lists, w/ possible newlines stripped out
r = [[i.split('\n')[0]] for i in tl]

print 'Analyzing List...'

fl = []
# remove all downsampled, tile, and preview files
for i in r:
    if not (    '\\tiles\\' in i[0] \
             or '_preview.tif' in i[0] \
             or '\\undistorted_images\\' in i[0] \
             or '_downsampled.tif' in i[0]):
        fl.append(i)

dates = []
# Parse file names and find attributes
for i in fl:
    # split the file name #[0][1][2]
    filename = i[0].split('\\')
    i.append(filename[-1])
    i.append(i[0].replace(filename[-1], ''))

    # find categories [3]
    if '_dsm.tif' in i[0] or '_dtm.tif' in i[0]:
        i.append('relief')
    elif '_mosaic_' in i[0]:
        i.append('orthomosaic')
    elif '_index_' in i[0]:
        i.append('index')
    elif '_reflectance_' in i[0]:
        i.append('reflectance')
    else:
        i.append('unknown')

    # find types[4]
    if '_dsm.tif' in i[0]:
        i.append('dsm')
    elif '_dtm.tif' in i[0]:
        i.append('dtm')
    elif 'blue.tif' in i[0]:
        i.append('1-blue')
    elif 'red.tif' in i[0]:
        i.append('3-red')
    elif 'green.tif' in i[0]:
        i.append('2-green')
    elif 'nir.tif' in i[0]:
        i.append('5-nir')
    elif 'red edge.tif' in i[0]:
        i.append('4-red edge')
    elif '_ndvi' in i[0]:
        i.append('ndvi')
    elif '_ndre' in i[0]:
        i.append('ndre')
    elif '_msavi2' in i[0]:
        i.append('msavi2')
    else:
        i.append('unknown')

    # scan for dates[5]
    dpos = i[0].find('_20')
    if dpos > 0:
        d = i[0][dpos + 1:dpos + 11]
        # check if date is known and make sure it contains no letters
        if d not in dates and bool(re.search('[a-zA-Z]', d)) == False:
            dates.append(d)
        i.append(d)
    else:
        i.append('unknown')

#find day numbers[6]
dates.sort()
for i in fl:
    if i[5] in dates:
        i.append(dates.index(i[5])+1)
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

csvtxt = ['Day,Date,Band,Res,Proc,PrBase,quality,Collection,Orbit,Tile,Sat,Cam,Flag,Name,Path,Path including Name\n']
# build csv
for i in fl:
    csvtxt.append(str(i[6]) + ',' + i[5] + ',' + i[4] + ',,' + i[3] + ',,,,,,,,,' + i[1] + ',' + i[2] + ',' + i[0] + '\n')

f = open(outputfile, 'w')
f.writelines(csvtxt)
f.close()

print ''
print 'Done!'
time.sleep(3)
