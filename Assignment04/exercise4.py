# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
# due to problems with python 3.7, run this with version 3.6
import time
import os
import re
import gdal
import numpy
import numpy.ma as ma
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
folder_array_dict = {} #key=folder #value=array of the 6 bands-np-array
folder_mask_dict = {} #key=folder #value=mask-array
number_of_bands = 0




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
    # print(folder_files_dict)


def is_tif(file):
    if file and os.path.splitext(file)[1] == ".tif":
        return True
    return False

def get_qa_file(file_list):
    for file in file_list:
        if re.search(".*_qa_", file) and is_tif(file):
            return file

def get_sr_file(file_list):
    for file in file_list:
        if re.search(".*_sr_", file) and is_tif(file):
            return file


def create_array_from_files():
    global folder_files_dict
    global folder_array_dict
    global folder_mask_dict
    global number_of_bands
    print("folder_array_dict: " + str(len(folder_files_dict)))

    # folder = "/home/billy/workspaces/geoprocessing-with-python/Assignment04/data/landsat8_2015/LC81930232015164LGN00"
    # files = folder_files_dict[folder]
    # qa_file = get_qa_file(files)
    #
    # qa_arr = get_np_array_for_qa_file(folder, qa_file)
    # mask_array = get_mask_for_np_array_from_qa_file(qa_arr)
    # folder_mask_dict[folder] = mask_array
    #
    # # get band-array
    # sr_file = get_sr_file(files)
    # bands_array = get_bands_as_array_for_sr_file(folder, sr_file)
    # if not number_of_bands:
    #     number_of_bands = len(bands_array)
    # folder_array_dict[folder] = bands_array
    #
    #
    # folder = "/home/billy/workspaces/geoprocessing-with-python/Assignment04/data/landsat8_2015/LC81930232015180LGN00"
    # files = folder_files_dict[folder]
    # qa_file = get_qa_file(files)
    #
    # qa_arr = get_np_array_for_qa_file(folder, qa_file)
    # mask_array = get_mask_for_np_array_from_qa_file(qa_arr)
    # folder_mask_dict[folder] = mask_array
    #
    # # get band-array
    # sr_file = get_sr_file(files)
    # bands_array = get_bands_as_array_for_sr_file(folder, sr_file)
    # if not number_of_bands:
    #     number_of_bands = len(bands_array)
    # folder_array_dict[folder] = bands_array

    for folder, files in folder_files_dict.items():
         #create mask-array
        qa_file = get_qa_file(files)
        qa_arr = get_np_array_for_qa_file(folder, qa_file)
        mask_array = get_mask_for_np_array_from_qa_file(qa_arr)
        folder_mask_dict[folder] = mask_array

        # get band-array
        sr_file = get_sr_file(files)
        bands_array = get_bands_as_array_for_sr_file(folder, sr_file)
        if not number_of_bands:
            number_of_bands = len(bands_array)
        folder_array_dict[folder] = bands_array


def calculate_mean_image():
    # init dict of list
    band_dict = {} #key = number of band, value = list of arrays, from each file
    for item in range(0, number_of_bands):
        band_dict[item] = []

    # get data from each file, calulate masked-array and save sorted by band
    for folder, bands in folder_array_dict.items():
        mask = folder_mask_dict[folder]
        for index, band_array in enumerate(bands):
            masked_array = ma.masked_array(band_array, mask=mask)
            band_dict[index].append(masked_array.filled(numpy.nan))

    arr = band_dict[0]
    mean = numpy.nanmean(ma.masked_array(arr, 0), axis=0)
    print(mean)
    # print(ma.masked_values(band_dict[0]))


def calculate_masked_band(band_array, mask_array):
    return ma.masked_array(band_array, mask=mask_array)




def get_np_array_for_qa_file(folder, qa_file):
    ds = gdal.Open(os.path.join(folder, qa_file))
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    return arr

def get_bands_as_array_for_sr_file(folder, sr_file):
    ds = gdal.Open(os.path.join(folder, sr_file))
    #https:// gis.stackexchange.com/questions/308767/how-to-calculate-mean-for-each-band-in-raster-using-gdal-and-python-3
    bands = [ds.GetRasterBand(n + 1).ReadAsArray().astype('float') for n in range(ds.RasterCount)]
    return bands


def get_mask_for_np_array_from_qa_file(arr):
    fct = numpy.vectorize(check_qa_file_pixel, otypes=[numpy.float])
    return fct(arr)

def check_qa_file_pixel(pixel_value):
    if pixel_value == 0 or pixel_value == 1 or pixel_value == 3:
        # return True
        return False
    if pixel_value == 255:
        return numpy.nan
    else:
        return True


# Calculates the mean, median, min, max, range, standard deviation for each year.
# Calculate the same statistics for the image differences between 2000-2010, and 2010-2018.
def do_statistics_for_string(text, arr):
    string_to_write = "---do statistics for " + text + "\n"
    if len(arr) > 0:
        shape = arr.shape
        string_to_write += "max x size: \t\t" + str(shape[1]) + "\n"
        string_to_write += "max y size: \t\t" + str(shape[0]) + "\n"

        string_to_write += "min: \t\t\t\t" + str(numpy.amin(arr))+ "\n"
        string_to_write += "max: \t\t\t\t" + str(numpy.amax(arr))+ "\n"
        string_to_write += "mean: \t\t\t\t" + str(numpy.mean(arr))+ "\n"
        string_to_write += "median: \t\t\t" + str(numpy.median(arr))+ "\n"
        string_to_write += "range: \t\t\t\t" + str(numpy.amax(arr) - numpy.amin(arr))+ "\n"
        string_to_write += "standard deviation: " + str(numpy.std(arr))+ "\n"
        return string_to_write
    return "array ist leer\n"



# ####################################### PROCESSING ########################################################## #


create_folder_file_dict()
create_array_from_files()
calculate_mean_image()
# print(folder_array_dict)

# filePath = os.path.join(localhome, "answer_exercise3.txt")
# writeIntoFile(filePath, string_to_write)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
