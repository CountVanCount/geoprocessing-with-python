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
forest_mask_file = os.path.join(data_home, "gpy_poland_forestmask.tif")
vertex_image_file = os.path.join(data_home, "gpy_poland_landtrendr_tcw_vertex_8618.tif")
number_of_bands = 0
geo_transform = None
projection = None


# ####################################### FUNCTIONS ########################################################### #


def get_bands_arr_vertex_image(folder, qa_file):
    ds = gdal.Open(os.path.join(folder, qa_file))
    set_geo_transform_and_projection(ds)

    vertex_array = ds.ReadAsArray() #[22 vertices/layer, y=461, x=514]
    transposed = numpy.transpose(vertex_array)
    fitted_values_array = transposed[:, :, 14:21]
    fitted_values_array[fitted_values_array < 500] = 0 #filter out all values < 500
    dif_array = numpy.diff(fitted_values_array)



    # nx = band_list[0].shape[0]  # we need that only once
    # ny = band_list[0].shape[1]

    return vertex_array




def get_masked_band_dict():

    arr = get_np_array_for_mask_file(data_home, forest_mask_file)
    fct = numpy.vectorize(check_qa_file_pixel, otypes=[numpy.float])
    mask_arr = fct(arr)


    # mask_array = get_mask_for_np_array_from_qa_file(qa_arr)
    # folder_mask_dict[folder] = mask_array

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



def check_qa_file_pixel(pixel_value):
    if pixel_value == 1 :
        return False
    else:
        return True

def get_np_array_for_mask_file(folder, qa_file):
    ds = gdal.Open(os.path.join(folder, qa_file))
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    return arr

def set_geo_transform_and_projection(ds):
    global geo_transform
    global projection
    if not geo_transform: #set once
        geo_transform = ds.GetGeoTransform()
        projection = ds.GetProjection()
        print("Geotransform is set to: " + str(geo_transform))
        print("Projection is set to: " + str(projection))



# def get_masked_band_dict():
#     init dict of list
#     band_dict = {} #key = number of band, value = list of arrays, from each file
#     for item in range(0, number_of_bands):
#         band_dict[item] = []
#
    # get data from each file, calulate masked-array and save sorted by band
    # for folder, bands in folder_array_dict.items():
    #     mask = folder_mask_dict[folder]
    #     for index, band_array in enumerate(bands):
    #         masked_array = ma.masked_array(band_array, mask=mask)
    #         band_dict[index].append(masked_array.filled(numpy.nan)) #fill masked array with NaNs
    # return band_dict


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



# ####################################### PROCESSING ########################################################## #


get_bands_arr_vertex_image(data_home, vertex_image_file)
# get_masked_band_dict()

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
