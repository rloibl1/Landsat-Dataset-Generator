# Todo: Check that the random selection of non_aiports tiles is working properly, theres seems to be little variation
# This script moves all tiles from separate entityID folders into shared folders by class & band

import os
from shutil import copyfile
from darkness_filter import checkTile
from random import randint

# Creates a directory if one doesn't exist
def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Check if a file exists at the specified path
def fileExist(path):
    if os.path.exists(path):
        return True
    else:
        return False

def airportsMove(loadPath, savePath):
    # Tracks the number of airports that were moved so that an equal number of non airports can be moved
    num_airports = 0

    # Make sure every airport has an image in these bands
    band_labels = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']

    # Airport Sub-Types
    sub_classes = os.listdir(loadPath)
    sub_classes.remove('all_airports')

    for airport_type in sub_classes:
        # Listing of all folders containing images
        entityIDs = os.listdir(os.path.join(loadPath, airport_type))
        for entityID in entityIDs:
            images = os.listdir(os.path.join(loadPath, airport_type, entityID))
            unique_names = set()
            for img in images:
                # Get names of each airport in directory
                unique_names.add(img.split('_')[0])

            # Check that each airport has a full compliment of bands (Band 2 - Band 8)
            for name in unique_names:
                move_airport = True
                # Check if each band is present
                for band in band_labels:
                    filename = name + '_' + band + '.TIF'
                    if fileExist(os.path.join(loadPath, airport_type, entityID, filename)) == False:
                        move_airport = False
                        # print(name, 'missing', band)

                # If the airport has all bands move the files into new folders
                if move_airport == True:
                    num_airports += 1
                    # Move images band by band
                    for band in band_labels:
                        filename = name + '_' + band + '.TIF'
                        oldFilePath = os.path.join(loadPath, airport_type, entityID, filename)
                        newFilePath = os.path.join(savePath, 'airports', band, filename)
                        # Handle name conflicts for multiple images of same airport
                        i = 0
                        while (fileExist(newFilePath)):
                            newFileName = name + '_' + band + '_' + str(i) + '.TIF'
                            newFilePath = os.path.join(savePath, 'airports', band, newFileName)
                            i += 1
                        # Move the file
                        copyfile(oldFilePath, newFilePath)
    return num_airports

def non_airportsMove(loadPath, savePath, quantity):
    num_moved = 0
    selected_tiles = set()
    print('Moving', quantity, 'non_airports')
    # Make sure every on airport has an image in these bands
    band_labels = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']

    # List entityIDs
    entityIDs = os.listdir(loadPath)

    # Selects one tile round-robin from each entityID until the num of non_airports equals the num airports
    while 1:
        for entityID in entityIDs:
            if num_moved < quantity:
                imgs = os.listdir(os.path.join(loadPath, entityID))
                if len(imgs) != 0:
                    # Select random image from directory
                    rand_index = randint(0, len(imgs) - 1)
                    img = imgs[rand_index]
                    name = img.split('_')[0]

                    # Check if this tile was selected already
                    before_add = len(selected_tiles)
                    selected_tiles.add(os.path.join(entityID, img))
                    after_add = len(selected_tiles)

                    if before_add != after_add:
                        # This is a new tile
                        band_check = True
                        darkness_check = True
                        # Check if all bands exist
                        for band in band_labels:
                            filename = name + '_' + band + '.TIF'
                            if fileExist(os.path.join(loadPath, entityID, filename)) == False:
                                band_check = False

                            if band_check == True:
                                # Test if any of the images are black or grey
                                darkness_check = checkTile(os.path.join(loadPath, entityID, filename))
                            else:
                                darkness_check = False

                        if darkness_check == True:
                            # Move all bands
                            for band in band_labels:
                                filename = name + '_' + band + '.TIF'
                                oldFilePath = os.path.join(loadPath, entityID, filename)
                                newFilePath = os.path.join(savePath, 'non_airports', band, filename)
                                # Handle name conflicts for multiple images of same airport
                                i = 0
                                while (fileExist(newFilePath)):
                                    newFileName = name + '_' + band + '_' + str(i) + '.TIF'
                                    newFilePath = os.path.join(savePath, 'non_airports', band, newFileName)
                                    i += 1
                                copyfile(oldFilePath, newFilePath)
                            num_moved += 1
            else:
                return

def consolidate(tilePath, savePath, genMissing=False):

    # Create the new file structure
    band_labels = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']
    class_labels = ['airports', 'non_airports']

    createDir(savePath)
    for class_type in class_labels:
        createDir(os.path.join(savePath, class_type))
        for band in band_labels:
            createDir(os.path.join(savePath, class_type, band))

    # Move tiles into new folders & check for band consistency
    batches = os.listdir(tilePath)

    # Loop through each batch of tiles
    for batch in batches:
        num_airports_moved = airportsMove(os.path.join(tilePath, batch, 'airports'), savePath)
        print(batch, num_airports_moved)
        non_airportsMove(os.path.join(tilePath, batch, 'non_airports'), savePath, num_airports_moved)

    return num_airports_moved
