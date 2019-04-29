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
data_home = os.path.join(localhome, "data")
primary_table_file = "DE_2015_20180724.csv"
grid_table_file = "GRID_CSVEXP_20171113.csv"


# ####################################### FUNCTIONS ########################################################### #


def writeIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()



# ####################################### PROCESSING ########################################################## #

print(data_home)

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
