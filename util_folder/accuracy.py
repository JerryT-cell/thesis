from util_folder.accuracy_utils import get_nodes_and_links, truncate_predicted_nodes, normalize_nodes

def accuracy_less_strict(y_true, y_pred, truncate=True, printing = False):
    """
    Compute node and link accuracy separately with less strict node matching.
    less strict means that the 'id' attribute is not considered in the matching.

    Steps:
    1. Truncate predicted nodes if there are more than in the reference.
    2. Normalize nodes (excluding 'id').
    3. Match nodes based on all attributes except 'id' (case-insensitive).
    4. Match links based on matched nodes.
    5. Compute node accuracy and link accuracy separately.

    Returns:
    node_accuracy, link_accuracy
    """
    true_nodes, true_links, pred_nodes, pred_links = get_nodes_and_links(y_true, y_pred)
    if truncate:
     pred_nodes, pred_links = truncate_predicted_nodes(true_nodes, pred_nodes, pred_links)
    normalized_true_nodes = normalize_nodes(true_nodes)
    normalized_pred_nodes = normalize_nodes(pred_nodes)
    node_accuracy, matched_nodes = match_nodes(normalized_true_nodes, normalized_pred_nodes, strict=False, truncated=truncate, printing= printing)
    link_accuracy = match_links(true_links, pred_links, matched_nodes, strict = False, printing = printing)
    return {"node accuracy": node_accuracy, "link accuracy" : link_accuracy}



def accuracy_strict(y_true, y_pred, truncate=True, printing = False):
    """
    Compute node and link accuracy separately with strict node matching.
    strict means that all attributes including 'id' are considered in the matching.

    Steps:
    1. Get the nodes and links from the true and predicted data.
    2. Truncate predicted nodes if there are more than in the reference.
    3. Normalize nodes (including 'id').
    4. Match nodes based on all attributes (including 'id').
    5. Match links based on matched nodes.
    6. Compute node accuracy and link accuracy separately.

    Returns:
    node_accuracy, link_accuracy
    """
    true_nodes, true_links, pred_nodes, pred_links = get_nodes_and_links(y_true, y_pred)
    if truncate:
     pred_nodes, pred_links =  truncate_predicted_nodes(true_nodes, pred_nodes, pred_links)
    normalized_true_nodes = normalize_nodes(true_nodes)
    normalized_pred_nodes = normalize_nodes(pred_nodes)
    node_accuracy, matched_nodes = match_nodes(normalized_true_nodes, normalized_pred_nodes, strict=True, truncated=truncate, printing= printing)
    link_accuracy = match_links(true_links, pred_links, matched_nodes, strict=True, printing = printing)
    return {"node accuracy": node_accuracy, "link accuracy": link_accuracy}





############################################ Helper functions ############################################################


def match_nodes(normalized_true_nodes, normalized_pred_nodes, strict=False, truncated=True, printing = False):
    """
    Match nodes between true and predicted sets based on the matching criteria.
    If strict is false, i.e the 'id' attribute is not considered in the matching. The node with the correct id will nevertheless be matched first, if it exists.

    Parameters:
    - normalized_true_nodes: List of normalized true nodes.
    - normalized_pred_nodes: List of normalized predicted nodes.
    - strict: Matching criteria flag.
    - truncated: If True, predicted nodes are either truncated or less than true nodes.

    Returns:
    - correct_nodes: Number of correctly matched nodes.
    - matched_nodes: Dictionary mapping predicted node IDs to true node IDs.
    """
    pred_nodes_copy = normalized_pred_nodes[:]
    matched_nodes = {}  # Now mapping t_id -> p_id because of less strict matching, because p_id can be reused
    correct_nodes = 0
    total_nodes = len(normalized_true_nodes)

    # Assuming all true nodes are unique
    for t_node in normalized_true_nodes:
        matched_ids = False
        candidate_matching = []
        for i, p_node in enumerate(pred_nodes_copy):
            if nodes_equal(t_node, p_node, strict) == 1:
                correct_nodes += 1
                t_id = t_node["id"]
                p_id = p_node["id"]
                if t_id == p_id:
                    matched_ids = True
                    matched_nodes[t_id] = p_id
                    del pred_nodes_copy[i]
                    break
                candidate_matching.append((t_id, p_id))
                #matched_nodes[t_id] = p_id  # Store true_id -> pred_id
                #del pred_nodes_copy[i]
                #break
        if not matched_ids:
            #If no exact match, choose the first from the candidates and remove it from prediction. This is mostly for less strict matching
            if candidate_matching:
                t_id, p_id = candidate_matching[0]
                matched_nodes[t_id] = p_id
                pred_nodes_copy = [p_node for p_node in pred_nodes_copy if p_node["id"] != p_id]




    if printing:
        printing_matched_nodes(matched_nodes, normalized_true_nodes, normalized_pred_nodes)
    if not truncated:
        total_nodes = max(len(normalized_true_nodes), len(normalized_pred_nodes))
    node_accuracy = (correct_nodes / total_nodes) if total_nodes > 0 else 1.0
    return node_accuracy, matched_nodes


def printing_matched_nodes(matched_nodes, true_nodes, pred_nodes):
    """
    Print the matched nodes in a readable format.
    """
    print("Matched Nodes:")
    for t_id, p_id in matched_nodes.items():
        t_node = next((n for n in true_nodes if n["id"] == t_id), None)
        p_node = next((n for n in pred_nodes if n["id"] == p_id), None)
        if t_node and p_node:
            print(f"True: {t_node}, Predicted: {p_node}")


def match_links(true_links, pred_links, matched_nodes, strict = False, printing = False):
    """
    Match links between true and predicted sets based on matched nodes.
    if there are no matched nodes, the link accuracy is 0.
    calculate link accuracy only for the matched nodes.
    no prediction is considered 0 else 1.

    Only the links of the matched nodes are considered.



    Parameters:
    - true_links: List of true links.
    - pred_links: List of predicted links.
    - matched_nodes: Dictionary mapping true nodes to predicted nodes.
    - strict: If True, predicted links are matched directly with the true links.

    Returns:
    - link_accuracy: Accuracy of correctly matched links.
    """

    # If there are no true links:
    if not true_links:
        # If no predicted links either, accuracy is 1.0, else 0.0
        return 1.0 if not pred_links else 0.0

    #if matched_nodes is empty return 0
    # If no nodes are matched, no links can be matched
    if not matched_nodes:
        return 0.0



    # Create a set of true link tuples for quick lookup
    true_link_set = set()
    for link in true_links:
        source = str(link.get("source"))
        target = str(link.get("target"))
        if source and target:
            true_link_set.add((source, target))
    pred_link_set = set()

    # consider the links of the matched nodes only
    number_of_links_to_consider = 0
    rev_matched_nodes = {}
    for t_id, p_id in matched_nodes.items():
        if p_id not in rev_matched_nodes:
            rev_matched_nodes[str(p_id)] = set()
        rev_matched_nodes[str(p_id)].add(str(t_id))

    #if strict is true, the predicted links are matched directly with the true links
    if strict:
        for link in pred_links:
            source_pred = str(link.get("source"))
            target_pred = str(link.get("target"))
            if source_pred and target_pred:
               if source_pred in rev_matched_nodes or target_pred in rev_matched_nodes:
                     number_of_links_to_consider += 1
                     pred_link_set.add((str(source_pred), str(target_pred))) # Don't care about duplicates because at the end number_of_links_to_consider will make sure a penalty is given for each extra link
        correct_links = len(true_link_set & pred_link_set)
        if printing:
            print("Matched Links:")
            for link in pred_link_set:
                print(link)
        total_links = max(len(true_link_set), number_of_links_to_consider)
        link_accuracy = (correct_links / total_links) if total_links > 0 else 1.0
        return link_accuracy
    else:
        # Create a set of predicted link tuples based on matched nodes
        # pred id is replaced with true id in the matched nodes for less strict matching
        print("Matched Links:")
        for link in pred_links:
            source_pred = str(link.get("source"))
            target_pred = str(link.get("target"))
            if source_pred in rev_matched_nodes and target_pred in rev_matched_nodes:
             # Both source and target map to one or more true_ids.
             for s_true in rev_matched_nodes[source_pred]:
                 for t_true in rev_matched_nodes[target_pred]:
                    number_of_links_to_consider += 1
                    if printing:
                     print((str(s_true), str(t_true)))
                    pred_link_set.add((str(s_true), str(t_true)))
            else:
                if source_pred in rev_matched_nodes:
                    # Only source is matched, add (s_true, target_pred)
                    for s_true in rev_matched_nodes[source_pred]:
                        number_of_links_to_consider += 1
                        if printing:
                            print("less strict original:")
                            print((source_pred, target_pred))
                            print("true:")
                            print((s_true, target_pred))
                        pred_link_set.add((str(s_true), target_pred))
                if target_pred in rev_matched_nodes:
                    #Only target is matched, add (source_pred, t_true)
                    for t_true in rev_matched_nodes[target_pred]:
                        number_of_links_to_consider += 1
                        if printing:
                            print("less strict original:")
                            print((source_pred, target_pred))
                            print("true:")
                            print((source_pred, t_true))
                        pred_link_set.add((source_pred, str(t_true)))


        total_links = min(len(true_link_set), number_of_links_to_consider)   # Only consider the links of the matched nodes
        # Count correctly matched links
        correct_links = len(true_link_set & pred_link_set)
        link_accuracy = (correct_links / total_links) if total_links > 0 else 1.0
        return link_accuracy



########################### Test #######################################

# Example true and predicted data (Directed Graph)
y_true = {
    "nodes": [
        {"id": "1", "type": "Server", "status": "Active"},
        {"id": "2", "type": "Client", "status": "Inactive"},
        {"id": "3", "type": "Database", "status": "Active"},
    ],
    "links": [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
        {"source": "3", "target": "1"},  # Creates a cycle
    ],
}

y_pred = {
    "nodes": [
        {"id": "1", "type": "server", "status": "active"},
        {"id": "2", "type": "client", "status": "inactive"},
        {"id": "3", "type": "database", "status": "active"},
    ],
    "links": [
        {"source": "1", "target": "2"},  # Correct
        {"source": "2", "target": "3"},  # Correct
        {"source": "3", "target": "1"},  # Correct
        {"source": "a", "target": "c"},  # Extra link
    ],
}


# Compute accuracies
#node_acc_less_strict, link_acc_less_strict = accuracy_less_strict(y_true, y_pred)
#node_acc_strict, link_acc_strict = accuracy_strict(y_true, y_pred)

#print(f"Less Strict - Node Accuracy: {node_acc_less_strict:.2f}, Link Accuracy: {link_acc_less_strict:.2f}")
#print(f"Strict - Node Accuracy: {node_acc_strict:.2f}, Link Accuracy: {link_acc_strict:.2f}")

