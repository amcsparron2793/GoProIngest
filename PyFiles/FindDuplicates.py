# Importing Libraries
import os
import sys
from os.path import isdir, join
from pathlib import Path
import hashlib


# TODO: clean this up and make it work as an importable module.
def make_test_files(num_files):
    counter = 1
    misc_files = "../Misc_Project_Files"
    if isdir(misc_files):
        pass
    else:
        os.mkdir(misc_files)
    while counter < num_files + 1:
        with open(join(misc_files, f"test_num_{str(counter)}.txt"), "w") as f:
            if counter / 2 % 1:
                f.write(str(counter))
            counter += 1
    print(f"{num_files} written")


# Joins dictionaries
def join_dictionary(dict_1, dict_2):
    for key in dict_2.keys():
        # Checks for existing key
        if key in dict_1:
            # If present Append
            dict_1[key] = dict_1[key] + dict_2[key]
        else:
            # Otherwise Stores
            dict_1[key] = dict_2[key]


# Calculates MD5 hash of file
# Returns HEX digest of file
def hash_file(path):
    # open the file as bytes
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    blocksize = 65536
    buf = afile.read(blocksize)

    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def make_hash_dict():
    # TODO: make this more portable
    checked = {}
    path_to_folder = "../Misc_Project_Files"
    all_files_hashes = {}
    duplicates = {}
    folders = Path(path_to_folder)
    files = sorted(os.listdir(folders))

    # this part works
    for file in files:
        h = hash_file(join(folders, file))
        all_files_hashes.update({file: h})
    # print(all_files_hashes)

    # FIXME: this part doesnt work since update overwrites the previous value
    for k, v in all_files_hashes.items():
        if v not in checked.values():
            checked.update({k: v})
        else:
            duplicates.update({k: v})

    print(duplicates)
    return duplicates


make_hash_dict()
#make_test_files(5)