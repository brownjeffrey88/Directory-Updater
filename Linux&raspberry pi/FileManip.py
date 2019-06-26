import time
from datetime import date, datetime, timedelta
import os
import shutil
from Data import catalog

images_Directory = "/home/pi/Pictures"
replacements_Directory = "/home/pi/Pictures/Replacements"
# pulls all image files and dates to the images dict from the data.py file
images = catalog


# check to see if the catalog is empty, if it is, add every .png to the images dict. if it isnt empty, check for new
# files in images_directory and add them to the catalog ----needs to happen before check expired images
def catalogCheck():
    changes = False
    directory = os.fsencode(images_Directory)
    if len(images) == 0:
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".png"):
                images[str(filename)] = "12/31/2099"
            else:
                continue
        changes = True
    else:
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".png"):
                if filename in images:
                    continue
                else:
                    images[str(filename)] = "12/31/2099"
                    changes = True
    if changes:
        print("saving changes")
        updateCatalog()
    else:
        print("catalog up to date")


# checks images dict for files with dates that have passed, if the date has passed, replace the file with a renamed blank
# and send an email to marketing that tells them its expired ----needs to be run before check messages
def checkExpiredImages():
    todaysDate = time.strptime((str(date.today().strftime("%m/%d/%Y"))), "%m/%d/%Y")
    for x in images:
        checkDate = images.get(x)
        todaysDate = time.strptime((str(date.today().strftime("%m/%d/%Y"))), "%m/%d/%Y")
        expireDate = time.strptime(checkDate, "%m/%d/%Y")
        if expireDate < todaysDate:
            print(x, "image old replacing with blank")
            replaceFile(x, "blank.png")
            setDate(x, "12/31/2099")
            sendMessage("jbrown@nceent.com", x + "'s expiration date has passed, need to update image ",
                        "image has been replaced with a blank slide")
        else:
            print("date valid")


# sets the date of x file, updates data.py files after setting a date.
def setDate(file, date):
    images[file] = date
    updateCatalog()


# overwrites the data.py file will all the data in the images dict
def updateCatalog():
    with open("Data.py", "w") as dataFile:
        dataFile.write("catalog = " + str(images))
    dataFile.close()


# takes a file and replaces another
def replaceFile(imageToUse, imageToReplace):
    # look for image to use to make sure replacement executes properly, if its not found, copy it from the main directory
    found = False
    for file in os.listdir(replacements_Directory):
        filename = os.fsdecode(file)
        if filename == imageToUse:
            found = True
            # print("file found no need to copy")
            continue
    if found == False:
        shutil.copy(os.path.join(images_Directory, imageToUse), replacements_Directory)
        found = True
        # print("file not found copying")

    os.replace(os.path.join(replacements_Directory, imageToUse), os.path.join(images_Directory, imageToReplace))
    # print("file replaced")
    shutil.copy(os.path.join(images_Directory, imageToUse), replacements_Directory)
    # print("new file copy made in replacements directory\n\n")

catalogCheck()