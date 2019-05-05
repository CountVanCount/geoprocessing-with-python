# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
# due to problems with python 3.7, run this with version 3.6
import time
import os
import statistics
import copy
from collections import Counter
import pandas as pandas
from geopandas import GeoDataFrame
from shapely.geometry import Point

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
primary_table_filename = "DE_2015_20180724.csv"
observation_file = os.path.join(data_home, primary_table_filename)
grid_table_filename = "GRID_CSVEXP_20171113.csv"
grid_file = os.path.join(data_home, grid_table_filename)

shapefile_home = os.path.join(localhome, "shapefile")
filtered_shapefilename = "filtered_DE_2015_20180724.shp"
shapefile = os.path.join(shapefile_home, filtered_shapefilename)

raw_values_dict = {}  # dict of dictionaries for data from primary table, each entry correspnds to a row (dict like {column -> {index -> value}})
filtered_values_dict = {}


# ####################################### FUNCTIONS ########################################################### #


def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()


# reads the data from the primary-table and writes it to the global variable 'raw_values_dict'
def read_data_from_primary_table():
    string_to_write = ""
    if observation_file:
        global raw_values_dict
        # string_to_write += "Observation FilePath: " + observation_file + "\n"
        raw_values_dict = pandas.read_csv(observation_file, index_col=False).transpose().to_dict()
        string_to_write += "Number of sampling points before filtering: " + str(len(raw_values_dict)) + "\n"
    else:
        print("Observation file does not exist. Check file-path")
    return string_to_write


# reads data from the global variable 'raw_values_dict' and writes the filtered data (corresponding to the filter
# criteria given in the exercise-text) to the global variable 'filtered_values_dict'
def fliter_raw_data():
    global filtered_values_dict
    filtered_values_dict = copy.deepcopy(raw_values_dict)

    for key in raw_values_dict:
        #old version: add
        # if filter_single_sampling_point(raw_values_dict[key]):
        #     filtered_values_dict[key] = raw_values_dict[key]

        #new version, using deepcopy and pop from it
        if not filter_single_sampling_point(raw_values_dict[key]):
            filtered_values_dict.pop(key, None)

    return "Number of sampling points after filtering: " + str(len(filtered_values_dict)) + "\n"


# checks if a given sampling_point should be filtered out (returns 'False') or not (returns 'True')
def filter_single_sampling_point(sampling_point):
    if sampling_point.get('OBS_TYPE') != 1:
        return False
    if sampling_point.get('OBS_DIR') != 1:  # in exercise 1 it is called 'OBS_DIRECT'-but this seems to be what is meant
        return False
    if sampling_point.get('OBS_RADIUS') > 3:
        return False
    if sampling_point.get('AREA_SIZE') < 2:
        return False
    if sampling_point.get('FEATURE_WIDTH') <= 1:
        return False
    if sampling_point.get('LC1_PCT') < 5:
        return False
    return True


# evaluates the data from the given dict (which should be 'raw_values_dict' or 'filtered_values_dict') and returns
# a human readable string of the results
def evaluate_data(dict):
    string_to_write = ""
    if dict:
        #collect data
        land_cover_classes = []
        observer_distance = []
        class_A21_observer_distance = []


        for key in dict:
            land_cover_classes.append(dict[key].get('LC1'))
            observer_distance.append(dict[key].get('OBS_DIST'))

            if dict[key].get('LC1') == "A21":
                class_A21_observer_distance.append(dict[key].get('OBS_DIST'))

        #create strings
        land_cover_classes_set = set(land_cover_classes)
        string_to_write += "Number of land cover classes (LC1): " + str(len(land_cover_classes_set)) + "\n"
        # string_to_write += "land cover classes (LC1): " +str(land_cover_classes_set) + "\n"

        string_to_write += "Average observer distance (OBS_DIST): " + str(statistics.mean(observer_distance)) + "\n"
        # string_to_write += "observer distance list: " + str(observer_distance) + "\n"

        string_to_write += "Average observer distance (OBS_DIST) of land cover class(LC1) 'A21': " + str(
            statistics.mean(class_A21_observer_distance)) + "\n"
        # string_to_write += "observer distance list of class A21: " + str(class_A21_observer_distance) + "\n"

        counter_dict = Counter(land_cover_classes).most_common(1)
        string_to_write += "Number of most common samples in land cover class (LC1): " + str(counter_dict) + "\n"
    else:
        string_to_write = "Given dict is empty or null."
    return string_to_write


# merges the filtered_values_dict and the gridfile and composes an ESRI shapefile
def create_esri_file():
    grid = pandas.read_csv(grid_file)
    df = pandas.DataFrame(filtered_values_dict).transpose()
    ds = pandas.merge(grid, df)

    geometry = [Point(xy) for xy in zip(df.GPS_LONG, df.GPS_LAT)]
    crs = "+init=epsg:4326"  # http://www.spatialreference.org/ref/epsg/4326/
    geo_df = GeoDataFrame(df, crs=crs, geometry=geometry)

    if not os.path.exists(shapefile_home):
        os.makedirs(shapefile_home)

    geo_df.to_file(driver='ESRI Shapefile', filename=shapefile)


# ####################################### PROCESSING ########################################################## #

string_to_write = ""

string_to_write += "----------Before filtering: \n"
string_to_write += read_data_from_primary_table()
string_to_write += evaluate_data(raw_values_dict)

string_to_write += "\n----------After filtering: \n"
string_to_write += fliter_raw_data()
string_to_write += evaluate_data(filtered_values_dict)

print(string_to_write)

create_esri_file()

# filePath = os.path.join(localhome, "answer_exercise2.1.txt")
# writeIntoFile(filePath, string_to_write)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
