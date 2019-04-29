# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import os
import pandas
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
data_home = os.path.join(localhome, "data")
primary_table_filename = "DE_2015_20180724.csv"
observation_file = os.path.join(data_home, primary_table_filename)
grid_table_filename = "GRID_CSVEXP_20171113.csv"


# ####################################### FUNCTIONS ########################################################### #


def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()


# ####################################### PROCESSING ########################################################## #


#read: https://pandas.pydata.org/pandas-docs/stable/reference/frame.html
# Filter criteria:
# • OBS_TYPE = 1
# • OBS_DIRECT = 1
# • OBS_RADIUS <= 2
# • AREA_SIZE >= 2
# • FEATURE_WIDTH > 1
# • LC1_PCT >= 5

print(observation_file)
data_frame = pandas.read_csv(observation_file)
values = data_frame.values
# values = data_frame.to_numpy() #New in version 0.24.0.
print("number of values: " + str(len(values)))
counter = 0
number_to_print = 1
print(data_frame.columns)
# print(data_frame.columns.values)

# for label, content in data_frame.iteritems():
#     if (number_to_print == counter):
#         break
#     print(label)
#     print(content)
#     counter += 1


# examples
# x = [1, 2, 3]
# y = ["a", "b", "c"]
# zipped = zip(x, y)
# for item in zipped:
#     print(item)

# for item in enumerate(y):
#     print(item)


# get_data_from_files()
# stringToWrite = ""
# stringToWrite = get_number_of_layers()
# print("-----------shapelist: " + (str(len(shape_list))))

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
