# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
# due to problems with python 3.7, run this with version 3.6
import time
import os
import re #sudo apt-get install python3-regex
import gdal
import numpy
import ntpath

# ####################################### SET TIME-COUNT ###################################################### #

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #

# path of the data
localhome = os.getcwd()
data_home = os.path.join(localhome, "data")
landsat_home = os.path.join(data_home, "landsat8_2015")

folder_files_dict = {} #key=folder #value=list of the 2 tif-files
folder_array_dict = {}



# ####################################### FUNCTIONS ########################################################### #


def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()

def create_folder_file_dict():
    global folder_files_dict
    iterator = os.walk(landsat_home)
    for item in iterator:  # each item is a triple (root,dirs,files)
        if item[0] != landsat_home: #ignore first folder
            tmp_files = []
            for file in item[2]:
                if is_tif(file):
                    tmp_files.append(file)
            folder_files_dict[item[0]] = tmp_files
    print(folder_files_dict)


def is_tif(file):
    if file and os.path.splitext(file)[1] == ".tif":
        return True
    return False

def create_array_from_files():
    global folder_files_dict
    global folder_array_dict
    print("folder_array_dict: " + str(len(folder_files_dict)))
    for folder, files in folder_files_dict.items():
        qa_file = get_qa_file(files)

        # print(qa_file)
        # geodatatransform
        ds = gdal.Open(os.path.join(folder, qa_file))
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()
        folder_array_dict[folder] = arr

def get_qa_file(file_list):
    for file in file_list:
        if re.search(".*_qa_", file) and is_tif(file):
            return file


# ####################################### PROCESSING ########################################################## #


create_folder_file_dict()
create_array_from_files()
print(folder_array_dict)

# filePath = os.path.join(localhome, "answer_exercise3.txt")
# writeIntoFile(filePath, string_to_write)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
