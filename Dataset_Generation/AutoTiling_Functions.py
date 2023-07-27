import os
import numpy as np
from osgeo import gdal
from osgeo import osr
from PIL import Image


########################################################################################################################
# http://monkut.webfactional.com/blog/archive/2012/5/2/understanding-
# raster-basic-gis-concepts-and-the-python-gdal-library/
########################################################################################################################

# Returns coordinates converted into the format supported by gdal libraries
def transform_wgs84_to_utm(lon, lat):
    def get_utm_zone(longitude):
        return int(1 + (longitude + 180.0) / 6.0)

    def is_northern(latitude):
        """
        Determines if given latitude is a northern for UTM
        """
        if latitude < 0.0:
            return 0
        else:
            return 1

    utm_coordinate_system = osr.SpatialReference()
    utm_coordinate_system.SetWellKnownGeogCS("WGS84")  # Set geographic coordinate system to handle lat/lon
    utm_coordinate_system.SetUTM(get_utm_zone(lon), is_northern(lat))

    wgs84_coordinate_system = utm_coordinate_system.CloneGeogCS()  # Clone ONLY the geographic coordinate system

    # Create transform component
    wgs84_to_utm_geo_transform = osr.CoordinateTransformation(wgs84_coordinate_system, utm_coordinate_system)  # (, )
    return wgs84_to_utm_geo_transform.TransformPoint(lon, lat, 0)  # Returns easting, northing, altitude


# Finds the number of targets in the string grouping
def find_num_targets(names):
    result = 1
    for char in range(len(names)):
        if names[char] == '|':
            result += 1
    return result


# Finds the specific target value based on separator_num
def find_target_value(value, separator_num, max_separators):

    # Initialize variables to track the position of the desired target value
    beginning_sep, ending_sep = 0, 0
    counter = 0
    endpoint = len(value)

    # Find the correct value in the string separated by '|'
    for position in range(endpoint):
        if value[position] == '|':
            if counter <= separator_num:
                beginning_sep = ending_sep
                ending_sep = position
                counter += 1
    if separator_num == 0 and max_separators == 0:
        result = value
    elif separator_num == 0:
        result = value[beginning_sep:ending_sep]
    elif separator_num == max_separators:
        result = value[ending_sep+1:]
    else:
        result = value[beginning_sep+1:ending_sep]
    return result


# Returns a set of tiles that should not be cut from the landsat image
def tile_non_targets(entityID, band, tile_save_path, target_coord, size, directory):

    # Create the Landsat path and the specific storage directory for this entityId
    landsat_image_path = directory + '/' + entityID + '/' + band
    if not os.path.exists(tile_save_path + '/' + entityID + '/'):
        os.makedirs(tile_save_path + '/' + entityID + '/')

    # Open Geotiff
    landsat_geotiff = gdal.Open(landsat_image_path)

    # Grab corner coordinates & resolution from metadata
    # xMin and yMax make up the origin, xRes and yRes are the pixel size
    # xMin, xRes, xSkew, yMax, ySkew, yRes = geotiff.GetGeoTransform()
    xMin_func, xRes_func, xSkew_func, yMax_func, ySkew_func, yRes_func = landsat_geotiff.GetGeoTransform()
    xMax_func = xMin_func + (landsat_geotiff.RasterXSize * xRes_func)
    yMin_func = yMax_func + (landsat_geotiff.RasterYSize * yRes_func)
    x_resolution = xRes_func

    # Determine the number of tiles on x and y axis of landsat image
    num_x = np.int((xMax_func - xMin_func) / (size * x_resolution))
    num_y = np.int((yMax_func - yMin_func) / (size * x_resolution))

    # find a value that will be used to check if the tile will be saved or not
    checker = round((num_x * num_y // 100) ** .5)

    # Loop to tile a Landsat-8 Image Preserving Metadata
    tileyMax_func = yMax_func
    for y_position in range(num_y):
        tileyMin_func = tileyMax_func - (size * x_resolution)
        tilexMin_func = xMin_func
        for x_position in range(num_x):
            tilexMax_func = tilexMin_func + (size * x_resolution)

            # Saves a small porition of the non-target tiles (those that pass the mod check with checker) and checks to make sure they do not overlap with targets, does not save the tile if they do.
            if (x_position % checker == 0) and (y_position % checker == 0):
                for k in range(0, len(target_coord)):

                    # Check that the tile's coordinates do not overlap with any of the target's coordinates, pass if it does
                    if (target_coord[k][0] < tilexMin_func < target_coord[k][2] or target_coord[k][0] < tilexMax_func <
                        target_coord[k][2]) and (
                                        target_coord[k][1] < tileyMin_func < target_coord[k][3] or target_coord[k][
                                1] < tileyMax_func < target_coord[k][3]):
                        pass
                    else:

                        # Save the tile as a geotiff file
                        image_options = gdal.WarpOptions(options=[], format='GTiff',
                                                         outputBounds=[tilexMin_func, tileyMin_func, tilexMax_func,
                                                                       tileyMax_func])
                        tile_filename = tile_save_path + '/' + entityID + '/' + 'Tile: ' + str(x_position) + '.' + str(y_position) + band[len(entityID):]
                        gdal.Warp(tile_filename, landsat_image_path, options=image_options)

                        # Check that the tile has no black pixels, and if it does delete the image and add it to the cut_check set
                        img = Image.open(tile_filename)
                        pixels = img.load()  # get the pixels as a flattened sequence
                        black_thresh = 50
                        has_black = False
                        if pixels[0, size - 1] < black_thresh or pixels[0, 0] < black_thresh or pixels[size - 1, 0] < black_thresh or pixels[size - 1, size - 1] < black_thresh:
                            has_black = True

                        if has_black:
                            os.remove(tile_filename)
            tilexMin_func = tilexMax_func
        tileyMax_func = tileyMin_func
    return


# Main function that tiles Landsat images
def Tile_Targets(start_row, end_row, target_info, Directory, pixel_size, tile_all, target_path, non_target_path, all_targets):
    for targets in range(start_row, end_row + 1):

        # Initialize/Reset the list of target coordinates for the specific Landsat Image
        coord = []

        # Initialize/Reset a set of targets that are tiled with errors
        empty_targets = set([])

        # Get the grouped values for the targets in this scene
        target_entityId = target_info['entityID'].iloc[targets]
        target_lat_group = str(target_info['lat'].iloc[targets])
        target_lon_group = str(target_info['lon'].iloc[targets])
        target_name_group = target_info['name'].iloc[targets]
        target_type_group = target_info['type'].iloc[targets]

        # Find number of unique targets
        num_targets = find_num_targets(target_name_group)

        # Initialize first_band to True to indicate the process is working with the first (of possibly many) bands
        first_band = True

        for file in os.listdir(Directory + '/' + target_entityId):
            if file.endswith(".TIF"):

                # Create path for geotiff file
                image_path = Directory + '/' + target_entityId + '/' + file

                # Open Geotiff file
                geotiff = gdal.Open(image_path)

                # Grab corner coordinates & resolution from metadata
                # xMin and yMax make up the origin, xRes and yRes are the pixel size
                # xMin, xRes, xSkew, yMax, ySkew, yRes = geotiff.GetGeoTransform()
                geoTransform = geotiff.GetGeoTransform()
                px_resolution = geoTransform[1]

                # Convert target lat/lon into generic values (match landsat bounds for cropping)
                offset = (pixel_size / 2) * px_resolution

                # Creates the target tiles and adds their coordinates in an array that is cross reference when cutting tiles
                for sep in range(0, num_targets):

                    # Get the lat, lon, name, and type for the specific target being tiled
                    target_lat = find_target_value(target_lat_group, sep, num_targets - 1)
                    target_lat = float(target_lat)
                    target_lon = find_target_value(target_lon_group, sep, num_targets - 1)
                    target_lon = float(target_lon)
                    target_name = find_target_value(target_name_group, sep, num_targets - 1)

                    if target_name in empty_targets:
                        pass
                    else:

                        target_type = find_target_value(target_type_group, sep, num_targets - 1)

                        # Create target save location based on type
                        target_save_path = target_path + '/' + target_type + '/' + target_entityId + '/'
                        if not os.path.exists(target_save_path):
                            os.makedirs(target_save_path)

                        # Convert from WGS84 Lat/Lon --> UTM
                        target_x, target_y, target_z = transform_wgs84_to_utm(target_lon, target_lat)

                        # Determine the boundaries of the cropped target
                        aTilexMin = target_x - offset
                        aTilexMax = target_x + offset
                        aTileyMin = target_y - offset
                        aTileyMax = target_y + offset

                        # Crop and save image, if it is a black box remove it and add the target name and entityId to an error list
                        options = gdal.WarpOptions(options=[], format='GTiff',
                                                   outputBounds=[aTilexMin, aTileyMin, aTilexMax, aTileyMax])
                        filename = target_save_path + target_name + file[len(target_entityId):]
                        gdal.Warp(filename, image_path, options=options)

                        # Save the file to be used to create DigiGlobe coordinates
                        if first_band:
                            all_filename = all_targets + '/' + target_name + file[len(target_entityId):]
                            gdal.Warp(all_filename, image_path, options=options)

                            # Stores coordinates relative to image in list of tuples
                            coordinates = (aTilexMin, aTileyMin, aTilexMax, aTileyMax)
                            coord.append(coordinates)

                # Tiles the Landsat Image (without overlapping targets) if specified to do so in AutoTiling_Multicore
                if tile_all:

                    # Cut out the non_target tiles
                    tile_non_targets(target_entityId, file, non_target_path, coord, pixel_size, Directory)

                # Set first to false
                first_band = False