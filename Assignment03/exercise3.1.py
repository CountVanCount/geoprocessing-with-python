# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
# due to problems with python 3.7, run this with version 3.6
import time
import os
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

intersec_dict = {} #key=filname, value=tuple of array-positions, wher the data should be sliced
intersect_array_dict = {}

# ####################################### FUNCTIONS ########################################################### #


def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()


# Identifies what the overlap area between the different raster files is (i.e., the maximum common extent).
# Prints out the coordinates of all four corners (rounded to three decimals)
def find_overlap_area(file_list):
    print("---Try to find overlaping areas.")
    global intersec_dict
    geo_transform_dict = {}
    UL_and_LR_tuple_list = []
    #collect the geodatatransforms and corners of all files
    for file in file_list:
        #geodatatransform
        gdal_dataset = gdal.Open(file)
        geo_transform = gdal_dataset.GetGeoTransform() #Fetch the affine transformation coefficients
        geo_transform_dict[file] = geo_transform

        #corners
        width = gdal_dataset.RasterXSize
        height = gdal_dataset.RasterYSize
        UL_and_LR_tuple = calculate_UL_and_LR(geo_transform, width, height)
        UL_and_LR_tuple_list.append(UL_and_LR_tuple)
        print("UL_and_LR_tuple: " + str(UL_and_LR_tuple))
        print("-------------")

    # for further calculations we got to be sure that pixelSize and rotation is the same in all geotransforms
    if check_pixelSize_and_pixelRotation(list(geo_transform_dict.values())):

        #do the intersection using the corner-data
        uper_left_intersec = calculate_upper_left(UL_and_LR_tuple_list)
        lower_right_intersec = calculate_lower_right(UL_and_LR_tuple_list)
        print("uper_left_intersec " + str(uper_left_intersec))
        print("lower_right_intersec " + str(lower_right_intersec) + "\n")
        #calculate the pixel-coords of the intersec-corners for each geotransorm
        for file, gt in geo_transform_dict.items():
            inv_gt = gdal.InvGeoTransform(gt)

            image_coord_UL = calculate_image_coord(inv_gt, uper_left_intersec[0], uper_left_intersec[1])
            image_coord_LR = calculate_image_coord(inv_gt, lower_right_intersec[0], lower_right_intersec[1])
            print("Array-Coords for intersection: "+ str(file))
            print(str(image_coord_UL) + " / " + str(image_coord_LR))
            intersec_dict[file] = (image_coord_UL, image_coord_LR)

            #print out all 4 corners
            calculate_corners(image_coord_UL[0], image_coord_UL[1], image_coord_LR[0], image_coord_LR[1])
            print("-------------")


def calculate_image_coord(inv_gt, x, y):
    offsets = gdal.ApplyGeoTransform(inv_gt, x, y)
    xoff, yoff = map(int, offsets)
    return (xoff, yoff)


#source: https://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file
def calculate_UL_and_LR(geo_transform, width, height):
    minx = geo_transform[0]

    # this is the solution from stackoverflow, but why should width*pixelwidth be added to the y-axis-minimum?
    # miny = geo_transform[3] + width * geo_transform[4] + height * geo_transform[5]
    miny = geo_transform[3] + height * geo_transform[5]

    #this is the solution from stackoverflow, but why should height*pixelheight be added to the x-axis-maximum?
    # maxx = geo_transform[0] + width * geo_transform[1] + height * geo_transform[2]
    maxx = geo_transform[0] + width * geo_transform[1]
    maxy = geo_transform[3]
    # return print_corners(minx, miny, maxx, maxy)
    return calculate_corners(minx, maxy, maxx, miny) #minx/maxy = UL, maxx/miny = LR)

def print_corners_from_2_points(uper_left, lower_right):
    return calculate_corners(uper_left[0], uper_left[1], lower_right[0], lower_right[1])

def calculate_corners(minx, maxy, maxx, miny):
    uper_left = (minx, maxy)
    uper_right = (maxx, maxy)
    lower_left = (minx, miny)
    lower_right = (maxx, miny)
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
    return (numpy.amax(upper_left_x_list), numpy.amin(upper_left_y_list))

def calculate_lower_right(rect_points_list):
    lower_right_x_list = []
    lower_right_y_list = []
    for rect_points in rect_points_list:
        lower_right_x_list.append(rect_points[1][0])
        lower_right_y_list.append(rect_points[1][1])
    return (numpy.min(lower_right_x_list), numpy.amax(lower_right_y_list))



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


def slice_all_images():
    string_to_write = ""
    for key, value in intersec_dict.items():
        string_to_write += slice_image(key, value)
    return string_to_write

# Applies image slicing using numpy.
# Loads the part of the raster files into individual arrays that is contained in the overlap area.
# Prints out the size of the overlap (i.e., the array dimensions)
def slice_image(file, array_coords):
    string_to_write = ""
    string_to_write += "\n---Try to slize image: " + str(file) + "\n"
    string_to_write +="array_coords: " + str(array_coords)+ "\n"
    if file:
        ds = gdal.Open(file)
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()

        # slicing: in numpy the syntax is (y/x) respectively (row/column)
        arr = arr[array_coords[0][1]:array_coords[1][1], array_coords[0][0]:array_coords[1][0]]
        # string_to_write += "after slicing: \n" + do_statistics(file, arr)

        intersect_array_dict[file] = arr
    else:
        string_to_write += "tif file does not exist. Check file-path"
    return string_to_write

def do_statistic_all_files():
    string_to_write = ""
    for key in intersect_array_dict:
        string_to_write += do_statistics_for_file(key, intersect_array_dict[key]) + "\n"
    return string_to_write


def do_statistics_for_file(file, arr):
    file = str(ntpath.basename(file))
    return do_statistics_for_string(file, arr)

# Calculates the mean, median, min, max, range, standard deviation for each year.
# Calculate the same statistics for the image differences between 2000-2010, and 2010-2018.
def do_statistics_for_string(text, arr):
    string_to_write = "---do statistics for " + text + "\n"
    if len(arr) > 0:
        # string_to_write += str(arr)
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


def calculate_image_def(minuend, subtrahend):
    string_to_write = ""
    if minuend in intersect_array_dict and subtrahend in intersect_array_dict:
        arr_minuend = intersect_array_dict[minuend]
        arr_subtrahend = intersect_array_dict[subtrahend]
        sub = arr_minuend-arr_subtrahend
        # file = str(ntpath.basename(file))
        string_to_write += do_statistics_for_string(str(ntpath.basename(minuend)) + " - " + str(ntpath.basename(subtrahend)), sub)
    else:
        string_to_write = "Error in calculate_image_def, file not in intersect_array_dict"
    return string_to_write

# ####################################### PROCESSING ########################################################## #

file_list =[tif2000_file, tif2005_file, tif2010_file, tif2015_file, tif2018_file]
find_overlap_area(file_list)
print("\nintersec_dict: ")
print(intersec_dict)

print(slice_all_images())
print(do_statistic_all_files())
print(calculate_image_def(tif2000_file, tif2010_file))
print(calculate_image_def(tif2010_file, tif2018_file))

# filePath = os.path.join(localhome, "answer_exercise3.txt")
# writeIntoFile(filePath, string_to_write)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
