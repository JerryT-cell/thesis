from util_folder.accuracy_utils import get_nodes_and_links, truncate_predicted_nodes, normalize_nodes

def accuracy(y_true, y_pred, truncate=True, printing = False):
    """
    Compute node and link accuracy separately with strict node matching.
    strict means that all attributes including 'id' are considered in the matching.

    Steps:
    1. Truncate predicted nodes if there are more than in the reference.
    2. Normalize nodes (including 'id').
    3. Match nodes based on all attributes (including 'id').
    4. Match links based on matched nodes.
    5. Compute node accuracy and link accuracy separately.

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