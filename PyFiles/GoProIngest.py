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


def StoragePresent(DriveNameToCheck=StorageName):
    d_count = 0
    drive_letters = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    for d in drive_letters:
        if d_count + 1 >= len(drive_letters):
            try:
                raise EnvironmentError(f"Storage could not be found, please connect {DriveNameToCheck}")
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
            #d_count += 1
            continue

        if vol_name == DriveNameToCheck:
            print(f"{DriveNameToCheck} found")
            return d
        else:
            d_count += 1


def GetDate():
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


def _CreateDirLoop(dirpath):
    if os.path.isdir(dirpath):
        print(f"\'{dirpath}\' detected")
        os.chdir(dirpath)
        return os.getcwd()
    else:
        os.mkdir(dirpath)
        print(f"{dirpath} Created")
        os.chdir(dirpath)
        return os.getcwd()


def CreateDirStruc(StorageLetter=None):
    if not StorageLetter:
        StorageLetter = StoragePresent()
    else:
        pass
    for firstsubdir in folder_names["LocationSubDirs"]:
        dir_path = os.path.join(StorageLetter, folder_names['root'], firstsubdir)
        # print(dir_path)
        _CreateDirLoop(dir_path)
        # for LocationSub in folder_names["LocationSubDirs"]:
        dir_path = os.path.join(StorageLetter, folder_names['root'], firstsubdir, folder_names["DateOfFootageDir"])
        _CreateDirLoop(dir_path)

        for PerDump in folder_names['PerDumpSubdirs']:
            dir_path = os.path.join(StorageLetter, folder_names['root'],
                                    firstsubdir, folder_names["DateOfFootageDir"], PerDump)
            _CreateDirLoop(dir_path)
    # TODO: fix this so that it works with both the PhoneData and RawGoProData subdirs
    return os.path.join(StorageLetter, folder_names['root'], folder_names["LocationSubDirs"][0],
                        folder_names["DateOfFootageDir"])


def _SaveLocationCheck(media_save_location, support_save_location):
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


def SortContent(base_save_location):
    media_save_location = os.path.join(base_save_location, "MP4andJPEG")
    support_save_location = os.path.join(base_save_location, "THMandLRV")

    media_files = [os.path.join(CamSD_ContentBasePath, x) for x in os.listdir(CamSD_ContentBasePath)
                   if x.lower().endswith(".mp4") or x.lower().endswith(".jpeg")]
    # print(media_files)
    support_files = [os.path.join(CamSD_ContentBasePath, x) for x in os.listdir(CamSD_ContentBasePath)
                     if x.lower().endswith(".thm") or x.lower().endswith(".lrv")]

    _SaveLocationCheck(media_save_location, support_save_location)

    for f in media_files:
        # shutil.Error
        shutil.copy2(f, media_save_location)
        print(f"{f} copied")

    for f in support_files:
        shutil.copy2(f, support_save_location)
        print(f"{f} copied")


def yesnoquit(question):
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


def StartIngest():
    # TODO: Add Logging - handle in separate thread?
    # TODO: add "file already copied" checker - hash?
    # TODO: add in shutil error handling
    global folder_names, CamSD_ContentBasePath, CamSD_DriveLetter

    folder_names = {
        'root': 'P-Town',
        'LocationSubDirs': LocationSubDirs,
        'DateOfFootageDir': f"{GetDate()}-{current_date}",
        'PerDumpSubdirs': PerDumpSubdirs
    }

    BaseSaveLocation = CreateDirStruc()  # StorageLetter="C:\\Users\\amcsp\\Desktop")

    CamSD_DriveLetter = StoragePresent(CameraSDName)  # 'D:\\'
    CamSD_ContentBasePath = os.path.join(CamSD_DriveLetter, "DCIM", "100GOPRO")
    # TODO: make this easier to look at and PAUSE BEFORE QUITTING
    SortContent(BaseSaveLocation)


def welcome():
    print("**** GoPro Ingest Script *****")
    if yesnoquit("Start Ingest"):
        StartIngest()
    else:
        print("Ok goodbye!")


if __name__ == "__main__":
    welcome()
    """folder_names = {
        'root': 'P-Town',
        'LocationSubDirs': LocationSubDirs,
        'DateOfFootageDir': f"{GetDate()}-{current_date}",
        'PerDumpSubdirs': PerDumpSubdirs
    }

    BaseSaveLocation = CreateDirStruc()  # StorageLetter="C:\\Users\\amcsp\\Desktop")

    CamSD_DriveLetter = StoragePresent(CameraSDName)  # 'D:\\'
    CamSD_ContentBasePath = os.path.join(CamSD_DriveLetter, "DCIM", "100GOPRO")
    # TODO: make this easier to look at and PAUSE BEFORE QUITTING
    SortContent(BaseSaveLocation)"""
