# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import os
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
buff_m = 100

#path of the data
localhome = os.getcwd()
assignment01DataFolder = "Assignment01_data"
landsatFolder = "Part01_Landsat"
foldername = os.path.join(localhome, assignment01DataFolder, landsatFolder)


# satellite-identifier
l4 = "LT04"
l5 = "LT05"
l7 = "LE07"
l8 = "LC08"

# dictonaries to store satellite-data in
l4list = {}
l5list = {}
l7list = {}
l8list = {}

# ####################################### FUNCTIONS ########################################################### #

def resetSatLists():
    l4list.clear()
    l5list.clear()
    l7list.clear()
    l8list.clear()


# ####################################### PROCESSING ########################################################## #

print("foldername:" + foldername)
if os.path.exists(foldername):
    iterator = os.walk(foldername)
    for item in iterator: #each item is a triple (root,dirs,files)
        item[1].sort()
        if item[1]: #dirs
            print("check footprint: " + item[0])
            for subdir in item[1]:
                pathOfCurrentDir = os.path.join(item[0], subdir)
                fileList = os.listdir(pathOfCurrentDir)
                if subdir.startswith(l4):
                    l4list.update({pathOfCurrentDir: fileList})
                elif subdir.startswith(l5):
                    l5list.update({pathOfCurrentDir: fileList})
                elif subdir.startswith(l7):
                    l7list.update({pathOfCurrentDir: fileList})
                elif subdir.startswith(l8):
                    l8list.update({pathOfCurrentDir: fileList})
                # else:
                #     print("parent file: " + subdir) #ignore others and parent-folder
            print("l4 size: \t\t " + str(len(l4list)))
            print("l5 size: \t\t " + str(len(l5list)))
            print("l7 size: \t\t " + str(len(l7list)))
            print("l8 size: \t\t " + str(len(l8list)))
            print("sum dirs: \t\t " + str(len(l4list)+len(l5list)+len(l7list)+len(l8list)))
            resetSatLists()
            print("---------------")

else:
    print("file does not exist")



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: \t" + starttime)
print("end: \t" + endtime)
print("")