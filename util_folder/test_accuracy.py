import unittest
from util_folder.accuracy_without_embedding.accuracy_less_strict import simple_accuracy_less_strict as accuracy_less_strict
from util_folder.accuracy_without_embedding.accuracy_strict import accuracy_strict

'''
Overview of Test Cases
1. Empty Graphs: Both true and predicted graphs have no nodes or links.
2. No Links: Graphs with nodes but no links.
3. Single Node: Graphs with a single node.
4. Single Link: Graphs with two nodes connected by a single directed link.
5. Exact Match (Strict): True and predicted graphs are identical.
6. Test more predicted nodes: Predicted graph has more nodes than the true graph and more links.
7. Exact Match (Less Strict): Nodes have different IDs but matching attributes.
8. Extra Predicted Nodes: Predicted graph has more nodes than the true graph.
9. Missing Predicted Nodes: Predicted graph has fewer nodes than the true graph.
10. Extra Predicted Links: Predicted graph has additional links not present in the true graph.
11. Missing Predicted Links: Predicted graph is missing some links present in the true graph.
12. Different Link Directions: Links exist but in opposite directions.
13. Case Sensitivity: Attributes differ only in letter casing.

14. Attribute Mismatch: Nodes have differing attributes beyond 'id'.
15. Duplicate Predicted Nodes: Predicted graph has duplicate nodes matching a true node.
16. Cyclic Graphs: Graphs containing cycles.
17. Disconnected Graphs: Graphs with multiple disconnected components.
18. Partial Node Matching: Only some nodes match between true and predicted graphs.
19. Partial Link Matching: Only some links match between true and predicted graphs.
20. Nodes with Extra Attributes: Predicted nodes have additional attributes not present in true nodes.
21. Links with Unmatched Nodes: Predicted links reference nodes that weren't matched.
22. Predicted nodes have same ids but are correct
22. Predicted nodes have same ids but are correct, and nodes are identical
23. links are duplicated
'''

class TestGraphAccuracy(unittest.TestCase):

    def test_empty_graphs(self):
        """1. Test accuracy functions with empty true and predicted graphs."""
        y_true = {"nodes": [], "links": []}
        y_pred = {"nodes": [], "links": []}

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 1.0)
        self.assertEqual(link_acc_ls, 1.0)
        self.assertEqual(node_acc_s, 1.0)
        self.assertEqual(link_acc_s, 1.0)

    def test_no_links(self):
        """2. Test accuracy functions with nodes but no links."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "Inactive"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": 3, "type": "server", "status": "active"},
                {"id": 4, "type": "client", "status": "inactive"},
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred, printing=True)
        nodes_link_s = accuracy_strict(y_true, y_pred, printing=True)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)  # 2 correct nodes
        self.assertEqual(link_acc_ls, 1.0)  # No links to evaluate
        self.assertEqual(node_acc_s, 0.0)  # IDs don't match
        self.assertEqual(link_acc_s, 1.0)  # No links to evaluate but node_accuracy affects it?

    def test_single_node(self):
        """3. Test accuracy functions with a single node."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": 2, "type": "server", "status": "active"},
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 1.0)  # Attributes match ignoring 'id'
        self.assertEqual(link_acc_ls, 1.0)  # No links
        self.assertEqual(node_acc_s, 0.0)   # 'id's do not match
        self.assertEqual(link_acc_s, 1.0)   # No links but node_accuracy affects it

    def test_single_link(self):
        """4. Test accuracy functions with two nodes and one link"""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": 1, "target": 10}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": 3, "type": "server", "status": "active"},
                {"id": 4, "type": "client", "status": "inactive"},
            ],
            "links": [
                {"source":3, "target": 10}
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)  # All nodes matched ignoring 'id'
        self.assertEqual(link_acc_ls, 1/1)  # One correct link 3<->1 (after mapping) -> 10
        self.assertEqual(node_acc_s, 0/2)   # No nodes matched strictly
        self.assertEqual(link_acc_s, 0/1)   # No links matched strictly

    def test_exact_match_strict(self):
        """5. Test accuracy functions with exact matching graphs (strict)."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": 1, "target": 2}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": 1, "target": 2}
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)  # All nodes matched ignoring 'id'
        self.assertEqual(link_acc_ls, 1/1)  # One correct link
        self.assertEqual(node_acc_s, 2/2)   # All nodes matched strictly
        self.assertEqual(link_acc_s, 1/1)   # One correct link

    def  test_more_predicted_nodes(self):
        """6. Test accuracy functions when predicted graph has more nodes."""
        y_true = {
            "nodes": [
                {"id": 10, "type": "class", "name": "Order"}
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
               {"id": 20, "type": "class", "name": "order"},
               {"id": 21, "type": "class", "name": "customer"}  # extra node, should be truncated
           ],
           "links": [
                   {"source": 20, "target": 21}  # link referencing truncated node should be removed
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Expected after truncation:
        # Only first predicted node retained: {"id": 20, "type": "class", "name": "order"}
        # Extra link referencing node 21 removed.
        # Less strict: node matches ignoring 'id' and case. order vs Order => node_accuracy=1.0, link_accuracy=0.0 (no links now)
        # Strict: 'id' must match. 20 vs 10 does not match => node_accuracy=0.0, link_accuracy=10.0
        self.assertEqual(node_acc_ls, 1.0)
        self.assertEqual(link_acc_ls, 1.0)
        self.assertEqual(node_acc_s, 0.0)
        self.assertEqual(link_acc_s, 1.0)


    def test_exact_match_less_strict_different_ids(self):
        """Test accuracy_less_strict with matching attributes but different IDs."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": 1, "target": 2}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": 3, "type": "Server", "status": "Active"},
                {"id": 4, "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": 3, "target": 4}
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)  # All nodes matched ignoring 'id'
        self.assertEqual(link_acc_ls, 1/1)  # One correct link
        self.assertEqual(node_acc_s, 0/2)   # No nodes matched strictly
        self.assertEqual(link_acc_s, 0/1)   # No links matched strictly

    def test_extra_predicted_nodes(self):
        """Test accuracy functions when predicted graph has extra nodes."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "Server", "status": "Active"},
                {"id": "2", "type": "Client", "status": "Inactive"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "3", "type": "Server", "status": "Active"},
                {"id": "4", "type": "Client", "status": "Inactive"},
                {"id": "5", "type": "Database", "status": "Active"},  # Extra node
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Truncate predicted nodes to 2, '5' is removed
        self.assertEqual(node_acc_ls, 2/2)
        self.assertEqual(link_acc_ls, 1.0)  # No links
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 1.0)  # No matching nodes

        nodes_link_ls = accuracy_less_strict(y_true, y_pred, truncate=False)
        nodes_link_s = accuracy_strict(y_true, y_pred, truncate=False)

        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Truncate predicted nodes to 2, '5' is removed
        self.assertEqual(node_acc_ls, 2/3)
        self.assertEqual(link_acc_ls, 1.0)  # No links
        self.assertEqual(node_acc_s, 0.0)
        self.assertEqual(link_acc_s, 1.0)  # No matching nodes

    def test_missing_predicted_nodes(self):
        """Test accuracy functions when predicted graph has fewer nodes."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "Server", "status": "Active"},
                {"id": "2", "type": "Client", "status": "Inactive"},
                {"id": "3", "type": "Database", "status": "Active"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "4", "type": "Server", "status": "Active"},
                {"id": "5", "type": "Client", "status": "Inactive"},
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Only 2 nodes are present
        self.assertEqual(node_acc_ls, 2/3)  # Two correct matches
        self.assertEqual(link_acc_ls, 1.0)  # No links
        self.assertEqual(node_acc_s, 0/3)   # No strict matches
        self.assertEqual(link_acc_s, 1.0)   # No matching nodes

    def test_extra_predicted_links(self):
        """Test accuracy functions when predicted graph has extra links."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "Server", "status": "Active"},
                {"id": "2", "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": "1", "target": "2"}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "3", "type": "Server", "status": "Active"},
                {"id": "4", "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": "3", "target": "4"},
                {"source": "4", "target": "6"}  # Extra link
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)
        # Only one true link, and 'a'->'b' matches '1'->'2' after mapping
        self.assertEqual(link_acc_ls, 1/2) # since all links are considered
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 0.0)  # no matching nodes

    def test_missing_predicted_links(self):
        """Test accuracy functions when predicted graph is missing some links."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "Server", "status": "Active"},
                {"id": "2", "type": "Client", "status": "Inactive"},
                {"id": "3", "type": "Database", "status": "Active"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "3", "type": "Server", "status": "Active"},
                {"id": "4", "type": "Client", "status": "Inactive"},
                {"id": "5", "type": "Database", "status": "Active"},
            ],
            "links": [
                {"source": "3", "target": "4"},  # Matches '1'->'2'
                # Missing '2'->'3'
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 3/3)
        self.assertEqual(link_acc_ls, 1/2)  # Only one correct link out of two
        self.assertEqual(node_acc_s, 0/3)
        self.assertEqual(link_acc_s, 0/2)

    def test_different_link_directions(self):
        """Test accuracy functions when links exist but in opposite directions."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "Server", "status": "Active"},
                {"id": "2", "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": "1", "target": "2"}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "Server", "status": "Active"},
                {"id": "b", "type": "Client", "status": "Inactive"},
            ],
            "links": [
                {"source": "b", "target": "a"}  # Opposite direction
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)
        self.assertEqual(link_acc_ls, 0/1)  # Direction matters
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 0/1)

    def test_case_sensitivity(self):
        """Test accuracy functions with attribute case differences."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "SERVER", "status": "ACTIVE"},
                {"id": "2", "type": "CLIENT", "status": "INACTIVE"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "server", "status": "active"},
                {"id": "b", "type": "client", "status": "inactive"},
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)
        self.assertEqual(link_acc_ls, 1.0)
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 1.0)  # Nodes don't match strictly

    def test_attribute_mismatch(self):
        """Test accuracy functions with nodes having different attributes."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "Server", "status": "Active"},
                {"id": "2", "type": "Client", "status": "Inactive"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "Server", "status": "Inactive"},  # Status mismatch
                {"id": "b", "type": "Client", "status": "Inactive"},
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 1/2)  # Only 'b' matches
        self.assertEqual(link_acc_ls, 1.0)  # No links
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 1.0)  # No links

    def test_duplicate_predicted_nodes(self):
        """Test accuracy functions with duplicate predicted nodes matching a true node."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "Server", "status": "Active"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "Server", "status": "Active"},
                {"id": "b", "type": "Server", "status": "Active"},  # Duplicate
            ],
            "links": []
        }

        # Comparing with true having one node
        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 1/1)
        self.assertEqual(link_acc_ls, 1.0)
        self.assertEqual(node_acc_s, 0/1)
        self.assertEqual(link_acc_s, 1.0)

        nodes_link_ls = accuracy_less_strict(y_true, y_pred, truncate=False )
        nodes_link_s = accuracy_strict(y_true, y_pred,  truncate=False)

        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 1/2)
        self.assertEqual(link_acc_ls, 1.0)
        self.assertEqual(node_acc_s, 0/1)
        self.assertEqual(link_acc_s, 1.0)

    def test_cyclic_graphs(self):
        """Test accuracy functions with cyclic graphs."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "1"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "X"},
                {"id": "b", "type": "B", "status": "Y"},
                {"id": "c", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "a", "target": "b"},
                {"source": "b", "target": "c"},
                {"source": "c", "target": "a"},
                {"source": "a", "target": "c"},  # Extra link
            ]
        }
        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 3/3)
        self.assertEqual(link_acc_ls, 3/4)  # Extra link affect because it is a matched node
        self.assertEqual(node_acc_s, 0/3)
        self.assertEqual(link_acc_s, 0.0)

    def test_graphs_with_outside_id_links(self):
        """Test accuracy functions with disconnected components."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
                {"id": "4", "type": "D", "status": "W"},
            ],
            "links": [
                {"source": "1", "target": "10"},
                {"source": "3", "target": "70"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "X"},
                {"id": "b", "type": "B", "status": "Y"},
                {"id": "c", "type": "C", "status": "Z"},
                {"id": "d", "type": "D", "status": "W"},
            ],
            "links": [
                {"source": "a", "target": "10"},
                {"source": "c", "target": "70"},
                {"source": "d", "target": "c"},  # Extra link
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred, printing=True)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 4/4)
        self.assertEqual(link_acc_ls, 2/3)  # affects because it is a matched node
        self.assertEqual(node_acc_s, 0/4)
        self.assertEqual(link_acc_s, 0.0)  # Links matched via node mapping

    def test_partial_node_matching(self):
        """Test accuracy functions where only some nodes match."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Different"},  # Status mismatch
                {"id": "3", "type": "D", "status": "Z"},          # Type mismatch
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 1/3)  # Only 'a' matches
        self.assertEqual(link_acc_ls, 1.0)  # No links
        self.assertEqual(node_acc_s, 1/3)
        self.assertEqual(link_acc_s, 1.0)  # No links


    def test_partial_link_matching(self):
        """Test accuracy functions where only some links match."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "1"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "1", "target": "2"},  # Correct
                {"source": "2", "target": "3"},  # Correct
                {"source": "3", "target": "4"},  # Incorrect (node 'd' doesn't exist)
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 3/3)
        self.assertEqual(link_acc_ls, 2/3)  # Two correct links
        self.assertEqual(node_acc_s, 3/3)
        self.assertEqual(link_acc_s, 2/3)  # Nodes don't match strictly

    def test_nodes_with_extra_attributes(self):
        """Test accuracy functions where predicted nodes have extra attributes."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X", "extra": "data"},  # Extra attribute
            ],
            "links": []
        }
        y_true_extra = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "A", "status": "X"},
            ],
            "links": []
        }
        y_pred_extra = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X", "extra": "data"},
                {"id": "2", "type": "A", "status": "X", "extra": "info"},
            ],
            "links": []
        }

        # Single node
        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 1/1)
        self.assertEqual(link_acc_ls, 1.0)
        self.assertEqual(node_acc_s, 0/1)
        self.assertEqual(link_acc_s, 1.0)  # Extra attributes are ignored in strict?

        # Single node
        nodes_link_ls_ex = accuracy_less_strict(y_true, y_pred)
        nodes_link_s_ex = accuracy_strict(y_true, y_pred)

        # Multiple nodes
        node_acc_ls_ex, link_acc_ls_ex = nodes_link_ls_ex["node accuracy"], nodes_link_ls_ex["link accuracy"]
        node_acc_s_ex, link_acc_s_ex = nodes_link_s_ex["node accuracy"], nodes_link_s_ex["link accuracy"]

        self.assertEqual(node_acc_ls_ex, 2/2)
        self.assertEqual(link_acc_ls_ex, 1.0)
        self.assertEqual(node_acc_s_ex, 0/2)
        self.assertEqual(link_acc_s_ex, 1.0)

    def test_truncate_predicted_nodes_links(self):
        """Test that truncate_predicted_nodes correctly truncates nodes and links."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "4"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},  # Extra node to be truncated
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "1"},
                {"source": "3", "target": "4"},  # Link referencing truncated node
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Only 'a' and 'b' are considered
        self.assertEqual(node_acc_ls, 2/2)
        self.assertEqual(link_acc_ls, 1/2)
        self.assertEqual(node_acc_s, 2/2)
        self.assertEqual(link_acc_s, 1/2)

        nodes_link_ls = accuracy_less_strict(y_true, y_pred, truncate=False)
        nodes_link_s = accuracy_strict(y_true, y_pred, truncate=False)

        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Only 'a' and 'b' are considered
        self.assertEqual(node_acc_ls, 2/3)
        self.assertEqual(link_acc_ls, 1/2)
        self.assertEqual(node_acc_s, 2/3)
        self.assertEqual(link_acc_s, 1/2)

    def test_large_graph(self):
        """Test accuracy functions with a large graph."""
        num_nodes = 100
        y_true_nodes = [{"id": str(i), "type": "Type{}".format(i % 5), "status": "Status{}".format(i % 3)} for i in range(1, num_nodes + 1)]
        y_true_links = [{"source": str(i), "target": str(i+1)} for i in range(1, num_nodes)]

        y_pred_nodes = [{"id": str(i), "type": "Type{}".format(i % 5), "status": "Status{}".format(i % 3)} for i in range(1, num_nodes + 1)]
        y_pred_links = [{"source": str(i), "target": str(i+1)} for i in range(1, num_nodes)]
        # Add some extra links
        y_pred_links += [{"source": str(i) , "target": str(i+2)} for i in range(1, num_nodes - 1)]

        y_true = {"nodes": y_true_nodes, "links": y_true_links}
        y_pred = {"nodes": y_pred_nodes, "links": y_pred_links}

        true_acc = len(y_true_links) / len(y_pred_links)


        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, num_nodes / num_nodes)
        # Only the first num_nodes -1 links match
        print(y_true_links)
        print(y_pred_links)
        self.assertEqual(link_acc_ls, true_acc)
        self.assertEqual(node_acc_s, 1.0)
        # All links do not match strictly
        self.assertEqual(link_acc_s, true_acc)





############################ Attributes or no attributes ######################################


    def test_no_matching_nodes(self):
        """Test accuracy functions when no nodes match."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
            ],
            "links": [
                {"source": "1", "target": "2"}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "C", "status": "Z"},
                {"id": "b", "type": "D", "status": "W"},
            ],
            "links": [
                {"source": "a", "target": "b"}
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 0/2)
        self.assertEqual(link_acc_ls, 0/2)
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 0/2)

    def test_partial_attribute_matching(self):
        """Test accuracy functions with partial attribute matching."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X", "extra": "data1"},
                {"id": "2", "type": "B", "status": "Y", "extra": "data2"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "X"},  # Missing 'extra'
                {"id": "b", "type": "B", "status": "Y", "extra": "data3"},  # Different 'extra'
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # In less strict, 'extra' is considered because normalize_nodes does not exclude 'extra'
        # For matching, 'extra' in y_true node1 is not present in y_pred node a, so no match
        # y_true node2 has 'extra': 'data2' vs y_pred node b has 'extra': 'data3', no match
        self.assertEqual(node_acc_ls, 0/2)
        self.assertEqual(link_acc_ls, 1.0)  # No links to match
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 1.0)  # No links

    def test_mixed_matching(self):
        """Test accuracy functions with mixed node and link matches."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "Active"},
                {"id": "2", "type": "B", "status": "Inactive"},
                {"id": "3", "type": "C", "status": "Active"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "active"},
                {"id": "b", "type": "B", "status": "inactive"},
                {"id": "c", "type": "C", "status": "active"},
            ],
            "links": [
                {"source": "a", "target": "b"},  # Correct
                {"source": "a", "target": "c"},  # Extra
                {"source": "c", "target": "a"},  # Incorrect direction
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 3/3)
        self.assertEqual(link_acc_ls, 1/3)
        self.assertEqual(node_acc_s, 0.0)
        self.assertEqual(link_acc_s, 0.0)


    def test_links_with_partial_matched_nodes(self):
        """Test accuracy functions where only some links have both nodes matched."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "X"},
                {"id": "b", "type": "B", "status": "Y"},
                {"id": "c", "type": "C", "status": "Different"},  # Status mismatch
            ],
            "links": [
                {"source": "a", "target": "b"},  # Correct
                {"source": "b", "target": "c"},  # Mismatch
                {"source": "a", "target": "c"},  # Mismatch
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/3)
        self.assertEqual(link_acc_ls, 1/3)
        self.assertEqual(node_acc_s, 0/3)
        self.assertEqual(link_acc_s, 0.0)

    def test_truncated_links_in_predicted(self):
        """Test accuracy functions when truncation removes links referencing extra nodes."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
                {"id": "4", "type": "D", "status": "W"},  # Extra node to be truncated
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "4"},  # Link referencing truncated node
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Only first 3 nodes are considered (truncate 'd')
        self.assertEqual(node_acc_ls, 3/3)
        self.assertEqual(link_acc_ls, 2/2)
        self.assertEqual(node_acc_s, 3/3)
        self.assertEqual(link_acc_s, 2/2)

    def test_partial_matching_with_truncated_predicted(self):
        """Test accuracy functions with partial node matches and truncation."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "X"},  # Matches '1'
                {"id": "b", "type": "B", "status": "Different"},  # Does not match '2'
                {"id": "c", "type": "C", "status": "Z"},  # Matches '3'
                {"id": "d", "type": "D", "status": "W"},  # Extra node
            ],
            "links": [
                {"source": "a", "target": "b"},  # Partially matches '1'->'2' (b does not match)
                {"source": "b", "target": "c"},  # Does not match
                {"source": "c", "target": "d"},  # 'd' is truncated
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Truncate to first 3 nodes: 'a', 'b', 'c'
        # 'a' matches '1', 'c' matches '3', 'b' does not match '2'
        self.assertEqual(node_acc_ls, 2/3)
        # Only 'a'->'b' is considered, but 'b' does not match '2', so no link matches
        self.assertEqual(link_acc_ls, 0/2)
        self.assertEqual(node_acc_s, 0/3)
        # No strict node matches, so no link matches
        self.assertEqual(link_acc_s, 0/2)

    def test_overlapping_links(self):
        """Test accuracy functions with overlapping links."""

        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "1", "target": "3"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "X"},
                {"id": "b", "type": "B", "status": "Y"},
                {"id": "c", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "a", "target": "b"},  # Correct
                {"source": "a", "target": "c"},  # Correct
                {"source": "b", "target": "c"},  # Extra
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 3/3)
        self.assertEqual(link_acc_ls, 2/3)  # Extra link does not affect
        self.assertEqual(node_acc_s, 0/3)
        self.assertEqual(link_acc_s, 0.0)


    def test_partial_truncated_links(self):
        """Test accuracy functions where only some links are truncated due to node truncation."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
                {"id": "3", "type": "C", "status": "Z"},
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "4"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "X"},
                {"id": "b", "type": "B", "status": "Y"},
                {"id": "c", "type": "C", "status": "Z"},
                {"id": "d", "type": "D", "status": "W"},  # Extra node to be truncated
            ],
            "links": [
                {"source": "a", "target": "b"},
                {"source": "b", "target": "c"},
                {"source": "c", "target": "d"},  # truncate
                {"source": "d", "target": "a"},  # truncate
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        # Truncate to first 4 nodes (no truncation needed)
        # All nodes match ignoring 'id'
        self.assertEqual(node_acc_ls, 4/4)
        # 'a'->'b' matches '1'->'2'
        # 'b'->'c' matches '2'->'3'
        # 'c'->'d' is truncated (only first 4 nodes are considered)
        # So 2 correct links out of 3
        self.assertEqual(link_acc_ls, 2/3)
        self.assertEqual(node_acc_s, 0/4)
        # 'a'->'b', 'b'->'c', 'c'->'d' do not match true IDs
        self.assertEqual(link_acc_s, 0.0)


    def test_predicted_nodes_same_ids(self):
        """Test accuracy functions when predicted nodes have the same IDs."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "3", "type": "A", "status": "X"},
                {"id": "3", "type": "B", "status": "Y"},
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)
        self.assertEqual(link_acc_ls, 1.0)
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 1.0)

    def test_predicted_nodes_same_ids_identical(self):
        """Test accuracy functions when predicted nodes have the same IDs."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": "3", "type": "A", "status": "X"},
            ],
            "links": []
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 1/2)
        self.assertEqual(link_acc_ls, 1.0)
        self.assertEqual(node_acc_s, 0/1)
        self.assertEqual(link_acc_s, 1.0)

    def duplicated_links(self):
        """Test accuracy functions with duplicated links."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "A", "status": "X"},
                {"id": "2", "type": "B", "status": "Y"},
            ],
            "links": [
                {"source": "1", "target": "2"},
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "A", "status": "X"},
                {"id": "b", "type": "B", "status": "Y"},
            ],
            "links": [
                {"source": "a", "target": "b"},
                {"source": "a", "target": "b"},
            ]
        }

        nodes_link_ls = accuracy_less_strict(y_true, y_pred)
        nodes_link_s = accuracy_strict(y_true, y_pred)
        
        node_acc_ls, link_acc_ls = nodes_link_ls["node accuracy"], nodes_link_ls["link accuracy"]
        node_acc_s, link_acc_s = nodes_link_s["node accuracy"], nodes_link_s["link accuracy"]

        self.assertEqual(node_acc_ls, 2/2)
        self.assertEqual(link_acc_ls, 0.5)
        self.assertEqual(node_acc_s, 0/2)
        self.assertEqual(link_acc_s, 0.0)

    def test_multiple_nodes_partial_strict_match(self):
        """Test scenario where only some nodes match strictly by id and attributes."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "Inactive"},
                {"id": 3, "type": "Database", "status": "Active"},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                # Matches 1 exactly
                {"id": 1, "type": "Server", "status": "Active"},
                # Different 'id', should not match ID=2 node strictly
                {"id": 4, "type": "Client", "status": "Inactive"},
                # Same attributes as node 3 but different ID
                {"id": 10, "type": "Database", "status": "Active"},
            ],
            "links": []
        }

        result = accuracy_strict(y_true, y_pred)
        # Only node ID=1 matches strictly
        # correct_nodes = 1
        # len(y_true_nodes)=3, len(y_pred_nodes)=3 -> denominator=3 because predicted nodes = ground truth nodes count
        # node_accuracy = 1/3
        # No links, so link_accuracy = 1.0
        self.assertEqual(result["node accuracy"], 1 / 3)
        self.assertEqual(result["link accuracy"], 1.0)

    def test_strict_duplicate_pred_nodes(self):
        """Test scenario with duplicate predicted nodes having the same id."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"}
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 1, "type": "Server", "status": "Active"},  # duplicate same ID and attributes
            ],
            "links": []
        }

        # Once we match the first predicted node with id=1, we remove it from future consideration.
        # Still, there's only one true node, so correct_nodes=1.
        # GT=1, Pred=2 => denominator = 2 (more predicted)
        # node_accuracy = 1/2
        # link_accuracy=1.0 (no links)
        result = accuracy_strict(y_true, y_pred, truncate=False)
        self.assertEqual(result["node accuracy"], 1/2)
        self.assertEqual(result["link accuracy"], 1.0)

    def test_strict_multiple_links_some_match(self):
        """Test scenario with multiple links, some match strictly, some do not."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "Active"},
                {"id": 3, "type": "Database", "status": "Inactive"},
            ],
            "links": [
                {"source": 1, "target": 2},
                {"source": 1, "target": 3}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "Active"},
                {"id": 10, "type": "Database", "status": "Inactive"},
            ],
            "links": [
                # This link will match because nodes 1 and 2 are matched
                {"source": 1, "target": 2},
                # This link won't match because node 3 didn't match strictly in predicted
                {"source": 1, "target": 3},
                # Extra link
                {"source": 2, "target": 1},
            ]
        }

        result = accuracy_strict(y_true, y_pred)
        self.assertAlmostEqual(result["node accuracy"], 2 / 3)
        self.assertAlmostEqual(result["link accuracy"], 2 / 3)

    def test_strict_no_node_match_links_present(self):
        """Test scenario where no nodes match but links exist."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"}
            ],
            "links": [
                {"source": 1, "target": 2}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": 2, "type": "Server", "status": "Active"}
            ],
            "links": [
                {"source": 2, "target": 5}
            ]
        }

        # No node match: correct_nodes=0
        # GT=1, Pred=1, fewer predicted or equal => denominator=1
        # node_accuracy = 0/1 = 0.0

        # For links, since no nodes matched, no links are considered:
        # If no nodes matched, we have no matched links to consider.
        # Usually if no links are considered, link_accuracy=1.0 by the given tests.
        # Check given tests: if node accuracy is zero because no nodes matched,
        # do we still say link_accuracy=1.0?
        # The test cases show that if no links are considered (like when nodes don't match), link accuracy is 1.0.
        # result: link_accuracy=1.0
        result = accuracy_strict(y_true, y_pred)
        self.assertEqual(result["node accuracy"], 0.0)
        self.assertEqual(result["link accuracy"], 0.0)

    def test_strict_case_insensitive_attributes(self):
        """Test that attribute comparison is case-insensitive for strict matching."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "SeRvEr", "status": "aCtIvE"},
                {"id": 2, "type": "ClIeNt", "status": "InAcTiVe"}
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": 1, "type": "server", "status": "Active"},
                {"id": 2, "type": "Client", "status": "inactive"}
            ],
            "links": []
        }

        # Both nodes match strictly by ID and case-insensitive attributes
        # correct_nodes=2
        # GT=2, Pred=2 => denominator=2
        # node_accuracy=2/2=1.0
        # No links => link_accuracy=1.0

        result = accuracy_strict(y_true, y_pred)
        self.assertEqual(result["node accuracy"], 1.0)
        self.assertEqual(result["link accuracy"], 1.0)

    def test_strict_additional_attributes_in_pred(self):
        """Test scenario where predicted node has extra attributes not in ground truth."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active"}
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active", "location": "US"}
            ],
            "links": []
        }

        # Extra attributes in predicted node should not prevent a match,
        # as long as all attributes in GT match in Pred.
        # correct_nodes=1
        # GT=1, Pred=1
        # node_accuracy=1/1=1.0
        # No links => link_accuracy=1.0

        result = accuracy_strict(y_true, y_pred)
        self.assertEqual(result["node accuracy"], 0.0)
        self.assertEqual(result["link accuracy"], 1.0)

    def test_strict_mismatched_non_string_attribute(self):
        """Test scenario where a non-string attribute differs."""
        y_true = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active", "version": 2},
            ],
            "links": []
        }
        y_pred = {
            "nodes": [
                {"id": 1, "type": "Server", "status": "Active", "version": 3},
            ],
            "links": []
        }

        # Same id, attributes differ by a non-string attribute (version=2 vs 3)
        # This fails strict match.
        # correct_nodes=0
        # GT=1, Pred=1
        # node_accuracy=0/1=0.0
        # No links => link_accuracy=1.0

        result = accuracy_strict(y_true, y_pred)
        self.assertEqual(result["node accuracy"], 0.0)
        self.assertEqual(result["link accuracy"], 1.0)

    def test_partial_cycle_break(self):
        """Test scenario where ground truth forms a cycle but predicted does not match all nodes."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "Server", "status": "X"},
                {"id": "2", "type": "Client", "status": "Y"},
                {"id": "3", "type": "Database", "status": "Z"}
            ],
            "links": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "1"}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "A", "type": "Server", "status": "X"},  # matches 1
                {"id": "B", "type": "Cache", "status": "Y"},  # not a client, no match to node 2
                {"id": "C", "type": "Database", "status": "W"}  # doesn't match node 3
            ],
            "links": [
                {"source": "A", "target": "B"},  # partial link
                {"source": "B", "target": "C"},
                {"source": "C", "target": "A"}
            ]
        }

        # Only node 1 matches to A.
        # correct_nodes=1
        # GT=3, Pred=3 => denominator=3
        # node_accuracy=1/3

        # Links:
        # Only consider links from matched sources: source=1 matches A, so links from node 1 are considered.
        # GT links from node 1: (1->2)
        # Translate (1->2) -> (A-> [node that matches 2? no match, so "2" is literal? Wait, 2 is unmatched GT node ID.
        # Since it is not matched, we treat "2" as literal. So we need a predicted link (A->2).
        # Pred links: (A->B), (B->C), (C->A). None is (A->2). No link match.
        # correct_links=0
        # GT=1 considered link, Pred=1 considered link? Actually, we considered only links from matched sources in predicted as well.
        # Pred matched sources: A only. Links from A: (A->B)
        # GT considered links=1, Pred considered links=1
        # link_accuracy=0/1=0.0

        result = accuracy_less_strict(y_true, y_pred)
        self.assertEqual(result["node accuracy"], 1 / 3)
        self.assertEqual(result["link accuracy"], 0.0)


    def test_large_graph_with_mixed_matches(self):
        """Test a larger graph with multiple nodes and partial matches to verify scaling."""
        y_true = {
            "nodes": [
                {"id": "1", "type": "S", "status": "active"},
                {"id": "2", "type": "C", "status": "inactive"},
                {"id": "3", "type": "S", "status": "active"},
                {"id": "4", "type": "C", "status": "inactive"},
                {"id": "5", "type": "DB", "status": "active"}
            ],
            "links": [
                {"source": "1", "target": "5"},
                {"source": "2", "target": "5"},
                {"source": "3", "target": "2"},
                {"source": "4", "target": "10"}
            ]
        }
        y_pred = {
            "nodes": [
                {"id": "a", "type": "S", "status": "active"},
                {"id": "b", "type": "C", "status": "inactive"},
                {"id": "c", "type": "S", "status": "active"},
                {"id": "d", "type": "C", "status": "inactive"},
                {"id": "e", "type": "DB", "status": "active"},
                {"id": "f", "type": "Cache", "status": "active"} # extra unmatched node
            ],
            "links": [
                {"source": "a", "target": "e"},
                {"source": "b", "target": "e"},
                {"source": "c", "target": "b"},
                {"source": "d", "target": "10"},
                {"source": "e", "target": "e"}  # extra self-loop link
            ]
        }

        # Node matches:
        # GT: 1(S,active),2(C,inactive),3(S,active),4(C,inactive),5(DB,active)
        # Pred: A(S,active),B(C,inactive),C(S,active),D(C,inactive),E(DB,active),F(Cache,active)
        # Perfect matching possible:
        # 1->A, 2->B, 3->C, 4->D, 5->E (F is unmatched)
        # correct_nodes=5
        # GT=5, Pred=6 => denominator=6
        # node_accuracy=5/6

        # Links:
        # Consider only links from matched sources. All GT nodes 1,2,3,4 are matched.
        # GT links from these matched sources: (1->5), (2->5), (3->2), (4->10)
        # Translate using mapping:
        # 1->A, 5->E, 2->B, 4->D
        # (1->5) -> (A->E)
        # (2->5) -> (B->E)
        # (3->2) -> (C->B)
        # (4->10) -> (D->10) literal 10 remains 10
        #
        # Pred links with matched sources:
        # Matched sources: {A,B,C,D,E} (all matched except F)
        # Pred links from matched sources:
        # (A->E), (B->E), (C->B), (D->10), (E->E)
        #
        # Matching:
        # (A->E) found in pred
        # (B->E) found in pred
        # (C->B) found in pred
        # (D->10) found in pred
        # correct_links=4
        # GT=4 links considered, Pred=5 links considered
        # More predicted => denominator=5
        # link_accuracy=4/5

        result = accuracy_less_strict(y_true, y_pred, truncate=False)
        self.assertEqual(result["node accuracy"], 5/6)
        self.assertEqual(result["link accuracy"], 4/5)


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)









