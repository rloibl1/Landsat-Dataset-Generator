# Script to assess how many targets were expected to be cropped vs how many were actually generated

import os
import pandas as pd

def checkTargets(csv_filename, basePath):
    # Hardcoded paths for airports only
    airport_path = os.path.join(basePath, 'airports')
    classes = os.listdir(airport_path)
    classes.remove('all_airports')

    # Start general code
    csv = pd.read_csv(csv_filename)
    num_est_targets = 0
    num_not_tiled_targets = 0

    # Estimated Targets
    for i, target in enumerate(csv['name']):
        # Entity ID
        entity_ID = csv.loc[i, 'entityID']

        if csv.loc[i, 'downloaded'] == 'Y':
            # Number of expected targets
            split_target_names = str(target).split('|')
            est_count = len(split_target_names)
        else:
            est_count = 0

        num_est_targets += est_count

        # Actual number of targets
        for target_type in classes:
            unique_names = set()
            try:
                tiles = os.listdir(os.path.join(airport_path, target_type, entity_ID))
                for tile in tiles:
                    # See if this tile is a new airport or just another band
                    unique_names.add(tile.split('_')[0])
                num_unique_names = len(unique_names)
            except:
                num_unique_names = 0
        delta = est_count - num_unique_names
        if delta != 0:
            num_not_tiled_targets += delta
            print(entity_ID, "has", delta, "not tiled")

    # Delta calculation to determine pass/fail
    final_delta = num_not_tiled_targets

    if final_delta == 0:
        print('Passed test')
        return True
    else:
        print('Failed test', final_delta, "targets are missing")
        return False