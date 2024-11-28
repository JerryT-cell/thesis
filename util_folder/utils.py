import shutil
import os
import json


def zip_folder(folder_path):
    shutil.make_archive(folder_path, 'zip', folder_path)


def unzip_folder(folder_path):
    shutil.unpack_archive(folder_path, folder_path.replace(".zip",""))


def copy_file(file_path, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    shutil.copy(file_path, destination_folder)

def create_folders(folder_one = None, folder_two= None):
    if folder_one is not None and not os.path.exists(folder_one):
        os.makedirs(folder_one)

    if folder_two is not None and not os.path.exists(folder_two):
        os.makedirs(folder_two)


def write_into_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)


def write_into_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, separators=(',', ':'))

def open_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
