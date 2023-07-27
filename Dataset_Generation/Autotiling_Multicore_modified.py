import os
import pandas as pd
from datetime import datetime
from multiprocessing import Pool
import AutoTiling_Functions_modified
import DigiGlobe_Coord

def autoTile(csv_path, Directory, storage_location, tile_size=256, target_tiles='airports', non_target_tiles='non_airports',
             tile_all=True, gen_DG_cords=True):

    # Create paths for folders if they do not exist
    if not os.path.exists(storage_location):
        os.makedirs(storage_location)
    target_path = storage_location + '/' + target_tiles
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    all_targets = target_path + '/all_' + target_tiles
    if not os.path.exists(all_targets):
        os.makedirs(all_targets)
    non_target_path = storage_location + '/' + non_target_tiles
    if not os.path.exists(non_target_path):
        os.makedirs(non_target_path)

    #############################################
    # Start Timing of Advanced Cropping Algorithm
    startTime = datetime.now()

    # Read target list into dataframe
    target_info = pd.read_csv(csv_path)

    # Find number of physical cores to determine number of worker processes to create
    cpu_info = dict()

    # Finds the number of physical cores on a linux computer
    # Source:  https://github.com/teamdiamond/analysis/blob/master/lib/qutip/hardware_info.py
    for l in [l.split(':') for l in os.popen('lscpu').readlines()]:
        cpu_info[l[0]] = l[1].strip('.\n ').strip('kB')
    sockets = int(cpu_info['Socket(s)'])
    cores_per_socket = int(cpu_info['Core(s) per socket'])
    num_processes = sockets * cores_per_socket * 5 // 4  # Only do this with hyperthreading, otherwise remove the '* 5//4'
    print("Creating", num_processes, "worker processes")

    # Split the csv rows as evenly as possible into X processes
    row_count = len(target_info.index)
    floor_inc = row_count // num_processes
    ceil_inc = (row_count + num_processes) // num_processes
    num_ceil = int((row_count - (floor_inc*num_processes)) / (ceil_inc - floor_inc))
    num_floor = int(num_processes - num_ceil)

    # --Debug Test--
    # print(floor_inc, ceil_inc)
    # print(num_floor, num_ceil)

    # Create a list of inputs for each worker process
    input_list = []
    current_row = 0
    for floor in range(0, num_floor):
        input_list.append([current_row, current_row + floor_inc - 1, target_info, Directory, tile_size, tile_all, target_path, non_target_path, all_targets])
        current_row += floor_inc
    for ceil in range(0, num_ceil):
        input_list.append([current_row, current_row + ceil_inc - 1, target_info, Directory, tile_size, tile_all, target_path, non_target_path, all_targets])
        current_row += ceil_inc

    # Create a number of worker processes 5/4 times the number of cores and run the tiling function over all of them
    #if __name__ == '__main__':
    with Pool(processes=num_processes) as p:
        p.starmap(AutoTiling_Functions_modified.Tile_Targets, input_list)

    # Calculate and print time taken to tile images
    time_taken = datetime.now() - startTime
    print('\nTime taken to tile Landsat images: ' + str(time_taken))

    # Generate DigiGlobe target coordinate csv
    if gen_DG_cords == True:
        DigiGlobe_Coord.generate_coord_csv(all_targets + '/')