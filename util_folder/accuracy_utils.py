from typing import List, Dict, Any


def initialize_data(y_true, y_pred, truncate):
    """
    Initialize the data and truncate predicted nodes if there are more than in the reference.
    """
    true_nodes, true_links, pred_nodes, pred_links = get_nodes_and_links(y_true, y_pred)
    if truncate:
        pred_nodes, pred_links = truncate_predicted_nodes(true_nodes, pred_nodes, pred_links)
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
