from typing import List, Dict, Any
from collections import defaultdict

def initialize_data(y_true, y_pred, truncate , normalize = True):
    """
    Initialize the data and truncate predicted nodes if there are more than in the reference.
    """
    true_nodes, true_links, pred_nodes, pred_links = get_nodes_and_links(y_true, y_pred)
    if truncate:
        pred_nodes, pred_links = truncate_predicted_nodes(true_nodes, pred_nodes, pred_links)

    if normalize:
        true_nodes = normalize_nodes(true_nodes)
        pred_nodes = normalize_nodes(pred_nodes)
    return true_nodes, true_links, pred_nodes, pred_links


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

def nodes_equal(t_node, p_node, strict=False, threshold=None, model=None):
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


def get_candidates(t, normalized_pred_nodes, strict=False, threshold=None, model=None):
    """
    Get the candidates for a given node in the predictions.
    :param t:  The node to match
    :param normalized_pred_nodes:  The normalized predicted nodes
    :param strict:  If True, all attributes including 'id' must match.
    :return:
    """
    candidates = []
    pred_nodes_copy = normalized_pred_nodes[:]
    for i, p in enumerate(pred_nodes_copy):
        if nodes_equal(t, p["node"], strict, threshold=threshold, model=model) == 1:
            candidates.append(p)
            del pred_nodes_copy[i]

    return candidates

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

        # Associate link with target node
        if target_id in node_id_to_links:
            node_id_to_links[target_id].append(link)

    # Prepare the final list of nodes with their associated links
    nodes_with_links = []
    for node_id, node in node_id_to_node.items():
        associated_links = node_id_to_links.get(node_id, [])
        nodes_with_links.append({
            "node": node,
            "links": associated_links
        })

    return nodes_with_links

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

        # Associate link with target node
        if target_id in node_id_to_links:
            node_id_to_links[target_id].append(link)

    # Prepare the final dictionary mapping node IDs to their data and associated links
    nodes_with_links_dict = {}
    for node_id, node in node_id_to_node.items():
        associated_links = node_id_to_links.get(node_id, [])
        nodes_with_links_dict[node_id] = {
            "node": node,
            "links": associated_links
        }

    return nodes_with_links_dict

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

def compute_accuracies(matches, true_nodes, pred_nodes, true_links, pred_links, ids_to_pred_links):
    """
    Compute node and link accuracies based on the matches and return a dictionary.
    - Node accuracy is the proportion of matched nodes to the maximum number of nodes.
    - Link accuracy is the proportion of matched links to the maximum number of links. Only links of matched nodes are
    considered.
    params:
    - matches: A dictionary of matches between true and predicted nodes.
    - true_nodes: A list of true node dictionaries.
    - pred_nodes: A list of predicted node dictionaries.
    - true_links: A list of true link dictionaries.
    - pred_links: A list of predicted link dictionaries.
    - ids_to_pred_links: A dictionary mapping link IDs to predicted link dictionaries.
    """

    # recall data structure of matches is {node_id: (candidate_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c, true node with links), ...}
    # Remove nodes with no match
    matches = {k: v for k, v in matches.items() if v is not None}

    # Calculate node accuracy
    total_true_nodes = len(true_nodes)
    if total_true_nodes != 0:
        total_pred_nodes = len(pred_nodes)
        denominator_nodes = max(total_true_nodes, total_pred_nodes)
        matched_nodes = len(matches)
        accuracy_nodes = matched_nodes / denominator_nodes if denominator_nodes > 0 else 1.0 # avoid division by zero
    else:
        matched_nodes = 0
        accuracy_nodes = 1.0 if not pred_nodes else 0.0

    # Calculate link accuracy
    if not true_links:
        # If no true links, link accuracy depends on whether there are pred links
        links_accuracy = 1.0 if not pred_links else 0.0
        return {"node accuracy": accuracy_nodes, "link accuracy": links_accuracy}

    if matched_nodes == 0:
        # No matched nodes => no matched links
        return {"node accuracy": accuracy_nodes, "link accuracy": 0.0}

    pred_nodes_ids = set(v[0] for v in matches.values())

    total_number_of_links_matched_with_the_true_node = 0
    total_number_of_links_in_pred_matched_nodes = 0
    # get the links (match = True) from ids_to_pred_links and count them
    for k, v in ids_to_pred_links.items():
        if v["match"]:
            total_number_of_links_matched_with_the_true_node += 1
        if v["source"] in pred_nodes_ids or v["target"] in pred_nodes_ids:
            total_number_of_links_in_pred_matched_nodes += 1

    all_keys = matches.keys()
    total_number_of_matched_true_links = 0
    for l in true_links:
        if l["source"] in all_keys or l["target"] in all_keys:
            total_number_of_matched_true_links += 1


    # Compute link accuracy
    denominator_links = max(total_number_of_matched_true_links, total_number_of_links_in_pred_matched_nodes)
    accuracy_links = total_number_of_links_matched_with_the_true_node / denominator_links if denominator_links > 0 else 1.0

    return {"node accuracy": accuracy_nodes, "link accuracy": accuracy_links}



def introduce_ids_to_links(links):
    """
    Introduce ids to links beginning from 0. links have the form [{"source": source, "target": target}, ...].
    The new form will be [{"source": source, "target": target, "id": id}, ...]
    This is because the links may contain duplicates, and we need to distinguish them.
    :param links : list of links
    :return: the links with ids
    """
    # introduce ids to links beginning from 0. links have the form [{"source": source, "target": target}, ...], the new form will be [{"source": source, "target": target, "id": id}, ...]
    links = [{"source": l["source"], "target": l["target"], "id": i} for i, l in enumerate(links)]
    return links

def links_with_ids_to_dict(links):
    """
    Convert a list of links with IDs to a dictionary with the ID as the key and the link as the value.
    Adds a boolean value to the link to indicate if it is a match, add the boolean as "match" = False
    :param links: list of links with ids
    :return: dictionary with the id as the key and the link as the value
    """
    res_link = {}
    for link in links:
        link["match"] = False
        res_link[link["id"]] = link
    return res_link


def attach_links_to_nodes_with_duplicates(nodes: List[Dict[str, Any]], links: List[Dict[str, Any]]) -> List[
    Dict[str, Any]]:
    """
    Associates each node with its connected links, allowing duplicate node IDs.

    :param nodes: A list of node dictionaries. Node IDs may not be unique.
    :param links: A list of link dictionaries. Each link must have 'source' and 'target' keys.
    :return: A list of dictionaries, each containing a 'node' and its associated 'links'.
    """

    # Create a mapping from node_id to list of node dicts
    node_id_to_nodes = defaultdict(list)
    for node in nodes:
        node_id = node.get('id')
        if node_id is not None:
            node_id_to_nodes[node_id].append(node)

    # Initialize a mapping from node to its list of associated links
    node_to_links = defaultdict(list)

    # Associate each link with all source and target nodes
    for link in links:
        source_id = link.get('source')
        target_id = link.get('target')

        if source_id is not None:
            source_nodes = node_id_to_nodes.get(source_id)
            if source_nodes:
                for src_node in source_nodes:
                    node_to_links[id(src_node)].append(link)

        if target_id is not None:
            target_nodes = node_id_to_nodes.get(target_id)
            if target_nodes:
                for tgt_node in target_nodes:
                    node_to_links[id(tgt_node)].append(link)

    # Prepare the final list of nodes with their associated links
    nodes_with_links = []
    for node in nodes:
        associated_links = node_to_links.get(id(node), [])
        nodes_with_links.append({
            "node": node,
            "links": associated_links
        })

    return nodes_with_links
