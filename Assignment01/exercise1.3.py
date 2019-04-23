# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import os
import statistics
import re

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
buff_m = 100

# path of the data
localhome = os.getcwd()
assignment01DataFolder = "Assignment01_data"
landsatFolder = "Part02_GIS-Files"
foldername = os.path.join(localhome, assignment01DataFolder, landsatFolder)

# file-endings
# shape-file-source: http://desktop.arcgis.com/de/arcmap/10.3/manage-data/shapefiles/shapefile-file-extensions.htm
# and https://de.wikipedia.org/wiki/Shapefile
shape_files_mandatory = ["shp", "shx", "dbf"]
shape_files_optional = ["sbn", "sbx", "fbn", "fbx", "ain", "aih", "atx", "ixs", "mxs", "prj", "shp.xml", "cpg"]

# list from https://de.wikipedia.org/wiki/GIS-Datenformat, seems to be not heplful
# vector_files = ["dgn", "dwg", "dxf", "E00", "edb", "gdb", "gdf", "gml", "gpkg", "gpx", "iff", "ili", "ilt", "itf",
#                 "xtf", "kml", "kmz", "lay", "mdb", "mif", "mid", "mxd", "sfa", "shp", "shx", "dbf", "geojson"
#                 ]

# raster-file-source: https://www.igismap.com/raster-data-file-format/ and https://de.wikipedia.org/wiki/GIS-Datenformat
raster_files = ["png", "gif", "gpkg", "grid", ".img", "jpg", "tif", "tiff", "jp2", "j2c", "j2k", "jpx",
                "jpg", "jpeg", "jpc", "jpe", "sid", "img", "ovr", "lgg"]

# list to store GIS-data in
gis_dict = []
shape_list = []


# ####################################### FUNCTIONS ########################################################### #


def get_data_from_files():
    # print("foldername:" + foldername)
    if os.path.exists(foldername):
        iterator = os.walk(foldername)
        counter = 0
        for item in iterator:  # each item is a triple (root,dirs,files)
            item[2].sort()
            number_of_files = len(item[2])
            if item[2]:  # files
                templist = []  # save correspondig files in one list
                item[2].sort()  # we assume that corresponding files have the same filnames, but different extensions
                for file in item[2]:
                    counter += 1
                    # file = os.path.join(item[0], file) #if you need the full path, uncomment this line
                    file_split_list = file.split(os.extsep)  # seperate using dots
                    # print(str(file_split_list))
                    if not templist:
                        templist.append(file_split_list)
                    elif file_split_list[0] != templist[-1][0]:  # new set of files
                        gis_dict.append(templist)
                        templist = [file_split_list]
                    elif file_split_list[0] == templist[-1][0]:
                        templist.append(file_split_list)
                    else:
                        print("unexpected: " + str(file_split_list))
            # a bit dirty way for saving the last item TODO: find better way
            if counter == number_of_files:
                gis_dict.append(templist)
    else:
        print(str(foldername) + " - file does not exist")

    # print list
    print("found layers: " + str(len(gis_dict)))
    for entry in gis_dict:
        print("length: " + str(len(entry)))
        print(entry)
    print("--------")


def get_number_of_layers():
    shape_counter = 0
    raster_counter = 0
    stringToWrite = ""
    for corresponding_files in gis_dict:
        shape = is_shapefile(corresponding_files)
        raster = is_rasterfile(corresponding_files)
        if (shape):
            shape_counter += 1
            stringToWrite += shape
        if (raster):
            raster_counter += 1
            stringToWrite += raster

    stringToWrite += "shape-files: " + str(shape_counter) + "\n"
    stringToWrite += "raster-files: " + str(raster_counter)+ "\n"
    return stringToWrite
    # for corresponding_files in gis_dict:


#TODO: find definition of complete shapefile and finish method
def is_shapefile_complete(shapefile_list):
    # With view to the given example data these are the mandatory file-extensions for a complete shapefile.
    # It does not fit to e.g. https://de.wikipedia.org/wiki/Shapefile, which says only shp, dbf and shx are mandatory,
    # But let's get this exercise done...
    # stringToWrite = ""
    for layer in shape_list:
        if len(layer) != 80:
            # print("layer: " + str((layer)))
            print("layer length: " + str(len(layer)))
    # return stringToWrite

#TODO: find definition of complete rasterfile and finish method
def is_rasterfile_complete(files):
    for layer in shape_list:
        if len(layer) != 80:
            print("raster layer length: " + str(len(layer)))


# very simple method to identify shapefiles
def is_shapefile(file_list):
    for file_entry in file_list:
        if file_entry[1] in shape_files_mandatory:
            shape_list.append(file_list)
            # print(str(file_list))
            return str(file_entry[0]) + "\t\t seems to be a shape-file\n"
    return ""

# very simple method to identify shapefiles
def is_rasterfile(file_list):
    for file_entry in file_list:
        if file_entry[1] in raster_files:
            # print(str(file_list))
            return str(file_entry[0]) + "\t\t seems to be a raster-file\n"
    return ""

def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()



# ####################################### PROCESSING ########################################################## #

get_data_from_files()
stringToWrite = ""
stringToWrite = get_number_of_layers()
# print("-----------shapelist: " + (str(len(shape_list))))
# is_shapefile_complete(shape_list)
# is_rasterfile_complete(raster_files)
# filePath = os.path.join(localhome, "answer_exercise1.3.txt")

# print(stringToWrite)
# writeIntoFile(filePath, stringToWrite)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
