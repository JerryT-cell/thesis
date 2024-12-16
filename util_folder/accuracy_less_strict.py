from util_folder.accuracy_utils import initialize_data, normalize_nodes, attach_links_to_nodes, \
    get_list_of_ids_from_list_of_nodes, nodes_equal, attach_links_to_nodes_dict, create_node_link_dict


def simple_accuracy_less_strict(predictions, ground_truth, truncate=False, printing=False):
    """
    Compute node and link accuracy separately with simple less strict nodes matching.
    less strict means that all attributes except 'id' are considered in the matching.
    In this accuracy function, the nodes are considered equal if
    - all attributes except 'id' are the same.
    - all the links are pointing to the same nodes.

    The function is call simple because in the matching of the links, it suffices that if the links are pointing to
    nodes in the set of the true nodes, then the predicted links should point to the nodes that are structurally(the
    links are not checked) the same in the set of the predicted nodes.

    Steps:
    1. initialize the data and truncate predicted nodes if there are more than in the reference.
    2. Normalize nodes (excluding 'id'). Normalize mean that all the attributes are converted to lowercase.
    3. Match nodes based on all attributes except 'id'. Match the links as well
    4. Compute node accuracy and link accuracy separately.

    Returns:
    node_accuracy, link_accuracy

    Parameters:
    - predictions: List of predicted nodes and links.
    - ground_truth: List of true nodes and links.
    - truncate: Boolean indicating whether to truncate predicted nodes.
    - printing: Boolean indicating whether to print the results.
    """
    #1 Initialization
    true_nodes, true_links, pred_nodes, pred_links = initialize_data(ground_truth, predictions, truncate)

    #2 Normalize nodes
    normalized_true_nodes = normalize_nodes(true_nodes)
    normalized_pred_nodes = normalize_nodes(pred_nodes)

    #3 Match nodes and links
    true_nodes_with_links = attach_links_to_nodes(normalized_true_nodes, true_links)
    pred_nodes_with_links = attach_links_to_nodes(normalized_pred_nodes, pred_links)
    pred_ids = get_list_of_ids_from_list_of_nodes(true_nodes_with_links)
    true_ids = get_list_of_ids_from_list_of_nodes(pred_nodes_with_links)
    ids_to_true_nodes = attach_links_to_nodes_dict(normalized_true_nodes, true_links)
    ids_to_pred_nodes = create_node_link_dict(normalized_pred_nodes, pred_links)
    matches = perform_matching(true_nodes_with_links, pred_nodes_with_links, pred_ids, true_ids,
                               ids_to_true_nodes, ids_to_pred_nodes)

    #4 Compute node and link accuracy
    results = compute_accuracies(matches, true_nodes, pred_nodes, true_links, pred_links)

    # Optional printing
    if printing:
        print("Matches:", matches)
        print("Results:", results)

    return results




def compute_accuracies(matches, true_nodes, pred_nodes, true_links, pred_links):
    """
    Compute node and link accuracies based on the matches and return a dictionary.
    - Node accuracy is the proportion of matched nodes to the maximum number of nodes.
    - Link accuracy is the proportion of matched links to the maximum number of links. Only links of matched nodes are
    considered.
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

    # Compute link accuracy
    all_keys = matches.keys()
    links_of_matched_nodes = []
    total_number_of_links_in_candidates = 0
    total_number_of_links_matched_with_the_true_node = 0
    for key in all_keys:
        c = matches[key]
        links_of_matched_nodes.append(matches[3]["links"])
        total_number_of_links_in_candidates += c[2]
        total_number_of_links_matched_with_the_true_node += c[1]

    total_number_of_matched_true_links = sum(len(links) for links in links_of_matched_nodes)
    denominator_links = max(total_number_of_matched_true_links, total_number_of_links_in_candidates)
    accuracy_links = total_number_of_links_matched_with_the_true_node / denominator_links if denominator_links > 0 else 1.0

    return {"node accuracy": accuracy_nodes, "link accuracy": accuracy_links}


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


def perform_matching(true_nodes_with_links, pred_nodes_with_links, pred_ids, true_ids, ids_to_true_nodes,
                     ids_to_pred_nodes):
    matches = {}
    normalized_pred_nodes = pred_nodes_with_links
    for t in true_nodes_with_links:
        match, normalized_pred_nodes = best_matches(t, pred_ids, true_ids, normalized_pred_nodes, ids_to_true_nodes,
                                                    ids_to_pred_nodes)
        node_id = t["node"]["id"]
        matches[node_id] = match[node_id]
    return matches


def best_matches(node_with_links, pred_ids, true_ids, normalized_pred_nodes, ids_to_true_nodes, ids_to_pred_nodes):

    # recall data structure of matches is {node_id: (candidate_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c, node with links), ...}
    true_node_with_links = node_with_links
    node_id = node_with_links["node"]["id"]
    matches = {}
    # Get the candidates for the matching
    candidates = get_candidates(true_node_with_links["node"], normalized_pred_nodes)
    if not candidates:
        matches[node_id] = None # no candidate, no match
        return matches, normalized_pred_nodes

    # Else we have candidates ! Now we need to find the best match
    # The best match is the candidate that has the most links matched with the true node
    true_node_links = true_node_with_links["links"]
    list_links_matched = []

    if not true_node_links:
        # If the true node has no links, we can match it with any candidate
        # We can just take the first candidate
        matches[node_id] = (candidates[0]["node"]["id"], 0, 0, node_with_links)
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
                        # Check if the node in the true nodes is matched with the node in the predicted nodes structurally(have the same attributes)
                        pred_nodes = ids_to_pred_nodes[c_target]
                        # I get the first element of the list because the list either contains one element or more but with the same attributes
                        pred_node = pred_nodes[0]
                        if nodes_equal(ids_to_true_nodes[target]["node"], pred_node["node"] , False) == 1:
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
                            pred_nodes = ids_to_pred_nodes[c_source]
                            pred_node = pred_nodes[0]
                            if nodes_equal(ids_to_true_nodes[source]["node"], pred_node["node"], False) == 1:
                                number_of_links_matched_with_the_true_node += 1


            list_links_matched.append((c_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c))
        # get the best candidate
        if list_links_matched:
            best_candidate = max(list_links_matched, key=lambda x: x[1])
            # enter the best candidate in the matches
            matches[node_id] = (best_candidate[0], best_candidate[1], best_candidate[2], node_with_links)
            # remove from normalized_pred_nodes and pred_nodes
            normalized_pred_nodes = [c for c in normalized_pred_nodes if c["node"]["id"] != best_candidate[0]]


    return matches , normalized_pred_nodes





