# Script Written By JmsChaf, 2023

from rich.console import Console
from datetime import datetime
from PIL import Image as im
import pandas as pd
import numpy as np
import subprocess
import pathlib
import time
import cv2
import csv
import os

print('Compiling please wait.')

# Implements relative paths so the user doesn't have to manualy change them
script_path = os.getcwd()
parent_dir = os.path.dirname(script_path)

raw = os.path.join(parent_dir, 'raw')
results = os.path.join(parent_dir, 'results')

jpg_out = os.path.join(results, 'jpg')
radience_out = os.path.join(results, 'radience')
meta_out = os.path.join(results, 'meta')

# Creates a list of the dirs in the (raw) parent directory
dirlist = {}

# Makes a same-named directory in results with folders for all the extracted info
def makedir(dir_to_make):
    try:
        os.mkdir(dir_to_make)
        os.mkdir(os.path.join(dir_to_make, 'jpg'))
        os.mkdir(os.path.join(dir_to_make, 'radience'))
        os.mkdir(os.path.join(dir_to_make, 'meta'))
    except FileExistsError:
        print(dir_to_make + ' already exists.')

# Walks through all the dirs in raw and links them to a new output dir
for root, dirs, files in os.walk(raw):
    for dir in dirs:
        dir_path = os.path.join(root, dir)
        out_dir = os.path.join(results, dir)
        dirlist[dir_path] = out_dir
        makedir(out_dir)


# Converts the estimated seconds to finish to hour/min/sec format
def time_convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
     
    return "%d:%02d:%02d" % (hour, minutes, seconds)

# Calculates the number of files in the to-be-extracted directory
def SizeOfRaw():
    filecount = 0
    path = os.getcwd()
    parent = os.path.dirname(path)
    raw = parent + '\\raw'

    for root, dirs, files in os.walk(raw):
        for file in files:
            if pathlib.Path(file).suffix != '.IMG':
                continue
            filecount += 1
    
    return filecount

filecount = SizeOfRaw()
start_time = 0
filesprocessed = 0

def main():
    global start_time
    global filecount
    global filesprocessed

    start_time = time.time()

    for i in dirlist:
        files = os.listdir(i)
        outdir = dirlist[i]
        
        # Sets the path of the output directories
        radience_dir = os.path.join(outdir, 'radience')
        jpg_dir = os.path.join(outdir, 'jpg')
        meta_dir = os.path.join(outdir, 'meta')

        for j in files:
            # Drops all files that are not IMG type
            filetype = pathlib.Path(j).suffix
            if filetype != '.IMG':
                if filetype == '':
                    continue
                print('File dropped: ' + str(j))
                continue

            # Extract raw image
            file_path = os.path.join(i, j)
            stem = pathlib.Path(j).stem
            exiftool_command = ["exiftool", "-b", "-RawThermalImage", file_path]

            # Extracts the raw tiff data from the IMG file
            tif_data = subprocess.check_output(exiftool_command)

            # Decodes the extracted data into bits and saves it into an array
            decoded = np.frombuffer(tif_data, np.uint16)
            image = cv2.imdecode(decoded, cv2.IMREAD_UNCHANGED)
            imarray = np.array(image)
            
            # Creates a filepath for the jpg
            image_filepath = os.path.join(jpg_dir, stem + '.jpg')

            # Normalizes the raw radience data (array) and saves it as a jpg
            normimg = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            image = im.fromarray(normimg)
            image.save(image_filepath)

            # Saves the raw radience data into a csv file
            raw_radience_filepath = os.path.join(radience_dir, stem + '.csv')
            raw_radience = pd.DataFrame(imarray)
            raw_radience.to_csv(raw_radience_filepath, header=False, index=False)

            # Reads and saves the metada from the file into a csv file
            meta_filepath = os.path.join(meta_dir, stem + '.csv')
            exiftool_command = ["exiftool", "-csv", file_path]
            subprocess.run(exiftool_command, stdout=open(meta_filepath, 'x'))

            filesprocessed += 1

            console.log(str(filesprocessed) + ' of ' + str(filecount) + ' files done.')
            if filesprocessed % 30 == 0:
                eta = int(((float(time.time()) - start_time) / filesprocessed) * (filecount - filesprocessed))
                endtime = time.asctime(time.localtime((time.time() + eta)))
                endtime = endtime.split(' ')[3]

                console.print('Estimated time left ' + time_convert(eta) + '; Estimated end time ' + endtime, style='black on green')
 

console = Console()
with console.status("Working...") as status:
    print('Please wait while your files are extracted.')
    main()


# Benchmarking statistics
print('End Time: ' + str(time.asctime(time.localtime((time.time())))))

elapsed_time = (float(time.time()) - start_time)
print('Process Time: ' + str(time_convert(elapsed_time)))

secperfile = elapsed_time / filecount
print('Average File Time: ' + str(secperfile))
