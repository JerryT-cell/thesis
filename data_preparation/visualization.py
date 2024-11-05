import networkx as nx
import matplotlib.pyplot as plt
import json


json_uml_diagram_path = "/exploring_datasets/json_diagrams/Activity/0d1debf7-99b0-4e6d-8c61-6522adfa90e8.json"
with open(json_uml_diagram_path, 'r') as file:
    data = json.load(file)


nodes = data["nodes"]
links = data["links"]

# Create directed graph
G = nx.DiGraph()

# Add nodes and edges to the graph
for node in nodes:
    print(node)
    G.add_node(node["id"], label=node["name"] if "name" in node else node["eClass"])

for link in links:
    G.add_edge(link["source"], link["target"])

# Generate layout and plot
pos = nx.spring_layout(G)  # Use spring layout for better visualization
labels = nx.get_node_attributes(G, 'label')

plt.figure(figsize=(15, 15))
nx.draw(G, pos, labels=labels, with_labels=True, node_size=500, node_color='lightblue', font_size=8, font_color='black')
plt.title('Graph Representation')
plt.show()
