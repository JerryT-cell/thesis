import shutil
import os


def zip_folder(folder_path):
    shutil.make_archive(folder_path, 'zip', folder_path)


def unzip_folder(folder_path):
    shutil.unpack_archive(folder_path, folder_path.append("unzipped"))


def copy_file(file_path, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    shutil.copy(file_path, destination_folder)
