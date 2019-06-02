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

# for tif-file-writing
geo_transform = None
projection = None


# ####################################### FUNCTIONS ########################################################### #


def get_bands_arr_vertex_image(folder, vertex_file):
    ds = gdal.Open(os.path.join(folder, vertex_file))
    set_geo_transform_and_projection(ds)

    vertex_array = ds.ReadAsArray().astype('float')  # [22 vertices/layer, y=461, x=514]
    # transposed = numpy.transpose(vertex_array)
    # fitted_values_array = transposed[:, :, 14:21]
    # fitted_values_array[fitted_values_array < 500] = 0 #filter out all values < 500
    # dif_array = numpy.diff(fitted_values_array)

    # nx = band_list[0].shape[0]  # we need that only once
    # ny = band_list[0].shape[1]

    return vertex_array


def set_geo_transform_and_projection(ds):
    global geo_transform
    global projection
    if not geo_transform:  # set once
        geo_transform = ds.GetGeoTransform()
        projection = ds.GetProjection()
        print("Geotransform is set to: " + str(geo_transform))
        print("Projection is set to: " + str(projection))


def get_mask_array(folder, mask_file):
    ds = gdal.Open(os.path.join(folder, mask_file))
    mask_array = ds.ReadAsArray()
    mask_array = mask_array ^ 1 #invertes 1 and 0 -> ma.masked_array takes 1 as invalid and 0 as valid
    return mask_array


def generate_masked_array(vertex_array, mask_array):
    for i in range(0, vertex_array.shape[0]):
        vertex_array[i, :, :] = ma.masked_array(vertex_array[i, :, :], mask_array).filled(numpy.nan)
    return vertex_array


def is_shape_equal(np_array1, np_array2):
    print(np_array1.shape)
    print(np_array2.shape)
    return np_array1.shape == np_array2.shape


def write_tif_image(band_list, new_filename):
    if band_list:
        nx = band_list[0].shape[0]  # we need that only once
        ny = band_list[0].shape[1]
        number_of_bands = len(band_list)

        # create the n-band raster file
        dst_ds = gdal.GetDriverByName('GTiff').Create(new_filename + '.tif', ny, nx, number_of_bands, gdal.GDT_Float32)
        dst_ds.SetGeoTransform(geo_transform)  # specify coords
        dst_ds.SetProjection(projection)
        for index, data in enumerate(band_list):
            dst_ds.GetRasterBand(index + 1).WriteArray(data)
        dst_ds.FlushCache()  # write to disk
        dst_ds = None  # save, close


# ####################################### PROCESSING ########################################################## #


vertex_array = get_bands_arr_vertex_image(data_home, vertex_image_file)
mask_array = get_mask_array(data_home, forest_mask_file)
masked_array = generate_masked_array(vertex_array, mask_array)
print(masked_array.shape)

years_array = masked_array[0:7, :, :]
fitted_value_array = masked_array[14:21, :, :]

dif = numpy.diff(fitted_value_array, axis=0)
print(dif.shape)



dif[numpy.isnan(dif)] = 0
max_over_years = numpy.nanargmax(dif, axis=0)
print(max_over_years.shape)
print(numpy.version.version)
gdyear = numpy.take(years_array[0:6, :, :], max_over_years[numpy.newaxis, :, :], 0)
    # .squeeze()
print(gdyear.shape)

# if (is_shape_equal(vertex_array, mask_array)):
#     print("sind gleich")
#
# first = vertex_array[0:1, :, :]
# masked_array = ma.masked_array(first, mask_array)
# filled = masked_array.filled(numpy.nan)
# print(filled)
# print(masked_array)




# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
