import json
from typing import Dict, List, Tuple, Set
from transformers import EvalPrediction

def compute_metrics(eval_pred: EvalPrediction) -> Dict[str, float]:
    """
    Compute evaluation metrics for the UML model completion task.
    """
    predictions, labels = eval_pred

    # Convert byte tensors or token IDs to strings if necessary
    if isinstance(predictions, tuple):
        predictions = predictions[0]

    if hasattr(predictions, 'numpy'):
        predictions = predictions.numpy()
    if hasattr(labels, 'numpy'):
        labels = labels.numpy()

    # Decode predictions and labels from token IDs to strings
    decoded_preds = [pred.strip() for pred in predictions]
    decoded_labels = [label.strip() for label in labels]

    # Initialize accumulators for metrics
    total_ged = 0
    total_node_precision = 0
    total_node_recall = 0
    total_node_f1 = 0
    total_edge_precision = 0
    total_edge_recall = 0
    total_edge_f1 = 0
    n = len(decoded_preds)

    for pred_str, label_str in zip(decoded_preds, decoded_labels):
        # Parse the predicted and label graphs
        try:
            pred_graph = parse_uml_json(pred_str)
            label_graph = parse_uml_json(label_str)
        except json.JSONDecodeError:
            # If parsing fails, skip this example
            n -= 1
            continue

        # Normalize the graphs
        normalized_pred_graph = normalize_graph(pred_graph)
        normalized_label_graph = normalize_graph(label_graph)

        # Evaluate the graphs
        evaluation_metrics = evaluate_graphs(normalized_label_graph, normalized_pred_graph)

        # Accumulate the metrics
        total_ged += evaluation_metrics['Graph Edit Distance']
        total_node_precision += evaluation_metrics['Node Precision']
        total_node_recall += evaluation_metrics['Node Recall']
        total_node_f1 += evaluation_metrics['Node F1 Score']
        total_edge_precision += evaluation_metrics['Edge Precision']
        total_edge_recall += evaluation_metrics['Edge Recall']
        total_edge_f1 += evaluation_metrics['Edge F1 Score']

    # Handle the case where all examples were skipped
    if n == 0:
        return {
            'avg_graph_edit_distance': 0.0,
            'avg_node_precision': 0.0,
            'avg_node_recall': 0.0,
            'avg_node_f1': 0.0,
            'avg_edge_precision': 0.0,
            'avg_edge_recall': 0.0,
            'avg_edge_f1': 0.0
        }

    # Compute average metrics
    avg_ged = total_ged / n
    avg_node_precision = total_node_precision / n
    avg_node_recall = total_node_recall / n
    avg_node_f1 = total_node_f1 / n
    avg_edge_precision = total_edge_precision / n
    avg_edge_recall = total_edge_recall / n
    avg_edge_f1 = total_edge_f1 / n

    return {
        'avg_graph_edit_distance': avg_ged,
        'avg_node_precision': avg_node_precision,
        'avg_node_recall': avg_node_recall,
        'avg_node_f1': avg_node_f1,
        'avg_edge_precision': avg_edge_precision,
        'avg_edge_recall': avg_edge_recall,
        'avg_edge_f1': avg_edge_f1
    }

# Helper Functions
class UMLGraph:
    def __init__(self, nodes: List[Dict], links: List[Dict]):
        self.nodes = nodes
        self.links = links
        self.node_ids = set(node['id'] for node in nodes)
        self.edge_tuples = set((link['source'], link['target']) for link in links)

def parse_uml_json(uml_json_str: str) -> UMLGraph:
    uml_dict = json.loads(uml_json_str)
    return UMLGraph(nodes=uml_dict.get('nodes', []), links=uml_dict.get('links', []))

def normalize_graph(graph: UMLGraph) -> UMLGraph:
    # Map old IDs to new sequential IDs
    id_mapping = {old_id: idx for idx, old_id in enumerate(sorted(graph.node_ids))}
    # Update nodes
    normalized_nodes = []
    for node in graph.nodes:
        node_copy = node.copy()
        node_copy['id'] = id_mapping[node['id']]
        normalized_nodes.append(node_copy)
    # Update edges
    normalized_links = []
    for link in graph.links:
        link_copy = link.copy()
        link_copy['source'] = id_mapping[link['source']]
        link_copy['target'] = id_mapping[link['target']]
        normalized_links.append(link_copy)
    return UMLGraph(nodes=normalized_nodes, links=normalized_links)

def compute_ged(graph_true: UMLGraph, graph_pred: UMLGraph) -> int:
    node_diff = len(graph_true.node_ids.symmetric_difference(graph_pred.node_ids))
    edge_diff = len(graph_true.edge_tuples.symmetric_difference(graph_pred.edge_tuples))
    total_diff = node_diff + edge_diff
    return total_diff

def compute_precision_recall_f1(true_set: Set, pred_set: Set) -> Tuple[float, float, float]:
    true_positives = len(true_set.intersection(pred_set))
    predicted_positives = len(pred_set)
    actual_positives = len(true_set)

    precision = true_positives / predicted_positives if predicted_positives else 0
    recall = true_positives / actual_positives if actual_positives else 0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0

    return precision, recall, f1_score

def evaluate_graphs(graph_true: UMLGraph, graph_pred: UMLGraph) -> Dict[str, float]:
    # Compute GED
    ged = compute_ged(graph_true, graph_pred)

    # Compute Node Metrics
    node_precision, node_recall, node_f1 = compute_precision_recall_f1(
        graph_true.node_ids, graph_pred.node_ids
    )


    # Compute Edge Metrics
    edge_precision, edge_recall, edge_f1 = compute_precision_recall_f1(
        graph_true.edge_tuples, graph_pred.edge_tuples
    )

    return {
        'Graph Edit Distance': ged,
        'Node Precision': node_precision,
        'Node Recall': node_recall,
        'Node F1 Score': node_f1,
        'Edge Precision': edge_precision,
        'Edge Recall': edge_recall,
        'Edge F1 Score': edge_f1
    }