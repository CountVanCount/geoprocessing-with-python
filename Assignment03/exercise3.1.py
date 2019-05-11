# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
# due to problems with python 3.7, run this with version 3.6
import time
import os
import statistics
import math
from collections import Counter
import pandas as pandas
from Onboard.utils import Rect
from geopandas import GeoDataFrame
from shapely.geometry import Point
from shapely.geometry import box
import gdal
import numpy
import itertools
from collections import namedtuple


# ####################################### SET TIME-COUNT ###################################################### #

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #

# path of the data
localhome = os.getcwd()
data_home = os.path.join(localhome, "data")
tif2000 = "tileID_410_y2000.tif"
tif2000_file = os.path.join(data_home, tif2000)

tif2005 = "tileID_410_y2005.tif"
tif2005_file = os.path.join(data_home, tif2005)

tif2010 = "tileID_410_y2010.tif"
tif2010_file = os.path.join(data_home, tif2010)

tif2015 = "tileID_410_y2015.tif"
tif2015_file = os.path.join(data_home, tif2015)

tif2018 = "tileID_410_y2018.tif"
tif2018_file = os.path.join(data_home, tif2018)

uper_left_intersec = ()
lower_right_intersec = ()
# ####################################### FUNCTIONS ########################################################### #


def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()


# Identifies what the overlap area between the different raster files is (i.e., the maximum common extent).
# Prints out the coordinates of all four corners (rounded to three decimals)
def find_overlap_area(file_list):
    print("---Try to find overlaping areas.")
    global uper_left_intersec
    global lower_right_intersec
    geo_transform_list = []
    rect_points_list = []
    for file in file_list:

        gdal_dataset = gdal.Open(file)
        geo_transform = gdal_dataset.GetGeoTransform() #Fetch the affine transformation coefficients
        geo_transform_list.append(geo_transform)

        width = gdal_dataset.RasterXSize
        height = gdal_dataset.RasterYSize

        rect_points = calculate_all_corners(geo_transform, width, height)
        rect_points_list.append(rect_points)

        # print(calculate_all_corners(inv_gt, ))

        # projection = gdal_dataset.GetProjection()
        # print(projection)
        # origin = Point(geo_transform[0], geo_transform[3])
        # print (origin)
        print("-------------")
    isPixelSizeOkay = check_pixelSize_and_pixelRotation(geo_transform_list)
    uper_left_intersec = calculate_upper_left(rect_points_list)
    lower_right_intersec = calculate_lower_right(rect_points_list)

    for gt in geo_transform_list:
        print("original: \t" + str(gt))
        inv_gt = gdal.InvGeoTransform(gt)
        print("invers: \t" + str(inv_gt))

        image_coord = calculate_image_coord(inv_gt, uper_left_intersec[0],
                                            uper_left_intersec[1] + width * geo_transform[4] + height * geo_transform[5])
        # image_coord = calculate_image_coord(inv_gt, geo_transform[0],
        #                                     geo_transform[3] + width * geo_transform[4] + height * geo_transform[5])

        print(image_coord)


def calculate_image_coord(inv_gt, x, y):
    offsets = gdal.ApplyGeoTransform(inv_gt, x, y)
    xoff, yoff = map(int, offsets)
    return (xoff, yoff)

    # value = band.ReadAsArray(xoff, yoff, 1, 1)[0, 0]


#source: https://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file
def calculate_all_corners(geo_transform, width, height):
    minx = geo_transform[0]
    miny = geo_transform[3] + width * geo_transform[4] + height * geo_transform[5]
    maxx = geo_transform[0] + width * geo_transform[1] + height * geo_transform[2]
    maxy = geo_transform[3]
    return print_corners(minx, miny, maxx, maxy)

def print_corners_from_2_points(uper_left, lower_right):
    return print_corners(uper_left[0], uper_left[1], lower_right[0], lower_right[1])

def print_corners(minx, miny, maxx, maxy):
    uper_left = (minx, miny)
    uper_right = (maxx, miny)
    lower_left = (minx, maxy)
    lower_right = (maxx, maxy)
    print("Coordinates of the 4 Corners: ")
    print("uper_left: \t\t" + str(uper_left))
    print("uper_right: \t" + str(uper_right))
    print("lower_left: \t" + str(lower_left))
    print("lower_right: \t" + str(lower_right))
    return (uper_left, lower_right)


def calculate_upper_left(rect_points_list):
    upper_left_x_list = []
    upper_left_y_list = []
    for rect_points in rect_points_list:
        upper_left_x_list.append(rect_points[0][0])
        upper_left_y_list.append(rect_points[0][1])
    return (numpy.amax(upper_left_x_list), numpy.amax(upper_left_y_list))

def calculate_lower_right(rect_points_list):
    lower_right_x_list = []
    lower_right_y_list = []
    for rect_points in rect_points_list:
        lower_right_x_list.append(rect_points[1][0])
        lower_right_y_list.append(rect_points[1][1])
    return (numpy.min(lower_right_x_list), numpy.min(lower_right_y_list))




def check_pixelSize_and_pixelRotation(geo_transform_list):
    if geo_transform_list and len(geo_transform_list) > 1:
        current = geo_transform_list[0]
        for geo_transform in geo_transform_list:
            if (current[1] != geo_transform[1]):
                print("Pixel width is not equal")
                return False #Pixel width
            if (current[5] != geo_transform[5]):
                print("Pixel height is not equal")
                return False
            if (current[2] != geo_transform[2]):
                print("X-Pixel rotation is not equal")
                return False
            if (current[4] != geo_transform[4]):
                print("Y-Pixel rotation is not equal")
                return False
            current = geo_transform
        return True
    return False


def print_geotransform_list(geo_transform_list):
    string_to_write = ""
    for geo_transform in geo_transform_list:
        string_to_write += "geo_transform: " + str(geo_transform) + "\n"
    print(string_to_write)
    return string_to_write


# Applies image slicing using numpy.
# Loads the part of the raster files into individual arrays that is contained in the overlap area.
# Prints out the size of the overlap (i.e., the array dimensions)
def slice_image():
    print("---Try to slize images")

    print("Size of the overlap-Array-Size")
    string_to_write = ""
    if tif2000_file:
        ds = gdal.Open(tif2000_file)
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
        arr = arr[0:2, 0:1]  # row 1,
        string_to_write += str(arr)

        # arr_min = arr.Min()
        # arr_max = arr.Max()
        # arr_mean = int(arr.mean())
        # string_to_write += str(arr_min +", " +arr_max +", " +arr_mean +"\n")

    else:
        print("tif file does not exist. Check file-path")
    return string_to_write


# Calculates the mean, median, min, max, range, standard deviation for each year.
# Calculate the same statistics for the image differences between 2000-2010, and 2010-2018.
def do_statistics():
    print("---do_statistics")



# ####################################### PROCESSING ########################################################## #

string_to_write = ""



# string_to_write += read_data_from_tif_file()
#
print(string_to_write)
file_list =[tif2000_file, tif2005_file, tif2010_file, tif2015_file, tif2018_file]
# file_list =[tif2000_file, tif2005_file]
find_overlap_area(file_list)
print_corners_from_2_points(uper_left_intersec, lower_right_intersec)

# filePath = os.path.join(localhome, "answer_exercise2.2.txt")
# writeIntoFile(filePath, string_to_write)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
