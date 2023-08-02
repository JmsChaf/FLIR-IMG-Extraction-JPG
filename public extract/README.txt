Script Written by JmsChaf

This program was written for use with FLIR Systems Inc. (now Teledyne FLIR) A300 Camera IMG files.

Setup:
Navigate to the location of the 'extract' folder in your console. Type 'pip install -r requirements.txt' to install 
all library dependedncies. Put the raw IMG files in the 'raw' directory. The program uses relative paths, so there is
no need to change the file paths.

Exiftool, located in the exif folder, needs to be located in you computers Windows path, 'C:\Windows'. This allows the
computer to recognize it in any directory.

Operation:
To run the program, navigate to the scripts folder in your console, then type 'python extractscript.py'. This is extract 
the raw radience data,image, and metadata into the results folder. The data will be sorted into folders matching the 
directory structure in raw (see example for how data is formatted). IMG files not in a folder in raw will not be
processed, and the program can only walk into one-layer dirs, sub directories will not be considered. 

The script will produce an estimated end time for it execution every 30 files it processes. Files produced will
have the same name as there input, so NVL_IR_H000121511.IMG will produce NVL_IR_H000121511.jpg and two 
NVL_IR_H000121511.csv for the radience and metadata. These will be sorted into the sub directories 'meta', 'radience', and 
'jpg'.