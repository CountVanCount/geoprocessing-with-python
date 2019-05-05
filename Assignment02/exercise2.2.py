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
landsat_table_filename = "LANDSAT_8_C1_313804.csv"
landsat_file = os.path.join(data_home, landsat_table_filename)

shapefile_home = os.path.join(localhome, "shapefile_exercise_2.2")
landsat_shapefilename = "LANDSAT_8_C1_313804.shp"
shapefile = os.path.join(shapefile_home, landsat_shapefilename)

raw_values_dict = {}  # dict of dictionaries for data from landsat table, each entry correspnds to a row (dict like {column -> {index -> value}})
filtered_values_dict = {}


# ####################################### FUNCTIONS ########################################################### #


def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()


# reads the data from the landsat-table and writes it to the global variable 'raw_values_dict'
def read_data_from_landsat_table():
    string_to_write = ""
    if landsat_file:
        global raw_values_dict
        # string_to_write += "Observation FilePath: " + observation_file + "\n"
        raw_values_dict = pandas.read_csv(landsat_file, index_col=False).transpose().to_dict()
        string_to_write += "Number of landsat scenes: " + str(len(raw_values_dict)) + "\n"
        string_to_write += str(raw_values_dict[0])
    else:
        print("Observation file does not exist. Check file-path")
    return string_to_write


# reads data from the global variable 'raw_values_dict' and writes the filtered data (corresponding to the filter
# criteria given in the exercise-text) to the global variable 'filtered_values_dict'
def fliter_raw_data():
    global filtered_values_dict
    for key in raw_values_dict:
        if filter_single_landsat_scene(raw_values_dict[key]):
            filtered_values_dict[key] = raw_values_dict[key]

    return "Number of landsat scenes after filtering: " + str(len(filtered_values_dict)) + "\n"


# checks if a given landsat_scene should be filtered out (returns 'False') or not (returns 'True')
def filter_single_landsat_scene(landsat_scene):
    if landsat_scene.get('Day/Night Indicator') != "DAY":
        return False
    if landsat_scene.get('Data Type Level-1') != "OLI_TIRS_L1TP":
        return False
    if landsat_scene.get('Land Cloud Cover') >= 70:
        return False
    return True


# evaluates the data from the given dict (which should be 'raw_values_dict' or 'filtered_values_dict') and returns
# a human readable string of the results
def evaluate_data(dict):
    string_to_write = ""
    if dict:
        # collect data
        geometric_RMSE_Model_X = []
        geometric_RMSE_Model_Y = []
        land_Cloud_Cover = []
        wrsList = list()

        for key in dict:
            x = dict[key].get('Geometric RMSE Model X')
            if x and not math.isnan(x):
                geometric_RMSE_Model_X.append(x)

            y = dict[key].get('Geometric RMSE Model Y')
            if y and not math.isnan(y):
                geometric_RMSE_Model_Y.append(y)

            lcc = dict[key].get('Land Cloud Cover')
            if lcc and not math.isnan(lcc):
                land_Cloud_Cover.append(lcc)

            path = dict[key].get('WRS Path')
            row = dict[key].get('WRS Row')
            if path and not math.isnan(path) and row and not math.isnan(row):
                wrsList.append(str([path, row]))  # a bit dirty, save list as string to make the list hashable

        # create strings
        string_to_write += "Average geometric accuracy X: " + str(statistics.mean(geometric_RMSE_Model_X)) + "\n"
        # string_to_write += "geometric accuracy X list: " + str(geometric_RMSE_Model_X) + "\n"

        string_to_write += "Average geometric accuracy Y: " + str(statistics.mean(geometric_RMSE_Model_Y)) + "\n"
        # string_to_write += "geometric accuracy Y list: " + str(geometric_RMSE_Model_Y) + "\n"

        string_to_write += "Average Land Cloud Cover: " + str(statistics.mean(land_Cloud_Cover)) + "\n"
        # string_to_write += "land_Cloud_Cover list: " + str(land_Cloud_Cover) + "\n"

        unique_wrs_list = list(dict.fromkeys(wrsList))
        string_to_write += "Number of unique WRS Path/Row combination: " + str(len(unique_wrs_list)) + "\n"

        counter_dict = Counter(wrsList).most_common(10)
        string_to_write += "Most common wrs combinations: " + str(counter_dict) + "\n"

    else:
        string_to_write = "Given dict is empty or null."
    return string_to_write


# creates an ESRI shapefile out of filtered_values_dict
def create_esri_file():
    df = pandas.DataFrame(filtered_values_dict).transpose()

    geometry = [Point(xy) for xy in zip(df['UR Corner Lat dec'], df['UR Corner Long dec'])]
    crs = "+init=epsg:4326"  # http://www.spatialreference.org/ref/epsg/4326/
    geo_df = GeoDataFrame(df, crs=crs, geometry=geometry)

    if not os.path.exists(shapefile_home):
        os.makedirs(shapefile_home)

    geo_df.to_file(driver='ESRI Shapefile', filename=shapefile)


# ####################################### PROCESSING ########################################################## #

string_to_write = ""

string_to_write += "----------Before filtering: \n"
string_to_write += read_data_from_landsat_table()
string_to_write += evaluate_data(raw_values_dict)

string_to_write += "\n----------After filtering: \n"
string_to_write += fliter_raw_data()
string_to_write += evaluate_data(filtered_values_dict)

print(string_to_write)

# create_esri_file()

# filePath = os.path.join(localhome, "answer_exercise2.2.txt")
# writeIntoFile(filePath, string_to_write)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
