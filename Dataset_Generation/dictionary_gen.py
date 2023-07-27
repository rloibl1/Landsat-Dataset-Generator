# This script creates dictionary files which contain the path to an image & it's class
import os
import pickle

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def createDict(dataset_path):
    # Get training/val/test dirs
    data_subsets = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]

    for subset in data_subsets:
        # Create a dictionary file
        new_dict = {}
        classes = os.listdir(os.path.join(dataset_path, subset))
        for i, single_class in enumerate(classes):
            images = os.listdir(os.path.join(dataset_path, subset, single_class))
            for image in images:
                image_path = os.path.join(dataset_path, subset, single_class, image)
                new_dict[image_path] = i

        print(subset, 'dictionary created')
        save_obj(new_dict, os.path.join(dataset_path, subset + '_dict'))
