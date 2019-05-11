# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
# due to problems with python 3.7, run this with version 3.6
import time
import os
import statistics
import math
from collections import Counter
import pandas as pandas
from geopandas import GeoDataFrame
from shapely.geometry import Point
import gdal
import numpy

# ####################################### SET TIME-COUNT ###################################################### #

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
buff_m = 100

# path of the data
localhome = os.getcwd()
data_home = os.path.join(localhome, "data")
tif1 = "tileID_410_y2000.tif"
tif1_file = os.path.join(data_home, tif1)

# ####################################### FUNCTIONS ########################################################### #


def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()


# reads the data from the landsat-table and writes it to the global variable 'raw_values_dict'
def read_data_from_tif_file():
    string_to_write = ""
    if tif1_file:
        ds = gdal.Open(tif1_file)
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()

        string_to_write += str(arr)
        string_to_write += "\nmin: " + str(numpy.amin(arr))
        string_to_write += "\nmax: " + str(numpy.amax(arr))
        string_to_write += "\nmmean: " + str(numpy.mean(arr))
        string_to_write += "\nmedian: " + str(numpy.median(arr))
        # string_to_write += "\nrange: " + str(numpy.arange(arr))
        string_to_write += "\nstandard deviation: " + str(numpy.std(arr))
        string_to_write += "\n slicing \n"
        arr = arr[0:2, 0:1] #row 1,
        string_to_write += str(arr)


        # arr_min = arr.Min()
        # arr_max = arr.Max()
        # arr_mean = int(arr.mean())
        # string_to_write += str(arr_min +", " +arr_max +", " +arr_mean +"\n")

    else:
        print("tif file does not exist. Check file-path")
    return string_to_write

# ####################################### PROCESSING ########################################################## #

string_to_write = ""

string_to_write += read_data_from_tif_file()
#
print(string_to_write)


# filePath = os.path.join(localhome, "answer_exercise2.2.txt")
# writeIntoFile(filePath, string_to_write)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
