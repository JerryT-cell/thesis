from re import match
from typing import List, Dict, Any, Set






def get_candidates(t, normalized_pred_nodes):
    """
    Get the candidates for a given node in the predictions.
    :param t:  The node to match
    :param normalized_pred_nodes:  The normalized predicted nodes
    :return:
    """
    candidates = []
    pred_nodes_copy = normalized_pred_nodes[:]
    for i, p in enumerate(pred_nodes_copy):
        if nodes_equal(t, p["node"], False) == 1:
            candidates.append(p)
            del pred_nodes_copy[i]

    return candidates


def best_matches(t, pred_ids, true_ids, normalized_pred_nodes, id_to_true_nodes_and_links, matches, visited=None):

    # Initialize visited set if not provided
    if visited is None:
        visited = set()

    # Detect cycles: if 't' is already visited, we stop to avoid infinite recursion
    if t in visited:
        # We've encountered this node before in the current recursion chain
        # Return as is, no further processing
        return matches, normalized_pred_nodes

    visited.add(t)

    # recall data structure of matches is {node_id: (candidate_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c), ...}
    true_node_with_links = id_to_true_nodes_and_links[t]
    # Get the candidates for the matching
    candidates = get_candidates(true_node_with_links["node"], normalized_pred_nodes)
    if not candidates:
        node_id = t
        if node_id not in matches:
            matches[node_id] = None # no Match
        return matches, normalized_pred_nodes

    # Else we have candidates ! Now we need to find the best match
    # The best match is the candidate that has the most links matched with the true node
    true_node_links = true_node_with_links["links"]
    node_id = t
    list_links_matched = []
    if not true_node_links:
        # If the true node has no links, we can match it with any candidate
        # We can just take the first candidate
        matches[node_id] = (candidates[0]["node"]["id"], 0, 0)
        # remove from normalized_pred_nodes and pred_nodes
        normalized_pred_nodes = [c for c in normalized_pred_nodes if c["node"]["id"] != candidates[0]["node"]["id"]]
        return matches, normalized_pred_nodes

    for l in true_node_links:
        source = l["source"]
        target = l["target"]
        for c in candidates: # recall candidates have the form [{"node": node, "links": links}, ...]
            number_of_links_in_candidate_c = 0
            number_of_links_matched_with_the_true_node = 0
            c_id = c["node"]["id"]
            for c_l in c["links"]:  # recall c_l has the form {"source": source, "target": target}
                number_of_links_in_candidate_c += 1
                c_source = c_l["source"]
                c_target = c_l["target"]
                # now check if the link is a match
                if source == node_id: # if the source of the link in the true node is the node we are matching
                    if c_source != c_id: # if the source of the link in the candidate is not the candidate itself;
                        # it is not a match
                        continue
                    if target not in true_ids: # if the target of the link in the true node is not in the true ids;
                        # meaning it is a node in the uml diagram, the target of the candidate should point to the same
                        # node in the uml diagram
                        if c_target == target:
                            number_of_links_matched_with_the_true_node += 1
                    else:
                        # At this point, the target of the true node is in the true_nodes
                        if c_target not in pred_ids:
                            continue
                        # therefore the target of the candidate should be in the predicted nodes and match the target of the true node
                        if c_target in pred_ids:
                            # check if the node in the true nodes is matched with the node in the predicted nodes
                            match_from_target = matches.get(target, None)
                            if match_from_target:
                                if c_target == match_from_target[0]:
                                    number_of_links_matched_with_the_true_node += 1
                            else:
                                # find out the match of the true node associated with the candidate target node.
                                if target in matches:
                                    if c_target == matches[target][0]:
                                        number_of_links_matched_with_the_true_node += 1
                                else :
                                    new_matches, normalized_pred_nodes = best_matches(target, pred_ids, true_ids,normalized_pred_nodes, id_to_true_nodes_and_links,
                                                           matches, visited)
                                    # Done matching, is there a match for the target node in the predicted nodes ? If yes, is the match of the id of the candidate target node ?
                                    matches = new_matches
                                    match_from_target = matches.get(target)
                                    if match_from_target:
                                        if c_target == match_from_target[0]:
                                            number_of_links_matched_with_the_true_node += 1

                else:
                    if target == node_id:
                        if c_target != c_id:
                            continue
                        if source not in true_ids:
                            if c_source == source:
                                number_of_links_matched_with_the_true_node += 1
                        else:
                            if c_source not in pred_ids:
                                continue
                            match_from_source = matches.get(source, None)
                            if match_from_source:
                                if c_source == match_from_source[0]:
                                    number_of_links_matched_with_the_true_node += 1
                            else:
                                if source in matches:
                                    if c_source == matches[source][0]:
                                        number_of_links_matched_with_the_true_node += 1
                                else:
                                    new_matches, normalized_pred_nodes = best_matches(source, pred_ids, true_ids,normalized_pred_nodes, id_to_true_nodes_and_links,
                                                               matches, visited)
                                    matches = new_matches
                                    match_from_source = matches.get(source, None)
                                    if match_from_source:
                                        if c_source == match_from_source[0]:
                                            number_of_links_matched_with_the_true_node += 1

            list_links_matched.append((c_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c))
        # get the best candidate
        if list_links_matched:
            best_candidate = max(list_links_matched, key=lambda x: x[1])
            # enter the best candidate in the matches
            matches[node_id] = (best_candidate[0], best_candidate[1], best_candidate[2])
            # remove from normalized_pred_nodes and pred_nodes
            normalized_pred_nodes = [c for c in normalized_pred_nodes if c["node"]["id"] != best_candidate[0]]


    return matches , normalized_pred_nodes



def accuracy(predictions, ground_truth, strict=True, truncate=False, printing=False):
    """
    This function matches the nodes and links between the predictions and the ground truth.
    It finds the best match for each node in the predictions.
     - If strict is True, the match should be exact!
     - If strict is False, the id should not be considered for the match. For each node that matches all attributes
     check if the links are the same. If they are, the node is considered a match. To consider a link connected to the
     node a match, the link should have the same source and target nodes. i.e the nodes at the ends of the link should
     also be matches ! For the link match, if in ground truth, for example you have a link (source = 1, target = 2) and that the node id 1 matches with node id 3 and node id 2 matches with node id 4, then the link (source = 3, target = 4) should be in the predictions. So the links are not matched by their ids but by the nodes they are connected to.
     - If truncate is True, the predictions are truncated to the length of the ground truth.
     - If printing is True, the function prints the matches
    :param predictions: The predicted data
    :param ground_truth: The ground truth data
    :param strict: True if the nodes and links should be exact, False otherwise
    :param truncate: True if the predictions should be truncated to the length of the ground truth
    :param printing: True if the function should print the matches
    :return a list of tuples containing the matches. Each tuple contains 2 dicts, which are the matched 2 nodes with
    their links.
    """
    # 1. Prepare Data
    true_nodes, true_links, pred_nodes, pred_links = prepare_data(predictions, ground_truth, truncate)

    # Handle empty cases right away
    if not true_nodes and not pred_nodes:
        return {"node accuracy": 1.0, "link accuracy": 1.0}
    if not true_nodes and pred_nodes:
        return {"node accuracy": 0.0, "link accuracy": 0.0}

    # 2. Normalize and Link
    normalized_true_nodes, normalized_pred_nodes, pred_nodes_with_links, id_to_true_nodes_and_links = normalize_and_link_nodes(
        true_nodes, true_links, pred_nodes, pred_links)

    # 3. Get IDs for matching
    true_nodes_ids = get_ids_from_dict(id_to_true_nodes_and_links)
    pred_nodes_ids = get_list_of_ids_from_list_of_nodes(pred_nodes_with_links)

    # 4. Perform Matching
    matches, pred_nodes_with_links = perform_matching(id_to_true_nodes_and_links, pred_nodes_with_links, pred_nodes_ids,
                                                      true_nodes_ids)

    #recall data structure of matches is {node_id: (candidate_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c), ...}

    # 5. Compute Accuracies
    results = compute_accuracies(matches, true_nodes, pred_nodes, true_links, pred_links, id_to_true_nodes_and_links)

    # Optional printing
    if printing:
        print("Matches:", matches)
        print("Results:", results)

    return results



def normalize_and_link_nodes(true_nodes, true_links, pred_nodes, pred_links):
    """
    Normalize nodes and attach links to both predicted and true nodes.
    Returns:
    - normalized_true_nodes
    - normalized_pred_nodes
    - pred_nodes_with_links (predicted nodes and their links) nodes connected to links directly
    - true_nodes_and_links (true nodes and their links) nodes connected to links directly
    """
    normalized_true_nodes = normalize_nodes(true_nodes)
    normalized_pred_nodes = normalize_nodes(pred_nodes)
    pred_nodes_with_links = attach_links_to_nodes(normalized_pred_nodes, pred_links)
    true_nodes_and_links = attach_links_to_nodes_dict(normalized_true_nodes, true_links)
    return normalized_true_nodes, normalized_pred_nodes, pred_nodes_with_links, true_nodes_and_links

def perform_matching(true_nodes_and_links, pred_nodes_with_links, pred_nodes_ids, true_nodes_ids):
    """
    Perform the matching using best_matches for each node in the true_nodes_and_links.
    """
    matches = {}
    for t in true_nodes_and_links:
        # best_matches returns updated matches and pred_nodes_with_links
        matches, pred_nodes_with_links = best_matches(t, pred_nodes_ids, true_nodes_ids, pred_nodes_with_links,
                                                      true_nodes_and_links, matches)
    return matches, pred_nodes_with_links


def prepare_data(predictions: Dict[str, Any], ground_truth: Dict[str, Any], truncate: bool) -> (list, list, list, list):
    """
    Prepare and return nodes and links for both predictions and ground truth.
    Truncate predictions if requested.
    """
    true_nodes, true_links, pred_nodes, pred_links = get_nodes_and_links(predictions, ground_truth)

    # If no true nodes
    if not true_nodes:
        if not pred_nodes:
            # Both empty
            return [], [], [], []
        # True empty, pred not empty
        return true_nodes, true_links, pred_nodes, pred_links

    if truncate:
        pred_nodes, pred_links = truncate_predicted_nodes(true_nodes, pred_nodes, pred_links)

    return true_nodes, true_links, pred_nodes, pred_links



def compute_accuracies(matches, true_nodes, pred_nodes, true_links, pred_links, true_nodes_and_links):
    """
    Compute node and link accuracies based on the matches and return a dictionary.
    - Node accuracy is the proportion of matched nodes to the maximum number of nodes.
    - Link accuracy is the proportion of matched links to the maximum number of links. Only links of matched nodes are
    considered.
    """

    # Remove nodes with no match
    matches = {k: v for k, v in matches.items() if v is not None}

    # Calculate node accuracy
    total_true_nodes = len(true_nodes)
    total_pred_nodes = len(pred_nodes)
    denominator_nodes = max(total_true_nodes, total_pred_nodes)
    matched_nodes = len(matches)
    accuracy_nodes = matched_nodes / denominator_nodes if denominator_nodes > 0 else 1.0

    # Calculate link accuracy
    if not true_links:
        # If no true links, link accuracy depends on whether there are pred links
        links_accuracy = 1.0 if not pred_links else 0.0
        return {"node accuracy": accuracy_nodes, "link accuracy": links_accuracy}

    if matched_nodes == 0:
        # No matched nodes => no matched links
        return {"node accuracy": accuracy_nodes, "link accuracy": 0.0}

    # Compute link accuracy
    all_keys = matches.keys()
    links_of_matched_nodes = []
    total_number_of_links_in_candidates = 0
    total_number_of_links_matched_with_the_true_node = 0
    for key in all_keys:
        links_of_matched_nodes.append(true_nodes_and_links[key]["links"])
        c = matches[key]
        total_number_of_links_in_candidates += c[2]
        total_number_of_links_matched_with_the_true_node += c[1]

    total_number_of_matched_true_links = sum(len(links) for links in links_of_matched_nodes)
    denominator_links = max(total_number_of_matched_true_links, total_number_of_links_in_candidates)
    accuracy_links = total_number_of_links_matched_with_the_true_node / denominator_links if denominator_links > 0 else 1.0

    return {"node accuracy": accuracy_nodes, "link accuracy": accuracy_links}


























###################################################### Helper functions ###############################################

def get_nodes_and_links(y_true, y_pred):

    """
    Extract nodes and links from the true and predicted data.
    """
    true_nodes = y_true.get("nodes", [])
    true_links = y_true.get("links", [])
    pred_nodes = y_pred.get("nodes", [])
    pred_links = y_pred.get("links", [])
    return true_nodes, true_links, pred_nodes, pred_links




def truncate_predicted_nodes(true_nodes, pred_nodes, pred_links):


    """
    Truncate predicted nodes to match the number of true nodes and adjust links accordingly.
    """
    total_nodes_true = len(true_nodes)
    if len(pred_nodes) > total_nodes_true:
        # Truncate predicted nodes
        deleted_nodes = pred_nodes[total_nodes_true:]
        pred_nodes = pred_nodes[:total_nodes_true]
        # Remove links that reference truncated nodes
        valid_pred_ids = {n["id"] for n in pred_nodes}   #set
        deleted_ids = {n["id"] for n in deleted_nodes}  #set

        new_pred_links = []
        for l in pred_links:
            source = l.get("source")
            target = l.get("target")
            if source in valid_pred_ids and target in valid_pred_ids :
                new_pred_links.append(l)
            elif source in valid_pred_ids:
                if target not in deleted_ids:
                  new_pred_links.append(l)
            elif target in valid_pred_ids:
                if source not in deleted_ids:
                  new_pred_links.append(l)

        pred_links = new_pred_links


    return pred_nodes, pred_links


def nodes_equal(t_node, p_node, strict=False):
    """
    Determine if two nodes are equal based on the matching criteria.

    Parameters:
    - t_node: Normalized true node.
    - p_node: Normalized predicted node.
    - strict: If True, all attributes including 'id' must match.
              If False, all attributes except 'id' must match.

    Returns:
    - 1 if nodes are equal, 0 otherwise.
    """
    for k, v in t_node.items():
        if not strict and k == "id":
            continue
        if k not in p_node or p_node[k] != v:
            return 0
    if strict:
        # Ensure predicted node doesn't have extra attributes that differ
        for k, v in p_node.items():
            if t_node.get(k, None) != v:
                return 0
    return 1


def normalize_nodes(nodes):
    """
    Normalize node attributes to lowercase for comparison, except 'id' if not strict.

    Parameters:
    - nodes: List of node dictionaries.

    Returns:
    - List of normalized node dictionaries.
    """
    normalized = []
    for node in nodes:
        normalized_node = {}
        for k, v in node.items():
            normalized_node[k] = v.lower() if isinstance(v, str) else v
        normalized.append(normalized_node)
    return normalized


def get_associated_links(node: Dict[str, Any], links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Retrieve all links associated with a given node.

    A link is considered associated with the node if the node's 'id' matches either
    the 'source' or 'target' of the link.

    :param node: A dictionary representing the node. Must contain an 'id' key.
    :param links: A list of dictionaries, each representing a link with 'source' and 'target' keys.
    :return: A list of link dictionaries associated with the node.
    """
    node_id = node.get('id')
    if node_id is None:
        print("The provided node does not have an 'id'.")
        return []

    associated_links = [link for link in links if is_link_associated(link, node_id)]
    return associated_links


def is_link_associated(link: Dict[str, Any], node_id: Any) -> bool:
    """
    Determine if a link is associated with the given node ID.

    :param link: A dictionary representing a link with 'source' and 'target' keys.
    :param node_id: The 'id' of the node to check association with.
    :return: True if the link is associated with the node, False otherwise.
    """
    return link.get('source') == node_id or link.get('target') == node_id



def attach_links_to_nodes(nodes: List[Dict[str, Any]], links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Associates each node with its connected links.

    :param nodes: A list of node dictionaries. Each node must have a unique 'id'.
    :param links: A list of link dictionaries. Each link must have 'source' and 'target' keys.
    :return: A list of dictionaries, each containing a 'node' and its associated 'links'.
    """

    # Create a mapping from node_id to node dict
    node_id_to_node = {}
    for node in nodes:
        node_id_to_node[node['id']] = node


    # Initialize a mapping from node_id to list of associated links
    node_id_to_links = {node_id: [] for node_id in node_id_to_node}

    # Associate each link with its source and target nodes
    for link in links:

        source_id = link['source']
        target_id = link['target']

        # Associate link with source node
        if source_id in node_id_to_links:
            node_id_to_links[source_id].append(link)
        else:
            print(f"Warning: Source node ID {source_id} in link {link} not found in nodes.")

        # Associate link with target node
        if target_id in node_id_to_links:
            node_id_to_links[target_id].append(link)
        else:
            print(f"Warning: Target node ID {target_id} in link {link} not found in nodes.")

    # Prepare the final list of nodes with their associated links
    nodes_with_links = []
    for node_id, node in node_id_to_node.items():
        associated_links = node_id_to_links.get(node_id, [])
        nodes_with_links.append({
            "node": node,
            "links": associated_links
        })

    return nodes_with_links

def attach_links_to_nodes_dict(nodes: List[Dict[str, Any]], links: List[Dict[str, Any]]) -> Dict[Any, Dict[str, Any]]:
    """
    Associates each node with its connected links and returns a dictionary mapping node IDs to their data and links.

    :param nodes: A list of node dictionaries. Each node must have a unique 'id'.
    :param links: A list of link dictionaries. Each link must have 'source' and 'target' keys.
    :return: A dictionary where each key is a node's 'id' and its value is a dictionary with 'node' and 'links'.
    """

    # Create a mapping from node_id to node dict
    node_id_to_node = {}
    for node in nodes:
        node_id_to_node[node['id']] = node


    # Initialize a mapping from node_id to list of associated links
    node_id_to_links = {node_id: [] for node_id in node_id_to_node}

    # Associate each link with its source and target nodes
    for link in links:

        source_id = link['source']
        target_id = link['target']

        # Associate link with source node
        if source_id in node_id_to_links:
            node_id_to_links[source_id].append(link)
        else:
            print(f"Warning: Source node ID {source_id} in link {link} not found in nodes.")

        # Associate link with target node
        if target_id in node_id_to_links:
            node_id_to_links[target_id].append(link)
        else:
            print(f"Warning: Target node ID {target_id} in link {link} not found in nodes.")

    # Prepare the final dictionary mapping node IDs to their data and associated links
    nodes_with_links_dict = {}
    for node_id, node in node_id_to_node.items():
        associated_links = node_id_to_links.get(node_id, [])
        nodes_with_links_dict[node_id] = {
            "node": node,
            "links": associated_links
        }

    return nodes_with_links_dict

def get_ids_from_dict(nodes_dict: Dict[Any, Dict[str, Any]]) -> Set[Any]:
    """
    Given a dictionary where keys are node IDs and values are dicts containing node/links,
    return a set of the keys.
    """
    return set(nodes_dict.keys())


def get_list_of_ids_from_grouped_dict(grouped_dict: Dict[Any, List[Dict[str, Any]]]) -> List[Any]:
    """
    Given a dictionary of type Dict[Any, List[Dict[str,Any]]] (from Function 1),
    return a list of IDs. If an ID maps to multiple entries, that ID should appear multiple times.
    """
    result_list = []
    for node_id, entries in grouped_dict.items():
        # If there are N entries for a node_id, add that node_id N times
        count = len(entries)
        result_list.extend([node_id] * count)
    return result_list

def get_list_of_ids_from_list_of_nodes(nodes: List[Dict[str, Any]]) -> List[Any]:
    """
    Given a list of nodes, return a list of node IDs.
    If a node appears multiple times, its ID should be repeated in the list.
    """
    result_list = []
    for node in nodes:
        node_id = node.get('id')
        if node_id is not None:
            result_list.append(node_id)
    return result_list

def get_list_of_ids_from_list_of_nodes_and_links(nodes_with_links: List[Dict[str, Any]]) -> List[Any]:
    """
    Given a list of dicts, each containing a 'node' and 'links', return a list of node IDs.
    If a node appears multiple times, its ID should be repeated in the list.
    """
    result_list = []
    for entry in nodes_with_links:
        node = entry.get('node')
        if node is not None:
            node_id = node.get('id')
            if node_id is not None:
                result_list.append(node_id)
    return result_list

def create_node_link_dict(nodes: List[Dict[str, Any]], links: List[Dict[str, Any]]) -> Dict[Any, List[Dict[str, Any]]]:
    """
    Function 1:
    Given a list of nodes and links, return a dict of type Dict[Any, List[Dict[str, Any]]].
    Each key is a node's id, and the value is a list of dicts. Each dict in the list has:
    {
      "node": <node_dict>,
      "links": <list_of_associated_links>
    }
    If multiple nodes share the same 'id', store them all in the list.
    """
    # Build an adjacency-like structure for links
    node_id_to_links = {}
    for link in links:
        source = link.get('source')
        target = link.get('target')
        if source is not None:
            node_id_to_links.setdefault(source, []).append(link)
        if target is not None:
            node_id_to_links.setdefault(target, []).append(link)

    # Build the result dictionary
    result: Dict[Any, List[Dict[str, Any]]] = {}
    for node in nodes:
        node_id = node.get('id')
        if node_id is None:
            # If node doesn't have an id, skip it
            continue
        associated_links = node_id_to_links.get(node_id, [])
        entry = {
            "node": node,
            "links": associated_links
        }
        # Append to the list for this node_id
        result.setdefault(node_id, []).append(entry)

    return result











if __name__ == "__main__":
    # Example nodes and links
    nodes_example = [
        {"id": 1, "type": "Server", "status": "Active"},
        {"id": 1, "type": "Server", "status": "Active"},
        {"id": 2, "type": "Client", "status": "Inactive"},
        {"id": 3, "type": "Database", "status": "Active"},
        {"id": 4, "type": "Cache", "status": "Active"},
        {"id": 5, "type": "LoadBalancer", "status": "Active"}
    ]

    links_example = [
        {"source": 1, "target": 2},
        {"source": 1, "target": 3},
        {"source": 2, "target": 4},
        {"source": 3, "target": 4},
        {"source": 4, "target": 5},
        {"source": 5, "target": 1},  # Creates a cycle
        {"source": 6, "target": 1},  # Invalid link: node 6 does not exist
        {"source": 3, "target": 1}
    ]

    # Attach links to nodes
    associated_nodes = create_node_link_dict(nodes_example, links_example)
    print(associated_nodes)
    print(get_list_of_ids_from_grouped_dict(associated_nodes))




















