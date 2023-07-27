from datetime import datetime
from osgeo import gdal, osr  # ogr
import os
import csv
from PIL import Image


########################################################################################################################
# https://gis.stackexchange.com/questions/57834/how-to-get-raster-corner-coordinates-using-python-gdal-bindings
########################################################################################################################
def get_extent(geo_tr, cols_func, rows_func):
    """ Return list of corner coordinates from a geotransform

        @type geo_tr:   C{tuple/list}
        @param geo_tr: geotransform
        @type cols_func:   C{int}
        @param cols_func: number of columns in the dataset
        @type rows_func:   C{int}
        @param rows_func: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    """
    extent = []
    x_arr = [0, cols_func]
    y_arr = [0, rows_func]

    for px in x_arr:
        for py in y_arr:
            x = geo_tr[0] + (px * geo_tr[1]) + (py * geo_tr[2])
            y = geo_tr[3] + (px * geo_tr[4]) + (py * geo_tr[5])
            extent.append([x, y])
            # print x, y
        y_arr.reverse()
    return extent


def reproject_coords(coords, source_srs, target_srs):
    """ Reproject a list of x,y coordinates.

        @type coords:     C{tuple/list}
        @param coords:    List of [[x,y],...[x,y]] coordinates
        @type source_srs:  C{osr.SpatialReference}
        @param source_srs: OSR SpatialReference object
        @type target_srs:  C{osr.SpatialReference}
        @param target_srs: OSR SpatialReference object
        @rtype:         C{tuple/list}
        @return:        List of transformed [[x,y],...[x,y]] coordinates
    """
    trans_coords = []
    transform = osr.CoordinateTransformation(source_srs, target_srs)
    for x, y in coords:
        x, y, z = transform.TransformPoint(x, y)
        trans_coords.append([x, y])
    return trans_coords


########################################################################################################################
#
########################################################################################################################
def generate_coord_csv(directory):

    with open('target_digiGlobe_coords.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', dialect='excel')
        writer.writerow(['name', 'min_lon', 'max_lat', 'max_lon', 'min_lat'])
        for filename in os.listdir(directory):
            if filename.endswith(".TIF"):
                # print(os.path.join(directory, filename))

                # Check that the target is not a black box
                im = Image.open(directory + '/' + filename)
                if im.getbbox():
                    raster = directory + filename
                    ds = gdal.Open(raster)

                    gt = ds.GetGeoTransform()
                    columns = ds.RasterXSize
                    rows = ds.RasterYSize
                    ext = get_extent(gt, columns, rows)

                    src_srs = osr.SpatialReference()
                    src_srs.ImportFromWkt(ds.GetProjection())
                    tgt_srs = src_srs.CloneGeogCS()

                    geo_ext = reproject_coords(ext, src_srs, tgt_srs)
                    writer.writerow(
                        [filename[:len(filename) - 4], geo_ext[0][0], geo_ext[0][1], geo_ext[2][0], geo_ext[2][1]])
                else:
                    os.remove(directory + '/' + filename)
