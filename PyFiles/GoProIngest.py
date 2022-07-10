#! python3

# imports
import os
import shutil
from sys import stderr
from time import sleep

import win32api
from datetime import datetime
import re

# globals
current_date = datetime.now().strftime('%m%d%Y')
LocationSubDirs = ['GoProRAW', 'PhoneMedia']
PerDumpSubdirs = ["THMandLRV", "MP4andJPEG"]
StorageName = 'GoProStorage'
CameraSDName = 'GoProSDCard'


def convert_size(size_in_bytes: int) -> str:
    candidates = []
    correct_name_and_value = None
    prefex_dict = {"kilo": 1000,
                   "mega": 1000000,
                   "giga": 1000000000,
                   "tera": 1000000000000}

    for n, s in prefex_dict.items():
        if size_in_bytes < prefex_dict["kilo"]:
            correct_name_and_value = ('bytes', size_in_bytes)

        if s < size_in_bytes:
            rounded_value = round((size_in_bytes / s), 2)
            candidates.append({n: rounded_value})

    if not isinstance(correct_name_and_value, tuple):
        new_list = [[y for y in x.items()] for x in candidates]
        # this list gets rid of the inner list in new_list
        tuple_list = [x[0] for x in new_list]
        # gets the minimum value n the tuple_list
        correct_value = min([x[1] for x in [x[0] for x in new_list]])
        # makes a new tuple of the correct value and its associated prefex
        correct_name_and_value = [x for x in tuple_list if x[1] == correct_value][0]

        final_string = f"{correct_name_and_value[1]} {correct_name_and_value[0].capitalize()}bytes"
    else:
        final_string = f"{correct_name_and_value[1]} {correct_name_and_value[0]}"

    return final_string


def storage_present(drive_name_to_check=StorageName):
    d_count = 0
    drive_letters = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    for d in drive_letters:
        if d_count + 1 >= len(drive_letters):
            try:
                raise EnvironmentError(f"Storage could not be found, please connect {drive_name_to_check}")
            except EnvironmentError as e:
                stderr.write(f"\nERROR: {e.args[0]}\n")
                os.system("pause")
                exit(1)
        else:
            pass
        try:
            vol_name = win32api.GetVolumeInformation(d)[0]
        except BaseException as e:
            print(e.args)
            # d_count += 1
            continue

        if vol_name == drive_name_to_check:
            print(f"{drive_name_to_check} found")
            return d
        else:
            d_count += 1


def get_date():
    while True:
        try:
            start_date = input("Please enter start date of footage (MMDDYYYY): ")
            ptn = re.compile("^(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])(19|20)\d\d$")
            if ptn.fullmatch(start_date):
                break
            else:
                print("please enter as MMDDYYYY")
        except KeyboardInterrupt:
            stderr.write("Ctrl-C detected! Quitting")
            exit(-1)
    return start_date


def _create_dir_loop(dirpath):
    if os.path.isdir(dirpath):
        print(f"\'{dirpath}\' detected")
        os.chdir(dirpath)
        return os.getcwd()
    else:
        os.mkdir(dirpath)
        print(f"{dirpath} Created")
        os.chdir(dirpath)
        return os.getcwd()


def create_dir_struc(storage_letter=None):
    if not storage_letter:
        storage_letter = storage_present()
    else:
        pass
    for firstsubdir in folder_names["LocationSubDirs"]:
        dir_path = os.path.join(storage_letter, folder_names['root'], firstsubdir)
        # print(dir_path)
        _create_dir_loop(dir_path)
        # for LocationSub in folder_names["LocationSubDirs"]:
        dir_path = os.path.join(storage_letter, folder_names['root'], firstsubdir, folder_names["DateOfFootageDir"])
        _create_dir_loop(dir_path)

        for PerDump in folder_names['PerDumpSubdirs']:
            dir_path = os.path.join(storage_letter, folder_names['root'],
                                    firstsubdir, folder_names["DateOfFootageDir"], PerDump)
            _create_dir_loop(dir_path)
    # TODO: fix this so that it works with both the PhoneData and RawGoProData subdirs
    return os.path.join(storage_letter, folder_names['root'], folder_names["LocationSubDirs"][0],
                        folder_names["DateOfFootageDir"])


def _save_location_check(media_save_location, support_save_location):
    if os.path.isdir(media_save_location):
        print(f"media save location detected \'{media_save_location}\'")
    else:
        try:
            raise NotADirectoryError(f"\'{media_save_location}\' does not exist.")
        except NotADirectoryError as e:
            stderr.write(f"\nERROR: {e.args[0]}\n")
            os.system("pause")
            exit(1)

    if os.path.isdir(support_save_location):
        print(f"support save location detected \'{support_save_location}\'")
    else:
        try:
            raise NotADirectoryError(f"\'{support_save_location}\' does not exist.")
        except NotADirectoryError as e:
            stderr.write(f"\nERROR: {e.args[0]}\n")
            os.system("pause")
            exit(1)


def sort_content(base_save_location):
    total_size_of_copy = 0
    media_save_location = os.path.join(base_save_location, "MP4andJPEG")
    support_save_location = os.path.join(base_save_location, "THMandLRV")

    media_files = [os.path.join(CamSD_ContentBasePath, x) for x in os.listdir(CamSD_ContentBasePath)
                   if x.lower().endswith(".mp4") or x.lower().endswith(".jpeg")]
    # print(media_files)
    support_files = [os.path.join(CamSD_ContentBasePath, x) for x in os.listdir(CamSD_ContentBasePath)
                     if x.lower().endswith(".thm") or x.lower().endswith(".lrv")]

    _save_location_check(media_save_location, support_save_location)

    for f in media_files:
        # shutil.Error
        print(f"copying {f} - Filesize: {os.path.getsize(f)}")
        shutil.copy2(f, media_save_location)
        print(f"{f} copied to {media_save_location}")
        total_size_of_copy += os.path.getsize(f)

    for f in support_files:
        print(f"copying {f} - Filesize: {os.path.getsize(f)}")
        shutil.copy2(f, support_save_location)
        print(f"{f} copied to {support_save_location}")
        total_size_of_copy += os.path.getsize(f)
    pretty_size = convert_size(total_size_of_copy)
    print(pretty_size)


def yes_no_quit(question):
    while True:
        ans = input(f"{question}? (y/n/q): ")
        if ans.lower() == 'y':
            return True
        elif ans.lower() == 'n':
            return False
        elif ans.lower() == 'q':
            quit_ans = input("are you sure? (y/n): ")
            if quit_ans.lower() == 'y':
                print("Ok Quitting - Goodbye!")
                sleep(2)
                exit(0)
            else:
                pass


def start_ingest():
    # TODO: Add Logging - handle in separate thread?
    # TODO: add "file already copied" checker - hash?
    # TODO: add in shutil error handling
    global folder_names, CamSD_ContentBasePath, CamSD_DriveLetter

    folder_names = {
        'root': 'P-Town',
        'LocationSubDirs': LocationSubDirs,
        'DateOfFootageDir': f"{get_date()}-{current_date}",
        'PerDumpSubdirs': PerDumpSubdirs
    }

    BaseSaveLocation = create_dir_struc()  # StorageLetter="C:\\Users\\amcsp\\Desktop")

    CamSD_DriveLetter = storage_present(CameraSDName)  # 'D:\\'
    CamSD_ContentBasePath = os.path.join(CamSD_DriveLetter, "DCIM", "100GOPRO")
    # TODO: make this easier to look at and PAUSE BEFORE QUITTING
    sort_content(BaseSaveLocation)


def welcome():
    print("**** GoPro Ingest Script *****")
    if yes_no_quit("Start Ingest"):
        start_ingest()
    else:
        print("Ok goodbye!")


if __name__ == "__main__":
    welcome()
    #size = convert_size(170618077)
    # size = convert_size(199)
    #print(size)
