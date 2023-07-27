# Retrieved from: https://stackoverflow.com/questions/27868250/python-find-out-how-much-of-an-image-is-black
import os
from PIL import Image

def removeBadTiles(basePath, targetOnly=True):
    if targetOnly == True:
        subdir_names = ['airports/large_airport', 'airports/medium_airport']
    else:
        subdir_names = ['airports/large_airport', 'airports/medium_airport', 'non_airports']

    total_num_black = 0
    total_num_grey = 0
    total_images = 0

    for path in subdir_names:

        if os.path.exists(os.path.join(basePath, path)):

            subDirs = os.listdir(os.path.join(basePath, path))

            for dir in subDirs:
                files = os.listdir(os.path.join(basePath, path, dir))
                for file in files:
                    im = Image.open(os.path.join(basePath, path, dir, file))
                    pixels = im.getdata()          # get the pixels as a flattened sequence
                    black_thresh = 1
                    nblack = 0
                    ngrey = 0
                    for pixel in pixels:

                        if pixel < black_thresh:
                            nblack += 1

                        if pixel > 4990 and pixel < 5010:
                            ngrey += 1
                    n = len(pixels)

                    # Black Pictures (off edge)
                    if (nblack / float(n)) > 0.25:
                        total_num_black += 1
                        print('Image', total_images, 'removed')
                        os.remove(os.path.join(basePath, path, dir, file))

                    # Gray Pictures
                    elif (ngrey / float(n)) > 0.25:
                        print('Image', total_images, 'removed')
                        total_num_grey += 1
                        os.remove(os.path.join(basePath, path, dir, file))
                    else:
                        print('Image', total_images, 'passed')

                    total_images += 1
        else:
            print('Class', path, 'does not exist for this batch')

    return total_images, total_num_black, total_num_grey

def checkTile(path):
    im = Image.open(path)
    pixels = im.getdata()  # get the pixels as a flattened sequence
    black_thresh = 1
    nblack = 0
    ngrey = 0

    for pixel in pixels:

        if pixel < black_thresh:
            nblack += 1

        if pixel > 4990 and pixel < 5010:
            ngrey += 1

    n = len(pixels)

    # Black Pictures (off edge)
    if (nblack / float(n)) > 0.25:
        return False
    # Gray Pictures
    elif (ngrey / float(n)) > 0.25:
        return False
    else:
        return True