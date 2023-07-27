# This script modifies target_csv airport names to replace '/' characters with '-' characters
# It also checks for and removes duplicate target entries
# This change avoids filename errors when executing the auto-tiling script

import os
import pandas as pd

# Remove duplicate entries & rebuild dataframe cells
def removeDuplicate(string, index):
    temp = []
    split_str = string.split('|')
    split_str[index] = None
    for item in split_str:
        if item != None:
            temp.append(item)
            temp.append('|')
    temp = temp[:-1]
    return ''.join(temp)

def existingCSVFix(basePath):

    num_csv_files = 0
    num_mod_targets = 0
    num_removed = 0

    batch_folders = os.listdir(basePath)

    print("==================================================")
    print("Checking existing download lists for target errors")
    print("==================================================")

    # Find each csv file in existing downloads
    for batch_fldr in batch_folders:
        dir_contents = os.listdir(os.path.join(basePath, batch_fldr))
        for item in dir_contents:
            filename = os.path.join(basePath, batch_fldr, item)
            if os.path.isfile(filename):
                # Open csv file & fix target names
                num_csv_files += 1
                # print("==============================")
                # print("Fixing", item)
                # print("==============================")
                csv = pd.read_csv(filename)
                # Split each row into individual targets
                for i, target in enumerate(csv['name']):
                    split_target_names = str(target).split('|')
                    new_names = []
                    unique_names = set()
                    num_unique_names = 0
                    repeat_rmv = 0
                    # Check each target name for invalid character ('/')
                    for x, target_name in enumerate(split_target_names):
                        new_name = target_name.replace('/', '-')
                        # See if this name was modified
                        if new_name != target_name:
                            num_mod_targets += 1
                            # print(target_name, "===modified to==>", new_name)
                        # Check that all names are unique
                        unique_names.add(new_name)
                        num_unique_names += 1
                        if len(unique_names) != (num_unique_names - repeat_rmv):
                            # Have a repeat name & need to remove entry
                            csv_row = csv.iloc[i]
                            # print("Duplicate target", new_name, "removed at row", i + 2)
                            # Remove duplicate entries
                            type = removeDuplicate(csv_row['type'], x - repeat_rmv)
                            lat = removeDuplicate(csv_row['lat'], x - repeat_rmv)
                            lon = removeDuplicate(csv_row['lon'], x - repeat_rmv)
                            alt = removeDuplicate(csv_row['alt'], x - repeat_rmv)
                            # Reassign fixed row
                            csv.set_value(i, 'type', type)
                            csv.set_value(i, 'lat', lat)
                            csv.set_value(i, 'lon', lon)
                            csv.set_value(i, 'alt', alt)
                            # Update removal counter
                            repeat_rmv += 1
                        else:
                            # Name is not repeat add to list for merging at loop exit
                            new_names.append(new_name)
                            new_names.append('|')
                    # Update total counter of duplicate targets removed
                    num_removed += repeat_rmv
                    # Rebuild CSV row
                    # Remove last '|' character
                    new_names = new_names[:-1]
                    # Find row index
                    row_index = csv.loc[csv.name == target].index[0]
                    # Write new value to dataframe
                    csv.set_value(row_index, 'name', ''.join(new_names))
                # Write all updates to file
                csv.to_csv(filename, index=False)

    print("\n====Program Results=====")
    print("Read", num_csv_files, "downloaded csv files, fixed", num_mod_targets, "target names, and removed",
          num_removed, "duplicate targets\n")

def CSVFix(basePath):
    num_mod_targets = 0
    num_removed = 0

    files = os.listdir(basePath)
    num_csv_files = len(files)

    print("=========================================")
    print("Checking download lists for target errors")
    print("=========================================")

    # Loop through each CSV file
    for file in files:
        # print("==============================")
        # print("Fixing", file)
        # print("==============================")
        filename = os.path.join(basePath, file)
        csv = pd.read_csv(filename)
        # Split each row into individual targets
        for i, target in enumerate(csv['Name']):
            split_target_names = str(target).split('|')
            new_names = []
            unique_names = set()
            num_unique_names = 0
            repeat_rmv = 0
            # Check each target name for invalid character ('/')
            for x, target_name in enumerate(split_target_names):
                new_name = target_name.replace('/', '-')
                # See if this name was modified
                if new_name != target_name:
                    num_mod_targets += 1
                    # print(target_name, "===modified to==>", new_name)
                # Check that all names are unique
                unique_names.add(new_name)
                num_unique_names += 1
                if len(unique_names) != (num_unique_names - repeat_rmv):
                    # Have a repeat name & need to remove entry
                    csv_row = csv.iloc[i]
                    # print("Duplicate target", new_name, "removed at row", i + 2)
                    # Remove duplicate entries
                    type = removeDuplicate(csv_row[' Type'], x - repeat_rmv)
                    lat = removeDuplicate(csv_row[' Lat'], x - repeat_rmv)
                    lon = removeDuplicate(csv_row[' Lon'], x - repeat_rmv)
                    alt = removeDuplicate(csv_row[' Alt'], x - repeat_rmv)
                    # Reassign fixed row
                    csv.set_value(i, ' Type', type)
                    csv.set_value(i, ' Lat', lat)
                    csv.set_value(i, ' Lon', lon)
                    csv.set_value(i, ' Alt', alt)
                    # Update removal counter
                    repeat_rmv += 1
                else:
                    # Name is not repeat add to list for merging at loop exit
                    new_names.append(new_name)
                    new_names.append('|')
            # Update total counter of duplicate targets removed
            num_removed += repeat_rmv
            # Rebuild CSV row
            # Remove last '|' character
            new_names = new_names[:-1]
            # Find row index
            row_index = csv.loc[csv.Name == target].index[0]
            # Write new value to dataframe
            csv.set_value(row_index, 'Name', ''.join(new_names))
        # Write all updates to file
        csv.to_csv(filename, index=False)

    print("\n====Program Results=====")
    print("Read", num_csv_files, "csv files, fixed", num_mod_targets, "target names, and removed",
          num_removed, "duplicate targets\n")