import shutil
import os
import json


def if_string_is_present(file_path: str, search_string: str) -> bool:
    """
    Reads the content of the file until it encounters the string 'packagedElement xsi:type="uml:Class"'.

    :param search_string:
    :param file_path: The path to the file.
    :return: The content read until the specified string is found.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if search_string in line:
                return True
    return False


def format_json(json_string):
    try:
        # Load the JSON string into a Python dictionary
        json_object = json.loads(json_string)

        # Convert the dictionary back to a formatted JSON string
        formatted_json_string = json.dumps(json_object, indent=4)

        return formatted_json_string
    except json.JSONDecodeError as e:
        return f"Invalid JSON input: {e}"


def copy_files_to_folder(file_list, destination_folder):
    """
    Copy files to a destination folder.
    :param file_list: the list of files to copy
    :param destination_folder: the destination folder
    """
    os.makedirs(destination_folder, exist_ok=True)
    for file in file_list:
        shutil.copy(file, destination_folder)


def format_all_json_files(folder_name, destination_folder):
    """
    Format all JSON files in the folder and save them to the destination folder.
    :param folder_name: the folder containing the JSON files
    :param destination_folder: the destination folder to save the formatted JSON files
    """
    os.makedirs(destination_folder, exist_ok=True)
    for file_name in os.listdir(folder_name):
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            json_string = file.read()
            formatted_json = format_json(json_string)
            if formatted_json:
                output_file_path = os.path.join(destination_folder, file_name)
                with open(output_file_path, "w") as output_file:
                    output_file.write(formatted_json)


#### Specific functions for the json dataset  ####


def count_json_files_with_strings(folder_path: str, search_strings):
    """
        Counts the number of files in a folder.

        :param search_strings:
        :param folder_path: The path to the folder.
        :return: The number of files in the folder.
        """
    file_count = 0
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            for search_string in search_strings:
                if if_string_is_present(file_path, search_string):
                    file_count += 1
                    break
    return file_count


def count_json_files_without_class_diagrams(folder_path: str):
    """
        Counts the number of files in a folder without a class diagram.

        """
    file_count = 0
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            if not if_string_is_present(file_path, '"eClass":"Class"'):
                file_count += 1
    return file_count


def get_json_files_from_folder_with_class_diagrams(folder_path):
    """
    Returns the files_paths with class diagram in the folder.
    :param folder_path: the folder path
    :return: the files_paths with class diagram
    """
    file_count = 0
    files_paths = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if if_string_is_present(file_path, '"eClass":"Class"'):
            files_paths.append(file_path)
            file_count += 1
    # print the number of files
    print("The number of files is " + str(file_count))
    # print the file paths
    print(files_paths)
    return files_paths


def get_json_files_from_folder_without_activity_and_UseCase(folder_path):
    """
    Returns the files_paths with class diagram in the folder.
    :param folder_path: the folder path
    :return: the files_paths with class diagram
    """
    file_count = 0
    files_paths = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        is_class_diagram = True
        for other_diagrams in ['::Activity', 'model::UseCase']:
            if if_string_is_present(file_path, other_diagrams):
                is_class_diagram = False
                break
        if is_class_diagram:
            files_paths.append(file_path)
            file_count += 1
    # print the number of files
    print("The number of files is " + str(file_count))
    # print the file paths
    print(files_paths)
    return files_paths

    #######   Executions  ########


def extract_class_diagrams():
    """
    Extracts class diagrams from the input folder and copies them to the output folder.
    :param input_folder: the input folder
    :param output_folder: the output folder
    """
    folder1 = "json_dataset/json2000"
    folder2 = "json_dataset/json3000"
    class_diagrams1 = get_json_files_from_folder_with_class_diagrams(folder1)
    class_diagrams2 = get_json_files_from_folder_with_class_diagrams(folder2)
    print("The number of files in json2000 is " + str(len(class_diagrams1)))
    print("The number of files in json3000 is " + str(len(class_diagrams2)))
    destination_folder1 = "json_dataset/json2000_class_diagrams"
    destination_folder2 = "json_dataset/json3000_class_diagrams"
    copy_files_to_folder(class_diagrams1, destination_folder1)
    copy_files_to_folder(class_diagrams2, destination_folder2)


def formating_current_files():
    format_all_json_files("json_dataset/json2000_class_diagrams",
                          "json_dataset/formatted_json/with_classes/json2000_class_diagrams_formatted")
    #format_all_json_files("json_dataset/json2000", "json_dataset/formatted_json/json2000_formatted")
    #format_all_json_files("json_dataset/json3000", "json_dataset/formatted_json/json3000_formatted")
    format_all_json_files("json_dataset/json3000_class_diagrams",
                          "json_dataset/formatted_json/with_classes/json3000_class_diagram_formatted")


def extract_a_class_at_random_from_folder(folder_path):







def zip_folder(folder_path):
    shutil.make_archive(folder_path, 'zip', folder_path)

def unzip_folder(folder_path):
    shutil.unpack_archive(folder_path, folder_path.append("unzipped"))


if __name__ == "__main__":
    #formating_current_files()
    zip_folder("small_dataset")
    #extract_class_diagrams()

