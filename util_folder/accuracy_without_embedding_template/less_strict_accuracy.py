from util_folder.accuracy_without_embedding_template.accuracytemplate import AccuracyTemplate
from util_folder.accuracy_utils import initialize_data, attach_links_to_nodes, compute_accuracies, attach_links_to_nodes_with_duplicates, get_list_of_ids_from_list_of_nodes, create_node_link_dict, nodes_equal, get_candidates


class LessStrictAccuracy(AccuracyTemplate):




    def initialize_data(self, ground_truth, predictions, truncate):
        return initialize_data(ground_truth, predictions, truncate, normalize=True)

    def match_nodes_and_links(self, true_nodes, true_links, pred_nodes, pred_links, ids_to_pred_links):
        true_nodes_with_links = attach_links_to_nodes(true_nodes, true_links)
        pred_nodes_with_links = attach_links_to_nodes_with_duplicates(pred_nodes, pred_links)
        return perform_matching(
            true_nodes_with_links, pred_nodes_with_links, self.get_ids(pred_nodes), self.get_ids(true_nodes),
            self.create_node_dict(true_nodes, true_links), self.create_node_dict(pred_nodes, pred_links), ids_to_pred_links
        )

    def compute_final_accuracy(self, matches, true_nodes, pred_nodes, true_links, pred_links, updated_links):
        return compute_accuracies(matches, true_nodes, pred_nodes, true_links, pred_links, updated_links)

    def get_ids(self, nodes):
        return get_list_of_ids_from_list_of_nodes(nodes)

    def create_node_dict(self, nodes, links):
        return create_node_link_dict(nodes, links)



def perform_matching(true_nodes_with_links, pred_nodes_with_links, pred_ids, true_ids, ids_to_true_nodes,
                     ids_to_pred_nodes, ids_to_pred_links, printing=False):
    matches = {}
    normalized_pred_nodes = pred_nodes_with_links
    for t in true_nodes_with_links:
        match, normalized_pred_nodes, ids_to_pred_links = best_matches(t, pred_ids, true_ids, normalized_pred_nodes,
                                                                       ids_to_true_nodes,
                                                                       ids_to_pred_nodes, ids_to_pred_links,
                                                                       printing=printing)
        node_id = t["node"]["id"]
        matches[node_id] = match[node_id]
    return matches, ids_to_pred_links

def best_matches(node_with_links, pred_ids, true_ids, normalized_pred_nodes, ids_to_true_nodes, ids_to_pred_nodes,
                 ids_to_pred_links,
                 printing=False):

    # recall data structure of matches is {node_id: (candidate_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c, node with links), ...}
    true_node_with_links = node_with_links
    node_id = node_with_links["node"]["id"]
    matches = {}
    # Get the candidates for the matching
    candidates = get_candidates(true_node_with_links["node"], normalized_pred_nodes)
    if not candidates:
        matches[node_id] = None  # no candidate, no match
        return matches, normalized_pred_nodes, ids_to_pred_links

    # Else we have candidates ! Now we need to find the best match
    # The best match is the candidate that has the most links matched with the true node
    true_node_links = true_node_with_links["links"]
    list_links_matched = []

    if not true_node_links:
        # If the true node has no links, we can match it with any candidate
        # We can just take the first candidate
        if printing:
            print("match between " + str(node_with_links["node"]) + " and " + str(candidates[0]["node"]))
        matches[node_id] = (candidates[0]["node"]["id"], node_with_links)
        # remove from normalized_pred_nodes and pred_nodes
        for c in normalized_pred_nodes:
            if c["node"]["id"] == candidates[0]:
                normalized_pred_nodes.remove(c)
                break
        return matches, normalized_pred_nodes, ids_to_pred_links

    for c in candidates:  # recall candidates have the form [{"node": node, "links": links}, ...]
        # for each candidate, we use this set to remove the links that have been matched with the true node
        indices_of_links_matched = set()
        # number of links matched with the true node
        number_of_links_matched_with_the_true_node = 0
        # number of links in the candidate c
        number_of_links_in_candidate_c = 0
        c_id = c["node"]["id"]

        # matching of link starts here
        for l in true_node_links:
            source = l["source"]
            target = l["target"]

            index_matched = 0
            for c_l in c["links"]:  # recall c_l has the form {"source": source, "target": target}
                link_id = c_l["id"]
                number_of_links_in_candidate_c += 1
                index_matched += 1
                if index_matched in indices_of_links_matched:
                    continue

                c_source = c_l["source"]
                c_target = c_l["target"]
                # now check if the link is a match
                if source == node_id:
                    do_match = match_links(c_id, source, target, c_source, c_target, true_ids, pred_ids,
                                           ids_to_true_nodes, ids_to_pred_nodes, True)
                    if do_match == 0:
                        continue
                    else:
                        number_of_links_matched_with_the_true_node += 1
                        ids_to_pred_links[link_id]['match'] = True

                    # remove the link from the list of links of candidate c
                    index = index_matched - 1  # index of the link in the list of links of candidate c
                    indices_of_links_matched.add(index)
                    break
                else:
                    if target == node_id:
                        do_match = match_links(c_id, source, target, c_source, c_target, true_ids, pred_ids,
                                               ids_to_true_nodes, ids_to_pred_nodes, False)
                        if do_match == 0:
                            continue
                        else:
                            number_of_links_matched_with_the_true_node += 1
                            ids_to_pred_links[link_id]['match'] = True

                    # remove the link from the list of links of candidate c
                    index = index_matched - 1  # index of the link in the list of links of candidate c
                    indices_of_links_matched.add(index)
                    break

            list_links_matched.append(
                (c_id, number_of_links_matched_with_the_true_node, number_of_links_in_candidate_c))
    if list_links_matched:
        # get the best candidate(s)
        max_links_matched = max(list_links_matched, key=lambda x: x[1])[1]
        best_candidates = [c for c in list_links_matched if c[1] == max_links_matched]

        # choose the candidate with the number of links closest to the number of links in the true node
        best_candidate = min(best_candidates, key=lambda x: abs(x[2] - len(true_node_links)))

        if printing:
            print("match between " + str(node_with_links["node"]) + " and " + str(
                ids_to_pred_nodes[best_candidate[0]][0]["node"]))
        # enter the best candidate in the matches
        matches[node_id] = (best_candidate[0], node_with_links)

        # remove from normalized_pred_nodes and pred_nodes
        for c in normalized_pred_nodes:
            if c["node"]["id"] == best_candidate[0]:
                normalized_pred_nodes.remove(c)
                break

    return matches, normalized_pred_nodes, ids_to_pred_links

def match_links(candidate_id, source, target, c_source, c_target, true_ids, pred_ids, ids_to_true_nodes,
                ids_to_pred_nodes, is_source: bool):
    if is_source:
        parameter2 = target
        parameter3 = c_source
        parameter4 = c_target
    else:
        parameter2 = source
        parameter3 = c_target
        parameter4 = c_source
    if parameter3 != candidate_id:  # if the source/target of the link in the candidate is not the candidate itself;
        # it is not a match
        return 0
    if parameter2 not in true_ids:  # if the target/source of the link in the true node is not in the true ids;
        if parameter4 == parameter2:  # meaning it is a node in the uml diagram, the target/source of the candidate should point to the same
            return 1
    else:
        if parameter4 not in pred_ids:  # if the target/source of the candidate is not in the predicted nodes, it is not a match
            return 0
        pred_nodes = ids_to_pred_nodes[parameter4]
        pred_node = pred_nodes[0]
        if nodes_equal(ids_to_true_nodes[parameter2]["node"], pred_node["node"],
                       False) == 1:  # Check if the node in the true nodes is matched with the node in the predicted nodes structurally(have the same attributes)
            return 1
    return 0