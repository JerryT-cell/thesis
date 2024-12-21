from abc import ABC, abstractmethod
from util_folder.accuracy_utils import introduce_ids_to_links
from util_folder.accuracy_utils import links_with_ids_to_dict

class AccuracyTemplate(ABC):

    def compute_accuracy(self, ground_truth, predictions, truncate=True, printing=False):
        # Step 1: Initialize data
        true_nodes, true_links, pred_nodes, pred_links = self.initialize_data(ground_truth, predictions, truncate)

        # Step 2: Preprocess predictions links by adding ids(because duplicates may be present) and match boolean to links
        pred_links = self.add_ids_to_links(pred_links)
        ids_to_pred_links = self.create_links_dict(pred_links)

        # Step 3: Match nodes and links
        matches, updated_links = self.match_nodes_and_links(
            true_nodes, true_links, pred_nodes, pred_links, ids_to_pred_links
        )

        # Step 4: Compute final accuracy metrics
        results = self.compute_final_accuracy(
            matches, true_nodes, pred_nodes, true_links, pred_links, updated_links
        )

        if printing:
            print("Matches:", matches)
            print("Results:", results)

        return results



    @abstractmethod
    def initialize_data(self, ground_truth, predictions, truncate):
        pass

    @abstractmethod
    def match_nodes_and_links(self, true_nodes, true_links, pred_nodes, pred_links, ids_to_pred_links):
        pass

    @abstractmethod
    def compute_final_accuracy(self, matches, true_nodes, pred_nodes, true_links, pred_links, updated_links):
        pass

    @abstractmethod
    def add_ids_to_links(self, links):
        return introduce_ids_to_links(links)

    def create_links_dict(self, links):
        return links_with_ids_to_dict(links)