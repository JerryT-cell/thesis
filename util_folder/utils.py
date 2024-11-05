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

def create_folders(input_folder: str, output_folder= None):
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

    if output_folder is not None and not os.path.exists(output_folder):
        os.makedirs(output_folder)


def write_into_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)


def write_into_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, separators=(',', ':'))

def open_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
