import math
import os
import json
import random
import shutil
import networkx as nx
from matplotlib import pyplot as plt

def if_string_is_present(file_path: str, search_string: str) -> bool:
    """
    Checks if a string is present in a file.
    :param file_path: the file path
    :param search_string: the search string
    :return:
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if search_string in line:
                return True
    return False


def read_file(file_path: str) -> str:
    """
    Reads the content of a file.

    :param file_path: The path to the file.
    :return: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def format_json(json_string):
    try:
        # Load the JSON string into a Python dictionary
        json_object = json.loads(json_string)

        # Convert the dictionary back to a formatted JSON string
        formatted_json_string = json.dumps(json_object, indent=4)

        return formatted_json_string
    except json.JSONDecodeError as e:
        return f"Invalid JSON input: {e}"

def format_json_file(file_path):
    """
    Format a JSON file.
    :param file_path: the file path
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        json_string = file.read()
        formatted_json = format_json(json_string)
        if formatted_json:
            with open(file_path, "w") as output_file:
                output_file.write(formatted_json)


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
    Returns the files_paths from folder with class diagram.
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


def get_json_files_from_folder_without_activity_and_useCase(folder_path):
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


def extract_a_class_at_random_from_folder(folder_path):
    """
    Extracts a class at random from each file in a folder.
    remove all json objects of contains the id of that class
    saves each extracted class to a file and save it in a folder.
    saves the original file without the class removed in another folder.
    :param folder_path: the folder path where all the files can be found
    :return: none
    """
    os.makedirs(folder_path + "_class_removed", exist_ok=True)
    os.makedirs(folder_path + "_class_extracted", exist_ok=True)
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            json_string = file.read()
            if '"eClass":"Class"' in json_string:
                class_start = json_string.find('"eClass":"Class"')
                class_end = json_string.find('"eClass":"Class"', class_start + 1)
                if class_end == -1:
                    class_end = json_string.find("}", class_start)
                class_string = json_string[class_start: class_end + 1]
                class_removed = json_string.replace(class_string, "")
                class_removed_file_path = os.path.join(folder_path + "_class_removed", file_name)
                class_extracted_file_path = os.path.join(folder_path + "_class_extracted", file_name)
                with open(class_removed_file_path, "w") as class_removed_file:
                    class_removed_file.write(class_removed)
                with open(class_extracted_file_path, "w") as class_extracted_file:
                    class_extracted_file.write(class_string)

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            json_string = file.read()
            json_object = json.loads(json_string)
            class_id = json_object["id"]
            # remove all json objects of contains the id of that class
            for key in json_object:
                if json_object[key] == class_id:
                    del json_object[key]
            # save the extracted class to a file and save it in a folder.


def extract_software_models_type(folder_path):
    """
    Extracts the type of software models in the files in a folder.
    :param folder_path:
    :return: none
    """
    software_models_type = set()
    # get the string that comes after "eClass":  in that single line in all files of the folder. Store the string in the software_model_type if it is not "PackageImport","Package","Comment","Dependency" or "Usage"
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                if '"eClass":' in line:
                    software_model_type = line[line.find('"eClass":') + 10: line.find('"eClass":') + 30]
                    if software_model_type not in ['"Actor"\n', '"MergeNode"\n', '"InitialNode"\n', '"JoinNode"\n', '"EnumerationLiteral"','"Comment"\n','"DecisionNode"\n','"LiteralInteger"\n','"LiteralUnlimitedNat','"ActivityFinalNode"\n','"Usage"\n','"ForkNode"\n','"FlowFinalNode"\n']:
                        software_models_type.add(software_model_type)
    print(software_models_type)


def create_graph_image(json_data, output_filename='graph.png'):
    """
    Create a directed graph visualization from JSON data and save it as an image.
    :param json_data: the json data
    :param output_filename: the output image
    :return: none
    """
    # Parse the JSON data
    graph_data = json.loads(json_data)

    # Initialize a directed graph
    G = nx.MultiDiGraph() if graph_data['multigraph'] else nx.DiGraph()

    # Add nodes to the graph
    for node in graph_data['nodes']:
        G.add_node(node['id'], **node)

    # Add edges to the graph
    for link in graph_data['links']:
        G.add_edge(link['source'], link['target'])

    # Set positions for all nodes
    pos = nx.spring_layout(G)

    # Draw the graph
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=500)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
    nx.draw_networkx_labels(G, pos, labels={node['id']: node.get('name', node['id']) for node in graph_data['nodes']})

    # Save the graph image
    plt.title("Directed Graph Visualization")
    plt.axis('off')
    plt.savefig(output_filename, format="PNG")
    plt.close()


######################## Extraction and creation of input and output folders for fine-tuning  #########################
## the files in the folder path arte json files
## each file is the representation of a graph with a list of nodes and a list of links
## remove 20% of the nodes and remove all the list which have contain the id of the removed nodes(in the source or target). The nodes should be removed at random
## save the new graph in a new file in the input folder
## save the removed nodes in a new file in the output folder
## the name of the new files should be the same as the original file with the suffix "_input" for the input file and "_output" for the output file
## the input folder should be named "json_fine_tuning_input" and the output folder should be named "json_fine_tuning_output"
def extract_and_create_input_output_folders(folder_path, dataset_used, percentage=0.2):
    """
    Extracts and creates input and output folders for fine-tuning.
    :param percentage: How much percent do you want to remove?
    :param folder_path:
    :return: none
    """
    #os.makedirs("json_fine_tuning_input", exist_ok=True)
    #os.makedirs("json_fine_tuning_output", exist_ok=True)
    input_folder = "json_fine_tuning_input/json" + dataset_used
    output_folder = "json_fine_tuning_output/json" + dataset_used
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            json_string = file.read()
            json_object = json.loads(json_string)
            nodes = json_object["nodes"]
            links = json_object["links"]
            # remove 20% of the nodes and remove all the list which have contained the id of the removed nodes(in the source or target). The nodes should be removed at random
            number_of_nodes = len(nodes)
            number_of_nodes_to_remove = math.ceil(percentage * number_of_nodes)
            # sample with the condition that the node with id 0 should not be removed
            nodes_to_remove = random.sample(nodes[1:], number_of_nodes_to_remove)
            input_links = []
            output_links = []
            nodes_ids_to_remove = set()
            for node in nodes_to_remove:
                nodes.remove(node)
                nodes_ids_to_remove.add(node["id"])



            for link in links:
                if link["source"] not in nodes_ids_to_remove and link["target"] not in nodes_ids_to_remove:
                    input_links.append(link)
                else:
                    output_links.append(link)
            # save the new graph in a new file in the input folder
            #create input and output file names
            file_name_input = file_name.replace(".json", "_input.json")
            file_name_output = file_name.replace(".json", "_output.json")


            input_file_path = os.path.join(input_folder, file_name_input)
            output_file_path = os.path.join(output_folder, file_name_output)
            with open(input_file_path, "w") as input_file:
                json.dump({"nodes": nodes, "links": input_links}, input_file, separators=(',', ':'))
            with open(output_file_path, "w") as output_file:
                json.dump({"nodes": nodes_to_remove, "links": output_links }, output_file, separators=(',', ':'))
    print("Done extracting and creating input and output folders for fine-tuning.")




#################################################   Executions  ########################################################


def extract_class_diagrams():
    """
    Extracts class diagrams from the input folder and copies them to the output folder.
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
    """
    Format the current files in the folders.
    :return: none
    """
    #mac:
    #format_all_json_files("json_dataset/json2000_class_diagrams",
    #                      "json_dataset/json2000_class_diagrams_formatted")
    #format_all_json_files("json_dataset/json2000", "json_dataset/json2000_formatted")
    #format_all_json_files("json_dataset/json3000", "json_dataset/json3000_formatted")
    #format_all_json_files("json_dataset/json3000_class_diagrams",
    #                      "json_dataset/json3000_class_diagrams_formatted")
    #windows:
    # format_all_json_files("json_dataset/json2000_class_diagrams",
    #                      "json_dataset/formatted_json/with_classes/json2000_class_diagrams_formatted")
    #format_all_json_files("json_dataset/json2000", "json_dataset/formatted_json/json2000_formatted")
    #format_all_json_files("json_dataset/json3000", "json_dataset/formatted_json/json3000_formatted")
    #format_all_json_files("json_dataset/json3000_class_diagrams",
    #                     "json_dataset/formatted_json/with_classes/json3000_class_diagram_formatted")
    format_all_json_files("json_files/json_dataset/json8192","json_files/json_dataset/json8192_formated")



#################################################   Main   #############################################################

if __name__ == "__main__":
    #extract_class_diagrams()
    #formating_current_files()
    #zip_folder("small_dataset")
    #extract_class_diagrams()
    #extract_software_models_type("json_dataset/json3000_formatted")
    #create_graph_image(read_file("json_dataset/json2000_class_diagrams/5c85815a-d7c3-42f1-a521-a40f1a9d9757.json"), 'graph.png')
    #extract_and_create_input_output_folders("./json_files/json_dataset/json3000", "3000")
    #extract_and_create_input_output_folders("./json_files/json_dataset/json4000", "4000")
    #extract_and_create_input_output_folders("./json_files/json_dataset/json5000", "5000")
    #extract_and_create_input_output_folders("./json_files/json_dataset/json6000", "6000")
    #extract_and_create_input_output_folders("./json_files/json_dataset/json7000", "7000")
    #extract_and_create_input_output_folders("./json_files/json_dataset/json8192", "8192")
    #formating_current_files()
    extract_software_models_type("json_files/json_dataset/json8192_formated")