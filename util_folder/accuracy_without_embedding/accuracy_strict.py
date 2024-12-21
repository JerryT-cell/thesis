from util_folder.accuracy_utils import get_candidates \
    , initialize_data, attach_links_to_nodes, compute_accuracies, links_with_ids_to_dict, introduce_ids_to_links, \
    attach_links_to_nodes_with_duplicates


def accuracy_strict(ground_truth, predictions, truncate=True, printing=False):
    """
    Compute node and link accuracy separately with strict node matching.
    strict means that all attributes including 'id' are considered in the matching.

    Steps:
    1. initialize the data = truncate predicted nodes if there are more than in the reference. During init,
    The nodes are also normalized. Normalize mean that all the attributes are converted to lowercase.
    2. Match nodes based on all attributes. Match the links as well
    3. Compute node accuracy and link accuracy separately.

    Returns:
    node_accuracy, link_accuracy
    """

    # 1 Initialization
    normalized_true_nodes, true_links, normalized_pred_nodes, pred_links = initialize_data(ground_truth, predictions,
                                                                                           truncate)
    pred_links = introduce_ids_to_links(pred_links)
    ids_to_pred_links = links_with_ids_to_dict(pred_links)

    #2 Match nodes and links
    true_nodes_with_links = attach_links_to_nodes(normalized_true_nodes, true_links)
    pred_nodes_with_links = attach_links_to_nodes_with_duplicates(normalized_pred_nodes, pred_links)
    matches , ids_to_pred_links = perform_matching(true_nodes_with_links, pred_nodes_with_links, ids_to_pred_links,
                                                   printing=printing)

    #3 Compute node and link accuracy
    results = compute_accuracies(matches, normalized_true_nodes, normalized_pred_nodes, true_links, pred_links,
                                 ids_to_pred_links)
    if printing:
        print("Node accuracy_strict: ", results["node accuracy"])
        print("Link accuracy_strict: ", results["link accuracy"])


    return results



############################################ Helper functions ############################################################
def perform_matching(true_nodes_with_links, pred_nodes_with_links, ids_to_pred_links, printing=False):
    matches = {}
    normalized_pred_nodes = pred_nodes_with_links
    for t in true_nodes_with_links:
        match, normalized_pred_nodes, ids_to_pred_links = best_matches_strict(t,normalized_pred_nodes, ids_to_pred_links
                                                                              , printing=printing)
        node_id = t["node"]["id"]
        matches[node_id] = match[node_id]
    return matches , ids_to_pred_links




def best_matches_strict(node_with_links, normalized_pred_nodes, ids_to_pred_links , printing=False):
    # recall data structure of matches is {node_id: (candidate_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c, node with links), ...}
    true_node_with_links = node_with_links
    node_id = node_with_links["node"]["id"]
    matches = {}
    # Get the candidates for the matching, in a normal case, there should be only one candidate, but if the llm is not perfect, there could be more than one candidate
    candidates = get_candidates(true_node_with_links["node"], normalized_pred_nodes, strict=True)
    if not candidates:
        matches[node_id] = None  # no candidate, no match
        return matches, normalized_pred_nodes , ids_to_pred_links

    # Else we have candidates ! The candidates in accuracy strict are identical, so no need to get the best match
    # Get the first candidate and do matches with the links
    predicted_candidate = candidates[0]
    candidate_id = predicted_candidate["node"]["id"]
    candidate_links = predicted_candidate["links"]
    #We use this set to remove the links that have been matched with the true node
    indices_of_links_matched = set()
    links_matched = 0
    number_of_links_in_candidate = 0
    true_node_links = true_node_with_links["links"]

    for link in true_node_links:
        source = link["source"]
        target = link["target"]
        index_matched = 0
        for c_link in candidate_links:
            link_id = c_link["id"]
            index_matched += 1
            if index_matched in indices_of_links_matched:
                continue
            number_of_links_in_candidate += 1

            c_source = c_link["source"]
            c_target = c_link["target"]
            if source == c_source and target == c_target:
                links_matched += 1
                index = index_matched - 1
                indices_of_links_matched.add(index)
                ids_to_pred_links[link_id]['match'] = True


    if printing:
        print("match between " + str(node_with_links["node"]) + " and " + str(candidates[0]["node"]))
    matches[node_id] = (candidate_id, node_with_links)
    # remove from normalized_pred_nodes and pred_nodes
    for c in normalized_pred_nodes:
        if c["node"]["id"] == candidate_id:
            normalized_pred_nodes.remove(c)
            break

    return matches, normalized_pred_nodes , ids_to_pred_links


