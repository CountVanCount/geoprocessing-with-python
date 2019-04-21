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
landsatFolder = "Part01_Landsat"
foldername = os.path.join(localhome, assignment01DataFolder, landsatFolder)

# satellite-identifier - files associated to sats seem to begin with these strings
l4 = "LT04"
l5 = "LT05"
l7 = "LE07"
l8 = "LC08"

# dictonaries to store satellite-data in
l4dict = {}
l5dict = {}
l7dict = {}
l8dict = {}


# ####################################### FUNCTIONS ########################################################### #

def resetSatLists():
    l4dict.clear()
    l5dict.clear()
    l7dict.clear()
    l8dict.clear()


# iterates over the folders, subfolders and files and writes the filenames into the global dictionaries corresponding to
# its filename-beginnings
# key = directory-path
# value = list of filenames
def getDateFromFiles():
    # print("foldername:" + foldername)
    if os.path.exists(foldername):
        iterator = os.walk(foldername)
        for item in iterator:  # each item is a triple (root,dirs,files)
            item[1].sort()
            if item[1]:  # dirs
                for subdir in item[1]:
                    path_of_current_dir = os.path.join(item[0], subdir)
                    file_list = os.listdir(path_of_current_dir)
                    if subdir.startswith(l4):
                        l4dict.update({path_of_current_dir: file_list})
                    elif subdir.startswith(l5):
                        l5dict.update({path_of_current_dir: file_list})
                    elif subdir.startswith(l7):
                        l7dict.update({path_of_current_dir: file_list})
                    elif subdir.startswith(l8):
                        l8dict.update({path_of_current_dir: file_list})
                    # else:
                    #     print("parent file: " + subdir) #ignore others and parent-folder
    else:
        print(str(foldername) + " - file does not exist")


# this method assumes, that the median of the length of the given dictonary-values is the correct number of files
def checkCorrectNumberOfFilesInScene(dictonary):
    lengthList = []
    for values in dictonary.values():
        lengthList.append(len(values))
    ret = statistics.median(lengthList)
    return ret


def writeCorruptSceneIntoFile(filePath, textToWrite):
    with open(filePath, 'w') as f:
        f.write(textToWrite)
    f.close()


def getCorruptedScenes(dictonary):
    stringToWrite = ""
    numberOfExpectedFiles = checkCorrectNumberOfFilesInScene(dictonary)
    for key, value in dictonary.items():
        if len(value) != numberOfExpectedFiles:
            shortpath = re.sub(localhome, '', key)
            stringToWrite += str(shortpath) + " \t- should be " + str(int(numberOfExpectedFiles)) \
                             + " files, but is " + str(len(value)) + "\n"
    if not stringToWrite:
        stringToWrite += "No corrupted scenes found (should be " + str(int(numberOfExpectedFiles)) \
                         + " files in each) \n"
    return stringToWrite


# ####################################### PROCESSING ########################################################## #

getDateFromFiles()

stringToWrite = ""

filePath = os.path.join(localhome, "answer_exercise1.2.txt")

stringToWrite += "--------- " + str("l14") + " ---------\n"
stringToWrite += getCorruptedScenes(l4dict)

stringToWrite += "--------- " + str("l15") + " ---------\n"
stringToWrite += getCorruptedScenes(l5dict)

stringToWrite += "--------- " + str("l17") + " ---------\n"
stringToWrite += getCorruptedScenes(l7dict)

stringToWrite += "--------- " + str("l18") + " ---------\n"
stringToWrite += getCorruptedScenes(l8dict)

# print(stringToWrite)
writeCorruptSceneIntoFile(filePath, stringToWrite)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")
