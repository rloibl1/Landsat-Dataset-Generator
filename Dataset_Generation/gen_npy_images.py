# Creates images from .TIF tiles and saves them as numpy arrays
# Splits the generated images up into training, validation, and testing sets
# Creates dictionary files of image paths for use by datagenerator

import os
import numpy as np
from PIL import Image

# Creates a directory if one doesn't exist
def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Adds band to filename
def bandName(filename, band):
    file_splt = filename.split('_')
    if len(file_splt) > 2:
        name = file_splt[0] + '_' + band + '_' + file_splt[2]
    else:
        name = file_splt[0] + '_' + band + '.TIF'
    return name

# Returns a name with band removed
def rawName(filename):
    file_splt = filename.split('_')
    if len(file_splt) > 2:
        tif_rmv = file_splt[2].split('.')
        name = file_splt[0] + '_' + tif_rmv[0]
    else:
        name = file_splt[0]
    return name

# Load up individual colors and combine into a composite image (channels last)
def createImages(filenames, loadPath, savePath, colors, img_size):
    # Loop through each target/non_target
    for filename in filenames:
        # Initialize array in proper shape
        composite_img = np.empty([img_size, img_size, len(colors)], dtype=np.uint16)
        for i, color in enumerate(colors):
            # Get band independent filename
            band_filename = bandName(filename, color)
            # Load TIF image
            img = Image.open(os.path.join(loadPath, color, band_filename))
            composite_img[:, :, i] = img
        # Save composite image as numpy array
        raw_name = rawName(filename)
        np.save(os.path.join(savePath, raw_name), composite_img, allow_pickle=True, fix_imports=True)
        print('Saved new', len(colors), 'color image at', os.path.join(savePath, raw_name))

def createDataset(loadPath, savePath, colors, img_size=256, train=.6, val=.2, test=.2, pickle=False):
    # Create file structure of dataset
    class_labels = ['airports', 'non_airports']

    # Top level dir
    createDir(savePath)

    # Create train/val/test dirs
    if train != 0.0:
        createDir(os.path.join(savePath, 'train'))
        for class_type in class_labels:
            createDir(os.path.join(savePath, 'train', class_type))

    if val != 0.0:
        createDir(os.path.join(savePath, 'val'))
        for class_type in class_labels:
            createDir(os.path.join(savePath, 'val', class_type))

    if test != 0.0:
        createDir(os.path.join(savePath, 'test'))
        for class_type in class_labels:
            createDir(os.path.join(savePath, 'test', class_type))

    # Determine the number of total images available & size of train/val/test
    target_imgs = sorted(os.listdir(os.path.join(loadPath, 'airports', 'B2')))
    non_target_imgs = os.listdir(os.path.join(loadPath, 'non_airports', 'B2'))
    train_size = np.int(len(target_imgs) * train)
    val_size = np.int(len(target_imgs) * val)
    test_size = np.int(len(target_imgs) * test)

    # Get filenames for targets
    target_train = target_imgs[0:train_size]
    target_val = target_imgs[train_size:train_size + val_size]
    target_test = target_imgs[train_size + val_size:train_size + val_size + test_size]

    # Get filenames for non_targets
    non_target_train = non_target_imgs[0:train_size]
    non_target_val = non_target_imgs[train_size:train_size + val_size]
    non_target_test = non_target_imgs[train_size + val_size:train_size + val_size + test_size]

    # Generate the Images
    createImages(target_train, os.path.join(loadPath, 'airports'),
                 os.path.join(savePath, 'train', 'airports'), colors, img_size)
    createImages(target_val,  os.path.join(loadPath, 'airports'),
                 os.path.join(savePath, 'val', 'airports'), colors, img_size)
    createImages(target_test,  os.path.join(loadPath, 'airports'),
                 os.path.join(savePath, 'test', 'airports'), colors, img_size)

    createImages(non_target_train,  os.path.join(loadPath, 'non_airports'),
                 os.path.join(savePath, 'train', 'non_airports'), colors, img_size)
    createImages(non_target_val, os.path.join(loadPath, 'non_airports'),
                 os.path.join(savePath, 'val', 'non_airports'), colors, img_size)
    createImages(non_target_test, os.path.join(loadPath, 'non_airports'),
                 os.path.join(savePath, 'test', 'non_airports'), colors, img_size)

    return None
