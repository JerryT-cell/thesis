import os
import json
import random
from typing import Set
from util_folder.utils import create_folders, write_into_file, write_into_json_file
import statistics


def divide_json_string_contiguous( max_token_count: int,
                                   input_folder: str,
                                   folder_to_save: str,
                                   percentage: float = 0.2):
    """
    Divides the content of JSON files in the input folder into two parts based on the specified percentage.
    Saves the first part (e.g., 80%) in the input_output_folder and the second part (e.g., 20%) in the output_folder.

    Parameters:
       :parameter  input_folder : Path to the folder containing the original JSON files.
       :parameter  input_output_folder : Path to the folder where the first part of the JSON files will be saved.
       :parameter  output_folder : Path to the folder where the second part of the JSON files will be saved.
       :parameter  percentage : The percentage of the string to allocate to the output files (default is 0.2 for 20%).
    """

    #create folders for input_output_folder and output_folder
    input_output_folder = os.path.join(folder_to_save, 'processed_input' + str(max_token_count))
    output_folder = os.path.join(folder_to_save, 'processed_output' + str(max_token_count))
    create_folders(input_output_folder, output_folder)

    #Go into the input folder and read the files
    for filename in os.listdir(input_folder):
        print(f"Processing file: {filename}")

        file_path = os.path.join(input_folder, filename)

        # Read the JSON file as a string
        with open(file_path, 'r') as file:
            json_string = file.read()

        total_length = len(json_string)
        print(f"Total length of the JSON string: {total_length}")
        split_length = int(total_length * percentage)
        print(f"Split length: {split_length}")

        # Choose a random starting point for the output part
        start_index = random.randint(0, total_length - split_length)

        # Split the string into two parts
        input_part = json_string[:start_index] + json_string[start_index + split_length:]
        input_length = len(input_part)
        print(f"Length of the input part: {input_length}")
        print(f"start_index: {start_index}")
        print(f"split_length: {split_length}")
        output_part = json_string[start_index:split_length+start_index]
        output_length = len(output_part)
        print(f"Length of the output part: {output_length}")


        # Save the big% part in the input_output_folder
        input_output_file_path = os.path.join(input_output_folder, filename.replace('.json', '_input.json'))
        write_into_file(input_output_file_path, input_part)

        # Save the small% part in the output_folder
        output_file_path = os.path.join(output_folder, filename.replace('.json', '_output.json'))
        write_into_file(output_file_path, output_part)

        print(f"Processed file: {filename}")



def structurally_remove_elements_and_save(
        max_token_count: int,
        input_folder: str,
        folder_to_save: str,
        percentage: float,
        eClass_exclusions=None
):
    """
    Removes a specified percentage of elements (nodes) from JSON files in the input folder,
    excluding elements with specified eClasses.
    Saves the modified JSON files in the input_output_folder and the removed elements in the output_folder.
    Ensures that the saved files are minified (no additional whitespace).

    parameters:
        :param folder_to_save: Path to the folder where the modified JSON files will be saved.
        :parameter max_token_count : Maximum number of tokens in the input sequence.
        :parameter input_folder : Path to the folder containing the original JSON files.
        :parameter percentage : The percentage of elements to remove from each file.
        :parameter eClass_exclusions : Set of eClass names to exclude from removal.
    """
    input_output_folder = os.path.join(folder_to_save, 'processed_input' + str(max_token_count))
    output_folder = os.path.join(folder_to_save, 'processed_output' + str(max_token_count))

    if eClass_exclusions is None:
        eClass_exclusions = {"Interaction", "Activity", "StateMachine"}
    create_folders(input_output_folder, output_folder)
    max_percentage_removed = 0.0  # To track the maximum percentage of nodes removed
    percentages_removed = []

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(input_folder, filename)

            # Read the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)

            nodes = data.get('nodes', [])
            links = data.get('links', [])

            total_nodes_before = len(nodes)  # Total nodes before removal


            # Exclude nodes with specified eClasses
            removable_nodes = [
                node for node in nodes if node.get('eClass') not in eClass_exclusions
            ]
            print(f"Total nodes before removal: {len(removable_nodes)}")

            # Calculate number of nodes to remove
            num_nodes_to_remove = int(len(removable_nodes) * percentage)
            print(f"Number of nodes to remove: {num_nodes_to_remove}")

            # Randomly select nodes to remove
            nodes_to_remove_ids = set()
            if num_nodes_to_remove > 0:
                nodes_to_remove_ids = set(
                    random.sample([node['id'] for node in removable_nodes], num_nodes_to_remove)
                )

            # Prepare lists to store removed nodes and links
            removed_nodes = []
            removed_links = []

            # **First, remove the selected nodes from the nodes list**
            remaining_nodes = []
            for node in nodes:
                if node['id'] in nodes_to_remove_ids:
                    removed_nodes.append(node)
                else:
                    remaining_nodes.append(node)
            nodes = remaining_nodes  # Update nodes list
            print(f"nodes in removed_nodes: {len(removed_nodes)}")
            print(f"nodes in remaining_nodes: {len(remaining_nodes)}")


            # **Remove associated links of the removed nodes**
            remaining_links = []
            for link in links:
                if link.get('source') in nodes_to_remove_ids or link.get('target') in nodes_to_remove_ids:
                    removed_links.append(link)
                else:
                    remaining_links.append(link)
            links = remaining_links  # Update links list

            # Identify nodes without any links (excluding eClass exclusions)
            linked_node_ids: Set[int] = set()
            for link in links:
                linked_node_ids.add(link.get('source'))
                linked_node_ids.add(link.get('target'))

            # Find unlinked nodes to remove
            unlinked_nodes = [
                node for node in nodes
                if node['id'] not in linked_node_ids and node.get('eClass') not in eClass_exclusions
            ]
            print(f"nodes without links: {len(unlinked_nodes)}")

            # Remove unlinked nodes and add them to removed nodes
            nodes = [
                node for node in nodes
                if node['id'] in linked_node_ids or node.get('eClass') in eClass_exclusions
            ]
            removed_nodes.extend(unlinked_nodes)


            total_nodes_removed = len(removed_nodes)  # Total nodes removed
            print(f"nodes in removed_nodes after adding unlinked nodes: {total_nodes_removed}")

            # Calculate the percentage of nodes removed in this file
            if total_nodes_before > 0:
                percentage_removed = (total_nodes_removed / total_nodes_before) * 100
            else:
                percentage_removed = 0

            percentages_removed.append(percentage_removed)
            # Update the maximum percentage removed if current is greater
            if percentage_removed > max_percentage_removed:
                max_percentage_removed = percentage_removed

            # Update the data dictionaries
            modified_data= {
                'directed': data['directed'],
                'nodes': nodes,
                'links': links,
                'multigraph': data['multigraph']
            }
            removed_data = {'nodes': removed_nodes, 'links': removed_links}

            # Save the modified JSON (rest) to the input_output_folder (minified)
            input_output_file_path = os.path.join(input_output_folder, filename)
            write_into_json_file(input_output_file_path, modified_data)

            # Save the removed elements to the output_folder (minified)
            output_file_path = os.path.join(output_folder, filename)
            write_into_json_file(output_file_path, removed_data)

            print(f"Processed file: {filename}")
            print(f"Percentage of nodes removed in {filename}: {percentage_removed:.2f}%")

    #create a file that will store the maximum percentage removed, the median and the average, the number of files processed
    print(f"\nMaximum percentage of nodes removed across all files: {max_percentage_removed:.2f}%")
    file_statistics_of_files_processed(percentages_removed, max_percentage_removed, folder_to_save + '/statistics_' + str(max_token_count) +'.txt')




def structurally_remove_contiguous_elements_and_save(
        max_token_count: int,
        input_folder: str,
        folder_to_save: str,
        percentage: float,
        eClass_exclusions=None
):
    """
    Removes a contiguous block of elements (nodes) constituting a specified percentage from JSON files,
    excluding elements with specified eClasses.
    Saves the modified JSON files in the input_output_folder and the removed elements in the output_folder.
    Ensures that the saved files are minified (no additional whitespace).

    parameters:
        :param folder_to_save: Path to the folder where the modified JSON files will be saved.
        :parameter max_token_count : Maximum number of tokens in the input sequence.
        :parameter input_folder : Path to the folder containing the original JSON files.
        :parameter percentage : The percentage of elements to remove from each file.
        :parameter eClass_exclusions : Set of eClass names to exclude from removal.
    """
    input_output_folder = os.path.join(folder_to_save, 'processed_input' + str(max_token_count))
    output_folder = os.path.join(folder_to_save, 'processed_output' + str(max_token_count))
    #write a function to check if folder_to_save is a folder
    create_folders(input_output_folder, output_folder)

    if eClass_exclusions is None:
        eClass_exclusions = {"Interaction", "Activity", "StateMachine"}

    max_percentage_removed = 0.0  # To track the maximum percentage of nodes removed
    percentages_removed = []

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        nodes = data.get('nodes', [])
        links = data.get('links', [])

        total_nodes_before = len(nodes)  # Total nodes before removal

        if total_nodes_before == 0:
            print(f"No nodes to process in file {filename}. Skipping.")
            continue

        # Exclude nodes with specified eClasses
        removable_nodes = [
            node for node in nodes if node.get('eClass') not in eClass_exclusions
        ]

        # Sort the nodes to ensure consistent ordering
        removable_nodes.sort(key=lambda x: x['id'])

        # Calculate number of nodes to remove
        num_nodes_to_remove = max(1, int(len(removable_nodes) * percentage))
        num_nodes_to_remove = min(num_nodes_to_remove, len(removable_nodes))

        # Determine the range for starting index
        max_start_index = len(removable_nodes) - num_nodes_to_remove
        if max_start_index > 0:
            start_index = random.randint(0, max_start_index)
        else:
            start_index = 0

        # Select the contiguous block of nodes to remove
        nodes_to_remove = removable_nodes[start_index:start_index + num_nodes_to_remove]
        nodes_to_remove_ids = set(node['id'] for node in nodes_to_remove)

        # Prepare lists to store removed nodes and links
        removed_nodes = []
        removed_links = []

        # Remove the selected nodes from the nodes list
        nodes = [node for node in nodes if node['id'] not in nodes_to_remove_ids or removed_nodes.append(node)]

        # Remove associated links of the removed nodes
        links = [
            link for link in links
            if (link.get('source') not in nodes_to_remove_ids and link.get('target') not in nodes_to_remove_ids)
               or removed_links.append(link)
        ]

        # Identify unlinked nodes among the remaining nodes
        linked_node_ids: Set[int] = set()
        for link in links:
            linked_node_ids.add(link.get('source'))
            linked_node_ids.add(link.get('target'))

        # Remove unlinked nodes (excluding eClass exclusions)
        unlinked_nodes = [
            node for node in nodes
            if node['id'] not in linked_node_ids and node.get('eClass') not in eClass_exclusions
        ]
        nodes = [
            node for node in nodes
            if node['id'] in linked_node_ids or node.get('eClass') in eClass_exclusions
        ]

        # Add unlinked nodes to removed nodes
        removed_nodes.extend(unlinked_nodes)

        # Calculate percentages
        total_nodes_removed = len(removed_nodes)
        total_nodes_after = len(nodes)

        # Calculate the percentage of nodes removed in this file
        if total_nodes_before > 0:
            percentage_removed = (total_nodes_removed / total_nodes_before) * 100
        else:
            percentage_removed = 0


        percentages_removed.append(percentage_removed)
        # Update the maximum percentage removed if current is greater
        if percentage_removed > max_percentage_removed:
            max_percentage_removed = percentage_removed

        # Update the data dictionaries
        modified_data= {
            'directed': data['directed'],
            'nodes': nodes,
            'links': links,
            'multigraph': data['multigraph']
        }
        removed_data = {'nodes': removed_nodes, 'links': removed_links}

        # Save the modified JSON (rest) to the input_output_folder (minified)
        input_output_file_path = os.path.join(input_output_folder, filename)
        write_into_json_file(input_output_file_path, modified_data)

        # Save the removed elements to the output_folder (minified)
        output_file_path = os.path.join(output_folder, filename)
        write_into_json_file(output_file_path, removed_data)

        print(f"Processed file: {filename}")
        print(f"Percentage of nodes removed in {filename}: {percentage_removed:.2f}%")

    print(f"\nMaximum percentage of nodes removed across all files: {max_percentage_removed:.2f}%")
    file_statistics_of_files_processed(percentages_removed, max_percentage_removed, folder_to_save + '/statistics_' + str(max_token_count) +'.txt')


def file_statistics_of_files_processed(list_percentages_removed, max_percentage_removed, path):
    """
    Calculates the median and average of the percentage of nodes removed across all files processed.
    Writes the maximum percentage removed, median, average, and number of files processed to a text file.

    Args:
        list_percentages_removed (List[float]): List of percentages of nodes removed in each file.
        max_percentage_removed (float): Maximum percentage of nodes removed across all files.
        path (str): Path to the file where the statistics will be saved.
    """
    with open(path, 'w') as file:
        file.write(f"Maximum percentage of nodes removed across all files: {max_percentage_removed:.2f}%\n")
        median, average = calculate_median_and_average(list_percentages_removed)
        file.write(f"Median percentage of nodes removed: {median:.2f}%\n")
        file.write(f"Average percentage of nodes removed: {average:.2f}%\n")
        file.write(f"Number of files processed: {len(list_percentages_removed)}")



def calculate_median_and_average(numbers):
    if not numbers:
        return None, None  # Return None if the list is empty

    median = statistics.median(numbers)
    average = sum(numbers) / len(numbers)

    return median, average



##################### Producing exploring_datasets  #####################

org_path = '/Users/jerrytakou/University/Thesis/programming/Thesis_org'

def producing_datasets_at_random_contiguous(max_token_count, percentage):
    """
    Produces exploring_datasets by removing a contiguous block of elements (nodes) from JSON files at random,
    excluding elements with specified eClasses.
    Saves the modified JSON files in the input_output_folder and the removed elements in the output_folder.

    Parameters:
         :parameter  max_token_count : Maximum number of tokens in the input sequence.
         :parameter  percentage : The percentage of elements to remove from each file.
    """
    input_folder = os.path.join(org_path,'json_dataset/json' + str(max_token_count))
    path_to_save = os.path.join(org_path,'fine_tuning_raw_datasets/random_removal', 'processed_' + str(max_token_count))
    create_folders(path_to_save)

    # Call the function to process the files
    divide_json_string_contiguous(max_token_count, input_folder, path_to_save, percentage)

def producing_datasets_structurally_non_contiguous(max_token_count, percentage):
    """
    Produces exploring_datasets by removing a contiguous block of elements (nodes) from JSON files at random,
    excluding elements with specified eClasses.
    Saves the modified JSON files in the input_output_folder and the removed elements in the output_folder.

    Parameters:
         :parameter  max_token_count : Maximum number of tokens in the input sequence.
         :parameter  percentage : The percentage of elements to remove from each file.
    """
    input_folder = os.path.join(org_path,'json_dataset/json' + str(max_token_count))
    path_to_save = os.path.join(org_path,'fine_tuning_raw_datasets/structural_removal_non_contiguous' , 'processed_' + str(max_token_count))
    create_folders(path_to_save)

    # Call the function to process the files
    structurally_remove_elements_and_save( max_token_count, input_folder,path_to_save, percentage)


def producing_datasets_structurally_contiguous(max_token_count, percentage):
    """
    Produces exploring_datasets by removing a contiguous block of elements (nodes) from JSON files at random,
    excluding elements with specified eClasses.
    Saves the modified JSON files in the input_output_folder and the removed elements in the output_folder.

    Parameters:
         :parameter  max_token_count : Maximum number of tokens in the input sequence.
         :parameter  percentage : The percentage of elements to remove from each file.
    """
    input_folder = os.path.join(org_path,'json_dataset/json' + str(max_token_count))
    path_to_save = os.path.join(org_path,'fine_tuning_raw_datasets/structural_removal_contiguous' , 'processed_' + str(max_token_count))
    create_folders(path_to_save)

    # Call the function to process the files
    structurally_remove_contiguous_elements_and_save(max_token_count, input_folder, path_to_save, percentage)

producing_datasets_structurally_non_contiguous(2000,0.2)
producing_datasets_at_random_contiguous(2000,0.2)
producing_datasets_structurally_contiguous(2000,0.2)






















































def divide_json_string_with_masks(input_folder: str, input_output_folder: str, output_folder: str, percentage: float = 0.2):
    """
    Divides the content of JSON files in the input folder into two parts based on the specified percentage.
    Replaces the second part with mask tokens and saves the modified JSON in the input_output_folder.
    Saves the masked content in the output_folder, each prefixed with its corresponding <Mask:k> token.

    Parameters:
       input_folder (str): Path to the folder containing the original JSON files.
       input_output_folder (str): Path to the folder where the modified JSON files will be saved.
       output_folder (str): Path to the folder where the masked content will be saved.
       percentage (float): The percentage of the string to allocate to the masked content (default is 0.2 for 20%).
    """
    create_folders(input_output_folder, output_folder)

    mask_counter = 0

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(input_folder, filename)

            # Read the JSON file as a string
            with open(file_path, 'r') as file:
                json_string = file.read()

            total_length = len(json_string)
            split_index = int(total_length * (1 - percentage))

            # Split the string into two parts
            input_part = json_string[:split_index]
            output_part = json_string[split_index:]

            # Replace the output part with a mask token in the input
            mask_token = f'<Mask:{mask_counter}>'
            modified_json_string = input_part + mask_token

            # Save the modified JSON string to the input_output_folder
            input_output_file_path = os.path.join(input_output_folder, filename)
            with open(input_output_file_path, 'w') as input_output_file:
                input_output_file.write(modified_json_string)

            # Save the masked content to the output_folder, prefixed with the mask token
            masked_output_file_path = os.path.join(output_folder, filename)
            with open(masked_output_file_path, 'w') as output_file:
                output_file.write(mask_token + output_part)

            print(f"Processed file: {filename}")

            mask_counter += 1








def structurally_mask_contiguous_elements_bidirectional(
        input_folder: str,
        input_output_folder: str,
        output_folder: str,
        percentage: float,
        eclass_exclusions: Set[str] = {"Interaction", "Activity", "StateMachine"}
):
    """
    Masks a contiguous block of elements (nodes) in JSON files and creates two input files per original file:
    - One with left context + <Mask> + right context (lr version).
    - One with right context + <Mask> + left context (rl version).
    Each input file is associated with the same output file containing the masked middle part.
    Filenames include indicators like 'lr' and 'rl' to distinguish between the two versions.

    Args:
        input_folder (str): Path to the folder containing the original JSON files.
        input_output_folder (str): Path to the folder where modified input JSON files will be saved.
        output_folder (str): Path to the folder where masked elements (outputs) will be saved.
        percentage (float): The percentage of elements to mask from each file.
        eclass_exclusions (Set[str]): Set of eClass names to exclude from masking.
    """
    create_folders(input_output_folder, output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(input_folder, filename)

            # Read the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)

            nodes = data.get('nodes', [])
            links = data.get('links', [])

            total_nodes = len(nodes)
            if total_nodes == 0:
                print(f"No nodes to process in file {filename}. Skipping.")
                continue

            # Exclude nodes with specified eClasses
            maskable_nodes = [
                node for node in nodes if node.get('eClass') not in eclass_exclusions
            ]

            if not maskable_nodes:
                print(f"No maskable nodes in file {filename}. Skipping.")
                continue

            # Sort the nodes to have a consistent order
            nodes_sorted = sorted(nodes, key=lambda x: x['id'])

            # Calculate number of nodes to mask (middle part)
            num_nodes_to_mask = max(1, int(len(maskable_nodes) * percentage))
            num_nodes_to_mask = min(num_nodes_to_mask, len(maskable_nodes))

            # Determine the range of indices for maskable nodes
            maskable_indices = [i for i, node in enumerate(nodes_sorted) if node.get('eClass') not in eclass_exclusions]

            # Select a random starting index for the contiguous block
            max_start_index = len(maskable_indices) - num_nodes_to_mask
            if max_start_index > 0:
                start_idx_in_maskable = random.randint(0, max_start_index)
            else:
                start_idx_in_maskable = 0

            # Get the indices of nodes to mask in the sorted nodes list
            nodes_to_mask_indices = maskable_indices[start_idx_in_maskable:start_idx_in_maskable + num_nodes_to_mask]
            nodes_to_mask_ids = set(nodes_sorted[i]['id'] for i in nodes_to_mask_indices)

            # Split nodes into left, middle (masked), and right
            left_nodes = nodes_sorted[:nodes_to_mask_indices[0]]
            middle_nodes = [nodes_sorted[i] for i in nodes_to_mask_indices]
            right_nodes = nodes_sorted[nodes_to_mask_indices[-1] + 1:]

            # Collect masked nodes
            masked_nodes = middle_nodes  # Nodes to mask (middle)

            # Prepare the contexts for 'lr' and 'rl' versions
            contexts = {
                'lr': left_nodes + ['<Mask>'] + right_nodes,
                'rl': right_nodes + ['<Mask>'] + left_nodes
            }

            # Update links for each version
            for version in ['lr', 'rl']:
                context_nodes = contexts[version]

                # Create a set of node IDs present in the context (excluding '<Mask>')
                context_node_ids = set()
                for node in context_nodes:
                    if isinstance(node, dict):
                        context_node_ids.add(node['id'])

                # Adjust links to include only those between nodes in the context
                modified_links = []
                for link in links:
                    source = link.get('source')
                    target = link.get('target')
                    if source in nodes_to_mask_ids or target in nodes_to_mask_ids:
                        # Skip links connected to masked nodes
                        continue
                    if source in context_node_ids and target in context_node_ids:
                        # Include link if both ends are in the context
                        modified_links.append(link)

                # Prepare the modified data
                modified_data = {
                    'nodes': context_nodes,
                    'links': modified_links
                }

                # Save the modified JSON to the input_output_folder
                input_output_filename = f"{os.path.splitext(filename)[0]}_{version}.json"
                input_output_file_path = os.path.join(input_output_folder, input_output_filename)
                with open(input_output_file_path, 'w') as output_file:
                    json.dump(modified_data, output_file, separators=(',', ':'))

            # Prepare the masked data (output)
            masked_data = {
                'nodes': masked_nodes,
                'links': []
            }

            # Collect links connected between masked nodes
            masked_node_ids = set(node['id'] for node in masked_nodes)
            for link in links:
                source = link.get('source')
                target = link.get('target')
                if source in masked_node_ids and target in masked_node_ids:
                    masked_data['links'].append(link)

            # Save the masked elements to the output_folder
            output_filename = f"{os.path.splitext(filename)[0]}_masked.json"
            output_file_path = os.path.join(output_folder, output_filename)
            with open(output_file_path, 'w') as output_file:
                json.dump(masked_data, output_file, separators=(',', ':'))

            print(f"Processed file: {filename}")
            print(f"Generated input files: {input_output_filename.replace('_lr', '_lr.json')} and {input_output_filename.replace('_lr', '_rl.json')}")
            print(f"Generated output file: {output_filename}")