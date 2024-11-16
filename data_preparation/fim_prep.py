from util_folder.utils import create_folders, write_into_file
import os
import json
import random
from typing import Set

def divide_json_string_with_masks(input_folder: str,
                                  max_token_count: int,
                                  folder_to_save: str,
                                  percentage: float = 0.2,
                                  left_and_Right: bool = False):
    """
    Divides the content of JSON files in the input folder into two parts based on the specified percentage.
    Replaces the second part with mask tokens and saves the modified JSON in the input_output_folder.
    Saves the masked content in the output_folder, each prefixed with its corresponding <Mask:k> token.

    Parameters:
       :parameter input_folder : Path to the folder containing the original JSON files.
       :param folder_to_save: Path to the folder where the modified JSON files will be saved.
       :parameter max_token_count : Maximum number of tokens in the input sequence.
       :parameter percentage : The percentage of elements to remove from each file.
       :param left_and_Right:  if True, it will create a file with the left and right parts swapped
    """
    #create folders for input_output_folder and output_folder
    input_output_folder = os.path.join(folder_to_save, 'processed_input' + str(max_token_count))
    output_folder = os.path.join(folder_to_save, 'processed_output' + str(max_token_count))
    create_folders(input_output_folder, output_folder)

    for filename in os.listdir(input_folder):

        file_path = os.path.join(input_folder, filename)

        # Read the JSON file as a string
        with open(file_path, 'r') as file:
            json_string = file.read()

        total_length = len(json_string)
        split_length = int(total_length * percentage)

        # Choose a random starting point for the output part
        start_index = random.randint(0, total_length - split_length)

        # Split the string into two parts
        pre = json_string[:start_index]
        suf = json_string[start_index + split_length:]
        middle = json_string[start_index:split_length]

        input_part_left_to_right = '<PRE>' + pre + '<SUF>'+ suf
        output_part = middle
        # Save the modified JSON string to the input_output_folder
        input_output_file_path = os.path.join(input_output_folder, filename.replace('.json', '_inputps.json'))
        write_into_file(input_output_file_path, input_part_left_to_right)

        if left_and_Right:
            input_output_file_path = os.path.join(input_output_folder, filename.replace('.json', '_inputsp.json'))
            input_part_right_to_left = '<SUF>' + suf + '<PRE>'+ pre
            write_into_file(input_output_file_path, input_part_right_to_left)

        # Save the masked content to the output_folder, prefixed with the mask token
        masked_output_file_path = os.path.join(output_folder, filename + "_output")
        write_into_file(masked_output_file_path, output_part + '<EOT>')

        print(f"Processed file: {filename}")


def structurally_mask_contiguous_elements_and_save(
        input_folder: str,
        max_token_count: int,
        folder_to_save: str,
        percentage: float = 0.2,
        eclass_exclusions: Set[str] = {"Interaction", "Activity", "StateMachine"},
        right_and_left: bool = False
):
    """
    Masks a contiguous block of elements (nodes) in JSON files with a single mask token,
    excluding elements with specified eClasses.
    Saves the modified JSON files in the input_output_folder and the masked elements in the output_folder.
    Ensures that the saved files are minified (no additional whitespace).
    The masked nodes are replaced with a single <Mask> token in the 'nodes' list.
    Updates links accordingly.

    Args:
        input_folder (str): Path to the folder containing the original JSON files.
        input_output_folder (str): Path to the folder where modified JSON files will be saved.
        output_folder (str): Path to the folder where masked elements will be saved.
        percentage (float): The percentage of elements to mask from each file.
        eclass_exclusions (Set[str]): Set of eClass names to exclude from masking.
    """
    input_output_folder = os.path.join(folder_to_save, 'processed_input' + str(max_token_count))
    output_folder = os.path.join(folder_to_save, 'processed_output' + str(max_token_count))
    create_folders(input_output_folder, output_folder)

    max_percentage_masked = 0.0  # To track the maximum percentage of nodes masked

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        nodes = data.get('nodes', [])
        links = data.get('links', [])

        total_nodes_before = len(nodes)  # Total nodes before masking

        if total_nodes_before == 0:
            print(f"No nodes to process in file {filename}. Skipping.")
            continue

        # Exclude nodes with specified eClasses
        maskable_nodes = [
            node for node in nodes if node.get('eClass') not in eclass_exclusions
        ]

        # Sort the nodes to have a consistent order
        maskable_nodes.sort(key=lambda x: x['id'])

        # Calculate number of nodes to mask
        num_nodes_to_mask = max(1, int(len(maskable_nodes) * percentage))

        # Ensure that num_nodes_to_mask does not exceed the number of maskable nodes
        num_nodes_to_mask = min(num_nodes_to_mask, len(maskable_nodes))

        # Select a random starting index for the contiguous block
        max_start_index = len(maskable_nodes) - num_nodes_to_mask
        if max_start_index > 0:
            start_index = random.randint(0, max_start_index)
        else:
            start_index = 0

        # Get the contiguous block of nodes to mask
        nodes_to_mask = maskable_nodes[start_index:start_index + num_nodes_to_mask]
        nodes_to_mask_ids = set(node['id'] for node in nodes_to_mask)
        prefix_nodes = maskable_nodes[:start_index]
        suffix_nodes = maskable_nodes[start_index + num_nodes_to_mask:]

        # Prepare to collect masked nodes and adjust nodes and links
        masked_nodes = []
        node_id_to_mask = {}
        masked_node_ids = nodes_to_mask_ids

        # Replace the contiguous nodes with a single <Mask> token
        modified_nodes = []
        for node in nodes:
            if node['id'] in nodes_to_mask_ids:
                # Skip adding this node to modified_nodes
                masked_nodes.append(node)
            else:
                modified_nodes.append(node)

        #Prepend the modified nodes with "<PRE>"
        modified_nodes =  modified_nodes
        prefix_nodes = ["<PRE>"] + prefix_nodes
        suffix_nodes = ["<SUF>"] + suffix_nodes
        # Update links: remove links connected to masked nodes
        modified_links = []
        masked_links = []
        for link in links:
            source = link.get('source')
            target = link.get('target')
            if source in masked_node_ids or target in masked_node_ids:
                # Link is connected to a masked node, remove it
                masked_links.append(link)
            else:
                modified_links.append(link)

        # Update the data dictionaries
        modified_data = {'nodes': modified_nodes, 'links': modified_links}

        # Prepare the masked elements output
        masked_data = {
            'nodes': masked_nodes,
            'links': masked_links
        }

        # Calculate percentages
        total_nodes_masked = len(masked_nodes)
        total_nodes_after = len(modified_nodes)

        # Calculate the percentage of nodes masked in this file
        if total_nodes_before > 0:
            percentage_masked = (total_nodes_masked / total_nodes_before) * 100
        else:
            percentage_masked = 0

        # Update the maximum percentage masked if current is greater
        if percentage_masked > max_percentage_masked:
            max_percentage_masked = percentage_masked

        # Save the modified JSON to the input_output_folder (minified)
        input_output_file_path = os.path.join(input_output_folder, filename)
        with open(input_output_file_path, 'w') as output_file:
            json.dump(modified_data, output_file, separators=(',', ':'))

        # Save the masked elements to the output_folder (minified)
        output_file_path = os.path.join(output_folder, filename)
        with open(output_file_path, 'w') as output_file:
            json.dump(masked_data, output_file, separators=(',', ':'))

        print(f"Processed file: {filename}")
        print(f"Percentage of nodes masked in {filename}: {percentage_masked:.2f}%")

    print(f"\nMaximum percentage of nodes masked across all files: {max_percentage_masked:.2f}%")