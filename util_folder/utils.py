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

def fix_and_validate_json(json_str):
    # Check if "nodes" is present at all
    if '"nodes":' not in json_str:
        print("No 'nodes' found in the JSON.")
        return None

    # Try to load JSON as is
    try:
        data = json.loads(json_str)
        # If we get here, it's already valid
        # Check if nodes are present and is a list
        if "nodes" not in data or not isinstance(data["nodes"], list):
            print("JSON does not contain a valid 'nodes' list.")
            return None
        return data
    except json.JSONDecodeError:
        # JSON is malformed. Attempt to fix by looking backwards.
        pass

    # Attempt Fix:
    # We know it has "nodes", so let's try to fix the ending.
    # Strategy:
    # 1. Find the last '}' that might close the last node object.
    # 2. Slice the string up to that '}', then append "]}" to properly close.

    # Remove trailing whitespaces just in case
    truncated = json_str.rstrip()

    # If it already ends with ']}', it might be something else wrong
    if truncated.endswith(']}'):
        print("JSON is malformed in a different way, cannot fix easily.")
        return None

    # Search backward for the last closing brace '}' that might represent end of last node
    last_brace_index = truncated.rfind('}')

    if last_brace_index == -1:
        # No closing brace found at all, cannot fix
        print("No closing brace '}' found, cannot fix.")
        return None

    # Attempt to fix by appending "]}" after that brace
    fixed_str = truncated[:last_brace_index + 1] + "]}"

    # Try loading again
    try:
        data = json.loads(fixed_str)
        # Check nodes presence again
        if "nodes" not in data or not isinstance(data["nodes"], list):
            print("After fixing, JSON does not contain a valid 'nodes' list.")
            return None
        return data
    except json.JSONDecodeError:
        # Even after fix, it's not valid
        print("Could not fix the JSON structure.")
        return None