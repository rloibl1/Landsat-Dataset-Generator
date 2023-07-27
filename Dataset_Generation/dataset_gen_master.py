# This is the top level script for creating a new dataset from raw Landsat imagery

import os
from fix_airport_names import *
from AutoTiling_Multicore import *
from autotiling_check import *
from darkness_filter import *
from consolidate_bands import *
from gen_npy_images import *
from dictionary_gen import *

# =======================
# Configuration Variables
raw_data_path = '/datatank/raw_landsat_data' # Path to raw imagery location for CSV target checking
csv_path = '/media/afit/Seagate Backup Plus Drive/Landsat Download Lists' # Path to clean CSV target lists
load_path = '/home/afit/Desktop/Batches' # Path to load raw images from for tiling
tile_path = '/home/afit/Desktop/Tiles' # Base path to save generated tiles to
band_path = '/home/afit/Desktop/Bands' # Base path to consolidate each band's tiles to
dataset_path = '/home/afit/Desktop/Datasets/6clr' # Base path to the final dataset location

tile_size = 256 # Size in pixels of generated tiles
train_pct = .7 # Percentage of images to be used for training (Sum to 1.0)
val_pct = .1 # Percentage of images to be used for validation (Sum to 1.0)
test_pct = .2 # Percentage of images to be used for testing (Sum to 1.0)
channel_colors = ['B2', 'B5', 'B7', 'B3', 'B6', 'B4'] # List of what colors to make an image with (B2-B8)

tile_all = False # Variable to indicate whether non_target tiles should be generated
gen_DG_cords = False # Variable to indicate if a coordinate CSV should be generated for target tiles
test_targets_only = True # Variable that controls whether the black & grey test is applied to non target tiles
gen_missing_bands = False # Variable that indicates if you want a listing of missing bands for re-downloading
pickle_dataset = False # Set to true if you want to serialize the dataset
# =======================

# =======================
# Debug Variables
step_one = False
step_two = False
step_three = False
step_four = False
step_five = True
step_six = True
# =======================

# STEP #1: Run error checking & correction scripts against the target lists
if step_one:
    # Fix existing download lists
    existingCSVFix(raw_data_path)
    # Fix unused download lists
    CSVFix(csv_path)

# STEP #2: Run auto-tiling script & generate target/non_target tiles
if step_two:
    batches = os.listdir(load_path)
    for batch in batches:
        # Create load path, target list, and save path based on batch
        load_path_batch = os.path.join(load_path, batch)
        csv_name = 'airports_subset_' + batch.split(' ')[1] + '.csv'
        target_list = os.path.join(load_path_batch, csv_name)
        save_path_batch = os.path.join(tile_path, batch + ' tiles')
        # Run tiling code
        autoTile(target_list, load_path_batch, save_path_batch, tile_size=tile_size, tile_all=tile_all,
                 gen_DG_cords=gen_DG_cords)
        # Check that the number of target tiles generated matches the expected amount from CSV
        checkTargets(target_list, save_path_batch)

# STEP #3: Remove tiles that are outside of the actual images bounds or corrupted (Target tiles only)
if step_three:
    batches = os.listdir(tile_path)
    for batch in batches:
        # Run black & grey filter on each batch of tiles
        total_images, total_num_black, total_num_grey = removeBadTiles(os.path.join(tile_path, batch),
                                                                       targetOnly=test_targets_only)
        print('===============', batch, '===============')
        print('Number of starting images:', total_images)
        print('Number of removed black images:', total_num_black)
        print('Number of removed grey images:', total_num_grey)

# STEP #4: Consolidate batch tiles into shared folders, filter out partial band pairs, and sync num tiles per class
if step_four:
    num_files_moved = consolidate(tile_path, band_path, genMissing=gen_missing_bands)
    print(num_files_moved, 'from all classes moved')

# STEP #5: Generate Images as numpy arrays using selected colors, split into train/validation/test sets
if step_five:
    createDataset(band_path, dataset_path, channel_colors, img_size=tile_size,
                  train=train_pct, val=val_pct, test=test_pct)

# STEP #6: Create dictionary files with path & class information
if step_six:
    createDict(dataset_path)
