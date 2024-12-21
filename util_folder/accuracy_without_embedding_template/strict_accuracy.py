

from util_folder.accuracy_utils import initialize_data, attach_links_to_nodes, compute_accuracies, \
    get_candidates, attach_links_to_nodes_with_duplicates
from util_folder.accuracy_without_embedding_template.accuracytemplate import AccuracyTemplate


class StrictAccuracy(AccuracyTemplate):
    def initialize_data(self, ground_truth, predictions, truncate):

        return initialize_data(ground_truth, predictions, truncate, normalize=True)

    def match_nodes_and_links(self, true_nodes, true_links, pred_nodes, pred_links, ids_to_pred_links):

        true_nodes_with_links = attach_links_to_nodes(true_nodes, true_links)
        pred_nodes_with_links = attach_links_to_nodes_with_duplicates(pred_nodes, pred_links)
        return perform_matching(true_nodes_with_links, pred_nodes_with_links, ids_to_pred_links)

    def compute_final_accuracy(self, matches, true_nodes, pred_nodes, true_links, pred_links, updated_links):
        return compute_accuracies(matches, true_nodes, pred_nodes, true_links, pred_links, updated_links)





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
