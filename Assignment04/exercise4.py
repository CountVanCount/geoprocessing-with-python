# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
# due to problems with python 3.7, run this with version 3.6
import time
import os
import re
import gdal
import numpy
import numpy.ma as ma
from osgeo import gdal
from osgeo import gdal_array

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
geo_transform = None
projection = None



# ####################################### FUNCTIONS ########################################################### #


def get_np_array_for_qa_file(folder, qa_file):
    ds = gdal.Open(os.path.join(folder, qa_file))
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    return arr

def get_bands_as_array_for_sr_file(folder, sr_file):
    ds = gdal.Open(os.path.join(folder, sr_file))
    set_geo_transform(ds)
    #https:// gis.stackexchange.com/questions/308767/how-to-calculate-mean-for-each-band-in-raster-using-gdal-and-python-3
    bands = [ds.GetRasterBand(n + 1).ReadAsArray().astype('float') for n in range(ds.RasterCount)]
    return bands

def set_geo_transform(ds):
    global geo_transform
    global projection
    if not geo_transform: #set once
        geo_transform = ds.GetGeoTransform()
        projection = ds.GetProjection()
        print("Geotransform is set to: " + str(geo_transform))
        print("Projection is set to: " + str(projection))


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


def get_masked_band_dict():
    # init dict of list
    band_dict = {} #key = number of band, value = list of arrays, from each file
    for item in range(0, number_of_bands):
        band_dict[item] = []

    # get data from each file, calulate masked-array and save sorted by band
    for folder, bands in folder_array_dict.items():
        mask = folder_mask_dict[folder]
        for index, band_array in enumerate(bands):
            masked_array = ma.masked_array(band_array, mask=mask)
            band_dict[index].append(masked_array.filled(numpy.nan)) #fill masked array with NaNs
    return band_dict


#see https://stackoverflow.com/questions/33537599/how-do-i-write-create-a-geotiff-rgb-image-file-in-python
def write_mean_image(band_dict):
    mean_list = []
    #calulate mean
    for band in band_dict.values():
        mean_list.append(numpy.nanmean(ma.masked_array(band, 0), axis=0))
    write_tif_image(mean_list, "mean_image")


def write_tif_image(band_list, new_filename):
    if band_list:
        nx = band_list[0].shape[0] #we need that only once
        ny = band_list[0].shape[1]
        number_of_bands = len(band_list)

        # create the n-band raster file
        dst_ds = gdal.GetDriverByName('GTiff').Create(new_filename+'.tif', ny, nx, number_of_bands, gdal.GDT_Float32)
        dst_ds.SetGeoTransform(geo_transform)  # specify coords
        dst_ds.SetProjection(projection)
        for index, data in enumerate(band_list):
            dst_ds.GetRasterBand(index+1).WriteArray(data)
        dst_ds.FlushCache()  # write to disk
        dst_ds = None  # save, close


# calculates and writes the ndvi
#see: http://ceholden.github.io/open-geo-tutorial/python/chapter_2_indices.html
def write_max_ndvi_composite(folder, file):
    # Open a GDAL dataset
    complete_file = os.path.join(folder, file)
    dataset = gdal.Open(complete_file, gdal.GA_ReadOnly)
    set_geo_transform(dataset)
    # Allocate our array using the first band's datatype
    image_datatype = dataset.GetRasterBand(1).DataType

    image = numpy.zeros(
        (dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount),
        dtype=gdal_array.GDALTypeCodeToNumericTypeCode(image_datatype))

    bands = [dataset.GetRasterBand(n + 1).ReadAsArray().astype('float') for n in range(dataset.RasterCount)]

    for index, band in enumerate(bands):
        image[:, :, index] = band

    b_red = 2
    b_nir = 3

    ndvi = (image[:, :, b_nir] - image[:, :, b_red]) / (image[:, :, b_red] + image[:, :, b_nir])
    write_tif_image([ndvi], file+"_ndvi")



# ####################################### PROCESSING ########################################################## #


# exercise 1-3
# create_folder_file_dict()
# create_array_from_files()
# masked_bands = get_masked_band_dict()
# write_mean_image(masked_bands)


# exercice 4
create_folder_file_dict()
sat = "LC81930232015164LGN00"
folder = os.path.join(landsat_home, sat)
files = folder_files_dict[folder]
sr_file = get_sr_file(files)
write_max_ndvi_composite(folder, sr_file)


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
