# ############################################################################################################# #
# Raw-example for a basic script to be executed in python. The format is only a recommendation and everyone is  #
# encouraged to modify the scripts to her/his own needs.                                                        #
# (c) Matthias Baumann, Humboldt-Universität zu Berlin, 4/15/2019                                               #
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import os
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
SHP = "L:/_SHARED_DATA/CL_MB/tc_sc/_Version02_300m/points_300m_clip.shp"
outputFile = "L:/_SHARED_DATA/CL_MB/tc_sc/_Version02_300m/points_300m_clip_summary.shp"
buff_m = 100
# ####################################### FUNCTIONS ########################################################### #

# ####################################### PROCESSING ########################################################## #




# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")