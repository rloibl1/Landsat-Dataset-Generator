from Autotiling_Multicore_modified import *

tile_size = 256
tile_all = True
gen_DG_cords = False

load_path_batch = '/home/afit/Desktop/test_crop'
save_path_batch = '/home/afit/Desktop/test_tile_algo'
target_list = '/home/afit/Desktop/test_crop/airports_subset_0.csv'

# Creates a directory if one doesn't exist
def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Create save folder
createDir(save_path_batch)

autoTile(target_list, load_path_batch, save_path_batch, tile_size=tile_size, tile_all=tile_all,
                 gen_DG_cords=gen_DG_cords)

