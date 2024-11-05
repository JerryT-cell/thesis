import os
import json
import random
from os import write
from typing import Set
from util_folder.utils import create_folders, write_into_file, write_into_json_file, open_json_file


def structurally_causal_mask_elements_and_save(
        input_folder: str,
        input_output_folder: str,
        output_folder: str,
        percentage: float,
        eclass_exclusions: Set[str] = {"Interaction", "Activity", "StateMachine"}
):
    """
    Replaces a specified percentage of elements (nodes) in JSON files with mask tokens,
    excluding elements with specified eClasses.
    Saves the modified JSON files in the input_output_folder and the masked elements in the output_folder.
    Ensures that the saved files are minified (no additional whitespace).
    At the end, prints the maximum percentage of nodes masked across all files.

    Args:
        input_folder (str): Path to the folder containing the original JSON files.
        input_output_folder (str): Path to the folder where modified JSON files will be saved.
        output_folder (str): Path to the folder where masked elements will be saved.
        percentage (float): The percentage of elements to mask from each file.
        eclass_exclusions (Set[str]): Set of eClass names to exclude from masking.
    """
    create_folders(input_output_folder, output_folder)
    max_mask_counter= 0

    max_percentage_masked = 0.0  # To track the maximum percentage of nodes masked

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(input_folder, filename)

            ### Read the JSON file
            data = open_json_file(file_path)

            nodes = data.get('nodes', [])
            links = data.get('links', [])

            total_nodes_before = len(nodes)  # Total nodes before masking

            ### Exclude nodes with specified eClasses
            maskable_nodes = [
                node for node in nodes if node.get('eClass') not in eclass_exclusions
            ]

            ### Calculate number of nodes to mask
            num_nodes_to_mask = int(len(maskable_nodes) * percentage)

            ### Randomly select nodes to mask
            nodes_to_mask_ids = set()
            if num_nodes_to_mask > 0:
                nodes_to_mask_ids = set(
                    node['id'] for node in random.sample(maskable_nodes, num_nodes_to_mask)
                )

            ### Prepare lists to store masked nodes and links
            masked_nodes = []
            masked_links = []
            mask_counter = 0
            node_id_to_mask_token = {}

            ### Replace nodes to mask with <Mask:k> tokens
            modified_nodes = []
            for node in nodes:
                if node['id'] in nodes_to_mask_ids:
                    mask_token = f'<Mask:{mask_counter}>'
                    # Replace the node with a mask token
                    modified_nodes.append(mask_token)
                    # Keep track of the masked node
                    masked_nodes.append((mask_token, node))
                    # Map node ID to mask token
                    node_id_to_mask_token[node['id']] = mask_token
                    mask_counter += 1
                else:
                    modified_nodes.append(node)

            #### remove the link if any of the connected nodes were masked and add the links to masked links
            modified_links = []
            for link in links:
                source = link.get('source')
                target = link.get('target')
                if not(source in node_id_to_mask_token or target in node_id_to_mask_token):
                    modified_links.append(link)
                else:
                    masked_links.append(link)


            ### Identify and mask unlinked nodes (nodes not connected by any link)
            linked_node_ids: Set[int] = set()
            for link in modified_links:
                source = link.get('source')
                target = link.get('target')
                if isinstance(source, int):
                    linked_node_ids.add(source)
                if isinstance(target, int):
                    linked_node_ids.add(target)
               # If source/target are mask tokens, they are already accounted for

            updated_nodes = []
            for node in modified_nodes:
                if isinstance(node, dict):
                    node_id = node['id']
                    if node_id not in linked_node_ids and node.get('eClass') not in eclass_exclusions:
                        # Mask the unlinked node
                        mask_token = f'<Mask:{mask_counter}>'
                        masked_nodes.append((mask_token, node))
                        node_id_to_mask_token[node_id] = mask_token
                        mask_counter += 1
                    else:
                        updated_nodes.append(node)
                else:
                    # It's already a mask token
                    updated_nodes.append(node)

            ###put the last mask token in links
            link_mask = f'<Mask:{mask_counter}>'
            modified_links.append(link_mask)
            #Update the modified nodes
            modified_nodes = updated_nodes

            #Update the data dictionaries
            modified_data = {'nodes': modified_nodes, 'links': modified_links}

            ### Save the modified JSON to the input_output_folder (minified)
            input_output_file_path = os.path.join(input_output_folder, filename.replace('.json', '_masked.json'))
            write_into_json_file(input_output_file_path, modified_data)

            ### Save the masked elements to the output_folder (minified)
            output_file_path = os.path.join(output_folder, filename)
            prepareElementsForOutput(output_file_path,masked_nodes, masked_links, link_mask)

            ### Calculate percentages
            total_nodes_masked = len(masked_nodes)

            # Calculate the percentage of nodes masked in this file
            if total_nodes_before > 0:
                percentage_masked = (total_nodes_masked / total_nodes_before) * 100
            else:
                percentage_masked = 0

            # Update the maximum percentage masked if current is greater
            if percentage_masked > max_percentage_masked:
                max_percentage_masked = percentage_masked

            print(f"Processed file: {filename}")
            print(f"Percentage of nodes masked in {filename}: {percentage_masked:.2f}%")

            if mask_counter > max_mask_counter:
                max_mask_counter = mask_counter

    print(f"\nMaximum percentage of nodes masked across all files: {max_percentage_masked:.2f}%")
    return max_mask_counter


def prepareElementsForOutput(file_path,masked_nodes, masked_links, mask_link):

    with open(file_path, "w") as file:
        for mask, node in masked_nodes:
            file.write(mask)
            file.write(json.dumps(node, separators=(',', ':')))
            file.write("<EOM>")

        file.write(mask_link)
        for link in masked_links:
            file.write(json.dumps(link, separators=(',', ':')))
        file.write("<EOM>")
